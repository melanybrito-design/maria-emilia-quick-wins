# Abrir CAFI en Windows

1. Copia CAFI_MVP_Windows_v0.4.0.zip a la laptop que tiene CAFI y extrae toda la carpeta. No abras el BAT dentro del ZIP.
2. Abre INICIAR_CAFI.bat o CAFI.exe. No hace falta instalar Python ni usar un editor. Windows debe ser de 64 bits; el paquete está preparado para probarse en Windows 10/11.
3. Abre CAFI. En el asistente, pulsa Buscar CAFI y selecciona la ventana correcta.
4. La primera vez, configura los campos como se explica abajo. Después esta configuración queda guardada localmente.
5. Ingresa usuario/contraseña o marca que la sesión ya está abierta. Selecciona tu Excel y pulsa Validar Excel.
6. Pulsa Iniciar proceso completo. Mantén Windows desbloqueado. El RPA usa el mouse y el teclado y espera 12 segundos entre acciones críticas de SIAC; evita usarlos mientras opera. Puedes pulsar Detener en el asistente.
7. Después de cada impresión, valida el código de trámite, GPA y créditos que se muestran en CAFI. El Excel de salida se actualiza solo cuando confirmas esos resultados.
8. Abre Resultados para consultar el Excel de salida. «Crear acceso directo» añade el icono CAFI UEES al escritorio.

## Cómo obtiene acceso al CAFI local

El robot se ejecuta dentro de esa misma computadora, usando la sesión de Windows de la persona. Se asocia a la ventana del programa y maneja sus controles con pywinauto. No necesita publicar CAFI en internet ni enviar la contraseña a esta conversación. Debe poder interactuar con CAFI en la misma sesión y con permisos compatibles. No se configura acceso remoto en este paquete.

## Primera configuración, con apoyo técnico

Esta preparación se hace una vez y se repite si cambia la interfaz de CAFI. No necesitas escribir código para seleccionar un control; un técnico puede ajustar el selector si hay ambigüedad.

1. Abre Configurar CAFI. Prueba la tecnología UIA; si no ve los controles, prueba Win32. Cambiar de tecnología reinicia el mapa en edición para evitar mezclar identificadores.
2. Deja CAFI en la pantalla que quieres reconocer. Pulsa Leer controles de la pantalla abierta.
3. Elige una función, por ejemplo Formulario · Código del destinatario. Elige su control de la lista y pulsa Asignar a esta función. El selector proviene de esa computadora.
4. Repite con tipo de proceso, destinatario resuelto, título, detalle, prioridad y Guardar. Las listas desplegables usan el modo Lista desplegable. Configura el clic o doble clic observado para los nodos de navegación.
5. Registra los controles de acceso si quieres que el robot escriba las credenciales. Si usas una sesión ya iniciada, no son necesarios.
6. Durante un registro de prueba supervisado con datos autorizados, observa y asocia la confirmación de éxito/OK, las opciones de impresión, un indicador estático del reporte terminado, los campos de código/GPA/créditos y la limpieza. No uses como indicador de reporte listo una ventana que ya estuviera visible antes de imprimir.
7. Copia el texto exacto de confirmación en el campo correspondiente. Ajusta «Espera entre acciones de CAFI» entre 10 y 15 segundos según la respuesta observada del programa. El valor inicial viene del levantamiento, pero debe compararse con el mensaje real.
8. Guarda el mapa. Para valores que cambian (código, nombre, GPA, créditos), no incluyas su contenido como criterio del selector. Un control ambiguo detiene la operación; no se elige el primero a ciegas.
9. Prueba un Excel de una sola fila antes del lote. Confirma en CAFI que se creó exactamente un trámite, que aparece el reporte y que el Excel de resultados coincide. Después prueba dos filas y la detención.

La inspección genera un inventario estructural en data/inspeccion. Si no aparecen campos legibles en ninguno de los modos, necesitaremos adaptar la lectura a la tecnología de CAFI. Un video muestra el orden de pasos, pero no entrega los identificadores de controles. El reporte generado por otro proceso de Windows también requiere una adaptación: este controlador se limita al proceso CAFI seleccionado.

## Si algo falla

- Si no abre la ventana: ejecuta DIAGNOSTICO_WINDOWS.bat y comparte el archivo data/diagnostico_instalacion.json.
- Si no encuentra un campo: indica la etapa exacta y comparte el inventario estructural generado. No envíes contraseñas.
- Si se interrumpe después de Guardar: consulta CAFI antes de cualquier reintento. El robot marca el intento incierto o conserva el guardado confirmado.
- Si la impresión falla: el guardado no se repite. La fila requiere revisión de su reporte.
- Si Excel bloquea el archivo de salida: ciérralo y pulsa Resultados para volver a exportar desde la bitácora.
- Si solicitas cerrar mientras trabaja: el asistente pide detener y permanece abierto hasta que termine el trabajador. Luego puedes cerrarlo.

El ZIP contiene el programa preparado para probarlo. Todavía no acredita una ejecución exitosa en la laptop de CAFI.
