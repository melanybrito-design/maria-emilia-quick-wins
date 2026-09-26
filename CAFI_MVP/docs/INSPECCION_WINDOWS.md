# Inspección de SIAC / CAFI en Windows

Objetivo: observar controles reales para construir el adaptador. Esta herramienta no hace clic, no envía teclas, no inicia sesión y no guarda trámites.

## Preparación

1. Completar primero la prueba de interfaz/Excel/simulador.
2. En la laptop donde corre SIAC, abrir sesión manualmente y dejar **Ingreso de Procesos** vacío. No abrir información de estudiantes para la inspección.
3. Abrir Administrador de tareas, pestaña **Detalles**, y anotar el PID del proceso que contiene la ventana de SIAC. Si es Java, podría ser un proceso Java; no suponer que su nombre será CAFI.
4. Abrir PowerShell en la carpeta CAFI_MVP e instalar la herramienta opcional (requiere internet):

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-windows.txt
```

## Ejecutar inventarios

Reemplazar `1234` por el PID real obtenido; no copiar ese número como si fuese el de SIAC.

```powershell
.\.venv\Scripts\python.exe main.py --inspect-ui --backend uia --pid 1234
.\.venv\Scripts\python.exe main.py --inspect-ui --backend win32 --pid 1234
```

Sin `--pid`, se listan PID, handle y clase de ventanas, sin sus títulos. No se elige automáticamente una ventana por el texto de las capturas. Los informes dirigidos al PID contienen nombres/textos de controles visibles y se guardan en `data/inspeccion/controles_uia.json` y `controles_win32.json`. Cada ejecución del mismo backend reemplaza su inventario; copia el anterior si necesitas comparar pantallas.

Antes de compartir esos JSON, revisarlos: pueden incluir contenido visible del formulario. No son el mismo archivo que el reporte de prueba anonimizado de la interfaz. Usar formulario vacío y retirar información sensible.

## Qué necesitamos registrar junto al inventario

- Versión de Windows, versión de Python y si SIAC corre localmente o por escritorio remoto/Citrix.
- Si el bot se ejecutará dentro de la misma sesión remota. Una ventana de escritorio remoto puede exponer solo una imagen, sin controles internos.
- Cuáles controles aparecen para código, nombre/destinatario, título, detalle, prioridad, Guardar, OK, impresión, Limpiar y Proceso.
- Si UIA o Win32 no muestran campos internos, registrar esa limitación. Oracle Forms/Java puede necesitar inspección adicional; no sustituirla con coordenadas inferidas.
- Regla exacta del código de facultad/estudiante, catálogo de prioridad, impresión, reinicio del formulario y consulta para conciliar una transacción.

La lista observada no equivale a selectores aprobados. Después de revisarla se implementará un registro supervisado con lectura de vuelta y confirmación inequívoca. Esta entrega no proporciona una opción para cargar trámites reales.

## Cómo se asocia el acceso local

El botón `Buscar ventanas` no busca una URL ni una cuenta: enumera ventanas visibles en la misma sesión de Windows, guarda temporalmente su handle en memoria y la asocia por PID. La aplicación de escritorio puede usar ese handle con el backend Win32/UIA para inspeccionar la ventana. La ruta del `.exe` es opcional y solo sirve para abrir CAFI si la asistente lo cerró; no reemplaza el inicio de sesión.

CAFI debe estar abierto, autenticado y en la misma sesión de Windows que `CAFI.exe`. Si CAFI se ejecuta elevado como administrador, el asistente puede necesitar el mismo nivel de permisos para verlo. No se debe compartir el handle, la ruta del programa ni los JSON como si fueran credenciales.
