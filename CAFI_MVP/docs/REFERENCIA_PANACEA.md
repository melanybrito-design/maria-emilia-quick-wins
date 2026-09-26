# Referencia técnica utilizada

Se inspeccionó el ZIP Automatizacion RPA panacea facts-20260911T211006Z-1-001.zip aportado por la usuaria. Contiene 15 scripts Python.

control_rpa.pyw abre un panel nativo tkinter y lanza el robot. control_aprobacion.pyw utiliza un trabajador y cola para mantener la ventana disponible. robot_pasos.py, reconocimiento_panacea.py y la clase PanaceaUI de facturar_panacea.py muestran conexión pywinauto UIA/Win32, lectura de controles e inspección de ventanas.

Se adoptaron la entrada nativa, el trabajador separado, la asociación al proceso Windows y la verificación de campos. La interfaz CAFI usa Qt Widgets para su presentación y distribución embebida. No se copiaron rutas, credenciales, identificadores ni reglas de Panacea, pues corresponden a otro programa. El guardado CAFI no implementa reintentos automáticos del ejemplo: un intento incierto se concilia antes de continuar.

El proceso funcional se tomó de PROCESO_OBSERVADO_VIDEO_CAFI.md y los demás Markdown. No se volvió a revisar el video original en esta iteración. La secuencia documentada termina en confirmación, diálogo de impresión, reporte y limpieza para la siguiente fila.
