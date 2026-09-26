# Prompt para completar el mapeo y validar el ciclo autónomo del RPA en SIAC/CAFI

## Instrucción de uso

Pega este documento completo en Codex desde la laptop Windows donde está instalado SIAC/CAFI. Trabaja exclusivamente sobre el proyecto local `CAFI_MVP` y sobre una copia de prueba del Excel. No abras ni uses una página HTML para ejecutar el RPA.

## Objetivo

Completar el mapa real de controles de SIAC/CAFI y dejar funcionando el ciclo completo mediante el RPA:

`Excel de entrada → formulario Ingreso de Procesos → Guardar → esperar confirmación → abrir/imprimir reporte → leer código, GPA y créditos → cerrar reporte → limpiar formulario → siguiente fila → actualizar resultados_cafi.xlsx`.

El flujo debe ejecutarse sin que una persona tenga que escribir manualmente los datos de cada trámite. No debe solicitar confirmación después de cada reporte ni después de cada estudiante. La única pausa humana permitida es una confirmación de acción inmediata antes de crear el primer registro real si Windows/Codex la exige por política. Después de esa autorización, el RPA debe continuar las filas, imprimir, leer resultados y actualizar el Excel automáticamente.

## Estado conocido que debes tomar como punto de partida

- El RPA ya detecta SIAC y puede abrir `Ingreso de Procesos` con UI Automation y Win32.
- La última ejecución reportó 68 pruebas locales aprobadas.
- El formulario se completa en este orden: Proceso 12, Código de alumno, Colegio vacío, Título, Detalle, Destinatario resuelto por SIAC y Prioridad Media/sin modificar.
- El último reporte indicó un mapa parcial de 7 de 18 controles y que todavía no había un ciclo autónomo completo validado. No asumas que faltan exactamente 15: inspecciona el inventario actual y calcula el número real de controles pendientes.
- No declares que el RPA está terminado solo porque una prueba local pasa. La evidencia debe provenir de la ventana real de SIAC.

## Archivos que debes leer antes de modificar código

1. `AGENTS.md`.
2. `README.md`.
3. `docs/VALIDACION.md`.
4. `docs/INSPECCION_WINDOWS.md`.
5. `windows_rpa.py`.
6. `real_workflow.py`.
7. `native_app.py` y `CAFI.pyw`.
8. El mapa/configuración existente en `data/`.
9. `PROMPT_PRUEBA_IMPRESION_TRES_FILAS.md` y cualquier prueba existente.
10. El Excel de prueba autorizado y su plantilla de columnas.

Conserva la nomenclatura SIAC/CAFI. No vuelvas a usar nombres CIAT en archivos, clases, documentación, mensajes o configuración.

## Reglas de seguridad y fidelidad

- Trabaja en una copia del Excel. No uses la agenda productiva ni un Google Sheet real durante este piloto.
- No guardes usuario, contraseña ni tokens en código, archivos, logs, argumentos de procesos, capturas o el Excel. Las credenciales solo pueden permanecer en memoria durante la ejecución.
- No copies credenciales al portapapeles.
- No inventes selectores, AutomationId, nombres de controles, coordenadas, códigos de trámite, GPA ni créditos. Todo identificador debe estar respaldado por inspección real.
- No uses mocks, simuladores, HTML, datos ficticios ni una función que finja que el trámite se guardó.
- No ejecutes acciones destructivas, borres trámites ni cambies datos productivos.
- El RPA debe detenerse si un control no es único, está oculto, cambia de pantalla, devuelve un valor inesperado o no existe evidencia de guardado.
- No repitas `Guardar` automáticamente después de una respuesta incierta. Marca la fila como `requiere_revision` y detén el lote.
- Ejecuta SIAC y el RPA con el mismo nivel de permisos y en la misma sesión de Windows. Si SIAC está como administrador, el RPA también; si no, ninguno.
- Mantén una sola instancia del trabajador. Evita concurrencia, doble clic y duplicación de trámites.
- Conserva ceros iniciales de códigos y trata títulos, detalles y campos de Excel como texto.
- Usa esperas explícitas. El programa es lento: conserva al menos 12 segundos entre acciones críticas y espera por estado cuando sea posible. No avances solo porque transcurrió un tiempo fijo.

## Fase 1: inventario y diagnóstico real

