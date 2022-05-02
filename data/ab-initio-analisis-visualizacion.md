# Ab-Initio: Análisis y Visualización

Trabajar con imágenes satelitales implica incorporar conceptos tales como rasters, resolución, bandas, proyecciones,etc. Para su visualización o representación existen diferentes formas que pueden brindar una mejor interpretación de las mismas (cuando queremos resaltar algo en particular por ejemplo). Adicionalmente al trabajo con rasters le sumamos ciertas representaciones geométricas, lineas, puntos polígonos (también asociados a cierta clase de referencia geométrica) que nos permiten marcar sobre un raster ciertas zonas de interés por ejemplo

![raster-vector-2](./media/Raster_vector_tikz.png)

_[fuente](http://tysmagazine.com/los-sig-raster-herramienta-de-analisis-medioambiental-y-territorial/)_


## Raster

En forma simplificada un raster es una grilla de puntos (pensemos en una matriz) cada uno de los cuales tiene alguna clase de identificación geográfica, que nos permite ubicarlos en el espacio. El valor del punto se corresponde con lo medido por el instrumento en cuestión. Respecto a ubicarlos en el "espacio" estamos implicando alguna clase de representacion geografica de la magnitud que medimos.

![coordenadas-raster](./media/raster-coordinate.gif)

[fuente](https://desktop.arcgis.com/es/arcmap/10.3/manage-data/geodatabases/raster-basics.htm)

Por ejemplo en la imágen anterior, se resalta una de las diferencias usuales entre la representacion "imagen" y la representacion "raster" (imagen + coordenadas). 

Cada una de esas grillas de puntos se corresponde a una "banda" (si hablamos de imágenes satelitales). Se hace referencia a _banda_ porque esta asociada a un rango (espectral) en el cual el elemento sensor es capaz de "ver" o "capturar" datos.

Notemos que al decir grilla de puntos estamos implicando una representación discreta de lo que estamos queriendo medir, es decir tenemos un cierto nivel de resolución de la zona de interés. En los satelites pueden ir desde los centimetros a los cientos de metros. 

## Vectores

Por vectores nos referimos a un formato de almacenamiento digital donde se guarda la localización de los elementos geográficos y los atributos asociados a ellos. En este sentido no tienen la limitacion (si la podemos considerar de esa forma) de granularidad o resolución. Es decir no tenemos una resolución mínima. 
En un archivo vectorial, los elementos geográficos se representan a partir de tres estructuras básicas: puntos, líneas y polígono, mientras que en los archivos ráster se caracterizan por la existencia de una red formada por celdas o cuadrículas, más comúnmente conocidas como píxel, en la que cada cuadrícula o píxel presenta una cualidad o propiedad espacial (color, altitud, etc) [[fuente]](https://geoinnova.org/blog-territorio/modelo-vectorial-y-modelo-raster/).
 
 ![raster-vector](../data/media/1-raster-vs-vectorial.png )

_[fuente](https://mygisnotebook.blog/2019/03/03/raster-vs-vectorial/)_



## Como se complementan?

Ambos formatos o tipos de almacenamiento son complementarios. Particularmente la informacion que "captura" un satelite es en formato "raster". Para delimitar zonas (para algun analisis posterior por ejemplo) en cambio es mas facil definir un poligono (en un archivo vectorial) y posteriormente efectuar el match entre el vector y la región que abarcaria en el raster.

En la siguiente imagen se ilustra este concepto, donde dependiendo del nivel de granularidad del raster vamos a tener mas o menos "error" en el match y consecuentemente en la propiedad que busquemos calcular.
 
  ![vector-to-raster](../data/media/vector-to-raster.png)

_[fuente](https://ecoscript.org/vectorvsraster/)_


## Sentinel 2 (Plataforma Satelital)

The Copernicus Sentinel-2 mission comprises a constellation of two polar-orbiting satellites placed in the same sun-synchronous orbit, phased at 180° to each other. It aims at monitoring variability in land surface conditions, and its wide swath width (290 km) and high revisit time (10 days at the equator with one satellite, and 5 days with 2 satellites under cloud-free conditions which results in 2-3 days at mid-latitudes) will support monitoring of Earth's surface changes.

For mission planning and updated coverage status information, see the Revisit and Coverage page.

This Sentinel-2 Mission Guide provides a high-level description of the mission objectives, satellite description and ground segment. It also addresses the related heritage missions, thematic areas and Copernicus services, orbit characteristics and coverage, instrument payload, and data products.[REF](https://sentinel.esa.int/web/sentinel/user-guides/sentinel-2-msi/)

### Sentinel2 Bands

| Band | Central Wavelenght [nm] | Resolution [m] |
|---|---|---|
|1  - Coastal aerosol|  443  |  60 |
|2  - Blue|  490  |  10 |
|3  - Green|  560  |  10 |
|4  - Red|  665  |  10 |
|5  - Vegetation Red Edge|  705  |  20 |
|6  - Vegetation Red Edge|  740  |  20 |
|7  - Vegetation Red Edge|  783  |  20 |
|8  - NIR|  842  |  10 |
|8a - Vegetation Red Edge|  865  |  20 |
|9  - Water vapour|  945  |  60 |
|10 - SWIR Cirrus|  1380 |  60 |
|11 - SWIR|  1610 |  20 |
|12 - SWIR |  2190 |  20 |

### Revisit and Coverage

The Sentinel-2 mission will provide systematic coverage over the following areas:

- all continental land surfaces (including inland waters) between latitudes 56° South and 82.8° North
- all coastal waters up to 20 km from the shore
- all islands greater than 100 km2
- all EU islands
- the Mediterranean Sea
- all closed seas (e.g. Caspian Sea).

In addition, the Sentinel-2 observation scenario includes observations following member states or Copernicus Services requests (e.g. Antarctica, Baffin Bay). 

It is expected up to one revisit every five days.

Sentinel 2 coverage is managed by tiles.



#### Tiles en Córdoba

Por ejemplo para Córdoba el conjunto de tiles de Sentinel2 que la cubren:

![png](./media/cba-tiles-roi.jpg)

- En azul los limites de Córdoba
- En rojo la ciudad de Córdoba (y zona que vamos a monitorear)
- En negro las cuadriculas junto a su identificacion o codigo (20JLL por ejemplo)

El solapado de los tiles suele ser de unos ~10km.

### Ejemplos de Representación

A continuación mostramos algunos ejemplos de representación de un raster

#### RGB

Correspondiente a la combinación de bandas (4,3,2)
![png](./media/raster-rgb-cba.jpg)

#### False Color

Correspondiente a la combinación de bandas (8,4,3)

![png](./media/raster-false843-cba.jpg)

Correspondiente a la combinación de bandas (12,8,4)

![png](./media/raster-false1284-cba.jpg)

Notar como las combinaciones parecen resaltar la vegetación, la ciudad y suelo limpio dependiendo de las bandas utilizadas.

#### NDVI

Indice Diferencial de Vegetación Normalizado (con un threshold arbitrario de 0.45).

![png](./media/raster-ndvi-cba.jpg)

Notar como este indice resalta las _zonas verdes_ con existencia de vegetación.