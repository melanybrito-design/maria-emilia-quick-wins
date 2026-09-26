# Validación de la versión 0.4.0

15 de septiembre de 2026. La versión 0.4.0 conserva la base verificada de desarrollo y añade espera configurable de 10 a 15 segundos entre acciones críticas, además de confirmación humana obligatoria después de la impresión y antes de exportar resultados al Excel. No hubo sesión remota ni ejecución de CAFI en Windows.

## Comprobaciones realizadas

- **75 pruebas aprobadas** en 3,09 segundos con `python -m pytest tests -q`.
- 40 pruebas anteriores de lectura Excel, preservación, simulador, SQLite y API de desarrollo; no acreditan conexión CAFI.
- 35 pruebas de flujo real con dobles, contrato del controlador y sesión: orden de intención/guardado/OK/impresión, lectura de resultados, reanudación de filas completas, duplicados en otro archivo, resultado incierto, parada antes/después de Guardar, fallo de OK, fallo de reporte, fallo de exportación, caída antes de persistir éxito, contraseña no leída de vuelta ni enviada como teclas, texto literal y selectores estrictos.
- Ventanas Qt renderizadas con backend offscreen y revisadas visualmente a 1060×880 y 1060×720. Capturas 04-ventana-nativa.png, 05-configuracion-nativa.png y 06-ventana-720.png. La vista baja tiene desplazamiento para acceder a los botones inferiores. El tamaño inicial se ajusta al área disponible de la pantalla.
- Se resolvió un problema del renderizado local: los plugins Qt dentro de .venv tenían el atributo macOS «hidden» y Qt no los enumeraba. Se retiró ese atributo solo en los plugins de desarrollo. Esto no prueba ni afecta la ejecución del paquete Windows.
- CAFI.exe fue preparado como PE32+ GUI x86-64 con icono. El paquete operativo v0.4.0 abre la ventana nativa y excluye la interfaz web y los módulos web heredados. No se ejecutó ese binario en Windows.
- Runtime armado desde el ZIP Python 3.13.15 embebido y 14 wheels. Hash del archivo de intérprete comprobado contra el valor registrado de la descarga. El código de la app queda fuera del runtime; no se usan copias antiguas de módulos.
- INICIAR_CAFI.bat y CAFI.exe invocan CAFI.pyw, que importa native_app.py. No abren HTML. El ZIP operativo excluye UI web, servidor y módulos heredados.
- tools/make_release.py verifica CRC y SHA-256 de cada archivo, así como la inclusión de CAFI.pyw y runtime/pythonw.exe. No incluye data, perfiles de controles, credenciales, .venv ni el ZIP de Panacea.

## Prueba pendiente en la laptop Windows

1. Arranque de BAT/EXE, imports de Qt/pywin32/pywinauto, creación de acceso directo y compatibilidad con Windows/elevación/DPI.
2. Identificación UIA/Win32 y configuración de los controles reales de CAFI, incluidos acceso, navegación, éxito y reporte. El paquete no trae un mapa supuesto.
3. Piloto autorizado de una fila con revisión del destinatario y resultado. Después de imprimir, validar el cuadro de confirmación humana antes de comprobar la actualización del Excel; luego probar dos filas y detención.
4. Confirmar el indicador de reporte terminado y que código/GPA/créditos procedan del registro recién creado. Si el reporte abre en otro proceso, adaptar la asociación antes de probar.
5. Confirmar tipo de proceso, prioridad, longitud del código y regla de destinatario genérico. Verificar impresión en pantalla frente a cualquier necesidad adicional de papel o PDF en disco.

## Lo que las pruebas no demuestran

No demuestran login, carga ni impresión exitosos en CAFI; no hay controles observados aún. Tampoco acreditan idempotencia del servidor, interoperabilidad de ventanas en procesos distintos ni ahorro de tiempo. Un perfil completo permite intentar el flujo real; no certifica que sus controles estén bien configurados. El robot detiene los fallos y conserva intención/resultados para revisión.
