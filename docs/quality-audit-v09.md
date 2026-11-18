# Auditoría de calidad — PREPPER MAP 0.9

## Mejoras implementadas
- Biblioteca offline personal basada en IndexedDB: importa capas GeoJSON, valida estructura y geometrías, conserva los datos en el dispositivo y las vuelve a cargar al iniciar la aplicación.
- Gestión de capas personales: activar/desactivar, eliminar individualmente, exportar una copia de respaldo y borrar la biblioteca completa con confirmación.
- Límite defensivo de 250.000 elementos por archivo para evitar importar accidentalmente archivos excesivos.
- Service worker revisado: red primero para navegación y datos, respaldo local si no hay conexión y caché de recursos estáticos/datos descargados. No cachea teselas OSM ni servicios GIS en vivo.
- Versionado actualizado a 0.9.0.

## Límites explícitos
- Esta biblioteca guarda GeoJSON, no imágenes de mapa base. Sin teselas/PMTiles/MBTiles regionales descargadas legalmente, el fondo cartográfico puede quedar vacío sin internet.
- Las capas personales solo viven en el almacenamiento de ese dispositivo/navegador. Exporta el respaldo para transferirlas; borrar datos de la aplicación puede eliminarlas.
- La importación no valida la exactitud, vigencia, procedencia ni seguridad del contenido geográfico.
- La evaluación de rutas sigue siendo una comparación preliminar con polígonos disponibles; no produce rutas seguras ni instrucciones de evacuación.

## Validación pendiente
- Pruebas manuales en Android/iOS y Windows WebView.
- Pruebas de persistencia tras reinicio, actualización y poco espacio de almacenamiento.
- Prueba real de modo avión con capas importadas y paquete regional de mapa base.
- Compilación firmada de instaladores y pruebas en dispositivos físicos.
