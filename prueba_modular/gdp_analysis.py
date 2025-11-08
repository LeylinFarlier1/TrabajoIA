import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from datetime import datetime

# Datos de las series de FRED (GDP per capita en USD constantes 2010)
data_dict = {
    "USA": [
        {"date": "1980-01-01", "value": "31081.62163338"},
        {"date": "1981-01-01", "value": "31559.1293373937"},
        {"date": "1982-01-01", "value": "30696.0834358718"},
        {"date": "1983-01-01", "value": "31810.9216083487"},
        {"date": "1984-01-01", "value": "33818.8235524677"},
        {"date": "1985-01-01", "value": "34918.1302027193"},
        {"date": "1986-01-01", "value": "35794.8877745985"},
        {"date": "1987-01-01", "value": "36701.9453883904"},
        {"date": "1988-01-01", "value": "37889.3773472194"},
        {"date": "1989-01-01", "value": "38911.5418949927"},
        {"date": "1990-01-01", "value": "39200.0658103964"},
        {"date": "1991-01-01", "value": "38637.8398159491"},
        {"date": "1992-01-01", "value": "39447.9472847522"},
        {"date": "1993-01-01", "value": "40002.4762262205"},
        {"date": "1994-01-01", "value": "41106.9881841375"},
        {"date": "1995-01-01", "value": "41710.8207239918"},
        {"date": "1996-01-01", "value": "42783.8165710653"},
        {"date": "1997-01-01", "value": "44151.6860411494"},
        {"date": "1998-01-01", "value": "45596.4306860229"},
        {"date": "1999-01-01", "value": "47234.2455275781"},
        {"date": "2000-01-01", "value": "48616.2546267835"},
        {"date": "2001-01-01", "value": "48597.4246130164"},
        {"date": "2002-01-01", "value": "48967.3661209521"},
        {"date": "2003-01-01", "value": "49905.5233079503"},
        {"date": "2004-01-01", "value": "51348.3473392466"},
        {"date": "2005-01-01", "value": "52649.5713058632"},
        {"date": "2006-01-01", "value": "53596.3152369749"},
        {"date": "2007-01-01", "value": "54152.8292653448"},
        {"date": "2008-01-01", "value": "53703.9628962873"},
        {"date": "2009-01-01", "value": "51863.6183424227"},
        {"date": "2010-01-01", "value": "52812.682985453"}
    ],
    "Canada": [
        {"date": "1980-01-01", "value": "27622.3734030629"},
        {"date": "1981-01-01", "value": "28215.530855259"},
        {"date": "1982-01-01", "value": "26999.079084851"},
        {"date": "1983-01-01", "value": "27418.4916111044"},
        {"date": "1984-01-01", "value": "28762.9722015849"},
        {"date": "1985-01-01", "value": "29851.6432940057"},
        {"date": "1986-01-01", "value": "30183.4087940958"},
        {"date": "1987-01-01", "value": "31001.1298465676"},
        {"date": "1988-01-01", "value": "31951.5504658265"},
        {"date": "1989-01-01", "value": "32116.9233234971"},
        {"date": "1990-01-01", "value": "31700.5462613508"},
        {"date": "1991-01-01", "value": "30654.3331550624"},
        {"date": "1992-01-01", "value": "30563.3788132238"},
        {"date": "1993-01-01", "value": "31032.7546058282"},
        {"date": "1994-01-01", "value": "32074.1562636226"},
        {"date": "1995-01-01", "value": "32595.4515150443"},
        {"date": "1996-01-01", "value": "32801.3018574024"},
        {"date": "1997-01-01", "value": "33867.0079071879"},
        {"date": "1998-01-01", "value": "34894.6134264056"},
        {"date": "1999-01-01", "value": "36391.535343959"},
        {"date": "2000-01-01", "value": "37906.8601321366"},
        {"date": "2001-01-01", "value": "38200.456120621"},
        {"date": "2002-01-01", "value": "38921.6673033743"},
        {"date": "2003-01-01", "value": "39270.0234577749"},
        {"date": "2004-01-01", "value": "40108.7587456658"},
        {"date": "2005-01-01", "value": "41006.2229523971"},
        {"date": "2006-01-01", "value": "41663.5123057295"},
        {"date": "2007-01-01", "value": "42106.8724378248"},
        {"date": "2008-01-01", "value": "42067.5687072607"},
        {"date": "2009-01-01", "value": "40376.4153847836"},
        {"date": "2010-01-01", "value": "41164.3399119626"}
    ],
    "Japan": [
        {"date": "1980-01-01", "value": "19334.3747441799"},
        {"date": "1981-01-01", "value": "20011.8292508515"},
        {"date": "1982-01-01", "value": "20525.2958514217"},
        {"date": "1983-01-01", "value": "21122.9648423607"},
        {"date": "1984-01-01", "value": "21912.1518618966"},
        {"date": "1985-01-01", "value": "22898.9942415029"},
        {"date": "1986-01-01", "value": "23527.7125188746"},
        {"date": "1987-01-01", "value": "24503.0845657844"},
        {"date": "1988-01-01", "value": "26026.8648821365"},
        {"date": "1989-01-01", "value": "27199.9399695936"},
        {"date": "1990-01-01", "value": "28422.2131194472"},
        {"date": "1991-01-01", "value": "29308.2740881269"},
        {"date": "1992-01-01", "value": "29462.6539671073"},
        {"date": "1993-01-01", "value": "29232.4397928009"},
        {"date": "1994-01-01", "value": "29466.7552451648"},
        {"date": "1995-01-01", "value": "30171.1637924153"},
        {"date": "1996-01-01", "value": "31046.1701544217"},
        {"date": "1997-01-01", "value": "31276.1930771989"},
        {"date": "1998-01-01", "value": "30795.0888900919"},
        {"date": "1999-01-01", "value": "30636.2661169604"},
        {"date": "2000-01-01", "value": "31430.631130325"},
        {"date": "2001-01-01", "value": "31476.0520665746"},
        {"date": "2002-01-01", "value": "31416.1241772309"},
        {"date": "2003-01-01", "value": "31830.217584972"},
        {"date": "2004-01-01", "value": "32515.1158024695"},
        {"date": "2005-01-01", "value": "33098.5474664881"},
        {"date": "2006-01-01", "value": "33531.518563066"},
        {"date": "2007-01-01", "value": "33990.0360341367"},
        {"date": "2008-01-01", "value": "33557.6454041595"},
        {"date": "2009-01-01", "value": "31651.0837739562"},
        {"date": "2010-01-01", "value": "32942.2020783835"}
    ],
    "Germany": [
        {"date": "1980-01-01", "value": "23977.2698576818"},
        {"date": "1981-01-01", "value": "24067.4825489522"},
        {"date": "1982-01-01", "value": "23995.2661838189"},
        {"date": "1983-01-01", "value": "24436.5473264161"},
        {"date": "1984-01-01", "value": "25213.38204825"},
        {"date": "1985-01-01", "value": "25858.0588621429"},
        {"date": "1986-01-01", "value": "26437.4177349407"},
        {"date": "1987-01-01", "value": "26766.9600591944"},
        {"date": "1988-01-01", "value": "27651.0362699101"},
        {"date": "1989-01-01", "value": "28507.1621309974"},
        {"date": "1990-01-01", "value": "29747.6909354385"},
        {"date": "1991-01-01", "value": "31040.2935634693"},
        {"date": "1992-01-01", "value": "31425.6476019368"},
        {"date": "1993-01-01", "value": "30915.8728850114"},
        {"date": "1994-01-01", "value": "31609.1102824496"},
        {"date": "1995-01-01", "value": "31990.7949834569"},
        {"date": "1996-01-01", "value": "32229.4778712612"},
        {"date": "1997-01-01", "value": "32779.2802466297"},
        {"date": "1998-01-01", "value": "33461.3192177074"},
        {"date": "1999-01-01", "value": "34152.0032259735"},
        {"date": "2000-01-01", "value": "35087.0891588694"},
        {"date": "2001-01-01", "value": "35601.3628316391"},
        {"date": "2002-01-01", "value": "35460.4121391449"},
        {"date": "2003-01-01", "value": "35252.9745130135"},
        {"date": "2004-01-01", "value": "35670.4870225493"},
        {"date": "2005-01-01", "value": "36006.8578127742"},
        {"date": "2006-01-01", "value": "37437.3918784909"},
        {"date": "2007-01-01", "value": "38570.9146369495"},
        {"date": "2008-01-01", "value": "38996.1434106777"},
        {"date": "2009-01-01", "value": "36927.1920288238"},
        {"date": "2010-01-01", "value": "38517.4397880176"}
    ],
    "France": [
        {"date": "1980-01-01", "value": "23050.9255953042"},
        {"date": "1981-01-01", "value": "23186.7612665684"},
        {"date": "1982-01-01", "value": "23666.5121788084"},
        {"date": "1983-01-01", "value": "23836.4018927227"},
        {"date": "1984-01-01", "value": "24102.0176176027"},
        {"date": "1985-01-01", "value": "24358.1382748825"},
        {"date": "1986-01-01", "value": "24813.0302579158"},
        {"date": "1987-01-01", "value": "25308.620924146"},
        {"date": "1988-01-01", "value": "26374.1221811161"},
        {"date": "1989-01-01", "value": "27372.0534763161"},
        {"date": "1990-01-01", "value": "27992.9751471374"},
        {"date": "1991-01-01", "value": "28197.2359540607"},
        {"date": "1992-01-01", "value": "28482.5194675509"},
        {"date": "1993-01-01", "value": "28257.0962487817"},
        {"date": "1994-01-01", "value": "28822.5006495069"},
        {"date": "1995-01-01", "value": "29379.6158424052"},
        {"date": "1996-01-01", "value": "29683.7786067651"},
        {"date": "1997-01-01", "value": "30325.522871824"},
        {"date": "1998-01-01", "value": "31256.5073830655"},
        {"date": "1999-01-01", "value": "32152.7207478734"},
        {"date": "2000-01-01", "value": "33255.1379642335"},
        {"date": "2001-01-01", "value": "33640.6738002565"},
        {"date": "2002-01-01", "value": "33753.5782979758"},
        {"date": "2003-01-01", "value": "33840.6175720101"},
        {"date": "2004-01-01", "value": "34557.1471111581"},
        {"date": "2005-01-01", "value": "34946.0372494703"},
        {"date": "2006-01-01", "value": "35645.4162427116"},
        {"date": "2007-01-01", "value": "36322.1685141004"},
        {"date": "2008-01-01", "value": "36257.3658930938"},
        {"date": "2009-01-01", "value": "35052.8510772683"},
        {"date": "2010-01-01", "value": "35578.1968010183"}
    ],
    "Italy": [
        {"date": "1980-01-01", "value": "21901.9268708549"},
        {"date": "1981-01-01", "value": "22060.3287067697"},
        {"date": "1982-01-01", "value": "22135.1628545397"},
        {"date": "1983-01-01", "value": "22385.8416028019"},
        {"date": "1984-01-01", "value": "23102.8115427941"},
        {"date": "1985-01-01", "value": "23742.3854949723"},
        {"date": "1986-01-01", "value": "24420.0802858599"},
        {"date": "1987-01-01", "value": "25196.9881183266"},
        {"date": "1988-01-01", "value": "26241.1619056876"},
        {"date": "1989-01-01", "value": "27109.970559768"},
        {"date": "1990-01-01", "value": "27625.1792306413"},
        {"date": "1991-01-01", "value": "28030.7653841073"},
        {"date": "1992-01-01", "value": "28245.4271054692"},
        {"date": "1993-01-01", "value": "27987.4328969281"},
        {"date": "1994-01-01", "value": "28583.6255328648"},
        {"date": "1995-01-01", "value": "29408.3209572297"},
        {"date": "1996-01-01", "value": "29795.6597750915"},
        {"date": "1997-01-01", "value": "30353.3778243995"},
        {"date": "1998-01-01", "value": "30892.1758654455"},
        {"date": "1999-01-01", "value": "31405.2609007683"},
        {"date": "2000-01-01", "value": "32609.66746283"},
        {"date": "2001-01-01", "value": "33243.599343976"},
        {"date": "2002-01-01", "value": "33267.4474482048"},
        {"date": "2003-01-01", "value": "33110.1698494812"},
        {"date": "2004-01-01", "value": "33348.9744820456"},
        {"date": "2005-01-01", "value": "33407.6754716472"},
        {"date": "2006-01-01", "value": "33873.0493680093"},
        {"date": "2007-01-01", "value": "34159.9109244074"},
        {"date": "2008-01-01", "value": "33550.6340800063"},
        {"date": "2009-01-01", "value": "31587.0638416305"},
        {"date": "2010-01-01", "value": "31928.5543621096"}
    ],
    "United Kingdom": [
        {"date": "1980-01-01", "value": "23526.2555043517"},
        {"date": "1981-01-01", "value": "23332.8025676938"},
        {"date": "1982-01-01", "value": "23806.7980916528"},
        {"date": "1983-01-01", "value": "24803.4271519669"},
        {"date": "1984-01-01", "value": "25326.1296660232"},
        {"date": "1985-01-01", "value": "26316.7154348235"},
        {"date": "1986-01-01", "value": "27082.9819543398"},
        {"date": "1987-01-01", "value": "28482.8666757154"},
        {"date": "1988-01-01", "value": "30048.820666255"},
        {"date": "1989-01-01", "value": "30743.2275250086"},
        {"date": "1990-01-01", "value": "30876.3706404357"},
        {"date": "1991-01-01", "value": "30441.4813420211"},
        {"date": "1992-01-01", "value": "30481.0348883355"},
        {"date": "1993-01-01", "value": "31165.1544491287"},
        {"date": "1994-01-01", "value": "32281.4801601039"},
        {"date": "1995-01-01", "value": "33011.2945663233"},
        {"date": "1996-01-01", "value": "33777.5280810971"},
        {"date": "1997-01-01", "value": "35349.7906380412"},
        {"date": "1998-01-01", "value": "36446.2616767045"},
        {"date": "1999-01-01", "value": "37435.884438888"},
        {"date": "2000-01-01", "value": "38921.896573883"},
        {"date": "2001-01-01", "value": "39769.8719792093"},
        {"date": "2002-01-01", "value": "40312.9824110757"},
        {"date": "2003-01-01", "value": "41390.6062127939"},
        {"date": "2004-01-01", "value": "42167.3557264259"},
        {"date": "2005-01-01", "value": "43023.2277090836"},
        {"date": "2006-01-01", "value": "43724.8957366594"},
        {"date": "2007-01-01", "value": "44524.5706965197"},
        {"date": "2008-01-01", "value": "44065.6156693521"},
        {"date": "2009-01-01", "value": "41712.8319164411"},
        {"date": "2010-01-01", "value": "42311.4329830247"}
    ]
}

