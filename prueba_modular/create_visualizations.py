import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

# Cargar datos
df = pd.read_csv('gdp_data_raw.csv')
df_pivot = df.pivot(index='year', columns='country', values='value')

with open('analysis_results.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

print("Generando visualizaciones...")

# Configuracion de estilo
plt.style.use('seaborn-v0_8-darkgrid')
colors = {
    'USA': '#1f77b4',
    'Canada': '#ff7f0e',
    'Japan': '#2ca02c',
    'Germany': '#d62728',
    'France': '#9467bd',
    'Italy': '#8c564b',
    'United Kingdom': '#e377c2'
}

# ==============================================================================
# 1. GDP PER CAPITA EVOLUTION (1980-2010)
# ==============================================================================
fig, ax = plt.subplots(figsize=(14, 8))

for country in df_pivot.columns:
    ax.plot(df_pivot.index, df_pivot[country],
            label=country, color=colors.get(country, 'gray'),
            linewidth=2.5, marker='o', markersize=4)

ax.set_xlabel('Year', fontsize=14, fontweight='bold')
ax.set_ylabel('GDP per capita (constant 2010 USD)', fontsize=14, fontweight='bold')
ax.set_title('G7 GDP per Capita Evolution (1980-2010)', fontsize=16, fontweight='bold', pad=20)
ax.legend(loc='upper left', fontsize=11, framealpha=0.9)
ax.grid(True, alpha=0.3)

# Anotar crisis del 2008
ax.axvline(x=2008, color='red', linestyle='--', linewidth=2, alpha=0.5)
ax.text(2008, 55000, '2008 Crisis', fontsize=10, color='red',
        rotation=90, verticalalignment='bottom')

plt.tight_layout()
plt.savefig('1_gdp_evolution.png', dpi=300, bbox_inches='tight')
print("[OK] Grafico 1 guardado: 1_gdp_evolution.png")
plt.close()

# ==============================================================================
# 2. CAGR COMPARISON BAR CHART
# ==============================================================================
fig, ax = plt.subplots(figsize=(12, 7))

countries_list = [k for k, v in sorted(results['rankings']['by_cagr'],
                                       key=lambda x: x[1], reverse=True)]
cagr_values = [v for k, v in sorted(results['rankings']['by_cagr'],
                                    key=lambda x: x[1], reverse=True)]

bars = ax.barh(countries_list, cagr_values,
               color=[colors.get(c, 'gray') for c in countries_list],
               edgecolor='black', linewidth=1.5)

ax.set_xlabel('CAGR (%)', fontsize=14, fontweight='bold')
ax.set_title('GDP per Capita CAGR Ranking (1980-2010)', fontsize=16, fontweight='bold', pad=20)
ax.grid(axis='x', alpha=0.3)

# Agregar valores en las barras
for i, (bar, val) in enumerate(zip(bars, cagr_values)):
    ax.text(val + 0.02, i, f'{val:.2f}%',
            va='center', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('2_cagr_ranking.png', dpi=300, bbox_inches='tight')
print("[OK] Grafico 2 guardado: 2_cagr_ranking.png")
plt.close()

# ==============================================================================
# 3. BETA CONVERGENCE SCATTER PLOT
# ==============================================================================
fig, ax = plt.subplots(figsize=(12, 8))

countries_list = list(df_pivot.columns)
initial_gdps = [results['metrics_by_country'][c]['initial_gdp'] for c in countries_list]
cagrs = [results['metrics_by_country'][c]['cagr_pct'] for c in countries_list]
log_initial = np.log(initial_gdps)

# Scatter plot
for i, country in enumerate(countries_list):
    ax.scatter(log_initial[i], cagrs[i], s=300,
               color=colors.get(country, 'gray'),
               edgecolor='black', linewidth=2, alpha=0.8, zorder=3)
    ax.text(log_initial[i], cagrs[i] + 0.08, country,
            fontsize=10, ha='center', fontweight='bold')

# Regression line
from scipy import stats
slope, intercept, r_value, p_value, std_err = stats.linregress(log_initial, cagrs)
line_x = np.array([min(log_initial), max(log_initial)])
line_y = slope * line_x + intercept
ax.plot(line_x, line_y, 'r--', linewidth=2, alpha=0.7, label=f'Regression (β={slope:.3f})')

ax.set_xlabel('log(GDP per capita 1980)', fontsize=14, fontweight='bold')
ax.set_ylabel('CAGR (%) 1980-2010', fontsize=14, fontweight='bold')
ax.set_title('Beta Convergence Test: Initial GDP vs Growth Rate',
             fontsize=16, fontweight='bold', pad=20)
ax.legend(fontsize=12)
ax.grid(True, alpha=0.3)

# Agregar texto con resultado
convergence_text = results['convergence']['beta']
text_result = f"p-value: {convergence_text['p_value']:.4f}\n"
text_result += f"R²: {convergence_text['r_squared']:.4f}\n"
if convergence_text['catch_up_effect']:
    text_result += "Result: Catch-up effect detected"
else:
    text_result += "Result: No significant convergence"

ax.text(0.05, 0.95, text_result, transform=ax.transAxes,
        fontsize=11, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig('3_beta_convergence.png', dpi=300, bbox_inches='tight')
print("[OK] Grafico 3 guardado: 3_beta_convergence.png")
plt.close()

# ==============================================================================
# 4. SIGMA CONVERGENCE - COEFFICIENT OF VARIATION OVER TIME
# ==============================================================================
fig, ax = plt.subplots(figsize=(14, 8))

years = df_pivot.index.values
cv_values = []

for year in years:
    values = df_pivot.loc[year].values
    mean_val = np.mean(values)
    std_val = np.std(values, ddof=1)
    cv = std_val / mean_val
    cv_values.append(cv)

ax.plot(years, cv_values, color='#2ca02c', linewidth=3, marker='o', markersize=7)

# Trend line
X = np.arange(len(years))
slope, intercept, r_value, p_value, std_err = stats.linregress(X, cv_values)
trend_line = slope * X + intercept
ax.plot(years, trend_line, 'r--', linewidth=2, alpha=0.7,
        label=f'Trend (slope={slope:.6f})')

ax.set_xlabel('Year', fontsize=14, fontweight='bold')
ax.set_ylabel('Coefficient of Variation', fontsize=14, fontweight='bold')
ax.set_title('Sigma Convergence: Dispersion Over Time',
             fontsize=16, fontweight='bold', pad=20)
ax.legend(fontsize=12)
ax.grid(True, alpha=0.3)

# Resultado del test
sigma_result = results['convergence']['sigma']
result_text = f"p-value: {sigma_result['p_value']:.4f}\n"
result_text += f"R²: {sigma_result['r_squared']:.4f}\n"
if sigma_result['converging']:
    result_text += "Result: Countries converging"
elif sigma_result['significant']:
    result_text += "Result: Countries diverging"
else:
    result_text += "Result: No significant trend"

ax.text(0.05, 0.95, result_text, transform=ax.transAxes,
        fontsize=11, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))

plt.tight_layout()
plt.savefig('4_sigma_convergence.png', dpi=300, bbox_inches='tight')
print("[OK] Grafico 4 guardado: 4_sigma_convergence.png")
plt.close()

# ==============================================================================
# 5. VOLATILITY COMPARISON
# ==============================================================================
fig, ax = plt.subplots(figsize=(12, 7))

countries_sorted = [k for k, v in sorted(results['rankings']['by_stability'],
                                         key=lambda x: x[1], reverse=True)]
volatilities = [results['metrics_by_country'][c]['volatility_pct'] for c in countries_sorted]

bars = ax.barh(countries_sorted, volatilities,
               color=[colors.get(c, 'gray') for c in countries_sorted],
               edgecolor='black', linewidth=1.5)

ax.set_xlabel('Volatility (% Std Dev of Growth Rates)', fontsize=14, fontweight='bold')
ax.set_title('GDP Growth Volatility Comparison (1980-2010)',
             fontsize=16, fontweight='bold', pad=20)
ax.grid(axis='x', alpha=0.3)

# Agregar valores
for i, (bar, val) in enumerate(zip(bars, volatilities)):
    ax.text(val + 0.05, i, f'{val:.2f}%',
            va='center', fontsize=11, fontweight='bold')

# Linea de threshold
ax.axvline(x=2.0, color='orange', linestyle='--', linewidth=2, alpha=0.5)
ax.text(2.0, len(countries_sorted)-0.5, 'Threshold',
        color='orange', fontsize=10, rotation=90, verticalalignment='bottom')

plt.tight_layout()
plt.savefig('5_volatility_comparison.png', dpi=300, bbox_inches='tight')
print("[OK] Grafico 5 guardado: 5_volatility_comparison.png")
plt.close()

# ==============================================================================
# 6. STRUCTURAL BREAKS TIMELINE
# ==============================================================================
fig, ax = plt.subplots(figsize=(16, 10))

countries_list = list(df_pivot.columns)
structural_breaks = results['structural_breaks']

y_positions = {country: i for i, country in enumerate(countries_list)}

for country, breaks in structural_breaks.items():
    y_pos = y_positions[country]

    for brk in breaks:
        year = brk['year']
        if brk['type'] == 'variance_increase':
            marker = '^'
            color_brk = 'red'
        else:
            marker = 'v'
            color_brk = 'green'

        ax.scatter(year, y_pos, marker=marker, s=200,
                   color=color_brk, edgecolor='black', linewidth=1.5,
                   alpha=0.7, zorder=3)

# Crisis globales
ax.axvline(x=2008, color='darkred', linestyle='--', linewidth=3, alpha=0.6)
ax.text(2008, len(countries_list)-0.3, '2008\nFinancial\nCrisis',
        fontsize=10, color='darkred', ha='center', fontweight='bold')

ax.axvline(x=1990, color='purple', linestyle='--', linewidth=2, alpha=0.5)
ax.text(1990, len(countries_list)-0.3, '1990\nRecession',
        fontsize=10, color='purple', ha='center')

ax.set_yticks(range(len(countries_list)))
ax.set_yticklabels(countries_list, fontsize=12)
ax.set_xlabel('Year', fontsize=14, fontweight='bold')
ax.set_title('Structural Breaks Timeline (Volatility Changes)',
             fontsize=16, fontweight='bold', pad=20)
ax.grid(axis='x', alpha=0.3)

# Leyenda
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='^', color='w', markerfacecolor='red',
           markersize=12, label='Volatility Increase'),
    Line2D([0], [0], marker='v', color='w', markerfacecolor='green',
           markersize=12, label='Volatility Decrease')
]
ax.legend(handles=legend_elements, loc='upper left', fontsize=11)

