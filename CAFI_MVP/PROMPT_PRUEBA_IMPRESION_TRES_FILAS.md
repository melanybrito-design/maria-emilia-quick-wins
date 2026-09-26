# Prompt para prueba de impresión y tres filas en SIAC / CAFI

Copia este mensaje completo en Codex desde la laptop Windows donde SIAC–CAFI está instalado y abierto.

---

Trabaja en la carpeta local `CAFI_MVP`. Debes completar una prueba controlada del RPA existente. No rehagas el proyecto desde cero y no reemplaces la ventana nativa por HTML.

Lee antes `AGENTS.md`, `SPEC.md`, `README.md`, `LEEME_WINDOWS.md`, `native_app.py`, `windows_rpa.py` y `real_workflow.py`.

## Objetivo de esta sesión

Completar y validar el flujo de **tres filas consecutivas**:

`Excel → SIAC / CAFI → guardar → imprimir → confirmar resultados → cerrar reporte → siguiente fila → actualizar Excel de resultados`.

Usa como archivo de validación de estructura:

`ejemplos/Prueba_RPA_SIAC_3_filas_sinteticas.xlsx`

Este archivo contiene datos sintéticos. No lo envíes a SIAC si los códigos de prueba no son registros autorizados y existentes. Para un piloto real, la responsable debe proporcionar tres filas autorizadas con la misma estructura.

## Restricciones obligatorias

- No inventes selectores ni uses coordenadas tomadas de capturas.
- No guardes un trámite real sin autorización expresa de la responsable para esa fila.
- No guardes contraseñas ni datos estudiantiles en archivos, código, consola o bitácoras.
- No reintentes un Guardar cuyo resultado sea incierto.
- No actualices resultados hasta que una persona confirme el código de trámite, GPA y créditos mostrados después de imprimir.
- Mantén la espera configurable entre 10 y 15 segundos. Usa 12 segundos como valor inicial.
- SIAC y el RPA deben ejecutarse en la misma sesión de Windows y con el mismo nivel de permisos.

## Fase 1: inspección de impresión

Con SIAC abierto en la pantalla posterior al guardado, realiza inspección de solo lectura usando primero UIA y luego Win32.

Identifica y configura controles reales para:

1. Botón o acción que abre impresión.
2. Destino de impresión o generación de PDF, si existe.
3. Número de copias, si corresponde.
4. Botón final de imprimir.
5. Indicador verificable de que el reporte terminó de generarse.
6. Ventana del reporte y botón para cerrarla.
7. Código de trámite, GPA y créditos aprobados visibles en el reporte.
8. Acción para dejar el formulario vacío antes de la siguiente fila.

Guarda solo selectores observados en `data/perfil_cafi.json`. Si la ventana de impresión o el reporte pertenece a un proceso distinto, adapta la búsqueda para observar esa ventana real. No afirmes que está resuelto hasta poder detectar el reporte generado.

## Fase 2: confirmación humana y resultados

Verifica o implementa este orden exacto:

1. Guardar una sola vez.
2. Esperar el mensaje exacto de éxito.
3. Abrir impresión y esperar al menos 12 segundos entre acciones críticas.
4. Generar el reporte.
5. Leer código de trámite, GPA y créditos.
6. Mostrar un cuadro nativo con esos tres valores.
7. Esperar confirmación humana.
8. Si la persona confirma, escribir los tres valores en `resultados_cafi.xlsx`.
9. Cerrar el reporte y limpiar el formulario.
10. Continuar con la siguiente fila.

Si la persona rechaza la confirmación, detener el lote, conservar la bitácora y no volver a guardar esa fila.

## Fase 3: prueba escalonada

1. Ejecuta diagnóstico y pruebas de código disponibles.
2. Valida el Excel sintético solo como estructura de entrada.
3. Ejecuta primero una única fila autorizada y verifica registro, impresión, confirmación, cierre y actualización de resultados.
4. Solo después de que la primera fila funcione, prueba tres filas autorizadas consecutivas.
5. Comprueba que SIAC vuelva al formulario vacío entre filas y que no se duplique ningún trámite.

## Entrega al terminar

Reporta de forma verificable:

- Controles detectados y backend usado: UIA, Win32 o ambos.
- Archivos modificados.
- Resultado de diagnóstico y pruebas.
- Si se logró imprimir, cerrar reporte y leer los tres resultados.
- Si se actualizó `resultados_cafi.xlsx` solo después de la confirmación humana.
- Si se guardaron trámites reales; si no hubo autorización, indicar que no se guardó ninguno.
- Bloqueos pendientes para el piloto completo.
