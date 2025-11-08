# Propuesta de herramienta: analyze_gdp_cross_country

**Fecha:** 2025-11-03  
**Versión propuesta:** v1.0.0-proposal-final  
**Status:** Production-ready proposal

---

## 📋 Resumen ejecutivo

**"La herramienta definitiva para análisis de PIB comparativo."** 

Esta propuesta detalla `analyze_gdp_cross_country`, una herramienta enfocada exclusivamente en PIB y población, diseñada para producir análisis reproducibles, datasets listos para ML y reportes analíticos avanzados (convergencia sigma/beta, volatilidad, structural breaks, rankings dinámicos y más).

### Diferenciadores clave
- ✅ **8 variantes de PIB** con cálculo automático de derivadas
- ✅ **Análisis económico profundo**: convergencia, structural breaks, outliers
- ✅ **3 formatos de salida**: analysis (JSON), dataset (tidy), summary (snapshot)
- ✅ **238 países disponibles** con series históricas desde 1960
- ✅ **Arquitectura modular**: fetch → analysis → format
- ✅ **Trazabilidad completa**: metadata, source_series, transformations

---

## 🎯 Visión simplificada

- **Enfoque único:** PIB en todas sus formas + población (esencial para per capita)
- **Cobertura:** Hasta 238 países, series históricas desde 1960 cuando disponibles
- **Salidas:** `"analysis"` (JSON analítico), `"dataset"` (tidy long), `"summary"` (snapshot), `"both"` (JSON + DataFrame)
- **Análisis:** Convergencia sigma/beta, structural breaks, volatilidad, rankings dinámicos

---

## 📝 Función - Firma propuesta

```python
def analyze_gdp_cross_country(
    # === PAÍSES ===
    countries: List[str] | str,
    # Ejemplos: "argentina", ["argentina", "brazil"], "latam", "oecd", "emerging"
    
    # === QUÉ ANALIZAR ===
    gdp_variants: Optional[List[str]] = None,
    # None = todas las variantes disponibles
    # Options:
    #   - "nominal_usd"          # PIB nominal en USD corrientes
    #   - "nominal_lcu"          # PIB nominal en moneda local
    #   - "constant_2010"        # PIB constante (USD 2010)
    #   - "per_capita_nominal"   # PIB per capita nominal USD
    #   - "per_capita_constant"  # PIB per capita constante (USD 2010)
    #   - "per_capita_ppp"       # PIB per capita ajustado por PPP
    #   - "growth_rate"          # Tasa de crecimiento anual % (computed)
    #   - "ppp_adjusted"         # PIB total ajustado PPP
    
    include_population: bool = True,  # Necesario para per capita, útil para contexto
    
    # === PERÍODO ===
    start_date: Optional[str] = None,  # Default: "1960-01-01"
    end_date: Optional[str] = None,    # Default: latest available
    period_split: Optional[str] = None,  # NEW: "decade", "5y", "custom" → análisis por subperíodos
    
    # === MODO DE COMPARACIÓN ===
    comparison_mode: str = "absolute",
    # Options:
    #   - "absolute": Valores absolutos (USD, personas)
    #   - "indexed": Todo normalizado a 100 en base_year
    #   - "per_capita": Enfoque en per capita
    #   - "growth_rates": Solo tasas de crecimiento
    #   - "ppp": Ajustado por poder de compra
    #   - "relative_to_benchmark": Normalizar por benchmark cuando benchmark_against seteado
    
    base_year: Optional[int] = None,  # Para indexed mode (ej: 2000)
    
    # === ANÁLISIS ===
    include_rankings: bool = True,            # Ranking por variante
    include_convergence: bool = True,         # Convergencia sigma/beta con sigma_trend_slope
    include_growth_analysis: bool = True,     # CAGR, volatility, stability_index
    calculate_productivity: bool = False,     # GDP per hour worked (requires labor data)
    detect_structural_breaks: bool = True,    # NEW: Chow test / rolling variance
    
    # === OUTPUT ===
    output_format: str = "analysis",  
    # Options: "analysis", "dataset", "summary", "both" (JSON + DataFrame)
    frequency: str = "annual",        # "annual", "quarterly" (auto-agrega si necesario)
    
    # === TÉCNICO ===
    fill_missing: str = "interpolate",  # "interpolate", "forward", "drop"
    align_method: str = "inner",        # "inner", "outer"
    benchmark_against: Optional[str] = None,  # "usa", "world", "oecd_avg"
    validate_variants: bool = True      # NEW: Validar dependencias antes de fetch
) -> Dict:
    """
    Analyze GDP across countries with deep economic analysis.
    
    Returns comprehensive JSON with rankings, convergence analysis, 
    structural breaks, volatility metrics, and tidy datasets.
    
    See full documentation for output structure and examples.
    """
```

