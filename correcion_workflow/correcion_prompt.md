# PROMPT: Gráfico de Quiebres Estructurales - Timeline de Cambios de Volatilidad

Genera un script Python que cree un gráfico de línea de tiempo mostrando los quiebres estructurales detectados en series temporales económicas de múltiples países.

## Criterio de Detección de Quiebres

**Metodología de Varianza Móvil (Rolling Variance):**

1. **Cálculo de varianza móvil**: 
   - Calcular varianza en ventanas móviles de 5 años sobre las tasas de crecimiento
   - `rolling_var[i] = variance(growth_rates[i:i+5])`

2. **Comparación entre ventanas consecutivas**:
   - Ratio: `ratio = rolling_var[i] / rolling_var[i-1]`

3. **Clasificación de quiebres**:
   - **Aumento de volatilidad** (`variance_increase`): `ratio > 1.5`
     - La varianza actual es 50% mayor o más que la anterior
   - **Disminución de volatilidad** (`variance_decrease`): `ratio < 0.67` (1/1.5)
     - La varianza actual es 33% menor o menos que la anterior
Se define un quiebre estructural en la volatilidad cuando la varianza muestral del crecimiento del PIB, calculada en ventanas móviles de 5 años, cambia al menos un 50 % entre dos ventanas consecutivas (ratio > 1.5 para aumentos, ratio < 2/3 para reducciones), asignando el quiebre al último año de la ventana donde ocurre el cambio.
**Parámetros del análisis:**
- Window size: 5 años
- Threshold multiplier: 1.5
- Métrica: Varianza de tasas de crecimiento año a año

## Especificaciones del Gráfico

**Configuración Base:**
- Tipo: Scatter plot timeline
- Tamaño: 16x10 pulgadas
- Backend: matplotlib con 'Agg' (no interactivo)
- Estilo: 'seaborn-v0_8-darkgrid'

**Ejes:**
- **Eje X**: Años (rango automático extraído de los datos)
- **Eje Y**: Países (una posición por país, asignada automáticamente)

**Marcadores de Quiebres:**
- **Triángulo rojo hacia arriba (^)**: Aumento de volatilidad
  - Color: 'red'
  - Tamaño: 200
  - Condición: `type == 'variance_increase'`
- **Triángulo verde hacia abajo (v)**: Disminución de volatilidad
  - Color: 'green'
  - Tamaño: 200
  - Condición: `type == 'variance_decrease'`
- Todos los marcadores: borde negro (linewidth=1.5), transparencia=0.7, zorder=3

## Características Dinámicas

1. **Detección automática de crisis**: Identificar automáticamente años con múltiples quiebres simultáneos y marcarlos con líneas verticales
2. **Posicionamiento adaptativo**: Calcular posiciones Y según el número total de países
3. **Rango temporal flexible**: Adaptar límites de ejes según min/max años en los datos
4. **Escalado inteligente**: Ajustar tamaño de fuentes y marcadores si hay más de 10 países

## Formato Visual

- **Grid**: Solo eje X, alpha=0.3
- **Título**: "Structural Breaks Timeline (Volatility Changes)", fontsize=16, bold, pad=20
- **Etiqueta X**: "Year", fontsize=14, bold
- **Etiquetas Y**: Nombres de países, fontsize=12
- **Leyenda**: 
  - Ubicación: 'upper left'
  - Elementos: Explicar triángulo rojo (Volatility Increase) y verde (Volatility Decrease)
  - Fontsize: 11
  - Usar `matplotlib.lines.Line2D` para crear elementos personalizados

## Salida

- **Archivo**: `6_structural_breaks.png`
- **Resolución**: 300 dpi
- **Layout**: `tight_layout()` y `bbox_inches='tight'`
- **Mensaje**: "[OK] Grafico 6 guardado: 6_structural_breaks.png"

## Requisitos de Flexibilidad

- NO hardcodear años específicos de crisis
- NO asumir número fijo de países (debe funcionar con 3, 7, 20+ países)
- Adaptar automáticamente a cualquier rango temporal (1950-2024, 2000-2010, etc.)
- Si un país no tiene quiebres detectados, no mostrar marcadores para ese país
- Calcular dinámicamente límites de ejes X basados en los datos reales

## Librerías Requeridas
```python
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd
import json
import numpy as np