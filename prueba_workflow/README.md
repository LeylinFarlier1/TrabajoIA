# G7 GDP Cross-Country Analysis (1980-2010)

## Overview

This project presents a comprehensive economic analysis of the G7 countries (USA, Canada, UK, Germany, France, Italy, and Japan) from 1980 to 2010, focusing on GDP per capita in constant 2010 USD. The analysis examines growth patterns, economic convergence, volatility, and structural breaks across these major economies.

## Project Structure

```
prueba_workflow/
├── analysis_results.json          # Complete analysis output from MCP tool
├── gdp_data_raw.csv               # Raw time-series data (year, country, value)
├── series_ids.json                # FRED series IDs and metadata
├── README.md                      # This file
├── analysis_log.md                # Detailed analysis process log
├── analysis_output.txt            # Tool execution log
├── extract_and_visualize.py       # Python script for data extraction
├── save_full_data.py              # Python script for data persistence
├── create_visualizations.py       # Visualization generation script
└── *.png                          # 7 visualization charts
```

## Data Sources

### Primary Source
- **Federal Reserve Economic Data (FRED)** - Federal Reserve Bank of St. Louis
- **Original Source**: World Bank - World Development Indicators
- **Access Method**: MCP (Model Context Protocol) server for economic data

### Series Information
All data uses GDP per capita in constant 2010 U.S. dollars for cross-country comparability.

| Country | FRED Series ID      | Description                              |
|---------|---------------------|------------------------------------------|
| USA     | NYGDPPCAPKDUSA      | GDP per capita, constant 2010 USD        |
| Canada  | NYGDPPCAPKDCAN      | GDP per capita, constant 2010 USD        |
| UK      | NYGDPPCAPKDGBR      | GDP per capita, constant 2010 USD        |
| Germany | NYGDPPCAPKDDEU      | GDP per capita, constant 2010 USD        |
| France  | NYGDPPCAPKDFRA      | GDP per capita, constant 2010 USD        |
| Italy   | NYGDPPCAPKDITA      | GDP per capita, constant 2010 USD        |
| Japan   | NYGDPPCAPKDJPN      | GDP per capita, constant 2010 USD        |

## Methodology

### Analysis Components

1. **Growth Analysis**
   - Compound Annual Growth Rate (CAGR) calculation
   - Growth volatility measurement
   - Stability index computation

2. **Convergence Testing**
   - **Sigma Convergence**: Tests whether GDP dispersion (coefficient of variation) decreases over time
   - **Beta Convergence**: Tests whether poorer countries grow faster than richer ones (catch-up effect)

3. **Structural Break Detection**
   - Chow test for variance changes
   - Rolling variance analysis
   - Identification of significant economic regime shifts

4. **Comparative Rankings**
   - Final GDP levels (2010)
   - Growth rates across the period

## Key Findings

### Growth Performance (1980-2010)

| Rank | Country | CAGR (%) | Final GDP per Capita (2010 USD) |
|------|---------|----------|----------------------------------|
| 1    | UK      | 1.98     | $42,311                          |
| 2    | Japan   | 1.79     | $32,942                          |
| 3    | USA     | 1.78     | $52,813                          |
| 4    | Germany | 1.59     | $38,517                          |
| 5    | France  | 1.46     | $35,578                          |
| 6    | Canada  | 1.34     | $41,164                          |
| 7    | Italy   | 1.26     | $31,929                          |

### Economic Volatility

- **Lowest Volatility**: France (1.45%) - Most stable growth path
- **Highest Volatility**: Japan (2.39%) - Most variable growth
- **USA Volatility**: 1.98% - Moderate volatility despite highest GDP

### Convergence Analysis

**Sigma Convergence (Dispersion Trend)**
- **Result**: DIVERGING ⚠️
- **Slope**: +0.0011 per year
- **R²**: 0.353
- **P-value**: 0.0004 (statistically significant)
- **Interpretation**: GDP inequality among G7 countries increased from 1980-2010

**Beta Convergence (Catch-up Growth)**
- **Coefficient**: -0.0141
- **R²**: 0.00 (no relationship)
- **P-value**: 0.9859 (not significant)
- **Interpretation**: No evidence of catch-up growth - poorer countries did not systematically grow faster

### Structural Breaks

**Canada (1993)**: Variance decrease detected (ratio: 0.49)
- Likely related to NAFTA implementation (1994) and economic stabilization

## Visualizations

### 1. GDP Evolution (1980-2010)
Line chart showing the trajectory of all G7 countries over the 30-year period.

**Key Observations**:
- USA maintains consistent leadership
- UK and Canada show strong convergence toward similar levels
- Japan's dramatic rise in the 1980s followed by stagnation in the 1990s
- Italy shows slowest overall growth

