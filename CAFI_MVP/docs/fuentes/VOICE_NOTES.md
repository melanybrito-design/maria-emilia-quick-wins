# Voice notes de la conversación con María Emilia

## Fuente y alcance

- Fuente: transcripción aportada por Melany de una conversación con María Emilia; las marcas de tiempo corresponden al audio.
- La transcripción contiene lenguaje oral y algunos pasajes imprecisos. Este documento conserva los acuerdos y hallazgos útiles, pero no convierte explicaciones de la conversación en autorización para cargar datos reales ni en selectores técnicos verificados.
- Los datos de estudiantes y trámites reales siguen sujetos a autorización institucional. Para pruebas del software se deben usar datos sintéticos; las pruebas reales requieren un piloto autorizado.

## Hallazgos operativos útiles

- El dolor principal confirmado es la transcripción manual, trámite por trámite, desde la agenda al sistema CAFI.
- La agenda se arma actualmente en Word a partir de la revisión manual de correos por las asistentes administrativas. Revisar correos y determinar el contenido de cada solicitud queda fuera del primer alcance automatizable.
- Para cada registro, la información que la conversación identifica como necesaria es: nombre del estudiante, código del estudiante o de facultad, título/solicitud y detalle.
- La propuesta de origen más conveniente es que las asistentes registren esos datos directamente en una tabla estructurada de Excel/Sheets; desde esa tabla se alimentaría CAFI y, en una etapa posterior, podría generarse el Word de agenda. Esta es una propuesta de alcance futuro, no una función aprobada aún para el MVP.
- El sistema CAFI usa **Proceso 12** para **TRÁMITES ESTUDIANTE**. Tras limpiar el formulario, se borra también el proceso; para el siguiente registro se debe volver a escribir `12` y pulsar Enter antes de ingresar el código.
- El flujo explicado para un código es: pegar/escribir el código, reconocer que puede aparecer el mensaje `Undefined Function` al pegar, aceptar el mensaje con **OK**, pulsar Enter y esperar hasta que aparezca el nombre del estudiante o la descripción de facultad. Solo después se continúa con el título.
- María Emilia explicó que el mensaje `Undefined Function` observado al pegar no es, en ese caso, una invalidación del trámite. Es una condición de navegación que debe quedar registrada y ensayarse en el entorno real; no debe suprimirse ni reintentarse ciegamente.
- Para trámites de estudiantes, CAFI debe resolver el código en el nombre del estudiante. Para trámites de facultad, se utiliza un código especial y CAFI muestra la facultad como destinataria.
- El campo **Colegio** no se llena en el flujo descrito.
- Se copia el título y el detalle al formulario; la prioridad no fue discutida de forma concluyente en la conversación. El valor Media sigue siendo solo un valor observado en el video.
- Tras Guardar, el criterio de éxito visible es el mensaje `La transacción se realizó exitosamente`.
- Luego del éxito, el flujo actual responde **Sí** a la pregunta de imprimir el trámite. Cada trámite se imprime individualmente; no se confirmó una impresión masiva posterior.
- La impresora puede tardar en abrirse o responder. María Emilia considera viable reservar una computadora para el proceso, conectada a la red, mientras el personal realiza otras tareas. Esto es una condición operativa propuesta, no una solución técnica ya validada.
- Después de imprimir y cerrar, el formulario conserva datos del trámite anterior. El operador usa **Borrar / Limpiar forma / Limpiar formulario**, restablece Proceso 12 y continúa con el siguiente registro.
- Después de la impresión aparece un código de trámite de seis dígitos. Actualmente se agrega manualmente entre paréntesis en la agenda.
- María Emilia también indicó que, después de imprimir, se visualizan GPA y créditos aprobados al final del detalle o del trámite. Esos tres valores —código de trámite, GPA y créditos aprobados— son candidatos para registrarse de vuelta en la tabla y, después, incorporarse en la agenda Word.

## Títulos y estructura de entrada mencionados

