# PREPPER MAP 0.8 — aplicación multiplataforma

## Qué queda preparado
- Proyecto Tauri 2 en `src-tauri/`.
- Aplicación Windows empaquetable como instalador NSIS `.exe`.
- Inicialización de Android y generación de APK/AAB.
- Inicialización de iOS y compilación IPA mediante Xcode.
- Librerías Leaflet y Esri-Leaflet incorporadas desde dependencias npm y copiadas a `frontend/vendor`, evitando CDN para el motor cartográfico.
- Icono de aplicación, metadatos y caché local de recursos.
- Workflows de GitHub Actions para instalador Windows y paquetes Android.

## Dependencias
- Node.js 22 o superior.
- Rust estable.
- Para Windows: Microsoft C++ Build Tools y WebView2 Runtime.
- Para Android: Android Studio, Android SDK/NDK y Java instalado por Android Studio o compatible.
- Para iOS: macOS, Xcode y herramientas de línea de comandos. Para distribución pública se requiere firma, equipo Apple y los perfiles/certificados correspondientes.

## Preparación local
```bash
npm install
npm run sync:vendor
npm run check
npm run doctor
```

## Windows — instalador EXE
En Windows:
```powershell
npm run build:windows
```
Resultado esperado:
`src-tauri/target/release/bundle/nsis/*.exe`

## Android — APK de pruebas y AAB de tienda
Con Android Studio y SDK/NDK configurados:
```bash
npm run android:init
npm run build:android
npm run build:android:aab
```
Resultados esperados en `src-tauri/gen/android/app/build/outputs/`.

El APK sirve para pruebas e instalación controlada. El AAB es el formato recomendado para Google Play. La firma de publicación debe gestionarse con una clave propia y guardarse como secreto seguro; nunca incluirla en el repositorio.

## iOS — iPhone/iPad
En un Mac con Xcode:
```bash
npm run ios:init
npm run ios:dev
```
Para distribución en App Store se requiere cuenta Apple Developer, identificador de paquete registrado, certificados y perfiles de aprovisionamiento. La compilación IPA se realiza con:
```bash
npm run tauri ios build -- --export-method app-store-connect
```
La firma y el envío final deben completarse en el entorno Apple autorizado.

## Automatización de compilación
- `.github/workflows/build-windows.yml`: produce el instalador Windows en GitHub Actions.
- `.github/workflows/build-android.yml`: produce APK y AAB.
- `.github/workflows/quality.yml`: validación de JavaScript, JSON y pruebas Python.
Los archivos se descargan como artefactos de cada ejecución. No se publican automáticamente en las tiendas.

## Calidad y limitaciones actuales
1. La aplicación aún consulta mapas base y capas oficiales remotas; sin internet, solo estarán disponibles las capas descargadas y cacheadas.
2. El mapa base OSM no se descarga ni se almacena masivamente. Para modo sin conexión real, PREPPER MAP necesita paquetes MBTiles/PMTiles con licencia y atribución adecuadas.
3. Los servicios remotos pueden bloquear solicitudes desde ciertas redes o dispositivos. Debe probarse CORS, certificados y disponibilidad en Android/iOS.
4. La geolocalización debe probarse en dispositivo físico y configurarse con permisos nativos antes de distribuir públicamente. En esta versión no hay seguimiento en segundo plano ni permisos de ubicación solicitados al iniciar.
5. No se incluyen credenciales de firma, certificados, perfiles Apple ni claves Android.
6. No se afirma que un instalador o APK/IPA haya sido compilado hasta que un runner compatible produzca el archivo y pase pruebas reales.

## Privacidad y tiendas
Antes de publicar, preparar una política de privacidad que describa ubicación, registros de campo, almacenamiento local, transferencias, conservación y eliminación. La ubicación debe ser opcional y solicitarse solo cuando el usuario active la función. Apple exige una política de privacidad accesible y consentimiento para recopilar datos personales.


## Actualización 0.9.0
La versión 0.9 añade una biblioteca GeoJSON persistente mediante IndexedDB. Las capas importadas permanecen en el dispositivo y se pueden exportar como respaldo. Esta función no descarga ni almacena teselas del mapa base.
