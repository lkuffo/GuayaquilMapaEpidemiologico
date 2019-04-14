# Mapa Epidemiologico de Guayaquil
Una iniciativa sin fines de lucro de la Escuela Superior Politécnica del Litoral (ESPOL) y el Hospital León Becerra de Guayaquil.
Guayaquil Health Map es un proyecto que busca monitorear la incidencia de enfermedades a lo largo de los diferentes sectores de la ciudad de Guayaquil, haciendo uso de mapas geográficos divididos hasta una granularidad geográfica de barrios.

Con Guayaquil Health Map buscamos encontrar zonas en donde una condición de salud presenta un grado de aparición anómalo con respecto al resto de la ciudad. Esto, con el fin de poder encontrar correlaciones entre las características geográficas o factores externos (e.g. materiales de construcción) de un sector y la incidencia de las enfermedades.


## Gye Health Map
Aplicación Web desarrollada en el Framework Flask, y jQuery en Front End. La renderización de mapas se realiza en Leaflet.js. En esta aplicación se muestran las diferentes instituciones de la cual tenemos datos disponibles, una introducción al proyecto y los responsables.

La generación de mapas es dinámica, utilizando los filtros enviados desde la interfaz de usuario, partiendo de los datos anonimizados por parroquia-sector-cie10 localizado en el Back End.

Para la generación de mapas realizamos la construccion de un API al cual se le envian como parámetros los diferentes filtros que se desean utilizar, y devuelve un objeto con los casos absolutos y relativos por sector.

https://gye-health-map.herokuapp.com

## Testing Scripts

Scripts utilizados para realizar:
- Análisis exploratorios sobre los datos de las instituciones. (`./TestingScripts/scripts/exploratory_analysis/*`)
- Geolocalización de direcciones (`./TestingScripts/scripts/geolocation/neighbours_mapping.py  `): La geolocalización se realiza a través de el uso de expresiones regulares y una estrategia greedy siguiendo los siguientes pasos:
   - Detectar el tipo de direccion (intersección de calles o dirección completa) a través de expresiones regulares.
   - En caso de ser una intersección de calles, se compara la dirección con una base de datos depurada de intersecciones de calles para encontrar coincidencias.
   - En caso de ser una dirección completa, se procede a buscar entidades clave dentro de la dirección siguiendo el siguiente orden jerárquico de búsqueda de coincidencia de strings por n-grams para poder mapear la dirección a un sector de la ciudad.
      - Sector específico (e.g. Alborada X etapa, Sauces 8)
      - Sector General (e.g. Alborada, Sauces)
      - Parroquia (e.g. Tarqui, Tarqui)
- Generación de mapas en Bokeh. (`./TestingScripts/scripts/maps/points_mapping.py  `)

## Data

Los datos utilizados en el proyecto se encuentran dentro del directorio `./DATA`

Aquí se hace una distinción entre tres tipos de datos:
- Datos Geográficos: Archivos de tipo .geojson con los shapefiles de los diferentes sectores de la ciudad de Guayaquil. Aquí se encuentran dos archivos que comprenden la división a nivel de:
   - Parroquias
   - Sectores

- Datos en Crudo: Son los datos que tenemos de fuentes externas, sin haber pasado por ningun procesamiento. Aqui se encuentran los datos de:
   - Registros de los pacientes.
   - Mapeo de los sectores de Guayaquil
   - Agrupaciones de CIE10.

- Datos Anonimizados: Son los datos de los pacientes que han sido anonimizados. Este proceso comprende la deteccion de un sector a partir de la dirección en crudo del paciente.
   - Casos Totales por Sector (`./DATA/anonimizedData/casos_totales.csv`)
   - Casos por Sector y CIE10 (`./DATA/anonimizedData/neighboursMapping.csv`)
   - Casos por Registro (anonimizacion parcial) (`./DATA/anonimizedData/neighboursMappingByRegister`)