---

## 🌍 Presets expandidos

Se soportan alias/presets predefinidos para facilitar análisis exploratorios:

```python
PRESETS = {
    # América Latina
    "latam": ["argentina", "brazil", "chile", "colombia", "peru", "mexico", "uruguay"],
    
    # Organizaciones internacionales
    "oecd": [...],  # 38 países OECD
    "g7": ["usa", "canada", "uk", "france", "germany", "italy", "japan"],
    "g20": [...],   # 19 países + UE
    "brics": ["brazil", "russia", "india", "china", "south_africa"],
    
    # Clasificación por desarrollo (FMI/World Bank)
    "emerging": ["argentina", "brazil", "china", "india", "mexico", "turkey", ...],
    "developed": ["usa", "canada", "uk", "germany", "france", "japan", ...],
    
    # Regionales
    "north_america": ["usa", "canada", "mexico"],
    "eurozone": [...],
    "asia_pacific": [...],
    
    # Especial
    "world": "all_available",  # Todos los países con data
}
```

**Configuración personalizada:** Soporta archivo YAML para presets custom:
```yaml
# custom_presets.yaml
my_analysis:
  - chile
  - singapore
  - ireland
  - estonia
```

---

## 📊 GDP Variants - Tabla completa con trazabilidad
---

## 📊 GDP Variants - Tabla completa con trazabilidad

| Variant | Series pattern (FRED) | Disponibilidad | Computed? | Dependencies | Uso principal |
|---|---|---|:---:|---|---|
| `nominal_usd` | `NYGDPMKTPCD{country}` | 200+ países, 1960-2024 | ❌ | - | Tamaño económico nominal en USD |
| `nominal_lcu` | `NYGDPMKTPKN{country}` | ~180 países | ❌ | - | Análisis en moneda local (sin FX) |
| `constant_2010` | `NYGDPMKTPKD{country}` | 200+ países | ❌ | - | Crecimiento real base 2010 |
| `per_capita_nominal` | `PCAGDP{country}` | 200+ países | ❌ | - | Estándar de vida (USD corrientes) |
| `per_capita_constant` | `NYGDPPCAPKD{country}` | **238 países** ⭐ | ❌ | - | Progreso real (más usada) |
| `per_capita_ppp` | `NYGDPPCAPPPKD{country}` | ~180 países, 1990+ | ❌ | - | Comparación ajustada por compra |
| `growth_rate` | *Calculated* | 200+ países | ✅ | `constant_2010` | Velocidad de crecimiento % |
| `ppp_adjusted` | `PPPGDP{country}` | ~180 países | ❌ | - | PIB total ajustado PPP |

**Población (esencial):** `POPTOT{country}647NWDB` (200+ países, 1960-2024)

### GDP Variant Dependencies

Definición interna para validación y cálculo automático:

```python
GDP_VARIANT_DEPENDENCIES = {
    "growth_rate": {
        "source": "constant_2010",
        "formula": "((value_t / value_t-1) - 1) * 100",
        "fallback": None
    },
    "per_capita_nominal": {
        "source": ["nominal_usd", "population"],
        "formula": "(gdp_billion * 1e9) / population",
        "fallback": "fetch_direct"  # Intenta FRED primero
    },
    "per_capita_constant": {
        "source": ["constant_2010", "population"],
        "formula": "(gdp_billion * 1e9) / population",
        "fallback": "fetch_direct"
    },
    "per_capita_ppp": {
        "source": ["ppp_adjusted", "population"],
        "formula": "(gdp_billion * 1e9) / population",
        "fallback": "fetch_direct"
    }
}
```