1. Ejecuta las pruebas locales existentes y guarda el resultado exacto.
2. Inicia SIAC manualmente, inicia sesión con la cuenta autorizada y deja abierta la pantalla `Procesos > Trámites estudiante > Crear nuevo proceso`.
3. Ejecuta el diagnóstico UIA/Win32 en modo lectura, sin escribir ni guardar un trámite.
4. Registra para cada control: ventana, texto visible, tipo de control, AutomationId, ClassName, control_type, proceso/PID, estado habilitado, rectángulo y método de acceso preferido.
5. Prueba primero UI Automation; usa Win32 como respaldo cuando UIA no exponga el control. No sustituyas un control por coordenadas sin dejar la razón documentada.
6. Identifica el identificador de la ventana principal, la ventana del formulario, las ventanas modales y el PID de SIAC.
7. Guarda el mapa real en la configuración prevista por el proyecto, sin credenciales. Incluye versión, fecha, resolución/escala de Windows y evidencia de cada control.
8. Actualiza `docs/INSPECCION_WINDOWS.md` y `docs/VALIDACION.md` con los valores observados y una tabla de controles encontrados, no encontrados y pendientes.

## Contratos de control que debes completar

Verifica y registra cada contrato siguiente. Si el proyecto ya agrupa algunos, conserva esa agrupación, pero cubre todos los comportamientos.

### Formulario de ingreso

1. Ventana y formulario `Ingreso de Procesos`.
2. Selector del proceso 12.
3. Campo `Código de alumno`.
4. Campo `Colegio`, que debe quedar vacío cuando así lo indique el Excel.
5. Campo `Título`.
6. Campo `Detalle`.
7. Campo o selector de `Destinatario`, incluyendo la forma correcta de resolverlo en SIAC.
8. Campo `Prioridad`, conservando el valor permitido por el formulario.

### Registro y resultado de guardado

9. Botón `Guardar`.
10. Indicador real de procesamiento, espera o bloqueo después de guardar.
11. Mensaje de éxito o número de trámite creado.
12. Botón `Aceptar/OK` del mensaje de éxito, si existe.

### Reporte e impresión

13. Acción que abre el reporte o el cuadro de impresión.
14. Ventana/documento del reporte listo.
15. Control que muestra el código de trámite generado.
16. Control que muestra GPA.
17. Control que muestra créditos.
18. Botón `Imprimir`, destino de impresión/PDF y confirmación de impresión completada.

### Cierre y preparación de la siguiente fila

19. Botón `Cerrar` del reporte o del cuadro de impresión.
20. Limpieza o regreso al formulario vacío.
21. Evidencia verificable de que el formulario está vacío y listo para la siguiente fila.

El último estado decía 7/18 porque algunos elementos pueden estar agrupados. No fuerces el número 18: al finalizar informa cuántos controles/contratos existen realmente, cuántos se mapearon y cuál queda pendiente. No cierres la tarea mientras queden contratos necesarios sin inspeccionar.

## Fase 2: diseño del flujo autónomo

Implementa o corrige `real_workflow.py` y `windows_rpa.py` para que el flujo tenga estas etapas explícitas:

1. Validar el archivo de entrada, columnas obligatorias y filas autorizadas.
2. Abrir/enfocar SIAC y comprobar que la pantalla actual es `Ingreso de Procesos`.
3. Leer una fila sin alterar el Excel original.
4. Limpiar el formulario y comprobar que está vacío.
5. Completar los campos con los datos de la fila, respetando orden y ceros iniciales.
6. Tomar una instantánea de intención de guardado: código, título, detalle, destinatario y fila de origen.
7. Verificar que la instantánea coincide con la fila antes de pulsar `Guardar`.
8. Pulsar `Guardar` una sola vez. Si Windows solicita confirmación de acción para crear el registro real, solicitarla solo en ese instante. No pedir confirmación por cada reporte ni por cada estudiante.
9. Esperar el indicador real de éxito, capturar el número de trámite y confirmar que pertenece a la fila actual.
10. Aceptar el mensaje de éxito solo si el resultado fue positivo.
11. Abrir el reporte o el cuadro de impresión.
12. Esperar a que el reporte esté listo. El tiempo puede ser mayor a 12 segundos; usa espera por estado y un tiempo máximo configurable.
13. Leer código de trámite, GPA y créditos desde controles reales del reporte. Si un dato no está disponible, no inventarlo: registrar error y detener la fila.
14. Ejecutar la impresión configurada para el piloto. El flujo no debe depender de que una persona confirme cada impresión.
15. Esperar evidencia de impresión terminada o del destino seleccionado.
16. Cerrar el reporte y comprobar que se regresó al formulario.
17. Limpiar el formulario y comprobar que no quedan valores de la fila anterior.
18. Actualizar la fila correspondiente de `resultados_cafi.xlsx` con código, GPA, créditos, estado, fecha/hora y mensajes de error si los hubiera.
19. Continuar con la siguiente fila únicamente cuando la anterior tenga estado verificable.

## Política de errores y reanudación

