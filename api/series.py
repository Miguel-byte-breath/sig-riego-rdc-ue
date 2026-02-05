import json
import math
import calendar
from datetime import datetime
from pathlib import Path

import numpy as np
import xarray as xr
import cftime
from huggingface_hub import hf_hub_download


# ----------------------------
# CONFIG (EDITA ESTO)
# ----------------------------
HF_REPO_ID = "TU_USUARIO_HF/sig-riego-rdc-raw"  # <-- CAMBIA ESTO
NC_FILES = [
    "cds_fc_2023_2024.nc",
    "cds_fc_2025_2025.nc",
    "cds_fc_2026_2026.nc",
]
LEAD = 1  # leadtime_month


# ----------------------------
# Helpers de tu pipeline
# ----------------------------
def lon_to_360(lon: float) -> float:
    return lon % 360.0


def nearest_idx(values: np.ndarray, target: float) -> int:
    return int(np.argmin(np.abs(values - target)))


def add_months(dt: datetime, months: int) -> datetime:
    y = dt.year + (dt.month - 1 + months) // 12
    m = (dt.month - 1 + months) % 12 + 1
    return datetime(y, m, 1)


def seconds_in_month(year: int, month: int) -> int:
    days = calendar.monthrange(year, month)[1]
    return days * 86400


def parse_frt_to_datetime(frt_value, frt_attrs) -> datetime:
    if isinstance(frt_value, np.datetime64):
        return frt_value.astype("datetime64[ns]").astype(datetime)

    if isinstance(frt_value, (str, np.str_)):
        s = str(frt_value)
        try:
            return datetime.fromisoformat(s.replace("Z", ""))
        except Exception:
            pass

    if isinstance(frt_value, (int, np.integer)):
        s = str(int(frt_value))
        if len(s) == 8:
            return datetime(int(s[0:4]), int(s[4:6]), int(s[6:8]))

    units = frt_attrs.get("units") if isinstance(frt_attrs, dict) else None
    cal = frt_attrs.get("calendar", "standard") if isinstance(frt_attrs, dict) else "standard"
    if units and "since" in str(units).lower():
        dt_cf = cftime.num2date(frt_value, units=units, calendar=cal)
        return datetime(int(dt_cf.year), int(dt_cf.month), int(dt_cf.day))

    raise ValueError(f"No puedo interpretar forecast_reference_time={frt_value} units={units} cal={cal}")


def day_of_year_midmonth(year: int, month: int) -> int:
    import datetime as dt
    return int(dt.date(year, month, 15).timetuple().tm_yday)


def ra_mm_day(lat_deg: float, year: int, month: int) -> float:
    Gsc = 0.0820
    phi = math.radians(lat_deg)
    J = day_of_year_midmonth(year, month)

    dr = 1 + 0.033 * math.cos(2 * math.pi / 365 * J)
    delta = 0.409 * math.sin(2 * math.pi / 365 * J - 1.39)
    ws = math.acos(max(-1.0, min(1.0, -math.tan(phi) * math.tan(delta))))

    ra_mj_m2_day = (24 * 60 / math.pi) * Gsc * dr * (
        ws * math.sin(phi) * math.sin(delta) + math.cos(phi) * math.cos(delta) * math.sin(ws)
    )
    return 0.408 * ra_mj_m2_day


def eto_hargreaves_mm_day(tmean_c: float, tmax_c: float, tmin_c: float, ra_mm_day_val: float) -> float:
    td = max(0.0, tmax_c - tmin_c)
    return 0.0023 * (tmean_c + 17.8) * math.sqrt(td) * ra_mm_day_val


def parse_fecha_yyyy_mm(fecha: str) -> tuple[int, int]:
    y, m = fecha.split("-")[:2]
    return int(y), int(m)