### Orden de precedencia para per capita

Cuando se calcula per capita (si no existe directamente):
1. **PPP** > Constant > Nominal (preferir ajuste por compra)
2. Si `per_capita_ppp` no existe pero `ppp_adjusted` sí → calcular
3. Si `constant_2010` existe → calcular `per_capita_constant`
4. Último recurso: `nominal_usd` / `population`

### Validación dinámica

```python
def validate_variants(requested_variants: List[str], dependencies: Dict) -> Dict:
    """
    Valida que las variantes solicitadas tengan sus dependencias disponibles.
    
    Returns:
        {
            "valid": [...],
            "computable": [...],  # Pueden ser calculadas
            "missing_dependencies": {variant: [missing_sources]},
            "warnings": [...]
        }
    """
    pass
```

---

## 🏗️ Arquitectura: 3-layer modular design

### Layer 1: fetch_data_layer

**Responsabilidades:**
- Fetch series desde FRED/World Bank
- Caching inteligente (disk + memory)
- Rate-limit handling
- Missing data detection
- Frequency harmonization (quarterly → annual si necesario)

**Output:** `Dict[country][variant] = pd.Series` (time-indexed, cleaned)

```python
def fetch_data_layer(
    countries: List[str],
    variants: List[str],
    start_date: str,
    end_date: str,
    frequency: str
) -> FetchResult:
    """
    Returns:
        FetchResult(
            data=Dict[country][variant],
            metadata=FetchMetadata(
                series_fetched=count,
                missing_series=[...],
                source_series={variant: series_id},
                fetch_timestamps={...}
            )
        )
    """
    pass
```

### Layer 2: analysis_layer

**Responsabilidades:**
- Growth calculations (CAGR, volatility, stability_index)
- Convergence tests (sigma con trend_slope, beta con p-value)
- Structural breaks detection (Chow test / rolling variance)
- Outlier detection (±2σ rule)
- Benchmark gaps
- Rankings dinámicos (rank_change over time)

**Output:** `AnalysisResult` con todos los cálculos

```python
def analysis_layer(
    data: Dict,
    analysis_config: AnalysisConfig
) -> AnalysisResult:
    """
    Returns:
        AnalysisResult(
            by_country={...},
            cross_country={
                "convergence": {...},
                "structural_breaks": [...],
                "volatility_ranking": [...],
                "outliers": [...]
            },
            rankings={...},
            benchmark_gaps={...} if benchmark
        )
    """
    pass
```

#### Structural Breaks Detection (nuevo)

**Método 1: Chow Test**
- Divide serie en dos períodos (split point = median year)
- Estima regresión lineal para cada subperíodo
- H0: No hay cambio estructural (coeficientes iguales)
- Output: F-statistic, p-value, break_detected (bool)

**Método 2: Rolling Variance**
- Ventana móvil 5 años
- Detecta cambios significativos en σ² (variance doubling/halving)
- Identifica períodos de alta volatilidad

**Output:**
```json
{
    "structural_breaks": {
        "usa": {
            "chow_test": {
                "split_year": 1990,
                "f_statistic": 8.42,
                "p_value": 0.0003,
                "break_detected": true
            },
            "rolling_variance": {
                "high_volatility_periods": [
                    {"start": 2008, "end": 2009, "variance_ratio": 4.2}
                ]
            }
        }
    }
}
```

#### Enhanced Convergence Metrics

**Sigma Convergence (mejorado):**
- Calcula σ (cross-country std dev) por año
- Agrega `sigma_trend_slope`: pendiente de regresión σ ~ time
  - Negativa → converging
  - Positiva → diverging
  - Cercana a 0 → estable
- Interpretation: "Countries converging at 0.15% per year (p<0.01)"

