# Auditoría de calidad — PREPPER MAP 0.8

## Cambios aplicados
- Se añadió una capa de empaquetado Tauri 2 para Windows, Android e iOS.
- Se reemplazaron referencias CDN de Leaflet y Esri-Leaflet por recursos locales generados desde dependencias npm; el empaquetado ejecuta `npm run sync:vendor`.
- Se agregaron iconos, metadatos de instalación y manifest PWA.
- Se mejoró la adaptación a móviles: áreas seguras, controles táctiles y redimensionamiento de Leaflet al cambiar orientación.
- Se incorporó una política de privacidad visible dentro de la aplicación y una acción para borrar observaciones locales.
- Se agregaron pipelines de calidad, Windows y Android.
- Se mantuvo la advertencia de que el mapa base y los servicios GIS remotos necesitan internet; aún no hay paquete regional de teselas offline.

## Validaciones ejecutadas en el entorno de desarrollo
- 14 pruebas Python: aprobadas.
- Compilación de módulos Python: aprobada.
- Sintaxis JavaScript inline: aprobada con Node.
- Archivos JSON: validados.
- Workflows YAML: validados sintácticamente.
- Prueba estructural de configuración Tauri: aprobada.

## Pendientes antes de distribución
- Instalar dependencias npm y generar `frontend/vendor` en un entorno con conexión.
- Ejecutar compilación real en Windows y probar el instalador en Windows 10/11.
- Ejecutar compilación real en Android Studio, probar APK en dispositivos físicos y revisar permisos.
- Compilar y probar en iPhone/iPad con Xcode; firma, TestFlight/App Store y revisión Apple quedan pendientes.
- Probar geolocalización, enlaces externos, almacenamiento y recuperación de datos en Android/iOS.
- Ejecutar pruebas de interfaz automatizadas y pruebas de accesibilidad.
- Alojar una política de privacidad pública y completar datos de contacto institucionales antes de publicar.
- Implementar mapas base offline con paquetes PMTiles/MBTiles de licencia compatible.

## Estado honesto
Esta entrega contiene el código y la configuración de empaquetado. No contiene todavía instaladores `.exe`, `.apk`, `.aab` ni `.ipa` compilados. Este entorno no dispone de Rust/Cargo, SDK Android ni Xcode; por eso la compilación final debe ejecutarse en los runners o equipos adecuados.