def extract_from_nc(nc_path: str, lat: float, lon: float) -> dict:
    ds = xr.open_dataset(nc_path, engine="netcdf4", decode_times=False)

    lats = ds["latitude"].values
    lons = ds["longitude"].values

    lon_req = lon
    if np.nanmin(lons) >= 0 and np.nanmax(lons) > 180:
        lon_req = lon_to_360(lon_req)

    i_lat = nearest_idx(lats, lat)
    i_lon = nearest_idx(lons, lon_req)

    lat_sel = float(lats[i_lat])
    lon_sel = float(lons[i_lon])

    sub = ds.isel(latitude=i_lat, longitude=i_lon)

    # forecastMonth = 1
    fmonths = sub["forecastMonth"].values
    if np.ndim(fmonths) == 0:
        fmonths = np.array([int(fmonths)])
    fmonths = [int(x) for x in np.ravel(fmonths).tolist()]
    if 1 not in fmonths:
        raise ValueError(f"No encuentro forecastMonth=1. Disponibles: {fmonths}")

    sub = sub.sel(forecastMonth=1)

    frt_da = sub["forecast_reference_time"]
    frts = np.ravel(frt_da.values)
    frt_attrs = dict(frt_da.attrs) if hasattr(frt_da, "attrs") else {}

    rows = []
    for i in range(len(frts)):
        frt_dt = parse_frt_to_datetime(frts[i], frt_attrs)
        valid_dt = add_months(datetime(frt_dt.year, frt_dt.month, 1), LEAD)
        fecha = f"{valid_dt.year:04d}-{valid_dt.month:02d}"
        sec = seconds_in_month(valid_dt.year, valid_dt.month)

        sli = sub.isel(forecast_reference_time=i)
        row = {"fecha": fecha}

        if "t2m" in sli:
            t2m_k = np.squeeze(sli["t2m"].values)
            row["tmed"] = float(np.mean(t2m_k) - 273.15)
        if "mx2t24" in sli:
            mx_k = np.squeeze(sli["mx2t24"].values)
            row["tmax"] = float(np.mean(mx_k) - 273.15)
        if "mn2t24" in sli:
            mn_k = np.squeeze(sli["mn2t24"].values)
            row["tmin"] = float(np.mean(mn_k) - 273.15)
        if "tprate" in sli:
            tpr = np.squeeze(sli["tprate"].values)
            row["p"] = float(np.mean(tpr) * sec * 1000.0)

        rows.append(row)

    rows.sort(key=lambda r: r["fecha"])
    dedup = {}
    for r in rows:
        dedup[r["fecha"]] = r
    rows = [dedup[k] for k in sorted(dedup.keys())]

    for r in rows:
        for k in ("tmed", "tmax", "tmin", "p"):
            if k in r and r[k] is not None:
                r[k] = round(float(r[k]), 3)

    return {
        "meta": {
            "input_file": nc_path,
            "leadtime_month": LEAD,
            "point": {"lat_req": lat, "lon_req": lon, "lat_sel": lat_sel, "lon_sel": lon_sel},
        },
        "data": rows,
    }


def merge_series(objs: list[dict]) -> dict:
    by_date = {}
    for obj in objs:
        for r in obj["data"]:
            by_date[r["fecha"]] = r  # last wins
    data = [by_date[k] for k in sorted(by_date.keys())]

    meta0 = objs[0].get("meta", {})
    return {
        "meta": {**meta0, "merged_from": [o.get("meta", {}).get("input_file") for o in objs], "n_months": len(data)},
        "data": data,
    }


def add_eto(series_obj: dict, lat: float) -> dict:
    out_rows = []
    for r in series_obj["data"]:
        year, month = parse_fecha_yyyy_mm(r["fecha"])
        tmean = float(r["tmed"])
        tmax = float(r["tmax"])
        tmin = float(r["tmin"])
        p_mes = float(r["p"]) if r.get("p") is not None else None

        ra = ra_mm_day(lat, year, month)
        eto_d = eto_hargreaves_mm_day(tmean, tmax, tmin, ra)
        eto_mes = eto_d * calendar.monthrange(year, month)[1]

        out_rows.append({
            "fecha": r["fecha"],
            "tmed": round(tmean, 2),
            "tmax": round(tmax, 2),
            "tmin": round(tmin, 2),
            "p": round(p_mes, 2) if p_mes is not None else None,
            "ra_mm_d": round(ra, 3),
            "eto_mm_d": round(eto_d, 3),
            "eto_mes": round(eto_mes, 2),
        })

    return {
        "meta": {**(series_obj.get("meta") or {}), "metodo": "Hargreaves-Samani (FAO-56)", "lat": lat},
        "data": out_rows,
    }


# ----------------------------
# Vercel handler
# ----------------------------
def handler(request):
    try:
        body = request.get_json()
        lat = float(body["lat"])
        lon = float(body["lon"])
    except Exception:
        return (json.dumps({"error": "Body debe ser JSON con {lat, lon}"}), 400, {"Content-Type": "application/json"})

    try:
        # Descarga/cache de NetCDF desde HF (hf_hub_download cachea en disco automáticamente)
        local_paths = []
        for fn in NC_FILES:
            p = hf_hub_download(repo_id=HF_REPO_ID, repo_type="dataset", filename=fn)
            local_paths.append(p)

        extracted = [extract_from_nc(p, lat, lon) for p in local_paths]
        merged = merge_series(extracted)
        eto = add_eto(merged, lat)

        return (json.dumps(eto, ensure_ascii=False), 200, {"Content-Type": "application/json"})
    except Exception as e:
        return (json.dumps({"error": str(e)}, ensure_ascii=False), 500, {"Content-Type": "application/json"})
