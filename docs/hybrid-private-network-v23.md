# PREPPER MAP PRO 2.3 — Red privada híbrida

## Decisión de arquitectura
La aplicación se diseña para un grupo pequeño y privado de amistades. Cada dispositivo mantiene sus propios datos y una bandeja de salida IndexedDB. Puede operar sin internet; cuando recupera conectividad, el usuario puede habilitar el envío automático de eventos a una API privada HTTPS. La sesión y el token permanecen en memoria y se pierden al cerrar/recargar la aplicación.

## Flujo
1. Registrar datos en el dispositivo; los eventos publicados con `prepper:event` quedan en la outbox local.
2. Sin conexión: la cola se conserva y la aplicación informa que está en modo local.
3. Con conexión: si el usuario configuró una sesión y activó expresamente el envío automático, la cola se envía en lotes.
4. La descarga de eventos remotos sigue siendo manual y genera un JSON para revisión. No se aplican automáticamente, evitando sobrescribir cambios locales o propagar datos no revisados.
5. Cerrar sesión elimina el token de memoria y desactiva el envío automático.

## Configuración de red privada
- API accesible por HTTPS; HTTP solo se permite en localhost durante pruebas.
- Crear un tenant privado para el grupo y credenciales individuales con rol limitado.
- No publicar tokens en repositorios, capturas, archivos compartidos ni chats.
- Para un grupo de confianza pequeño, comenzar con una instancia privada y backups cifrados.
- No abrir puertos de base de datos a internet. Usar firewall y proxy TLS.
- No incluir domicilios privados, claves, códigos de acceso ni inventarios sensibles en los eventos compartidos.

## Límites de esta versión
- El envío automático es opt-in; no se hace pull automático.
- El pull produce un archivo de revisión, no aplica eventos a los módulos.
- Los registros creados en módulos solo se sincronizan si esos módulos emiten eventos `prepper:event`; la integración completa de cada entidad sigue siendo trabajo pendiente.
- IndexedDB no garantiza cifrado local. Proteger el dispositivo con bloqueo y cifrado del sistema operativo.
- El modo offline de mapas solo cubre teselas que hayan sido descargadas legalmente y empaquetadas; no se descargan mapas automáticamente.
- Esta herramienta no sustituye canales oficiales, despacho ni protocolos de emergencia.
