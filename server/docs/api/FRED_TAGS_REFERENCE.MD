FRED Tags Tool – API Reference
Tool: search_fred_tags

Herramienta para listar y filtrar tags de FRED. Los tags son atributos que FRED le asigna a las series (por ejemplo: frecuencia, país, fuente, estacionalidad). Podés filtrar por nombre de tag, grupo de tag o búsqueda de texto, y ordenar por popularidad o cantidad de series.

Parámetros
Parámetros requeridos

👉 A diferencia de search_fred_series, este endpoint no necesita un search_text obligatorio. Podés llamarlo sin filtros y te trae los tags más usados.
Por lo tanto: ningún parámetro es estrictamente obligatorio.

Parámetros opcionales
Parámetro	Tipo	Default	Descripción
tag_names	string	None	Lista separada por ; de tags que sí querés incluir. Solo se devuelven los que coinciden con todos los nombres.
tag_group_id	string	None	Filtra por grupo de tags (frecuencia, fuente, geografía, etc.). Ver valores válidos abajo.
search_text	string	None	Texto para buscar dentro del nombre del tag. Búsqueda parcial.
realtime_start	string	hoy	Inicio de ventana de real-time (YYYY-MM-DD).
realtime_end	string	hoy	Fin de ventana de real-time (YYYY-MM-DD).
limit	int	1000	Máx. resultados por página (1–1000).
offset	int	0	Desplazamiento para paginar.
order_by	string	series_count	Campo por el que ordenar. Ver lista abajo.
sort_order	string	asc	Dirección de orden: "asc" o "desc".
file_type	string	xml	Formato de respuesta: "xml" o "json".
api_key	string	—	Tu API key de FRED (32 chars). En una herramienta interna la podés inyectar desde config.
Valores válidos
tag_group_id

Te dice de qué tipo es el tag:

freq – Frecuencia (monthly, quarterly…)

gen – General / concepto (employment, gdp…)

geo – Geografía (USA, state…)

geot – Tipo de geografía (nation, msa…)

rls – Release

seas – Estacionalidad (sa, nsa)

src – Fuente (bls, bea, oecd…)

cc – Citation & Copyright

order_by

series_count (default)

popularity

created

name

group_id

sort_order

asc

desc

Comportamiento de los filtros

tag_names: si ponés "gdp;oecd" te devuelve solo los tags que tengan ambos.

tag_group_id: útil para “dame solo las frecuencias” (freq) o “solo estacionalidad” (seas).

search_text: es una búsqueda de texto simple sobre el nombre del tag, p.ej. "unemp" te trae unemployment.

Formato de respuesta
{
  "tool": "search_fred_tags",
  "data": [
    {
      "name": "nation",
      "group_id": "geot",
      "notes": "Country Level",
      "created": "2012-02-27 10:18:19-06",
      "popularity": 100,
      "series_count": 105200
    }
  ],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "realtime_start": "2025-11-01",
    "realtime_end": "2025-11-01",
    "tag_names": null,
    "tag_group_id": null,
    "search_text": null,
    "limit": 1000,
    "offset": 0,
    "order_by": "series_count",
    "sort_order": "asc",
    "api_info": {
      "url": "https://api.stlouisfed.org/fred/tags?...",
      "status_code": 200,
      "rate_limit_remaining": "120"
    }
  }
}


Observaciones:

El JSON original de FRED va en un array tags. Acá lo estamos envolviendo en data para que sea consistente con tu otro tool.

metadata replica los parámetros usados y la info de paginación.

Ejemplos de uso
1. Traer los tags más usados (lo más básico)
search_fred_tags()


Equivalente a pedir: “dame hasta 1000 tags, ordenados por cantidad de series”.

2. Filtrar por grupo de frecuencia
search_fred_tags(
    tag_group_id="freq",
    order_by="name",
    sort_order="asc"
)


Devuelve cosas como monthly, quarterly, annual.

3. Buscar tags que mencionen “unemployment”
search_fred_tags(
    search_text="unemployment",
    order_by="popularity",
    sort_order="desc",
    limit=50
)

4. Incluir solo ciertos tags
search_fred_tags(
    tag_names="gdp;oecd",
    order_by="series_count",
    sort_order="desc"
)


Devuelve tags que cumplan ambos: gdp y oecd.

5. Paginación manual
# Primera página
search_fred_tags(
    search_text="labor",
    limit=100,
    offset=0
)

# Segunda página
search_fred_tags(
    search_text="labor",
    limit=100,
    offset=100
)


(FRED no tiene paginate=True acá como en tu ejemplo inventado para series, así que lo normal es paginar con offset.)

6. Filtrar por estacionalidad
search_fred_tags(
    tag_group_id="seas",
    order_by="popularity",
    sort_order="desc"
)


Te va a devolver sa, nsa, etc.

7. Ventana de real-time
search_fred_tags(
    realtime_start="2024-01-01",
    realtime_end="2024-12-31",
    limit=200
)

Errores comunes

La herramienta devuelve algo así:

{
  "error": "Invalid tag_group_id 'freqs'",
  "tool": "search_fred_tags",
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "tag_group_id": "freqs"
  }
}

Posibles causas

tag_group_id no está en: freq, gen, geo, geot, rls, seas, src, cc

order_by no está en: series_count, popularity, created, name, group_id

limit fuera de 1–1000

realtime_start / realtime_end con formato inválido

rate limit

Notas de implementación (por si lo vas a mapear 1:1 a una función)

Nombre del tool: search_fred_tags

Entrada mínima: {} (sin filtros)

Salida: objeto con tool, data (array de tags) y metadata

Mapeo de campos:

FRED tags → nuestra respuesta data

FRED count, offset, limit → metadata

URL y status → metadata.api_info

Semicolons: igual que en tu otro tool, usar ; en tag_names

Resumen rápido

¿Querés saber qué tags existen? → search_fred_tags()

¿Querés solo frecuencias? → tag_group_id="freq"

¿Querés solo estacionalidad? → tag_group_id="seas"

¿Querés buscar por texto? → search_text="price"

¿Querés ordenar por popularidad? → order_by="popularity", sort_order="desc"