- Si falla la identificación de un control, toma un diagnóstico y detén el proceso antes de guardar.
- Si el guardado es incierto, no reintentes. Marca `requiere_revision` y deja evidencia.
- Si el reporte no aparece, no continúes a la siguiente fila.
- Si falta código, GPA o créditos, no escribas valores por defecto.
- Si el cierre no devuelve el formulario vacío, detén el lote.
- Registra errores en un log sin credenciales ni datos innecesarios.
- Permite reanudar desde la primera fila no completada sin volver a registrar filas verificadas.
- Usa estados explícitos, por ejemplo: `pendiente`, `formulario_completado`, `guardado_verificado`, `reporte_leido`, `impreso`, `excel_actualizado`, `requiere_revision`.

## Fase 3: medición de tiempos

Usa un reloj monotónico y registra, sin credenciales:

- inicio del lote;
- inicio y fin de cada fila;
- inicio y fin de completar el formulario;
- instante de `Guardar`;
- aparición de éxito y código;
- apertura y disponibilidad del reporte;
- lectura de código, GPA y créditos;
- fin de impresión;
- cierre y limpieza del formulario;
- actualización del Excel;
- fin del lote.

Calcula duración de la primera fila, duración de cada fila posterior, promedio de las filas válidas y duración total. Reporta por separado esperas programadas, espera de SIAC, impresión y escritura del Excel. No presentes las estimaciones actuales como tiempos reales hasta observarlas en SIAC.

## Fase 4: pruebas obligatorias en la laptop Windows

### Prueba 0: controles sin escritura

- Con SIAC abierto, ejecuta el inventario en modo lectura.
- No escribas campos y no pulses `Guardar`.
- Confirma que el mapa identifica todos los controles necesarios para el ciclo.

### Prueba 1: una fila autorizada

- Usa la primera fila del Excel de prueba, con datos autorizados.
- Ejecuta la fila exclusivamente mediante las funciones del RPA. No escribas manualmente para suplir una función faltante.
- La única confirmación posible es la de acción inmediata antes de crear el registro real, si Windows la solicita.
- Verifica guardado, código de trámite, GPA, créditos, impresión, cierre, formulario vacío y actualización de `resultados_cafi.xlsx`.
- Guarda tiempos observados y evidencia técnica.

### Prueba 2: tres filas consecutivas

- Ejecútala solo después de que la prueba de una fila haya sido exitosa.
- Usa tres filas autorizadas del Excel de prueba.
- No confirmes cada reporte y no intervengas para copiar datos.
- Verifica que el RPA limpia el formulario entre filas, no duplica registros, lee tres resultados y actualiza las tres filas del mismo Excel de resultados.
- Si una fila falla, detén el lote en esa fila y conserva las dos anteriores como verificadas.

## Pruebas de calidad del código

1. Ejecuta `python -m pytest tests -q`.
2. Ejecuta las pruebas de diagnóstico UIA/Win32 disponibles.
3. Revisa que el botón de ciclo completo solo se habilite cuando el mapa y la configuración reales estén completos.
4. Verifica que los mensajes de la interfaz indiquen claramente fila, etapa, espera y error.
5. Comprueba que no se impriman credenciales en consola ni en archivos.
6. Usa `tools/make_release.py` para preparar la distribución si el proyecto ya lo contempla.
7. No empaquetes una versión como lista si no existe evidencia real de la prueba de una fila y de las tres filas.

## Criterios de terminado

Considera el trabajo terminado únicamente cuando:

- el inventario real de SIAC esté documentado;
- todos los controles necesarios estén identificados por UIA o Win32 con evidencia;
- el RPA complete una fila real desde Excel hasta impresión, lectura, cierre y actualización;
- el RPA complete tres filas consecutivas sin confirmación por reporte;
- el formulario quede vacío entre filas y no haya duplicados;
- `resultados_cafi.xlsx` contenga código de trámite, GPA y créditos correctos para cada fila;
- los tiempos reales estén medidos y separados de las estimaciones;
- las pruebas locales pasen;
- `docs/VALIDACION.md` indique exactamente qué se probó, en qué Windows, con qué archivo y cuál fue el resultado;
- cualquier limitación restante esté escrita como pendiente concreto, no escondida como éxito.

## Informe final que debes devolver

Al terminar, responde en español con:

1. cantidad real de controles esperados, mapeados y pendientes;
2. archivos modificados;
3. resultado de las pruebas locales;
4. resultado de la prueba de una fila;
5. resultado de las tres filas;
6. tiempos observados por fila y lote;
7. filas actualizadas en `resultados_cafi.xlsx`;
8. errores encontrados y solución aplicada;
9. pendientes concretos, si todavía existe alguno;
10. confirmación explícita de si el ciclo completo autónomo quedó validado o no.

No afirmes que el ciclo funciona “a la perfección” sin esas evidencias. Si una política de Windows exige una confirmación puntual para crear el primer trámite real, indícalo como la única intervención externa y continúa automáticamente después de recibirla.
