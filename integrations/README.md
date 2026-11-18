# Integraciones de rutas y senderismo

## Wikiloc
No hay API pública de desarrolladores. PREPPER MAP no extrae páginas, no rastrea cuentas ni copia tracks. Permite abrir búsquedas/rutas compartidas y cargar GPX/TCX exportados por el usuario cuando su cuenta y permisos lo permiten. Wikiloc indica opciones de descarga GPX/TCX/KML en su ficha de ruta, según sus condiciones.

## komoot
No hay API pública general. Puede compartirse un enlace/embebido y exportarse/importarse archivos GPS individuales (GPX/TCX/FIT según función). El usuario aporta el archivo; PREPPER MAP lo visualiza localmente.

## OpenStreetMap
La capa de senderos se obtiene como datos abiertos (Overpass) para el área metropolitana y se atribuye OpenStreetMap contributors. Los datos OSM están sujetos a ODbL. No usar la API de edición para descargas masivas ni sobrecargar servicios públicos. Para producción, usar extractos regionales o infraestructura propia.

## Mapy.com y AllTrails
Se incluyen como portales externos de referencia. No se afirma una integración API ni se automatiza extracción.

## Importación local
Formatos: GPX, KML y GeoJSON. El archivo se procesa en el navegador y no se sube a un servidor. Los tracks importados se pueden exportar como GeoJSON. El sistema conserva el origen y fecha de importación en la sesión local.

## Seguridad
Una ruta popular o muy recorrida no es automáticamente transitable ni segura. Las rutas deben contrastarse con amenaza, cierres, condiciones meteorológicas, permisos, accesos y verificación de campo. No usar este módulo para ordenar evacuaciones.
