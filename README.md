# README agronómico – Uso de previsión climática estacional

## Contexto del proyecto

Este proyecto es una **extensión funcional del sistema sig-riego-rdc**, orientada a incorporar **información climática de previsión estacional** como apoyo a la planificación agronómica.

El objetivo no es sustituir los cálculos agronómicos existentes, sino **anticipar escenarios climáticos futuros** que permitan mejorar la toma de decisiones en riego y fertilización a medio plazo, manteniendo la coherencia técnica del modelo original.

---

## Naturaleza de los datos climáticos utilizados

Los datos empleados proceden del conjunto:

**“Seasonal forecast monthly statistics on single levels”** (Climate Data Store – Copernicus).

Estos datos **no son observaciones históricas** ni registros medidos en estaciones meteorológicas. Tampoco constituyen una predicción meteorológica diaria.

Se definen correctamente como:

> **Previsiones climáticas estacionales**, generadas por el sistema ECMWF (SEAS5), que estiman el comportamiento medio mensual del clima con varios meses de antelación mediante simulaciones probabilísticas (ensemble forecasts).

Cada mes se publica una nueva inicialización del modelo, a partir de la cual se generan escenarios climáticos para los meses siguientes.

---

## Por qué se trabaja con previsión climática estacional

La planificación agronómica (riego, abonado, manejo del cultivo) **no se apoya en decisiones diarias**, sino en estrategias definidas a escala semanal, mensual o estacional.

En este contexto:

* Los datos observados describen el pasado, pero **no permiten anticipar** escenarios futuros.
* Las predicciones meteorológicas a corto plazo **no son fiables** más allá de 7–10 días.
* La previsión climática estacional permite **anticipar tendencias** (meses más secos, más cálidos, o cercanos a la normalidad).

Por ello, este tipo de datos es el **más adecuado** para apoyar decisiones como:

* Dimensionamiento de necesidades hídricas futuras.
* Evaluación de riesgo de déficit o exceso hídrico.
* Ajuste preventivo de estrategias de fertilización.
* Planificación general de campaña.

---

## Coherencia con la lógica agronómica del sistema

El uso de previsión estacional **no modifica la lógica agronómica del modelo**, que se mantiene intacta:

```
ET₀ → ETc → Pe → NHn → RDC → reparto semanal
```

La única diferencia es la **fuente de información climática**, que pasa de ser observada a ser prevista.

Esto garantiza:

* Coherencia técnica.
* Reutilización del conocimiento agronómico existente.
* Interpretabilidad de los resultados por parte de técnicos y asesores.

---

## Método de cálculo de la evapotranspiración

Dado que la previsión estacional no proporciona todas las variables necesarias para Penman–Monteith (viento, humedad, radiación), se emplea el método **Hargreaves**, que:

* Requiere únicamente temperatura máxima, mínima y media.
* Es estable a escala mensual.
* Está ampliamente aceptado para estudios de planificación y escenarios climáticos.

Este enfoque evita introducir incertidumbre artificial derivada de variables no previstas.

---

## Alcance y limitaciones

Este sistema:

* **No pretende predecir el tiempo exacto** de un día concreto.
* **No sustituye** a la información observada o a la meteorología operativa.
* **Sí aporta valor** como herramienta de apoyo a la planificación agronómica.

Los resultados deben interpretarse como **escenarios probables**, no como certezas deterministas.

---

## Conclusión

La integración de previsión climática estacional permite evolucionar el sistema hacia un enfoque **proactivo**, anticipando necesidades y riesgos antes de que se materialicen.

Este enfoque es coherente con:

* La escala real de decisión agronómica.
* La robustez técnica exigida a nivel europeo.
* El desarrollo de herramientas digitales avanzadas para la gestión sostenible del riego y la fertilización.

---

*Documento orientado a uso interno técnico y documentación de proyecto.*