# Crear DataFrame
df_list = []
for country, data in data_dict.items():
    country_df = pd.DataFrame(data)
    country_df['date'] = pd.to_datetime(country_df['date'])
    country_df['year'] = country_df['date'].dt.year
    country_df['value'] = country_df['value'].astype(float)
    country_df['country'] = country
    df_list.append(country_df[['year', 'country', 'value']])

df = pd.concat(df_list, ignore_index=True)
df_pivot = df.pivot(index='year', columns='country', values='value')

print("=" * 80)
print("ANALISIS GDP G7 (1980-2010) - ENFOQUE MODULAR")
print("=" * 80)
print(f"\nData source: FRED (Federal Reserve Economic Data)")
print(f"Series: Constant GDP per capita (2010 US Dollars)")
print(f"Period: 1980-2010 (31 years)")
print(f"Countries: {', '.join(df_pivot.columns.tolist())}")
print("\n")

# =========================================================================
# FASE 1: CÁLCULO DE MÉTRICAS BÁSICAS
# =========================================================================
print("\n" + "=" * 80)
print("FASE 1: METRICAS BASICAS POR PAIS")
print("=" * 80)

metrics = {}
for country in df_pivot.columns:
    series = df_pivot[country].values

    # Valores iniciales y finales
    initial_value = series[0]
    final_value = series[-1]

    # CAGR: Compound Annual Growth Rate
    n_years = len(series) - 1
    cagr = ((final_value / initial_value) ** (1 / n_years) - 1) * 100

    # Calcular tasas de crecimiento año a año
    growth_rates = np.diff(series) / series[:-1] * 100

    # Volatilidad (desviación estándar de growth rates)
    volatility = np.std(growth_rates)

    # Índice de estabilidad
    stability_index = 1 / (1 + volatility)

    # Crecimiento total
    total_growth = ((final_value - initial_value) / initial_value) * 100

    metrics[country] = {
        'initial_gdp': initial_value,
        'final_gdp': final_value,
        'cagr': cagr,
        'volatility': volatility,
        'stability_index': stability_index,
        'total_growth': total_growth,
        'growth_rates': growth_rates
    }

    print(f"\n{country}:")
    print(f"  GDP 1980: ${initial_value:,.2f}")
    print(f"  GDP 2010: ${final_value:,.2f}")
    print(f"  Total Growth: {total_growth:.2f}%")
    print(f"  CAGR: {cagr:.2f}%")
    print(f"  Volatility: {volatility:.2f}%")
    print(f"  Stability Index: {stability_index:.4f}")

