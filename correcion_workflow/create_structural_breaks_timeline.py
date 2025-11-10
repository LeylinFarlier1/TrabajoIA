import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd
import json
import numpy as np

# Load GDP data
print("[INFO] Loading GDP data...")
with open('analysis_results.json', 'r') as f:
    data = json.load(f)

# Extract dataset
dataset = data['dataset']
df = pd.DataFrame(dataset)

# Convert date to year
df['year'] = pd.to_datetime(df['date']).dt.year
df = df[['year', 'country', 'per_capita_constant']].sort_values(['country', 'year'])
df.rename(columns={'per_capita_constant': 'value'}, inplace=True)

# Create pivot table (same structure as gdp_analysis.py)
df_pivot = df.pivot(index='year', columns='country', values='value')

print(f"[INFO] Loaded {len(df)} observations for {df['country'].nunique()} countries")
print(f"[INFO] Year range: {df['year'].min()} - {df['year'].max()}")

# Calculate year-over-year growth rates
print("[INFO] Calculating growth rates...")
growth_data = {}

# Extract years from pivot index (same as gdp_analysis.py)
years = df_pivot.index.values

for country in df_pivot.columns:
    # Use pivot data (same as gdp_analysis.py)
    values = df_pivot[country].values
    growth_rates = []

    for i in range(1, len(values)):
        growth_rate = ((values[i] - values[i-1]) / values[i-1]) * 100
        growth_rates.append(growth_rate)

    growth_data[country] = growth_rates

# Detect structural breaks using rolling variance method
print("[INFO] Detecting structural breaks (threshold: ±50% change)...")
breaks = []
window = 5
threshold_multiplier = 1.5  # Cambio de 50% o más

for country in growth_data.keys():
    growth_rates = growth_data[country]

    # Calcular varianza móvil (ventana de 5 años)
    rolling_var = []

    for i in range(len(growth_rates) - window + 1):
        window_data = growth_rates[i:i+window]
        rolling_var.append(np.var(window_data, ddof=1))

    # Detectar cambios grandes en la varianza
    for i in range(1, len(rolling_var)):
        ratio = rolling_var[i] / rolling_var[i-1] if rolling_var[i-1] != 0 else 0

        if ratio > threshold_multiplier:
            year_idx = i + window - 1
            if year_idx < len(years):
                breaks.append({
                    'year': int(years[year_idx]),
                    'country': country,
                    'type': 'variance_increase',
                    'ratio': ratio,
                    'variance_current': rolling_var[i],
                    'variance_previous': rolling_var[i-1]
                })
        elif ratio < (1/threshold_multiplier) and ratio > 0:
            year_idx = i + window - 1
            if year_idx < len(years):
                breaks.append({
                    'year': int(years[year_idx]),
                    'country': country,
                    'type': 'variance_decrease',
                    'ratio': ratio,
                    'variance_current': rolling_var[i],
                    'variance_previous': rolling_var[i-1]
                })

df_breaks = pd.DataFrame(breaks)
print(f"[INFO] Detected {len(df_breaks)} structural breaks")
print(f"  - Variance increases: {len(df_breaks[df_breaks['type']=='variance_increase'])}")
print(f"  - Variance decreases: {len(df_breaks[df_breaks['type']=='variance_decrease'])}")

# Save breaks to JSON
breaks_data = {
    'metadata': {
        'method': '5-year rolling variance',
        'threshold_increase': 1.5,
        'threshold_decrease': 2/3,
        'description': 'Variance change ≥50%: ratio >1.5 (increase) or ratio <2/3 (decrease)',
        'window_size': 5,
        'total_breaks': len(df_breaks)
    },
    'breaks': breaks
}

with open('structural_breaks_timeline.json', 'w') as f:
    json.dump(breaks_data, f, indent=2)

print("[OK] Breaks saved to structural_breaks_timeline.json")

# Create scatter plot timeline
print("[INFO] Creating timeline scatter plot...")