plt.tight_layout()
plt.savefig('6_structural_breaks.png', dpi=300, bbox_inches='tight')
print("[OK] Grafico 6 guardado: 6_structural_breaks.png")
plt.close()

# ==============================================================================
# 7. FINAL GDP RANKING (2010)
# ==============================================================================
fig, ax = plt.subplots(figsize=(12, 7))

countries_sorted = [k for k, v in sorted(results['rankings']['by_final_gdp'],
                                         key=lambda x: x[1], reverse=True)]
final_gdps = [v for k, v in sorted(results['rankings']['by_final_gdp'],
                                   key=lambda x: x[1], reverse=True)]

bars = ax.barh(countries_sorted, final_gdps,
               color=[colors.get(c, 'gray') for c in countries_sorted],
               edgecolor='black', linewidth=1.5)

ax.set_xlabel('GDP per capita (constant 2010 USD)', fontsize=14, fontweight='bold')
ax.set_title('G7 GDP per Capita Ranking (2010)', fontsize=16, fontweight='bold', pad=20)
ax.grid(axis='x', alpha=0.3)

# Agregar valores
for i, (bar, val) in enumerate(zip(bars, final_gdps)):
    ax.text(val + 500, i, f'${val:,.0f}',
            va='center', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('7_final_gdp_ranking.png', dpi=300, bbox_inches='tight')
print("[OK] Grafico 7 guardado: 7_final_gdp_ranking.png")
plt.close()

print("\n" + "=" * 80)
print("VISUALIZACIONES COMPLETADAS")
print("=" * 80)
print("\nArchivos generados:")
print("  1. 1_gdp_evolution.png - Evolucion del GDP per capita")
print("  2. 2_cagr_ranking.png - Ranking por tasa de crecimiento")
print("  3. 3_beta_convergence.png - Test de convergencia beta")
print("  4. 4_sigma_convergence.png - Test de convergencia sigma")
print("  5. 5_volatility_comparison.png - Comparacion de volatilidad")
print("  6. 6_structural_breaks.png - Linea de tiempo de quiebres estructurales")
print("  7. 7_final_gdp_ranking.png - Ranking GDP 2010")