# =========================================================================
# FASE 2: RANKINGS
# =========================================================================
print("\n\n" + "=" * 80)
print("FASE 2: RANKINGS")
print("=" * 80)

# Ranking por nivel actual (2010)
print("\n--- TOP 7 por GDP per capita 2010 ---")
ranking_level = sorted(metrics.items(), key=lambda x: x[1]['final_gdp'], reverse=True)
for i, (country, data) in enumerate(ranking_level, 1):
    print(f"{i}. {country}: ${data['final_gdp']:,.2f}")

# Ranking por crecimiento (CAGR)
print("\n--- TOP 7 por CAGR (1980-2010) ---")
ranking_growth = sorted(metrics.items(), key=lambda x: x[1]['cagr'], reverse=True)
for i, (country, data) in enumerate(ranking_growth, 1):
    print(f"{i}. {country}: {data['cagr']:.2f}%")

# Ranking por estabilidad
print("\n--- TOP 7 por Estabilidad ---")
ranking_stability = sorted(metrics.items(), key=lambda x: x[1]['stability_index'], reverse=True)
for i, (country, data) in enumerate(ranking_stability, 1):
    print(f"{i}. {country}: {data['stability_index']:.4f} (volatility: {data['volatility']:.2f}%)")

# =========================================================================
# FASE 3: ANÁLISIS DE CONVERGENCIA SIGMA
# =========================================================================
print("\n\n" + "=" * 80)
print("FASE 3: CONVERGENCIA SIGMA")
print("=" * 80)