### 2. CAGR Ranking
Horizontal bar chart comparing growth rates across countries.

**Highlights**:
- UK achieved highest growth despite mid-level starting position
- Japan's high growth reflects recovery from lower 1980 base
- Italy's low growth reflects structural economic challenges

### 3. Beta Convergence
Scatter plot with regression line showing initial GDP vs growth rate.

**Finding**: Flat regression line (R² ≈ 0) indicates no convergence pattern.

### 4. Sigma Convergence
Time series of coefficient of variation showing dispersion changes.

**Trend**: Upward slope confirms increasing inequality among G7 economies.

### 5. Volatility Comparison
Bar chart ranking countries by growth volatility.

**Insight**: France's low volatility contrasts with Japan's high variability, reflecting different economic structures.

### 6. Structural Breaks
Timeline showing detected variance shifts in GDP trajectories.

**Detection**: Canada's 1993 break is the only statistically significant structural change.

### 7. Final GDP Ranking (2010)
Bar chart showing GDP per capita levels at the end of the period.

**Outcome**: USA far ahead, followed by UK/Canada cluster, then Germany/France, and Italy/Japan.

## Technical Details

### Tools and Technologies
- **Analysis Tool**: `analyze_gdp_cross_country` (MCP tool)
- **Data Processing**: Python (pandas, numpy)
- **Visualization**: matplotlib
- **Statistical Tests**: scipy.stats

### Analysis Parameters
```json
{
  "countries": "g7",
  "gdp_variants": "per_capita_constant",
  "start_date": "1980-01-01",
  "end_date": "2010-12-31",
  "output_format": "both",
  "include_rankings": true,
  "include_convergence": true,
  "include_growth_analysis": true,
  "detect_structural_breaks": true
}
```

### Data Quality
- **Total Observations**: 217 (31 years × 7 countries)
- **Missing Series**: 0
- **Data Completeness**: 100%

## Economic Interpretation

### Divergence Explanation
The sigma divergence finding suggests:
1. **USA Exceptionalism**: Accelerating technological innovation and productivity gains
2. **Regional Variations**: Europe (UK, Germany, France) vs. Stagnant Japan and Italy
3. **Policy Divergence**: Different responses to globalization and technological change

### Growth Disparities
- **UK Success**: Financial sector expansion and market liberalization
- **Japan's Lost Decade**: Asset bubble burst (1991) leading to prolonged stagnation
- **Italy's Challenges**: Structural rigidities and competitiveness issues
- **Germany's Reunification**: 1990 reunification temporarily depressed per capita growth

### Volatility Patterns
- **France**: Strong social safety nets and industrial planning reduced volatility
- **Japan**: Extreme bubble and bust cycle increased variance
- **Canada**: NAFTA structural break reduced post-1993 volatility

## Limitations

1. **Time Period**: Analysis ends in 2010, missing:
   - 2008 financial crisis recovery patterns
   - Post-2010 divergence trends
   - Digital economy effects

2. **Measurement**: Constant 2010 USD may not fully capture:
   - Purchasing power differences
   - Quality of life improvements
   - Non-market economic activities

3. **Country-Level Aggregation**: Masks:
   - Regional disparities within countries
   - Income distribution changes
   - Sector-specific trends

## Reproducibility

### Running the Analysis

1. **Execute GDP Analysis**:
```python
from mcp_client import analyze_gdp_cross_country

result = analyze_gdp_cross_country(
    countries="g7",
    gdp_variants="per_capita_constant",
    start_date="1980-01-01",
    end_date="2010-12-31",
    output_format="both",
    include_rankings=True,
    include_convergence=True,
    include_growth_analysis=True,
    detect_structural_breaks=True
)
```

2. **Generate Visualizations**:
```bash
python extract_and_visualize.py
```

## References

1. Federal Reserve Economic Data (FRED) - https://fred.stlouisfed.org/
2. World Bank World Development Indicators - https://datatopics.worldbank.org/world-development-indicators/
3. Barro, R. J., & Sala-i-Martin, X. (1992). "Convergence". Journal of Political Economy
4. Young, A. T., Higgins, M. J., & Levy, D. (2008). "Sigma Convergence versus Beta Convergence"

## Contact & Contributions

This analysis was generated as part of a GDP cross-country analysis workflow using the FRED MCP economic data server.

**Date**: November 9, 2025
**Analysis Period**: 1980-2010
**Countries**: G7 (USA, Canada, UK, Germany, France, Italy, Japan)
**GDP Variant**: Per Capita Constant 2010 USD

---

*Generated using Claude Code with FRED Economic Data MCP server*
