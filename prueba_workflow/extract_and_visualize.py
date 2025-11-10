import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (12, 7)

# Load analysis results
with open('analysis_results.json', 'r') as f:
    data = json.load(f)

# Extract dataset
dataset = data['dataset']
df = pd.DataFrame(dataset)
df['date'] = pd.to_datetime(df['date'])
df['year'] = df['date'].dt.year

# Save raw data to CSV
df[['year', 'country', 'value']].to_csv('gdp_data_raw.csv', index=False)
print("Saved gdp_data_raw.csv")

# Extract analysis data for visualizations
analysis = data['analysis']
countries_data = analysis['countries']
rankings = analysis['rankings']

# Prepare data for visualizations
countries = ['usa', 'canada', 'uk', 'germany', 'france', 'italy', 'japan']
country_labels = {
    'usa': 'USA', 'canada': 'Canada', 'uk': 'UK',
    'germany': 'Germany', 'france': 'France', 'italy': 'Italy', 'japan': 'Japan'
}

# 1. GDP Evolution Line Chart
plt.figure(figsize=(14, 8))
for country in countries:
    country_df = df[df['country'] == country].sort_values('year')
    plt.plot(country_df['year'], country_df['value'], marker='o', label=country_labels[country], linewidth=2)

plt.xlabel('Year', fontsize=12)
plt.ylabel('GDP per capita (USD, constant 2010)', fontsize=12)
plt.title('G7 GDP per Capita Evolution (1980-2010)', fontsize=14, fontweight='bold')
plt.legend(loc='best', fontsize=10)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('1_gdp_evolution.png', dpi=300, bbox_inches='tight')
plt.close()
print("Saved 1_gdp_evolution.png")

# 2. CAGR Ranking Horizontal Bar Chart
cagr_ranking = rankings['per_capita_constant_growth']
cagr_countries = [country_labels[item['country']] for item in cagr_ranking]
cagr_values = [item['value'] for item in cagr_ranking]

plt.figure(figsize=(10, 7))
colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(cagr_countries)))
bars = plt.barh(cagr_countries, cagr_values, color=colors)
plt.xlabel('CAGR (%)', fontsize=12)
plt.ylabel('Country', fontsize=12)
plt.title('G7 GDP Growth Rate Ranking (CAGR 1980-2010)', fontsize=14, fontweight='bold')
plt.grid(axis='x', alpha=0.3)

# Add value labels
for i, (bar, value) in enumerate(zip(bars, cagr_values)):
    plt.text(value + 0.02, bar.get_y() + bar.get_height()/2, f'{value:.2f}%',
             va='center', fontsize=10)

plt.tight_layout()
plt.savefig('2_cagr_ranking.png', dpi=300, bbox_inches='tight')
plt.close()
print("Saved 2_cagr_ranking.png")

# 3. Beta Convergence Scatter Plot
initial_gdp = {}
cagr_dict = {}
for country in countries:
    country_df = df[df['country'] == country].sort_values('year')
    initial_gdp[country] = country_df.iloc[0]['value']
    cagr_dict[country] = countries_data[country]['per_capita_constant']['growth']['cagr_pct']

log_initial = [np.log(initial_gdp[c]) for c in countries]
cagr_vals = [cagr_dict[c] for c in countries]

# Linear regression
slope, intercept, r_value, p_value, std_err = stats.linregress(log_initial, cagr_vals)

plt.figure(figsize=(10, 8))
for i, country in enumerate(countries):
    plt.scatter(np.log(initial_gdp[country]), cagr_dict[country],
                s=150, alpha=0.7, label=country_labels[country])

# Regression line
x_line = np.array([min(log_initial), max(log_initial)])
y_line = slope * x_line + intercept
plt.plot(x_line, y_line, 'r--', linewidth=2, label=f'Regression (R²={r_value**2:.3f}, p={p_value:.3f})')

plt.xlabel('Log(Initial GDP per capita, 1980)', fontsize=12)
plt.ylabel('CAGR (%) 1980-2010', fontsize=12)
plt.title('Beta Convergence Analysis: Initial GDP vs Growth Rate', fontsize=14, fontweight='bold')
plt.legend(loc='best', fontsize=9)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('3_beta_convergence.png', dpi=300, bbox_inches='tight')
plt.close()
print("Saved 3_beta_convergence.png")

# 4. Sigma Convergence (Coefficient of Variation over time)
years = sorted(df['year'].unique())
cv_over_time = []