# Calcular coeficiente de variación por año
years = df_pivot.index.values
cv_values = []

for year in years:
    values = df_pivot.loc[year].values
    mean_val = np.mean(values)
    std_val = np.std(values, ddof=1)
    cv = std_val / mean_val
    cv_values.append(cv)

cv_values = np.array(cv_values)

# Regresión lineal: CV = a + b*time
X = np.arange(len(years))
slope, intercept, r_value, p_value, std_err = stats.linregress(X, cv_values)

print(f"\nCoeficiente de Variacion:")
print(f"  1980: {cv_values[0]:.4f}")
print(f"  2010: {cv_values[-1]:.4f}")
print(f"  Cambio: {(cv_values[-1] - cv_values[0]):.4f}")
print(f"\nRegresion lineal (CV vs tiempo):")
print(f"  Pendiente: {slope:.6f}")
print(f"  R-cuadrado: {r_value**2:.4f}")
print(f"  p-value: {p_value:.4f}")

if p_value < 0.05 and slope < 0:
    print(f"\n[OK] CONVERGENCIA SIGMA DETECTADA (p < 0.05, pendiente negativa)")
    print(f"  Los paises del G7 se estan volviendo mas similares en terminos de GDP per capita.")
elif p_value < 0.05 and slope > 0:
    print(f"\n[X] DIVERGENCIA DETECTADA (p < 0.05, pendiente positiva)")
    print(f"  Los paises del G7 se estan volviendo mas diferentes.")