**Beta Convergence (sin cambios):**
- Regresión: growth_rate ~ initial_gdp
- Negative β + p<0.05 → convergence confirmada

**Stability Index (nuevo):**
- Formula: `stability_index = CAGR / std_dev(growth_rate)`
- Interpretación: 
  - >2.0 → crecimiento estable y predecible
  - <1.0 → crecimiento volátil o bajo

#### Rankings Dinámicos

**rank_change tracking:**
- Compara ranking en `start_date` vs `end_date`
- Output: `{"usa": {"start_rank": 1, "end_rank": 1, "change": 0}}`
- Identifica países que mejoraron/empeoraron posición

**Example:**
```json
{
    "rankings": {
        "by_variant": {
            "per_capita_constant": {
                "top_10_end": [...],
                "rank_changes": {
                    "china": {"start_rank": 78, "end_rank": 45, "change": -33}
                }
            }
        }
    }
}
```

### Layer 3: format_layer

**Responsabilidades:**
- Generación de JSON analysis (compacto, AI-friendly)
- Transformación a tidy dataset (`id_vars`, `value_vars`)
- Summary generation (markdown/plain text)
- Metadata enrichment (source_series traceability)

**Output formats:**

#### 1. `output_format="analysis"` (default)
JSON compacto con análisis completo:
```json
{
    "tool": "analyze_gdp_cross_country",
    "request": {...},
    "metadata": {
        "series_fetched": 150,
        "missing_series": ["ppp_adjusted_ven"],
        "source_series": {
            "nominal_usd": "NYGDPMKTPCD{country}",
            "per_capita_constant": "NYGDPPCAPKD{country}",
            "population": "POPTOT{country}647NWDB"
        },
        "fetch_timestamp": "2025-01-15T10:30:00Z"
    },
    "analysis": {
        "by_country": {...},
        "cross_country": {
            "convergence": {
                "sigma": {
                    "start": 15234.5,
                    "end": 12890.3,
                    "trend_slope": -45.2,
                    "interpretation": "Converging at 45.2 USD/year (p=0.002)"
                },
                "beta": {...}
            },
            "structural_breaks": [...],
            "volatility_ranking": [...]
        },
        "rankings": {
            "by_variant": {
                "per_capita_constant": {
                    "top_10_end": [...],
                    "rank_changes": {...}
                }
            }
        }
    },
    "limitations": [...]
}
```

#### 2. `output_format="dataset"`
Tidy DataFrame listo para visualización:
```python
# id_vars: ['country', 'year', 'region'] 
# value_vars: ['gdp_value', 'variant_type']

   country  year  region         variant_type    gdp_value  source_series
0      usa  2020  g7        per_capita_constant    63543.2  NYGDPPCAPKDUSA
1      usa  2021  g7        per_capita_constant    64102.5  NYGDPPCAPKDUSA
2      chn  2020  brics     per_capita_constant    10408.7  NYGDPPCAPKDCHN
...
```

**Ventajas:**
- Compatible con `seaborn`, `plotly`, `pandas.plot()`
- Fácil filtrado: `df[df.variant_type == "per_capita_constant"]`
- Trazabilidad: columna `source_series` para cada observación

#### 3. `output_format="summary"`
Resumen ejecutivo en markdown:
```markdown
# GDP Cross-Country Analysis: G7 (2000-2023)

## Key Findings
- **Convergence:** Sigma declined from 15234 to 12890 USD (−15.4%, p<0.01)
- **Growth Champions:** China (+9.2% CAGR), India (+6.8%)
- **Structural Breaks Detected:** USA (2008), Japan (1990), China (2015)

## Top Performers (per_capita_constant)
1. USA: $63,543 (2023) — stable growth (stability_index=2.4)
2. Germany: $51,203 (2023) — rank improved (+2)
3. ...

## Volatility Leaders
1. Greece: σ=4.2% (2010-2015 crisis)
2. ...
```

