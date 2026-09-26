# Propuestas complementarias para el RPA de CAFI

Estas ideas están separadas del levantamiento. No son funcionalidades desarrolladas ni decisiones aprobadas. La dirección planteada por Melany es una automatización con código y sesión inicial manual.

## Propuesta principal

Construir primero un RPA atendido en Python. Inspeccionar la interfaz de SIAC con los backends Win32 y UIA antes de decidir cómo ubicar los campos. La [documentación oficial de pywinauto](https://pywinauto.readthedocs.io/en/latest/getting_started.html) describe esta selección según la tecnología de la aplicación. Las capturas permiten reconocer el flujo, pero no demostrar que los controles sean accesibles.

Usar lectura y validación de Excel como módulo independiente. Incorporar una bitácora persistente y copia de resultados desde el primer registro para poder reanudar sin repetir transacciones confirmadas. No se necesita un modelo de IA en cada ejecución: la IA puede ayudar a desarrollar el código y el bot ejecutar reglas deterministas.

## Alternativas condicionadas al diagnóstico

| Opción | Cuándo evaluarla | Limitación |
|---|---|---|
| Interacción por controles con pywinauto | SIAC expone controles accesibles en Windows | Requiere inspección y pruebas en destino. |
| Teclado e imágenes con pyautogui | Un control imprescindible no es accesible | Más sensible a foco, escala y cambios de pantalla; exige verificaciones adicionales. |
| Importación o API institucional | TI confirma que existe un mecanismo soportado | No hay evidencia de su existencia; no forma parte del MVP actual. |

No elegir automatización visual únicamente porque se dispone de capturas. Si el equipo usa escritorio remoto, evaluar dónde corre el bot antes de invertir en el adaptador.

## Mejoras posteriores que podrían aportar valor

- Una pantalla local sencilla para seleccionar el Excel, ver incidencias y ejecutar el diagnóstico. Evaluarla después de estabilizar el proceso.
- Una consulta de conciliación por identificador de proceso, si CAFI lo expone, para resolver intentos inciertos. No sustituirla por reintentos automáticos.
- Empaquetado para Windows y guía de uso, una vez comprobadas las dependencias en el equipo de María Emilia.
- Tras estabilizar la carga, evaluar una tabla única para que las asistentes registren nombre, código, título y detalle; usarla como entrada de CAFI y como fuente para generar la agenda Word. La revisión de correos y la clasificación inicial de solicitudes no forman parte de esta fase.
- Evaluar la captura trazable del código de trámite, GPA y créditos aprobados después de la impresión, para completar la tabla y después la agenda. Primero se debe confirmar dónde aparecen esos valores y cómo asociarlos inequívocamente con la fila cargada.

## Próximo paso recomendado

Resolver primero el significado y longitud exacta del código especial de facultad (la evidencia menciona tanto `00017` como `0000000017`), y validar el flujo posterior al guardado: impresión, limpieza del formulario y restablecimiento de Proceso 12. Después, desarrollar el diagnóstico Excel y un único registro de prueba supervisado. No asignar fechas ni prometer porcentajes de ahorro antes de medir el proceso.

## Ajuste de alcance confirmado

No se propone generar ni usar un Word de agenda en este proyecto. La fuente y salida operativa serán el Google Sheet preparado por la asistente administrativa: al finalizar cada trámite se actualizarán código de trámite, GPA y créditos aprobados en su misma fila, una vez que esa lectura esté inspeccionada y validada.