else:
    print(f"\n[O] NO HAY CONVERGENCIA/DIVERGENCIA SIGNIFICATIVA (p >= 0.05)")

# =========================================================================
# FASE 4: ANALISIS DE CONVERGENCIA BETA
# =========================================================================
print("\n\n" + "=" * 80)
print("FASE 4: CONVERGENCIA BETA")
print("=" * 80)

# Convergencia beta: países con menor GDP inicial deberían crecer más rápido
initial_gdps = [metrics[c]['initial_gdp'] for c in df_pivot.columns]
cagrs = [metrics[c]['cagr'] for c in df_pivot.columns]

# Log de GDP inicial
log_initial_gdps = np.log(initial_gdps)

# Regresión: CAGR = a + b*log(GDP_inicial)
slope_beta, intercept_beta, r_beta, p_beta, std_err_beta = stats.linregress(log_initial_gdps, cagrs)

print(f"\nRegresion: CAGR vs log(GDP inicial 1980)")
print(f"  Pendiente (beta): {slope_beta:.4f}")
print(f"  R-cuadrado: {r_beta**2:.4f}")
print(f"  p-value: {p_beta:.4f}")

if p_beta < 0.05 and slope_beta < 0:
    print(f"\n[OK] CONVERGENCIA BETA DETECTADA (p < 0.05, beta negativo)")
    print(f"  Los paises con menor GDP inicial crecieron mas rapido (catch-up effect).")
elif p_beta < 0.05 and slope_beta > 0:
    print(f"\n[X] DIVERGENCIA BETA DETECTADA (p < 0.05, beta positivo)")
    print(f"  Los paises con mayor GDP inicial crecieron mas rapido.")
else:
    print(f"\n[O] NO HAY CONVERGENCIA BETA SIGNIFICATIVA (p >= 0.05)")