for year in years:
    year_data = df[df['year'] == year]['value']
    cv = (year_data.std() / year_data.mean()) * 100
    cv_over_time.append(cv)

plt.figure(figsize=(12, 7))
plt.plot(years, cv_over_time, marker='o', linewidth=2, color='steelblue', markersize=6)

# Add trend line
z = np.polyfit(years, cv_over_time, 1)
p = np.poly1d(z)
plt.plot(years, p(years), "r--", linewidth=2, alpha=0.7,
         label=f'Trend (slope={z[0]:.4f})')

plt.xlabel('Year', fontsize=12)
plt.ylabel('Coefficient of Variation (%)', fontsize=12)
plt.title('Sigma Convergence: GDP Dispersion Over Time', fontsize=14, fontweight='bold')
plt.legend(loc='best', fontsize=10)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('4_sigma_convergence.png', dpi=300, bbox_inches='tight')
plt.close()
print("Saved 4_sigma_convergence.png")

# 5. Volatility Comparison Bar Chart
volatility_data = [(country_labels[c], countries_data[c]['per_capita_constant']['growth']['volatility'])
                   for c in countries]
volatility_data.sort(key=lambda x: x[1])
vol_countries, vol_values = zip(*volatility_data)

plt.figure(figsize=(10, 7))
colors = plt.cm.coolwarm(np.linspace(0.2, 0.8, len(vol_countries)))
bars = plt.bar(vol_countries, vol_values, color=colors, alpha=0.8)
plt.xlabel('Country', fontsize=12)
plt.ylabel('Volatility (%)', fontsize=12)
plt.title('GDP Growth Volatility by Country (1980-2010)', fontsize=14, fontweight='bold')
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', alpha=0.3)

# Add value labels
for bar, value in zip(bars, vol_values):
    plt.text(bar.get_x() + bar.get_width()/2, value + 0.05, f'{value:.2f}%',
             ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.savefig('5_volatility_comparison.png', dpi=300, bbox_inches='tight')
plt.close()
print("Saved 5_volatility_comparison.png")

# 6. Structural Breaks Timeline
plt.figure(figsize=(14, 8))

# Plot GDP evolution with structural breaks marked
for country in countries:
    country_df = df[df['country'] == country].sort_values('year')
    plt.plot(country_df['year'], country_df['value'], marker='', linewidth=1.5,
             alpha=0.5, label=country_labels[country])

    # Check for structural breaks
    if 'structural_breaks' in countries_data[country]['per_capita_constant']:
        breaks = countries_data[country]['per_capita_constant']['structural_breaks']
        for brk in breaks:
            break_year = pd.to_datetime(brk['date']).year
            break_value = country_df[country_df['year'] == break_year]['value'].values[0]
            plt.scatter(break_year, break_value, s=200, marker='X',
                       color='red', edgecolors='black', linewidth=2, zorder=5)
            plt.annotate(f"{country_labels[country]}\n{break_year}",
                        xy=(break_year, break_value),
                        xytext=(10, 10), textcoords='offset points',
                        fontsize=9, bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))

plt.xlabel('Year', fontsize=12)
plt.ylabel('GDP per capita (USD, constant 2010)', fontsize=12)
plt.title('Structural Breaks Detection in G7 GDP Evolution', fontsize=14, fontweight='bold')
plt.legend(loc='best', fontsize=9)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('6_structural_breaks.png', dpi=300, bbox_inches='tight')
plt.close()
print("Saved 6_structural_breaks.png")

# 7. Final GDP Ranking 2010
final_ranking = rankings['per_capita_constant_level']
final_countries = [country_labels[item['country']] for item in final_ranking]
final_values = [item['value'] for item in final_ranking]

plt.figure(figsize=(10, 7))
colors = plt.cm.plasma(np.linspace(0.3, 0.9, len(final_countries)))
bars = plt.bar(final_countries, final_values, color=colors, alpha=0.8)
plt.xlabel('Country', fontsize=12)
plt.ylabel('GDP per capita (USD, constant 2010)', fontsize=12)
plt.title('G7 GDP per Capita Ranking in 2010', fontsize=14, fontweight='bold')
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', alpha=0.3)

# Add value labels
for bar, value in zip(bars, final_values):
    plt.text(bar.get_x() + bar.get_width()/2, value + 500, f'${value:,.0f}',
             ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.savefig('7_final_gdp_ranking.png', dpi=300, bbox_inches='tight')
plt.close()
print("Saved 7_final_gdp_ranking.png")

print("\nAll visualizations created successfully!")
