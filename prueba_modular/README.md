# Análisis GDP G7 (1980-2010) - Enfoque Modular

## Resumen Ejecutivo

Este análisis examina la evolución del GDP per capita de los países del G7 durante el período 1980-2010, utilizando un enfoque modular con herramientas de FRED MCP.

**Fuente de datos:** FRED (Federal Reserve Economic Data)
**Métrica:** Constant GDP per capita (2010 US Dollars)
**Período:** 1980-2010 (31 años)
**Países:** USA, Canada, Japan, Germany, France, Italy, United Kingdom

---

## Hallazgos Principales

### 1. Rankings 2010

**Por Nivel de GDP per capita:**
1. USA: $52,812.68
2. United Kingdom: $42,311.43
3. Canada: $41,164.34
4. Germany: $38,517.44
5. France: $35,578.20
6. Japan: $32,942.20
7. Italy: $31,928.55

**Por Tasa de Crecimiento (CAGR):**
1. United Kingdom: 1.98%
2. Japan: 1.79%
3. USA: 1.78%
4. Germany: 1.59%
5. France: 1.46%
6. Canada: 1.34%
7. Italy: 1.26%

**Por Estabilidad:**
1. France: 0.4125 (volatilidad: 1.42%)
2. Italy: 0.3445 (volatilidad: 1.90%)
3. USA: 0.3396 (volatilidad: 1.94%)

### 2. Convergencia Sigma: DIVERGENCIA DETECTADA ❌

- **Coeficiente de Variación 1980:** 0.1587
- **Coeficiente de Variación 2010:** 0.1811
- **Cambio:** +0.0224
- **Tendencia:** Pendiente positiva (0.001207)
- **Significancia:** p-value = 0.0004 (< 0.05)

**Interpretación:** Los países del G7 se están volviendo MÁS diferentes en términos de GDP per capita. La dispersión entre países aumentó durante el período, lo que indica divergencia económica en lugar de convergencia.

### 3. Convergencia Beta: NO SIGNIFICATIVA ⭕

- **Pendiente (β):** -0.0141
- **R²:** 0.0001
- **p-value:** 0.9859 (>> 0.05)

**Interpretación:** No hay evidencia de "catch-up effect". Los países con menor GDP inicial no crecieron sistemáticamente más rápido que los países ricos.

### 4. Structural Breaks (Crisis Detectadas)

**Crisis Globales Identificadas:**
- **2008-2009:** Crisis Financiera Global - Detectada en TODOS los países G7
- **1990-1992:** Recesión de principios de los 90 - Detectada en múltiples países
- **2000-2001:** Dot-com bubble - Visible principalmente en USA

**Países con Mayor Volatilidad:**
- USA: 11 structural breaks detectados
- Germany: 13 structural breaks
- Italy: 14 structural breaks

---

## Metodología Modular

### Fase 1: Descubrimiento de Series
- **Herramienta:** `search_fred_series`
- **Objetivo:** Encontrar series IDs para cada país del G7
- **Series encontradas:**
  - USA: NYGDPPCAPKDUSA
  - Canada: NYGDPPCAPKDCAN
  - Japan: NYGDPPCAPKDJPN
  - Germany: NYGDPPCAPKDDEU
  - France: NYGDPPCAPKDFRA
  - Italy: NYGDPPCAPKDITA
  - United Kingdom: NYGDPPCAPKDGBR

### Fase 2: Obtención de Observaciones
- **Herramienta:** `get_fred_series_observations`
- **Período:** 1980-01-01 a 2010-12-31
- **Frecuencia:** Anual
- **Unidades:** Linear (sin transformación)
- **Observaciones por país:** 31 (1980-2010)

### Fase 3: Procesamiento y Métricas
**Métricas calculadas:**
- **CAGR:** Tasa de crecimiento anual compuesta
- **Volatilidad:** Desviación estándar de tasas de crecimiento año-a-año
- **Índice de Estabilidad:** 1 / (1 + volatilidad)
- **Crecimiento Total:** Cambio porcentual de inicio a fin

### Fase 4: Análisis de Convergencia
**Sigma Convergence:**
- Regresión lineal: CV = a + b*tiempo
- Test de significancia estadística

**Beta Convergence:**
- Regresión: CAGR = a + b*log(GDP_inicial)
- Test de catch-up effect

### Fase 5: Detección de Structural Breaks
- **Método:** Ventana móvil de 5 años
- **Criterio:** Cambios > 50% en varianza móvil
- **Identificación:** Aumentos y reducciones de volatilidad

### Fase 6: Visualización
7 gráficos generados mostrando:
1. Evolución temporal del GDP
2. Ranking por CAGR
3. Test de convergencia beta
4. Test de convergencia sigma
5. Comparación de volatilidad
6. Línea de tiempo de structural breaks
7. Ranking final GDP 2010

---

## Archivos Generados

### Datos
- `gdp_data_raw.csv` - Datos crudos en formato tidy
- `analysis_results.json` - Todos los resultados en formato JSON

### Visualizaciones
- `1_gdp_evolution.png` - Evolución del GDP per capita
- `2_cagr_ranking.png` - Ranking por tasa de crecimiento
- `3_beta_convergence.png` - Test de convergencia beta
- `4_sigma_convergence.png` - Test de convergencia sigma
- `5_volatility_comparison.png` - Comparación de volatilidad
- `6_structural_breaks.png` - Línea de tiempo de quiebres estructurales
- `7_final_gdp_ranking.png` - Ranking GDP 2010

### Scripts
- `gdp_analysis.py` - Script principal de análisis
- `create_visualizations.py` - Generación de gráficos

---

## Conclusiones

1. **Liderazgo Económico:** USA mantiene el liderazgo en GDP per capita absoluto ($52,812 en 2010), pero UK tuvo el mayor crecimiento (1.98% CAGR).

2. **Divergencia Regional:** Contrario a teorías de convergencia, los países G7 se distanciaron económicamente entre 1980-2010. El coeficiente de variación aumentó de 0.159 a 0.181.

3. **No Hay Catch-Up Effect:** Los países con menor GDP inicial (como Italia y Japan en 1980) no mostraron tasas de crecimiento significativamente mayores.

4. **Crisis del 2008:** Impactó a TODOS los países G7 con aumentos dramáticos de volatilidad detectados entre 2007-2008.

5. **Estabilidad vs Crecimiento:** Francia mostró la mayor estabilidad (menor volatilidad), pero no el mayor crecimiento. UK combinó alto crecimiento con volatilidad moderada.

---

## Herramientas FRED MCP Utilizadas

- `search_fred_series` - Búsqueda de series económicas
- `get_fred_series_observations` - Obtención de datos históricos

**Ventajas del Enfoque Modular:**
- ✅ Transparencia completa del proceso
- ✅ Flexibilidad para análisis personalizados
- ✅ Trazabilidad de cada paso
- ✅ Fácil extensión a nuevos países/períodos
- ✅ Reproducibilidad total

---

## Metadata

**Fecha de análisis:** 2025-11-08
**Fuente:** Federal Reserve Economic Data (FRED)
**Tipo de serie:** Constant GDP per capita (2010 US Dollars)
**Frecuencia:** Anual
**Método:** Análisis modular con herramientas FRED MCP
**Lenguaje:** Python 3.10
**Librerías:** pandas, numpy, scipy, matplotlib