#### 4. `output_format="both"` ⭐ (nuevo)
Retorna tupla `(analysis_json, dataset_df)`:
```python
result = analyze_gdp_cross_country(
    regions=["g7"],
    variants=["per_capita_constant"],
    start_date="2000-01-01",
    output_format="both"
)
# result = (analysis_dict, tidy_dataframe)
analysis, df = result

# Inmediatamente graficar:
import plotly.express as px
px.line(df, x="year", y="gdp_value", color="country")
```

**Metadata siempre incluido:**
- `source_series`: Mapeo variant → FRED series ID
- `fetch_timestamp`: Timestamp de última actualización
- `missing_series`: Series solicitadas pero no disponibles
- `computation_notes`: Variantes calculadas automáticamente

---

## 📈 Output Examples & Use Cases

### Example 1: LATAM Convergence Analysis (tesina universitaria)

```python
result = analyze_gdp_cross_country(
    regions=["latam"],
    variants=["per_capita_constant"],
    start_date="2000-01-01",
    end_date="2023-12-31",
    comparison_mode="indexed",
    base_year=2000,
    period_split="decade",
    output_format="both"
)

analysis, df = result
# → Sigma convergence per decade
# → Structural breaks detection (Venezuela 2014, Argentina 2018)
# → Tidy dataset para regresiones
```

### Example 2: Central Bank Quick Check

```python
result = analyze_gdp_cross_country(
    countries=["usa", "euro_area", "japan", "uk"],
    variants=["nominal_usd", "per_capita_constant", "growth_rate"],
    benchmark_against="usa",
    output_format="summary"
)
# → Markdown snapshot con gaps vs USA
# → Detección de recesiones técnicas
```

### Example 3: ML Dataset Preparation

```python
_, df = analyze_gdp_cross_country(
    regions=["oecd"],
    variants=["per_capita_constant", "growth_rate"],
    start_date="1990-01-01",
    output_format="dataset"
)

# df incluye:
# - country, year, region, variant_type, gdp_value, source_series
# - Listo para feature engineering o predicción
```

---

## 🔬 Modos de Comparación
## 🔬 Modos de Comparación

- **`absolute`**: Valores absolutos (USD o unidades según variante)
- **`indexed`**: Normalizar todo a 100 en `base_year` (útil para comparar trayectoria relativa)
- **`per_capita`**: Foco en per capita (divide por población automáticamente si no existe serie directa)
- **`growth_rates`**: Solo tasas de crecimiento (calculadas desde `constant_2010`)
- **`ppp`**: Adjusted view con PPP (requiere variantes `ppp_adjusted` o `per_capita_ppp`)
- **`relative_to_benchmark`**: Normalizar por benchmark si `benchmark_against` está seteado

**Default:** `absolute` (más directo y transparente)

---

## 🎯 By-Country Detail Structure

Para cada país en `analysis.by_country[country]`:

```json
{
    "country_code": "usa",
    "country_name": "United States",
    "region": "g7",
    "population": {
        "series_id": "POPTOTUSA647NWDB",
        "latest": 331893745,
        "unit": "persons",
        "growth_rate_10y": 0.65
    },
    "variants": {
        "per_capita_constant": {
            "series_id": "NYGDPPCAPKDUSA",
            "latest_value": 63543.2,
            "unit": "2010 USD",
            "changes": {
                "1y": 2.1,
                "5y_cagr": 1.8,
                "10y_cagr": 1.6
            },
            "volatility": {
                "std_dev": 2.3,
                "stability_index": 2.4
            }
        }
    },
    "historical_context": {
        "peak_year": 2019,
        "peak_value": 63902.4,
        "trough_year": 2009,
        "percentile_current": 95
    },
    "growth_analysis": {
        "recessions_detected": [
            {"start": 2008, "end": 2009, "cumulative_fall": -4.2}
        ]
    }
}
```

---

## 🌍 Cross-Country Analysis Structure

