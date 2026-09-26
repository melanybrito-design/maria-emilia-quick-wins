# Plan de implementación del MVP CAFI

## Objetivo

Construir un RPA atendido y seguro que tome una tabla previamente validada, cargue un trámite por vez en CAFI y deje un resultado trazable por cada fila. La usuaria inicia sesión manualmente; el MVP no revisa correos, no decide solicitudes y no genera todavía la agenda Word.

## Qué significa definir la tabla de entrada

Antes de programar, se debe acordar un formato único de Excel o Google Sheets para que el RPA sepa qué leer y qué no modificar. La propuesta inicial es:

| Columna | Uso | Estado |
|---|---|---|
| `NOMBRE_ESTUDIANTE` | Revisión humana y futura agenda; no se carga en CAFI | Propuesto |
| `COD_ALUMNO_O_FACULTAD` | Se escribe en CAFI como texto, preservando ceros | Obligatorio; regla exacta pendiente |
| `TITULO` | Se copia al campo Título de CAFI | Obligatorio |
| `DETALLE` | Se copia íntegro al campo Detalle de CAFI | Obligatorio |
| `PRIORIDAD` | Solo si se confirma su catálogo y regla por defecto | Pendiente |
| `COD_TRAMITE` | Resultado posterior al registro e impresión | Pendiente de ubicación y lectura verificadas |
| `GPA` | Resultado posterior, si CAFI lo muestra de forma estable | Pendiente |
| `CREDITOS_APROBADOS` | Resultado posterior, si CAFI lo muestra de forma estable | Pendiente |
| `ESTADO` | Resultado del lote: PENDIENTE, VALIDADO, EN_PROCESO, PROCESADO, ERROR o REQUIERE_REVISION | Salida del RPA |
| `MENSAJE_LOG` | Resumen mínimo sin datos académicos sensibles | Salida del RPA |

La plantilla actual ya contiene estas siete columnas, pero no un catálogo completo de títulos. La tabla será una copia operativa y de desarrollo con datos sintéticos. El Excel original no se sobreescribe; no se utilizarán datos reales hasta que exista autorización formal de piloto.

## Etapa 0: cerrar decisiones operativas

- Confirmar con María Emilia las preguntas del informe actualizado.
- Acordar la tabla de entrada y preparar un ejemplo sintético.
- Confirmar el código especial de facultad, longitud de códigos, títulos permitidos, prioridad y campos que permanecen vacíos.
- Definir el comportamiento esperado para `Undefined Function`, impresión, limpieza del formulario y reinicio de Proceso 12.
- Confirmar computadora, Windows, SIAC local/remoto, impresora, permisos y piloto autorizado.

**Salida:** reglas aprobadas y un lote sintético que pueda validarse sin CAFI.

## Etapa 1: adaptador y validaciones de Excel

- Leer una copia del archivo sin convertir códigos a número ni perder ceros.
- Verificar encabezados, filas vacías, campos obligatorios, títulos/detalles vacíos y prioridades no reconocidas.
- Identificar códigos repetidos o discrepancias entre código y nombre, pero nunca eliminar filas automáticamente.
- Generar un diagnóstico y una copia operativa con estados iniciales.

**Prueba de salida:** dry-run con datos sintéticos y sin abrir CAFI.

## Etapa 2: inspección de CAFI en Windows

- Inspeccionar la ventana y controles reales en el equipo destino; no usar coordenadas deducidas de capturas.
- Validar la navegación a Procesos, TRÁMITES ESTUDIANTE y Crear nuevo proceso.
- Confirmar la resolución del código: escribir/pegar, Enter, espera y lectura del nombre o facultad.
- Observar y documentar el diálogo `Undefined Function`, el mensaje de éxito, la impresión, Limpiar formulario y el restablecimiento de Proceso 12.
- Identificar dónde se muestran código de trámite, GPA y créditos aprobados y cómo asociarlos a la fila correcta.

**Prueba de salida:** inventario de controles y una demostración sin guardar trámites reales.

## Etapa 3: un trámite supervisado

- Iniciar sesión manualmente y abrir el primer formulario.
- Registrar en bitácora la intención antes de escribir.
- Cargar código, esperar resolución, validar destinatario y copiar título/detalle.
- Leer de vuelta los campos antes de guardar.
- Pulsar Guardar una vez y registrar éxito solo si aparece el mensaje concluyente.
- Si hay timeout o resultado ambiguo después de Guardar, marcar `REQUIERE_REVISION`, detenerse y conciliar manualmente.

**Prueba de salida:** un registro autorizado, confirmado y conciliado con una bitácora persistente.

## Etapa 4: impresión, reinicio y salida de resultados

- Implementar la impresión solo si María Emilia confirma que debe ser individual y si el diálogo puede automatizarse de forma segura.
- Tras imprimir, leer código de trámite, GPA y créditos aprobados únicamente si aparecen de forma estable y verificable.
- Limpiar el formulario, restablecer Proceso 12 y verificar que el siguiente formulario está listo antes de continuar.
- Escribir las salidas confirmadas en la copia operativa, sin volver a enviar los trámites ya procesados.

**Prueba de salida:** dos filas sintéticas o autorizadas procesadas secuencialmente sin mezclar sus resultados.

## Etapa 5: lote, recuperación y piloto

- Ejecutar un solo trabajador por lote con una detención manual accesible.
- Persistir cada transición de estado y bloquear reintentos de guardados inciertos.
- Conciliar al final: filas no vacías = procesadas + errores + revisión + pendientes.
- Probar pérdida de foco, error de impresión, caída de sesión, archivo de salida bloqueado e interrupción después de Guardar.
- Ejecutar un piloto supervisado con volumen autorizado y medir el tiempo humano antes y después.

**Salida del MVP:** lote conciliado, evidencia de resultados y validación de María Emilia. La generación de agenda Word desde la tabla se evalúa solo después.

## Criterios de no avance

- No avanzar a guardar si el destinatario resuelto no coincide con la regla aprobada.
- No reintentar automáticamente después de una acción Guardar con resultado incierto.
- No automatizar impresión, GPA, créditos o agenda Word sin observar controles y resultados repetibles.
- No utilizar credenciales en código, archivos, bitácoras ni pruebas.

## Actualización de alcance confirmada — 11 de septiembre de 2026

La asistente administrativa prepara el Google Sheet que sirve como fuente del lote. El código, el título y el detalle son variables por fila; se copian como estén validados en la hoja. La plantilla compartida es solamente una referencia y no se debe pedir a la usuaria que redefina el Excel.

El flujo objetivo es: fila validada del Google Sheet → CAFI en Windows con sesión preparada manualmente → validación del destinatario → Guardar → impresión → lectura de código de trámite, GPA y créditos aprobados → actualización de esos tres valores en la misma fila del Google Sheet. El Word de agenda no forma parte del MVP.

Una discrepancia de código/nombre o un destinatario inesperado detiene el lote para revisión manual. La referencia visual del video es de unos 1 min 20 s hasta el éxito y 2 min 40 s hasta quedar listo para una nueva fila, incluyendo impresión. La duración declarada de la operación es de 12 horas, ocho veces por semestre; deberá medirse por lote y por fila antes de calcular impacto.

El piloto real, cuando tenga autorización, será ejecutado por la asistente del área administrativa de la Facultad de Comunicación. Conectar la laptop a internet es una mejora a evaluar, no un tiempo de ejecución garantizado.