# Set style
plt.style.use('seaborn-v0_8-darkgrid')

# Get unique countries and years
# Custom order: Canada, France, Germany, Italy, Japan, USA, UK (bottom to top)
country_order = ['canada', 'france', 'germany', 'italy', 'japan', 'usa', 'uk']
countries = [c for c in country_order if c in df_pivot.columns]
years_plot = sorted(df['year'].unique())

# Detect crisis years (multiple simultaneous breaks)
crisis_years = df_breaks[df_breaks['type'] == 'variance_increase'].groupby('year')['country'].count()
crisis_years = crisis_years[crisis_years >= 3].index.tolist()  # 3+ countries affected
print(f"[INFO] Crisis years detected (3+ countries): {crisis_years}")

# Create figure
fig, ax = plt.subplots(figsize=(16, 10))

# Create country position mapping
country_positions = {country: i for i, country in enumerate(countries)}

# Adjust marker size if many countries
marker_size = 150 if len(countries) > 10 else 200

# Plot breaks
for _, row in df_breaks.iterrows():
    y_pos = country_positions[row['country']]

    if row['type'] == 'variance_increase':
        ax.scatter(row['year'], y_pos, marker='^', c='red', s=marker_size,
                  alpha=0.7, edgecolors='black', linewidths=1.5, zorder=3)
    else:  # variance_decrease
        ax.scatter(row['year'], y_pos, marker='v', c='green', s=marker_size,
                  alpha=0.7, edgecolors='black', linewidths=1.5, zorder=3)

# Add vertical lines for crisis years
for crisis_year in crisis_years:
    ax.axvline(x=crisis_year, color='gray', linestyle='--', alpha=0.4, linewidth=1, zorder=1)
    # Add label for crisis year
    ax.text(crisis_year, len(countries), f'{crisis_year}',
           ha='center', va='bottom', fontsize=9, color='gray', rotation=0)

# Configure axes
ax.set_xlabel('Year', fontsize=14, fontweight='bold')
ax.set_yticks(range(len(countries)))
ax.set_yticklabels(countries, fontsize=12 if len(countries) <= 10 else 10)

# Set x-axis limits with padding
year_min, year_max = min(years_plot), max(years_plot)
ax.set_xlim(year_min - 1, year_max + 1)
ax.set_ylim(-0.5, len(countries) - 0.5)

# Grid only on x-axis
ax.grid(axis='x', alpha=0.3, zorder=0)
ax.grid(axis='y', visible=False)

# Title
ax.set_title('Structural Breaks Timeline (Volatility Changes)',
            fontsize=16, fontweight='bold', pad=20)

# Create custom legend
legend_elements = [
    Line2D([0], [0], marker='^', color='w', markerfacecolor='red',
           markeredgecolor='black', markeredgewidth=1.5, markersize=12,
           label='Volatility Increase (ratio > 1.5)', alpha=0.7),
    Line2D([0], [0], marker='v', color='w', markerfacecolor='green',
           markeredgecolor='black', markeredgewidth=1.5, markersize=12,
           label='Volatility Decrease (ratio < 2/3)', alpha=0.7)
]

ax.legend(handles=legend_elements, loc='upper left', fontsize=11, framealpha=0.9)

# Tight layout
plt.tight_layout()

# Save figure with new name
output_file = '6_structural_breaks_50pct.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
plt.close()

print(f"[OK] Grafico guardado: {output_file}")

# Print summary
print("\n=== STRUCTURAL BREAKS SUMMARY ===")
print(f"Total breaks detected: {len(df_breaks)}")
print(f"\nBy type:")
for break_type in df_breaks['type'].unique():
    count = len(df_breaks[df_breaks['type'] == break_type])
    print(f"  {break_type}: {count}")

print(f"\nBy country:")
for country in countries:
    count = len(df_breaks[df_breaks['country'] == country])
    print(f"  {country}: {count} breaks")

print(f"\nCrisis years (3+ countries affected): {crisis_years}")