```json
{
    "convergence": {
        "sigma": {
            "start": 15234.5,
            "end": 12890.3,
            "trend_slope": -45.2,
            "p_value": 0.002,
            "interpretation": "Converging at 45.2 USD/year (significant)"
        },
        "beta": {
            "coefficient": -0.042,
            "p_value": 0.018,
            "r_squared": 0.31,
            "interpretation": "Conditional convergence detected (poor→rich grow faster)"
        }
    },
    "structural_breaks": [...],
    "volatility_ranking": [
        {"country": "greece", "std_dev": 4.2, "rank": 1},
        {"country": "ireland", "std_dev": 3.8, "rank": 2}
    ],
    "outliers": [
        {"country": "ven", "year": 2018, "value": -18.2, "threshold": -10.5}
    ],
    "leaders": {
        "highest_growth": {"country": "china", "cagr": 9.2},
        "lowest_volatility": {"country": "switzerland", "std_dev": 1.1}
    }
}
```

---

## 📊 Visualization Suggestions (auto-generated)

```json
{
    "visualization_suggestions": [
        {
            "type": "line",
            "title": "GDP per Capita Evolution (constant 2010 USD)",
            "x": "year",
            "y": "gdp_value",
            "color": "country",
            "library": "plotly"
        },
        {
            "type": "scatter",
            "title": "Convergence Plot (Initial GDP vs CAGR)",
            "x": "initial_gdp_pc",
            "y": "cagr_10y",
            "size": "population_2023",
            "library": "seaborn"
        },
        {
            "type": "bar",
            "title": "Rank Changes (2000 → 2023)",
            "x": "country",
            "y": "rank_change",
            "library": "matplotlib"
        }
    ]
}
```

---

## 🚀 Implementation Plan (1 semana)
## 🚀 Implementation Plan (1 semana)

### Día 1-2: Foundation & Mappings
- Crear `GDP_MAPPINGS` completo (238 países × 8 variants)
- Definir `GDP_PRESETS` con g7, g20, brics, latam, oecd, emerging, developed, regional
- Implementar `GDP_VARIANT_DEPENDENCIES` con lógica de cálculo automático
- Función `validate_variants()` con dependency checking
- Tests unitarios: mapping correctness, preset expansion

### Día 3-4: Fetch & Analysis Layers
- **fetch_data_layer:**
  - Integración con `fred_client.py` existente
  - Caching con TTL configurable
  - Rate-limiting respeto (FRED: 120 req/min)
  - Missing data handling con fallbacks
  - Population fetching automático para per_capita

- **analysis_layer:**
  - Growth calculations (CAGR, volatility, stability_index)
  - Convergence tests:
    - Sigma con `trend_slope` (scipy.stats.linregress)
    - Beta con R², p-value
  - Structural breaks:
    - Chow test con statsmodels
    - Rolling variance detector
  - Rankings con `rank_change` tracking
  - Outlier detection (±2σ)

### Día 5-6: Format Layer & Output Modes
- **format_layer:**
  - JSON analysis formatter (compacto, AI-optimized)
  - Tidy dataset transformer con `id_vars`/`value_vars`
  - Summary markdown generator
  - `output_format="both"` implementation
  - Metadata enrichment (`source_series`, `computation_notes`)

- **Visualization metadata:**
  - Auto-generate plotly/seaborn suggestions
  - Include axis labels, color schemes, library hints

### Día 7: Testing & Documentation
- **Testing:**
  - Unit tests: Each layer isolated
  - Integration tests: Full workflow (g7 example)
  - Edge cases: Missing data, single country, invalid variants
  - Performance: 50+ countries fetching time
  - Validation: Computed variants match direct fetch (where available)

- **Documentation:**
  - Update `server/docs/workflows/ANALYZE_GDP_REFERENCE.md`
  - Add examples to README
  - Changelog entry
  - Release notes draft

### Success Metrics
- ✅ 238 countries supported (per_capita_constant coverage)
- ✅ <3s response time for G7 analysis (with caching)
- ✅ 100% test coverage on analysis_layer
- ✅ Computed variants validate against direct series (±0.5% tolerance)
- ✅ All 10 presets tested with real data

---

## 📋 Key Insights Auto-Generation Logic

