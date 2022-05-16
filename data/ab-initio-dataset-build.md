# Construcción del Dataset (Raster-Side)

## Metodología

La metodología propuesta supone la descarga de las imágenes completas. Existen alternativas como el procesamiento
via secciones o usando COG (Cloud optimized GEOTiff) que son completamente viables y no invalidan el proceso
descripto a continuación.

### Ab-initio (Al inicio)

- Se descarga el conjunto total de imágenes para un dato lapso temporal (con ciertos criterios para la parte de nubes) 
se genera un recorte sobre la zona de interés (supongamos una ciudad)

- El parche obtenido se genera con un cierto numero de bandas y se archiva.
	- Las bandas que se utilizan se definen a priori y no son modificables (al menos fácilmente) una vez comenzado el flujo de procesamiento. La resolución es la nativa o la mayor posible (estamos pensando en Sentinel 2 a 10 m). En 
	aquellos casos que la banda tenga menor resolución se resamplea a la mayor consistente con el resto de las bandas.

- Dado un parche (y fecha)
	- calculamos los indices para cada uno de los ROIs dentro de la zona general
	- unimos el conjunto de datos
	- seguimos con la fecha siguiente
	
Esto nos permite construir una serie temporal para cada roi (dentro de una zona de interés), la cual sera analizada y caracterizada para su posterior uso. Esta caracterización permitirá generar el forecasting o predicción de comportamiento.

#### Análisis - Extra

El análisis inicial o exploración contempla la selección de aquellos indices que o 
"features" que nos van a permitir describir de manera mas realista el proceso que intentamos monitorear.


### On-Duty (En regimen)

- Descarga de zona de interés (en cuasi-tiempo real)
- Obtener los indices de los ROIs dentro de la zona de interés (por rois dentro de la zona de interés nos estamos refiriendo a cada parque, plaza, etc dentro de una ciudad por ejemplo)
- Fusionar los datos con el set histórico
- Generar la predicción y comparar el comportamiento.
- Generar las alarmas y acciones cuando (bajo cierto criterio) el comportamiento no sea el esperado.

### Información Respecto a Procesados

- El conjunto de datos procesados corresponde a todos aquellos circunscriptos bajo el [AOI de cordoba](./cba/cordoba.geojson).
 ![aoi](media/zona-interes-cba.png)
 en  lineas rojas la imagen satelital (pisada del satelite) y en azul el aoi de Córdoba

- Una muestra de los datos procesados se pueden observar en:
	- [sample-datos](cba/espacios-verdes-dataset-sample.csv)