print(f"\nDatos por pais:")
for country, initial, cagr_val in zip(df_pivot.columns, initial_gdps, cagrs):
    print(f"  {country}: GDP 1980 = ${initial:,.0f}, CAGR = {cagr_val:.2f}%")

# =========================================================================
# FASE 5: DETECCION DE STRUCTURAL BREAKS
# =========================================================================
print("\n\n" + "=" * 80)
print("FASE 5: DETECCION DE STRUCTURAL BREAKS")
print("=" * 80)

structural_breaks = {}

for country in df_pivot.columns:
    growth_rates = metrics[country]['growth_rates']

    # Calcular varianza móvil (ventana de 5 años)
    window = 5
    rolling_var = []

    for i in range(len(growth_rates) - window + 1):
        window_data = growth_rates[i:i+window]
        rolling_var.append(np.var(window_data, ddof=1))

    # Detectar cambios grandes en la varianza
    breaks = []
    threshold_multiplier = 1.5  # Cambio de 50% o más

    for i in range(1, len(rolling_var)):
        ratio = rolling_var[i] / rolling_var[i-1] if rolling_var[i-1] != 0 else 0

        if ratio > threshold_multiplier:
            year_idx = i + window - 1
            if year_idx < len(years):
                breaks.append({
                    'year': int(years[year_idx]),
                    'type': 'variance_increase',
                    'ratio': ratio
                })
        elif ratio < (1/threshold_multiplier) and ratio > 0:
            year_idx = i + window - 1
            if year_idx < len(years):
                breaks.append({
                    'year': int(years[year_idx]),
                    'type': 'variance_decrease',
                    'ratio': ratio
                })

    structural_breaks[country] = breaks

    if breaks:
        print(f"\n{country}:")
        for brk in breaks:
            tipo = "[UP] Aumento volatilidad" if brk['type'] == 'variance_increase' else "[DOWN] Reduccion volatilidad"
            print(f"  {brk['year']}: {tipo} (ratio: {brk['ratio']:.2f}x)")
    else:
        print(f"\n{country}: No se detectaron structural breaks significativos")

# =========================================================================
# FASE 6: GUARDAR METRICAS EN JSON
# =========================================================================
print("\n\n" + "=" * 80)
print("FASE 6: GUARDAR RESULTADOS")
print("=" * 80)

results = {
    'metadata': {
        'analysis_date': datetime.now().isoformat(),
        'period': '1980-2010',
        'countries': list(df_pivot.columns),
        'data_source': 'FRED',
        'series_type': 'Constant GDP per capita (2010 US Dollars)'
    },
    'metrics_by_country': {},
    'rankings': {
        'by_final_gdp': [(c, m['final_gdp']) for c, m in ranking_level],
        'by_cagr': [(c, m['cagr']) for c, m in ranking_growth],
        'by_stability': [(c, m['stability_index']) for c, m in ranking_stability]
    },
    'convergence': {
        'sigma': {
            'cv_initial': float(cv_values[0]),
            'cv_final': float(cv_values[-1]),
            'cv_change': float(cv_values[-1] - cv_values[0]),
            'slope': float(slope),
            'r_squared': float(r_value**2),
            'p_value': float(p_value),
            'significant': bool(p_value < 0.05),
            'converging': bool(p_value < 0.05 and slope < 0)
        },
        'beta': {
            'slope': float(slope_beta),
            'r_squared': float(r_beta**2),
            'p_value': float(p_beta),
            'significant': bool(p_beta < 0.05),
            'catch_up_effect': bool(p_beta < 0.05 and slope_beta < 0)
        }
    },
    'structural_breaks': structural_breaks
}

# Agregar métricas por país
for country, m in metrics.items():
    results['metrics_by_country'][country] = {
        'initial_gdp': float(m['initial_gdp']),
        'final_gdp': float(m['final_gdp']),
        'total_growth_pct': float(m['total_growth']),
        'cagr_pct': float(m['cagr']),
        'volatility_pct': float(m['volatility']),
        'stability_index': float(m['stability_index'])
    }

# Guardar JSON
with open('analysis_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\n[OK] Resultados guardados en: analysis_results.json")

# Guardar datos crudos en CSV
df.to_csv('gdp_data_raw.csv', index=False)
print(f"[OK] Datos crudos guardados en: gdp_data_raw.csv")

print("\n" + "=" * 80)
print("ANALISIS COMPLETADO")
print("=" * 80)
