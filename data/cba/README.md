# Datos Córdoba

- **cordoba.geojson**: contiene el bounding box para recortar la imagen satelital correspondiente
- **espacios-verdes-cba.gpkg**: contiene el conjunto de espacios verdes identificados en [atlas-espacios-verdes](https://github.com/bitsandbricks/atlas_espacios_verdes) y que están dentro de _cordoba.geojson_.
- **productos-descargados-cba.csv**: conjunto de imágenes descargadas, incluyendo product-id y nubosidad.
- **espacios-verdes-dataset-sample.csv**: muestra del conjunto de datos
- **cropped-files.{json,csv}**: conjunto de imágenes recortadas a la zona de interés.
- **clouds-on-raster-shape.csv**: contiene el porcentaje de nubes calculadas sobre el aoi de córdoba (no la imagen satelital completa) para cada imagen procesada (_cropped-files.{json,csv}_).