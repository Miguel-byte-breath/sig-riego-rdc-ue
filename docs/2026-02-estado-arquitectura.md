```# Checkpoint — Estado Arquitectura Proyecto
Fecha: 16 de Febrero 2026

## Infraestructura actual

### GitHub
Repositorio principal:
Miguel-byte-breath/sig-riego-rdc-ue

/api
   ping.py        → test runtime OK
   series.py      → backend principal
/data
   bunol_fc_...   → JSON de prueba (artefacto de validación)
/requirements.txt
/vercel.json
/index
/cultivos.json
```

\- El código fuente oficial

\- El que está conectado a Vercel

\- El que despliega producción automáticamente



---



\### ✅ Vercel — App web + Backend serverless



Proyecto: `sig-riego-rdc-ue`  

Dominio: `sig-riego-rdc-ue.vercel.app`



\- Runtime Python funcionando

\- `/api/ping` → OK

\- `/api/series` → OK (infraestructura correcta)



Problemas estructurales ya resueltos:



\- ❌ 404

\- ❌ Repo incorrecto

\- ❌ Root directory mal

\- ❌ Repo HF mal configurado

\- ❌ Cache en filesystem read-only



Estamos en fase de ajuste fino (`/tmp` para cache).



---



\### ✅ Hugging Face — Almacén de datos brutos



Dataset:



`Miguel-byte-breath/sig-riego-rdc-raw`



Contiene:



\- `cds\_fc\_2023\_2024.nc`

\- `cds\_fc\_2025\_2025.nc`

\- `cds\_fc\_2026\_2026.nc`



Funciona como:



\- 📦 Almacén gratuito

\- Persistente

\- Accesible vía `hf\_hub\_download`

\- Separado del código



Arquitectónicamente correcto.



---



\## 🧠 Flujo conceptual actual



Usuario → Vercel `/api/series`  

→ descarga NetCDF desde Hugging Face  

→ extrae punto lat/lon  

→ calcula:



\- tmed

\- tmax

\- tmin

\- precipitación

\- ETo (Hargreaves)



→ devuelve JSON



No hay ficheros intermedios.  

No hay almacenamiento local.  

Todo es bajo demanda.



Eso es exactamente lo que querías.



---



\## 🎯 Hacia dónde vamos



Estamos construyendo:



Una \*\*API climática agronómica serverless\*\*, que:



\- No depende de ficheros precalculados

\- No almacena datos en Vercel

\- Se apoya en:

&nbsp; - Hugging Face (datos)

&nbsp; - CDS (fuente original)

&nbsp; - Vercel (cómputo bajo demanda)



Es una arquitectura:



\- Escalable

\- Barata

\- Modular

\- Limpia conceptualmente



---



\## 🧩 Qué NO forma parte del producto final



\- JSON en `/data` → solo validación

\- Pipeline local → solo generación y pruebas

\- Cálculos offline → solo control técnico



El producto final es la API.



---



\## 📌 Estado real hoy



Infraestructura: ✔️ correcta  

Conectividad HF: ✔️ correcta  

Serverless runtime: ✔️ correcto  



Pendiente técnico actual:  

👉 usar `cache\_dir="/tmp"` para evitar error de filesystem read-only



Nada estructural está mal.  

Estamos en fase de consolidación técnica.