```python
def generate_key_insights(analysis: Dict) -> List[str]:
    """
    Auto-generates bullet points based on analysis results.
    
    Examples:
    - "Strong convergence detected: σ decreased by 15.4% (p<0.01)"
    - "China exhibited highest growth (9.2% CAGR) but with moderate volatility (σ=2.1%)"
    - "Structural break detected in USA (2008) — Great Recession impact"
    - "Greece ranked 1st in volatility (σ=4.2%) due to 2010-2015 crisis"
    """
    insights = []
    
    # Convergence insight
    if analysis['convergence']['sigma']['trend_slope'] < 0:
        insights.append(f"Strong convergence: σ decreased by {abs(...)}")
    
    # Growth leaders
    top_grower = analysis['leaders']['highest_growth']
    insights.append(f"{top_grower['country']} exhibited highest growth...")
    
    # Structural breaks
    for country, breaks in analysis['structural_breaks'].items():
        if breaks['chow_test']['break_detected']:
            insights.append(f"Structural break detected in {country}...")
    
    return insights
```

---

## 🔍 Limitations & Caveats

### Data Availability
- **PPP data:** Limited to ~180 countries, starts 1990 (vs 1960 for constant_2010)
- **Missing series:** Some small economies lack recent updates (e.g., Venezuela post-2019)
- **Frequency:** Most GDP data is annual (quarterly available for select OECD countries only)

### Methodological
- **Structural breaks:** Chow test assumes single break point (median year) — may miss multiple breaks
- **Convergence:** Beta convergence assumes linear relationship (may not hold for all periods)
- **Computed variants:** Growth rate precision depends on constant_2010 quality (revisions not tracked)
- **Population data:** World Bank population may have lags (latest updates ~1 year behind)

### Scope (v1.0.0)
- ❌ No component decomposition (C+I+G+NX breakdown) — requires separate series
- ❌ No quarterly analysis — annual only for cross-country consistency
- ❌ No real-time GDP nowcasting — historical data only
- ❌ No automatic outlier adjustment — flags outliers but doesn't remove them
- ❌ No PPP exchange rate time series — uses latest PPP conversion factor

### Future Enhancements (v2.0.0+)
- Component decomposition workflow (separate tool)
- Quarterly analysis for OECD subset
- Machine learning predictions (ARIMA, Prophet)
- Interactive Dash/Streamlit dashboard
- Export to Excel with pre-formatted charts

---

## 📚 Data Sources & References

### Primary Sources
- **FRED (Federal Reserve Economic Data):**
  - Series: `NYGDPMKTPCD{country}`, `NYGDPPCAPKD{country}`, etc.
  - Coverage: 200+ countries, 1960-2024
  - Update frequency: Annual (published with ~6-month lag)
  - Documentation: https://fred.stlouisfed.org/

- **World Bank:**
  - Population: `POPTOT{country}647NWDB`
  - PPP conversion factors
  - Coverage: 238 economies
  - Documentation: https://data.worldbank.org/

### Methodological References
- **Penn World Table (PWT 10.0):** PPP adjustments methodology
- **OECD National Accounts:** GDP measurement standards
- **IMF World Economic Outlook:** GDP forecasting approaches
- **Chow Test:** Gregory Chow (1960), "Tests of Equality Between Sets of Coefficients"

### Code Dependencies
- `pandas`: DataFrame operations
- `scipy.stats`: Statistical tests (linregress, f_oneway)
- `statsmodels`: Chow test implementation
- `fred_client.py`: FRED API wrapper (existing)
- `cache.py`: Disk+memory caching (existing)

---

## ✅ Testing Strategy

### Unit Tests
```python
# tests/unit/tools/test_gdp_analysis.py

def test_validate_variants_computed():
    """growth_rate requires constant_2010"""
    result = validate_variants(["growth_rate"], GDP_VARIANT_DEPENDENCIES)
    assert "constant_2010" in result["required_sources"]

def test_chow_test_detects_break():
    """USA GDP should show break around 2008"""
    data = fetch_usa_gdp_1990_2020()
    breaks = detect_structural_breaks(data, "usa")
    assert breaks["chow_test"]["break_detected"] is True
    assert 2006 <= breaks["chow_test"]["split_year"] <= 2010

def test_sigma_convergence_calculation():
    """Sigma trend slope negative = converging"""
    data = fetch_g7_gdp_2000_2023()
    convergence = calculate_sigma_convergence(data)
    assert convergence["trend_slope"] < 0  # G7 converged
    assert convergence["p_value"] < 0.05
```

