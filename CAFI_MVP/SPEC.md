# Especificación CAFI 0.4.0

La solicitud vigente pide RPA Windows con ventana emergente nativa, iniciador BAT/icono, credenciales, Excel y ciclo hasta impresión. Sustituye las decisiones anteriores de UI web y autenticación exclusivamente manual. Los documentos originales se conservan en docs/fuentes.

## Implementado

- Qt Widgets, sin HTML ni servidor web en la entrada operativa; branding inspirado en la captura UEES y logo CAFI suministrado.
- Python Windows x64 embebido y lanzador GUI compilado. BAT y EXE llaman a CAFI.pyw.
- Selección explícita de ventana por handle/PID/clase; comprobación de identidad y foco antes de acciones.
- Configurador nativo UIA/Win32 que obtiene selectores observados; no trae controles ficticios. Mapa local data/perfil_cafi.json.
- Login opcional con credenciales en memoria y escritura directa, sin portapapeles ni argumentos.
- Controlador de navegación, proceso, código, destinatario, texto, prioridad, lectura de vuelta, guardado, confirmación, impresión, resultados y limpieza; espera configurable de 10 a 15 segundos entre acciones críticas.
- Confirmación humana obligatoria después de imprimir y antes de escribir código de trámite, GPA y créditos en el Excel de resultados.
- Diarios independientes para operación y simulación; persistencia antes de Guardar, confirmación antes de OK; estados separados de impresión. Sin reintentos automáticos tras un guardado incierto o continuación incompleta.
- Detección de huellas ya intentadas en otros lotes del mismo historial; exportación real a copia del Excel y prevención de fórmula en resultados observados.
- Iniciadores de diagnóstico y pruebas sin editor y sin instalación externa de Python.

## Límites y decisiones pendientes

El mapa de controles y la ejecución Windows no están validados. No se ha tenido acceso a la laptop de la persona. El adaptador está implementado contra pywinauto y perfiles, pero la compatibilidad real de CAFI debe probarse en destino. Si CAFI dibuja campos sin accesibilidad o el reporte pertenece a otro proceso, hay que adaptar el controlador con evidencia local. No se hace clic por coordenadas inferidas de capturas.

Tipo de proceso 12, longitud 10, prioridad Media y destino Pantalla/PDF son valores iniciales basados en el levantamiento; no se modifican fechas ni plazos. La discrepancia entre nombre de estudiante y destinatario genérico de facultad sigue bloqueando esa fila. La impresión reproduce el reporte en pantalla; no implica una impresora física ni guardado de PDF en disco. El resultado se escribe en copia Excel después de confirmación humana, sin conexión Google Sheets.

PROCESADO significa confirmación de guardado. IMPRESION_CAFI=COMPLETO acredita que el controlador terminó el reporte, lectura y limpieza, únicamente cuando se ejecute contra controles reales. Las pruebas con dobles no acreditan ese funcionamiento en CAFI. Sin idempotencia de servidor; tampoco hay deduplicación entre carpetas/historiales distintos ni entre contenidos modificados.

## Verificación

Consultar docs/VALIDACION.md. El piloto pendiente debe comprobar instalación Windows, descubrimiento de controles, login o sesión abierta, fila única autorizada, destinatario, guardado único, impresión, resultados y dos filas secuenciales. Ninguna prueba de este equipo macOS debe presentarse como piloto Windows.