- Se mencionan como ejemplos de título: **Incompleto**, **Reconocimiento con créditos**, **Homologación** y **Examen supletorio**.
- La conversación no entrega un catálogo completo ni confirma que todos esos títulos sean valores fijos. Conviene que María Emilia proporcione la lista autorizada o confirme que el título debe copiarse libremente desde la solicitud.
- El nombre del estudiante es necesario para la agenda, aunque no se usa como campo de carga en CAFI según la explicación.
- La tabla futura debería separar, como mínimo: `NOMBRE_ESTUDIANTE`, `COD_ALUMNO_O_FACULTAD`, `TITULO`, `DETALLE`, `COD_TRAMITE`, `GPA` y `CREDITOS_APROBADOS`. Los tres últimos se completarían solo tras el flujo que los muestre de forma verificable.

## Dudas, contradicciones y validaciones pendientes

- **Código de facultad:** en el video/Excel de prueba se observa `0000000017`; en la conversación se pronuncia `00017`. Debe confirmarse el valor exacto, la longitud requerida y si hay un código especial por cada facultad. No se deben rellenar ni truncar ceros por inferencia.
- **Códigos de estudiante:** se explica una estructura de año + código de facultad + consecutivo, con ejemplo oral `2026170001`. Falta confirmar si todos los códigos tienen la misma longitud, cómo se valida y si existen excepciones.
- **Mensaje Undefined Function:** se debe comprobar en el equipo real qué evento lo genera, si siempre se resuelve con OK y Enter, y si puede coexistir con otros errores. El RPA no debe asumir que todos los diálogos son inocuos.
- **Impresión:** existe una conversación sobre elegir No para continuar ingresando y luego imprimir, pero la práctica descrita termina siendo imprimir cada trámite. María Emilia debe decidir el flujo objetivo: imprimir uno por uno, diferir impresión o confirmar si CAFI permite impresión segura por lote.
- **Código de trámite, GPA y créditos:** falta definir en qué pantalla exacta se leen, si siempre aparecen, cómo se asocian inequívocamente a la fila original y qué debe hacerse si están vacíos.
- **Word de agenda:** se propone generarlo desde la tabla después de CAFI, pero falta el formato definitivo, la plantilla autorizada, los campos obligatorios y la regla para insertar el código de trámite, GPA y créditos aprobados.
- **Volumen:** se mencionan aproximadamente “10 hojas de trámites” en un caso, pero no está claro si son 10 páginas de Word, 10 registros o 10 lotes. Hace falta medir registros por lote, frecuencia y tiempos reales.
- **Equipo dedicado y conectividad:** hay una computadora potencialmente disponible y se menciona Wi-Fi. Aún debe verificarse el Windows, modalidad local/remota, impresora predeterminada, permisos y estabilidad antes de automatizar.
- **Datos sintéticos:** la conversación es ambigua sobre su uso. La regla recomendada se mantiene: sintéticos para validar el software; datos reales solo en un piloto autorizado y supervisado.

## Decisiones recomendadas antes de implementar

- Confirmar con María Emilia el flujo de impresión objetivo y la lectura posterior del código de trámite, GPA y créditos aprobados.
- Obtener una copia anonimizada de la plantilla Word de agenda y acordar una tabla de entrada con encabezados estables.
- Definir la regla de códigos de estudiante y facultad, incluyendo la discrepancia de ceros del código especial.
- Inspeccionar en la computadora real el comportamiento de los diálogos, de Limpiar formulario, de Proceso 12 y de la impresora.
- Mantener el primer MVP acotado a tabla validada → CAFI → resultado trazable. La extracción de correos y la generación de Word deben evaluarse como fases posteriores, después de validar la carga segura.

## Decisiones posteriores confirmadas por Melany — 11 de septiembre de 2026

- El origen operativo será el Google Sheet que prepara la asistente administrativa. Código, título y detalle son variables por fila; no hay que solicitar un catálogo fijo ni una nueva definición del Excel.
- El Word de agenda se descarta del alcance. El proceso inicia y termina en el Google Sheet.
- Después de guardar se realiza la impresión. Al final se deben actualizar en la misma fila el código de trámite, GPA y créditos aprobados.
- Si CAFI presenta un código/nombre o destinatario inesperado, el proceso se detiene y se solicita revisión manual.
- La usuaria reporta 12 horas de duración operativa y ocho ejecuciones por semestre. El piloto futuro corresponde a la asistente del área administrativa de la Facultad de Comunicación, previa autorización.
