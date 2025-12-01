#  Calculadora Bayesiana A/B  
**Interfaz gráfica basada en Streamlit para analizar experimentos A/B utilizando modelos Bayesianos.**

Este proyecto envuelve la lógica estadística desarrollada originalmente por **Pablo González** en una interfaz gráfica moderna construida por **Eduardo Hernández**, permitiendo analizar tests A/B de forma visual, interactiva y accesible.

---

##  ¿Qué es este proyecto?

La herramienta permite analizar pruebas A/B con dos modelos bayesianos:

- **Gamma–Poisson** → para experimentos de *clicks / visitas* (CTR)  
  (Archivo original: `calculadora_bayesiana.py`)

- **Beta–Binomial** → para experimentos de *conversiones / visitas* (datos 0/1)  
  (Archivo original: `calculadora_bayesiana_conversiones.py`)

La aplicación **NO modifica la lógica matemática original**, solo la integra en una experiencia visual clara mediante **Streamlit**.

El proyecto también incluye un **tercer archivo con un modelo frecuentista**, que aún no está integrado en la app.

---


###  Funcionalidades disponibles

- Cargar datos mediante **CSV** o introducirlos manualmente.
- Actualización incremental de parámetros día a día.
- Cálculo de:
  - distribuciones posteriores,
  - probabilidades de que B sea mejor que A,
  - uplift (B vs A),
  - intervalos de credibilidad del 95%.
- Detección automática del ganador.
- Historial detallado (idéntico al output del código original).
- Gráficos visuales:
  - Distribuciones posteriores
  - Diferencias B–A
  - Evolución de tasas
- Interfaz moderna con tarjetas, métricas y colores.

---