### Integration Tests
```python
def test_full_workflow_g7():
    """Complete analysis: g7, per_capita_constant, 2000-2023"""
    result = analyze_gdp_cross_country(
        regions=["g7"],
        variants=["per_capita_constant"],
        start_date="2000-01-01",
        output_format="both"
    )
    analysis, df = result
    
    assert len(df) > 0  # Dataset populated
    assert "usa" in analysis["by_country"]
    assert "convergence" in analysis["cross_country"]
    assert analysis["metadata"]["series_fetched"] >= 7

def test_missing_data_handling():
    """Venezuela (missing recent data) should not crash"""
    result = analyze_gdp_cross_country(
        countries=["ven"],
        variants=["per_capita_constant"]
    )
    assert "ven" in result["metadata"]["missing_series"] or "ven" in result["by_country"]
```

### Performance Tests
```python
def test_performance_50_countries():
    """50 countries analysis should complete <5s (with cache)"""
    start = time.time()
    analyze_gdp_cross_country(regions=["oecd"], variants=["per_capita_constant"])
    elapsed = time.time() - start
    assert elapsed < 5.0
```

---

## 📝 Changelog Entry (Draft)

### [v0.3.0] - 2025-XX-XX - `analyze_gdp_cross_country` Tool

**Added:**
- 🎯 New tool: `analyze_gdp_cross_country` — comprehensive GDP cross-country analysis
  - 8 GDP variants (nominal, constant, per_capita, ppp, growth_rate)
  - 238 countries supported (World Bank + FRED coverage)
  - 10+ presets: g7, g20, brics, latam, oecd, emerging, developed, regional
  - 3 output formats: analysis (JSON), dataset (tidy DataFrame), summary (Markdown)
  - Enhanced analysis:
    - Sigma convergence with trend slope
    - Beta convergence with p-values
    - Structural breaks detection (Chow test + rolling variance)
    - Stability index (CAGR / volatility)
    - Rank change tracking
  - Auto-computed variants: growth_rate, per_capita (if missing)
  - Variant validation with dependency checking
  - Period split analysis (decade/5y subperiods)
  - Source series traceability in metadata

**Technical:**
- 3-layer architecture: fetch → analysis → format
- Integration with existing `fred_client.py` and `cache.py`
- Comprehensive test suite (unit + integration)
- Auto-generated visualization suggestions (plotly/seaborn)

**Documentation:**
- `docs/workflows/ANALYZE_GDP_REFERENCE.md` — complete API reference
- `docs/planning/analyze_gdp_cross_country_proposal.md` — design specification

---

## 🎉 Conclusion

**v1.0.0-proposal-final** está production-ready para implementación. Incluye:

✅ **Diferenciadores clave:**
1. 8 GDP variants con auto-cálculo inteligente
2. Deep analysis (convergence + structural breaks + rankings)
3. 3 formatos de salida + modo "both" para workflows híbridos
4. 238 países + 10+ presets
5. Arquitectura modular de 3 capas
6. Complete traceability (source_series en metadata)

✅ **Implementación estructurada:** Plan de 7 días con milestones claros

✅ **Testing robusto:** Unit + integration + performance + edge cases

✅ **Documentación completa:** API reference + examples + changelog

**Next steps:** Aprobar propuesta → Crear branch `feature/gdp-analysis` → Día 1 implementation 🚀

---

**Document generated:** 2025-11-03  
**Final review incorporated:** 2025-11-03  
**Status:** ✅ Production-ready proposal (v1.0.0-proposal-final)

**Next steps:** Approval → Branch `feature/gdp-analysis` → Implementation (Week 1)

  
