# CAFI · Asistente de trámites UEES

Versión 0.4.0 · Ventana nativa y controlador RPA Windows.

Abre **INICIAR_CAFI.bat** o **CAFI.exe** en Windows. Ambos lanzan la misma ventana nativa de Qt; no abren HTML, navegador, servidor web ni Visual Studio Code. El paquete incluye Python 3.13 de 64 bits y las bibliotecas necesarias. Extrae toda la carpeta antes de usarla.

## Flujo de uso

1. Abre el programa CAFI en la laptop Windows.
2. Abre el asistente y selecciona la ventana de CAFI con «Buscar CAFI».
3. Ingresa usuario y contraseña, o marca «CAFI ya está abierto con la sesión iniciada».
4. Selecciona el Excel, comprueba hoja y longitud de códigos, y pulsa «Validar Excel».
5. Con el mapa de controles configurado, pulsa «Iniciar proceso completo». El valor inicial de espera entre acciones críticas es de 12 segundos y se puede ajustar entre 10 y 15 segundos durante la configuración.
6. Después de cada impresión, revisa los datos visibles y confirma el cuadro de resultados. Solo entonces se actualiza el Excel de resultados. Puedes detener el robot desde su ventana.

**La conexión requiere una configuración inicial en esa laptop.** El código implementa las acciones reales de Windows, pero no se han observado todavía los identificadores de los controles de CAFI. No se distribuye un mapa inventado. Por eso el botón de ejecución se habilita al cargar un mapa completo. Consulta [LEEME_WINDOWS.md](LEEME_WINDOWS.md).

## Qué hace el controlador

Inicia sesión si se solicita, navega por los controles configurados hasta Ingreso de procesos, comprueba que el formulario esté vacío, restaura el proceso 12 configurado, introduce código y verifica destinatario. Completa título, detalle y prioridad, lee de vuelta y pulsa Guardar una vez. Espera el mensaje exacto de éxito, persiste el guardado, pulsa OK y configura el diálogo de impresión. Genera el reporte y lee código de trámite, GPA y créditos desde los controles observados. La usuaria confirma esos resultados antes de exportarlos al Excel y limpiar el formulario para la siguiente fila.

La impresión predeterminada reproduce lo observado: **Destino Pantalla, una copia y opción PDF**. No equivale a enviar papel a una impresora física ni garantiza un PDF guardado en disco. Esas variantes requieren observar el diálogo correspondiente.

## Excel y resultados

Hoja predeterminada: `Hoja 1`. Longitud provisional: 10 dígitos (ajustable). Encabezados: `COD. ALUMNO`, `NOMBRE ESTUDIANTE`, `TITULO`, `DETALLE`, y opcionalmente `PRIORIDAD`, `CÓDIGO:`, `GPA:`, `CRED.APROB:`. Los alias anteriores siguen definidos en excel_manager.py. Solo se admite Media en esta versión. Las columnas de resultados de una entrada nueva deben estar vacías.

El código es texto con ceros iniciales; solo se reconstruyen ceros desde una máscara numérica explícita del Excel. Fórmulas, columnas desconocidas, datos incompletos y destinatarios inconsistentes se detienen. Título y detalle se preservan. Si el código de facultad resuelve a un destinatario genérico diferente del nombre en Excel, el robot detiene la fila; falta confirmar esa regla con la responsable.

`data/operacion/<lote>/origen.xlsx` conserva el original exacto. `resultados_cafi.xlsx` contiene resultados observados, estado y fase de impresión únicamente después de la confirmación humana. No modifica el Excel de origen ni escribe en Google Sheets. Las credenciales no se guardan. No se usa el portapapeles para escribirlas.

`PROCESADO` indica guardado confirmado; consulta `IMPRESION_CAFI` para saber si el ciclo terminó (`COMPLETO`). Un guardado confirmado con impresión/limpieza pendiente no se vuelve a enviar. Un guardado incierto requiere conciliación. No borres data ni cambies de carpeta para reintentar: allí se conserva el historial. Se detectan filas idénticas a intentos anteriores en este mismo historial, incluso en un Excel modificado; esto no garantiza idempotencia del servidor ni detecta todos los cambios de contenido.

## Pruebas y diagnóstico

- `DIAGNOSTICO_WINDOWS.bat`: comprueba dependencias sin leer CAFI y genera `data/diagnostico_instalacion.json`.
- `PRUEBAS_WINDOWS.bat`: prueba el núcleo con datos sintéticos y dobles de controles. No guarda ni imprime en CAFI.
- [docs/VALIDACION.md](docs/VALIDACION.md): evidencia y límites de la verificación.

La interfaz y el núcleo se probaron en macOS; el ejecutable se compiló para Windows x64. **La ejecución del paquete y del flujo real en Windows sigue pendiente.** No hay acceso remoto a la laptop desde esta entrega.

## Desarrollo

La app nativa está en native_app.py, el controlador en windows_rpa.py, la orquestación y salida real en real_workflow.py. El RPA anterior de Panacea se usó como referencia de arquitectura, sin reutilizar sus credenciales, rutas ni selectores. El simulador antiguo queda como herramienta de desarrollo separada y no forma parte de la interfaz operativa.

Fuentes técnicas: [pywinauto: controles y backends](https://pywinauto.readthedocs.io/en/latest/getting_started.html), [Qt for Python: instalación y Widgets](https://doc.qt.io/qtforpython-6/gettingstarted.html). Dependencias y licencias: THIRD_PARTY_NOTICES.md.