- Los datos procesados entre 2017 y 2022 se pueden consultar en:
	- [datos pre-procesados 2017/2022](https://drive.google.com/file/d/1tgbIQaEXzIghcFYyd2YM9iMho4TDHHFd/view?usp=sharing) (csv comprimido en zip)

- El conjunto de datos procesados por raster (un csv x raster) se puede encontrar 
	- [datos pre-procesados csv x raster 2017 /2022 ](https://drive.google.com/file/d/1Cz3-LleDD1FGuCYnI8Y5Ih-MFWwnQtJK/view?usp=sharing) (276 csvs comprimidos en zip)

- El porcentaje de nubes calculadas sobre el aoi de córdoba (no la imagen satelital completa) para cada parche procesado se puede consultar en:
	- [clouds-on-raster-shape](../data/cba/clouds-on-raster-shape.csv)

#### Espacios NO verdes (o Indefinidos)

Adicionalmente para la etapa de clasificación adicionamos un dataset (que utiliza el mismo set de imágenes) que corresponde a zonas consideradas NO espacio verde (aunque alguna de ellas pueda involucrar parte de ellas):

- Los datos procesados entre 2017 y 2022 se pueden consultar en:
	- [datos pre-procesados 2017/2022- NO verde](https://drive.google.com/file/d/1mfir4DZxT3g9tQkPJzCAZYy2VS2VHp7O/view?usp=sharing) (csv comprimido en zip)

- El conjunto de datos procesados por raster (un csv x raster) se puede encontrar 
	- [datos pre-procesados csv x raster 2017 /2022  - NO Verde ](https://drive.google.com/file/d/1KYbBCwiqzEREX_2g5OYVDbMNjPkT9Qxs/view?usp=sharing) (276 csvs comprimidos en zip)




### Imágenes - CBA

El conjunto de imágenes utilizadas se puede encontrar en:

- descargadas: [imágenes-descargadas](cba/productos-descargados-cba.cvs)
- procesadas: [imágenes-descargadas](cba/cropped-files.csv)

Teniendo el product-id es posible descargarlas utilizando algunas de las apis al respecto.

__NOTA__: Las imágenes crudas no están disponibles en los links anteriores, pero si es posible descargarlas utilizando el primero de ellos y utilizando alguna de las apis mencionadas en [ab-initio-mev-cba-1](../notebooks/ab-initio-mev-cba-1.ipynb)


__NOTA__: Se procesaron 276 imágenes en total con un tamaño de ~ 178 Gb.

#### Imágenes x fecha y nubosidad

La cantidad de imágenes por fecha y nubosidad se puede observar en:
![imágenes-fecha-nubosidad](../data/cba/images-month-year-clouds.jpg)

#### Parches

Adicionalmente ponemos a disposición al menos 12 parches (1 por mes) de la ciudad de Cordoba:
- parches: [parches-tif](https://drive.google.com/drive/folders/1OhWuafgPCZxoASy29oCRvCCBDIn6vJ5n?usp=sharing)


Por parches nos referimos al stack o apilamiento de bandas de una imagen satelital. Actualmente estamos utilizando:
- BANDS = ["B02", "B03", "B04", "B05", "B06", "B07", "B8A", "B08", "B11", "B12"]

El conjunto total de parches están a disposición del que lo requiera (por tamaño no están disponibles en el link anterior).

La representación RGB de los parches junto a su mascara de nubes se pueden descargar de:
- [parches rbg/cloud-mask](https://drive.google.com/file/d/1VJnFvc9waDWPzm0i6UitKwlOSaQVwn_j/view?usp=sharing)

Dejamos algunos a modo de ejemplo:

| Imágenes | |
|--------|------|
| ![parches rbg/cloud-mask](cba/parches-rgb/S2A_MSIL1C_20200108T141701_N0208_R010_T20JLL_20200108T173844_cba.jpg) | ![parches rbg/cloud-mask](cba/parches-rgb/S2A_MSIL1C_20200227T141731_N0209_R010_T20JLL_20200227T175603_cba.jpg) |
| ![parches rbg/cloud-mask](cba/parches-rgb/S2A_MSIL1C_20200328T141731_N0209_R010_T20JLL_20200328T185640_cba.jpg) | ![parches rbg/cloud-mask](cba/parches-rgb/S2A_MSIL1C_20200417T141741_N0209_R010_T20JLL_20200417T173808_cba.jpg) |
| ![parches rbg/cloud-mask](cba/parches-rgb/S2A_MSIL1C_20200517T141741_N0209_R010_T20JLL_20200517T174050_cba.jpg) | ![parches rbg/cloud-mask](cba/parches-rgb/S2A_MSIL1C_20200616T141741_N0209_R010_T20JLL_20200616T174040_cba.jpg) |
| ![parches rbg/cloud-mask](cba/parches-rgb/S2A_MSIL1C_20200726T141741_N0209_R010_T20JLL_20200726T185652_cba.jpg) | ![parches rbg/cloud-mask](cba/parches-rgb/S2A_MSIL1C_20200825T141741_N0209_R010_T20JLL_20200825T192849_cba.jpg) |
| ![parches rbg/cloud-mask](cba/parches-rgb/S2A_MSIL1C_20200914T141741_N0209_R010_T20JLL_20200914T175310_cba.jpg) | ![parches rbg/cloud-mask](cba/parches-rgb/S2A_MSIL1C_20201024T141741_N0209_R010_T20JLL_20201024T174501_cba.jpg) |
| ![parches rbg/cloud-mask](cba/parches-rgb/S2A_MSIL1C_20201113T141741_N0209_R010_T20JLL_20201113T175045_cba.jpg) | ![parches rbg/cloud-mask](cba/parches-rgb/S2B_MSIL1C_20200123T141649_N0208_R010_T20JLL_20200123T173902_cba.jpg) |



## Notebooks

La metodología descripta se puede observar en las jupyter-notebooks:

- [ab-initio-mev-cba-0](../notebooks/ab-initio-mev-cba-0.ipynb): identificación de zona de interés y espacios verdes

- [ab-initio-mev-cba-1](../notebooks/ab-initio-mev-cba-1.ipynb): identificación de Tile (imagen satelital) y descarga.

- [ab-initio-mev-cba-2](../notebooks/ab-initio-mev-cba-2.ipynb): extracción de estadísticos de bandas y cálculos de indice (ejemplo en 1 imagen).

- [ab-initio-mev-cba-3](../notebooks/ab-initio-mev-cba-3.ipynb): procesado del conjunto total de imágenes y generación del [dataset](./estructura-datos.md)

- [ab-initio-mev-cba-4](../notebooks/ab-initio-mev-cba-4.ipynb): muestra conceptual de series temporales para un cierto conjunto de datos y espacio verde.

### Espacios NO verdes

El procesado de zonas consideradas NO verdes se pueden encontrar en:

- - [ab-initio-not-mev-cba](../notebooks/ab-initio-not-ev-cba.ipynb): procesado del conjunto total de imágenes y generación del [dataset](./estructura-datos.md)