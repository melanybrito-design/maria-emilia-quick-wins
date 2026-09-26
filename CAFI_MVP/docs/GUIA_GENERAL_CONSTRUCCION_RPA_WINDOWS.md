# Guía general para construir un RPA local de Windows

## Propósito

Esta guía resume el método utilizado para diseñar un RPA local que lee datos estructurados, controla una aplicación de escritorio de Windows y devuelve los resultados a un archivo. Está escrita como una referencia reutilizable para otros casos: no depende de un sistema, facultad, formulario, persona, código de proceso o conjunto de campos concreto.

La idea central es separar cuatro trabajos que suelen confundirse:

1. entender y documentar el proceso humano;
2. descubrir los controles reales de la aplicación;
3. convertir el proceso en un flujo verificable y seguro;
4. probarlo en la computadora donde se ejecutará.

Un RPA no se conecta a una aplicación de escritorio por conocer una captura de pantalla. Necesita encontrar la ventana real, inspeccionar sus controles, operar sobre ellos y verificar el resultado después de cada etapa.

## Resultado esperado

El resultado final debe ser una aplicación nativa de Windows que la persona pueda abrir con un `.exe` o `.bat`, sin usar Visual Studio Code ni abrir una página HTML. La aplicación debe permitir, según el caso:

- seleccionar un archivo de entrada;
- validar su estructura antes de iniciar;
- detectar o seleccionar la ventana de la aplicación objetivo;
- ejecutar un lote fila por fila;
- esperar a que la aplicación responda;
- comprobar cada cambio importante;
- guardar los resultados en un archivo de salida;
- detenerse de forma segura cuando exista incertidumbre;
- mostrar un resumen verificable del lote.

El ejecutable es solo la puerta de entrada. La automatización real está en el controlador de Windows y en la orquestación del flujo.

## 1. Levantar el proceso antes de programar

Primero se documenta cómo trabaja una persona sin automatización. Se debe observar al menos un caso completo y registrar:

- qué archivo o fuente contiene los datos de entrada;
- qué campos se copian y en qué orden;
- qué campos son obligatorios, opcionales o calculados;
- qué decisiones toma la persona;
- cuánto tarda cada etapa;
- qué mensajes o pantallas confirman que una etapa terminó;
- qué documento, impresión o resultado se genera;
- qué datos nuevos deben regresar al archivo;
- qué errores aparecen normalmente y cómo se recuperan;
- qué acciones requieren autorización o revisión humana.

El levantamiento debe distinguir hechos observados de supuestos. Una captura, un video o una explicación verbal sirven para entender el recorrido, pero no sustituyen la inspección de la aplicación que el robot controlará.

El documento de proceso debe terminar con una tabla similar a esta, usando nombres genéricos:

| Etapa | Entrada | Acción humana actual | Resultado esperado | Evidencia de finalización |
|---|---|---|---|---|
| Preparación | Archivo de datos | Seleccionar y revisar | Archivo válido | Validación sin errores |
| Acceso | Sesión de la aplicación | Abrir o iniciar sesión | Ventana disponible | Título, proceso o control visible |
| Registro | Fila actual | Completar formulario | Datos cargados | Lectura de vuelta de campos |
| Confirmación | Formulario completo | Guardar o enviar | Registro creado | Mensaje, código o estado de éxito |
| Resultado | Reporte o pantalla final | Leer datos generados | Resultados disponibles | Controles del reporte |
| Cierre | Pantalla final | Cerrar y preparar siguiente | Estado limpio | Formulario vacío o pantalla inicial |
| Salida | Resultados | Actualizar archivo | Lote trazable | Fila con estado y resultados |

## 2. Definir alcance y límites

Antes de desarrollar, escribe qué hará el primer piloto y qué queda para una fase posterior. Un alcance razonable para un primer piloto es:

`archivo local → aplicación de escritorio → resultado local`.

Conviene posponer integraciones externas, como Google Sheets, hasta que una fila real complete correctamente el ciclo local. Así se separan los problemas de automatización de Windows de los problemas de autenticación, permisos y conectividad.

También hay que decidir:

- si la persona abrirá la aplicación e iniciará sesión manualmente;
- si el RPA solo trabajará con una sesión abierta;
- si la impresión será física, PDF, vista previa o una combinación;
- si cada fila requerirá revisión humana;
- qué hacer cuando el resultado sea incierto;
- si se permitirá reanudar un lote;
- dónde se conservará el original y dónde se escribirán resultados.

Estas decisiones deben quedar escritas antes de implementar el flujo.

## 3. Preparar la arquitectura local

Una estructura práctica separa responsabilidades:

```text
proyecto_rpa/
├── launcher.bat                 # Entrada sencilla para la usuaria
├── app.pyw                      # Arranque de la aplicación nativa
├── native_app.py                # Ventana y controles de configuración
├── windows_driver.py            # Operaciones sobre ventanas y controles
├── workflow.py                  # Flujo de negocio fila por fila
├── input_manager.py             # Lectura y validación del archivo
├── journal.py                   # Estados, trazabilidad y reanudación
├── diagnostic.py                # Diagnóstico de instalación y ventanas
├── inspect_windows.py           # Inspección de controles reales
├── data/                        # Estado local; nunca credenciales
├── docs/                        # Evidencia, mapa y validación
├── tests/                       # Pruebas unitarias y de contrato
├── assets/                      # Icono y recursos visuales
└── runtime/                     # Dependencias para el paquete Windows
```

El nombre de los archivos puede cambiar, pero la separación debe mantenerse. La interfaz no debe contener la lógica completa del RPA, y el controlador de Windows no debe decidir cómo se actualiza el negocio.

## 4. Diseñar la interfaz de la aplicación

La ventana nativa debe ser sencilla para la persona que ejecuta el proceso. Como mínimo puede incluir:

1. selección del archivo de entrada;
2. selección o detección de la aplicación objetivo;
3. indicador de sesión encontrada;
4. botón para validar archivo;
5. parámetros de espera configurables;
6. botón para iniciar;
7. botón para detener;
8. progreso por fila;
9. etapa actual y mensaje legible;
10. ruta del archivo de resultados;
11. resumen de completados, detenidos y pendientes.

La interfaz debe impedir iniciar cuando faltan columnas, controles, sesión, permisos o configuración. Un botón deshabilitado por una causa explícita es preferible a iniciar un lote que puede duplicar registros.

## 5. Conectar el RPA con una aplicación de Windows

### 5.1. Trabajar en la computadora objetivo

El mapa de controles depende de la instalación, versión, resolución, escala DPI, permisos y sesión de Windows. Por eso el desarrollo conceptual puede hacerse en otra computadora, pero la inspección final debe hacerse en la computadora donde vive la aplicación objetivo.

La persona responsable debe:

1. abrir la aplicación;
2. iniciar sesión de acuerdo con sus políticas;
3. dejar disponible una pantalla de prueba;
4. mantener desbloqueada la sesión durante el diagnóstico;
5. ejecutar la herramienta de inspección con el mismo nivel de permisos que la aplicación.

### 5.2. Usar UI Automation y Win32

Primero se intenta UI Automation (UIA), porque suele exponer nombre, tipo, estado, AutomationId y jerarquía. Si la aplicación no expone un control de forma suficiente, se inspecciona con Win32 para obtener clase, identificador de control, título y mensajes disponibles.

La estrategia recomendada es:

1. identificar la ventana principal y su proceso/PID;
2. listar ventanas hijas y diálogos modales;
3. localizar un control visible conocido;
4. leer sus propiedades sin modificar nada;
5. comprobar si el control es único;
6. probar lectura o foco en modo seguro;
7. guardar el selector observado en un perfil local;
8. documentar backend, propiedades y limitaciones.

No se deben inventar selectores a partir de una imagen. Las coordenadas pueden servir para una investigación temporal, pero son frágiles frente a cambios de tamaño, DPI y posición.

### 5.3. Crear un mapa de controles

El mapa debe identificar, como mínimo:

- ventana principal;
- navegación necesaria;
- campos de entrada;
- listas, combos y casillas;
- botón de guardar o enviar;
- mensaje de éxito;
- botón de aceptación del mensaje;
- reporte o ventana de impresión;
- controles de resultados;
- botón de cerrar;
- evidencia de formulario limpio.

Para cada control registra:

| Dato | Ejemplo de contenido |
|---|---|
| Clave funcional | `guardar_registro` |
| Backend | `uia` o `win32` |
| Ventana | título o clase observada |
| Tipo | botón, edición, combo, documento |
| Nombre visible | texto real del control |
| AutomationId | valor observado, si existe |
| ClassName/control ID | valor observado, si existe |
| Selector alterno | segunda estrategia estable |
| Acción | leer, escribir, seleccionar, pulsar |
| Evidencia | fecha, pantalla y resultado |

Si un control no puede mapearse de manera fiable, el flujo debe detenerse y documentarlo. No se debe marcar como completo para que el botón de inicio se habilite.

## 6. Leer y validar datos estructurados

El lector debe validar el archivo antes de tocar la aplicación:

- hoja esperada;
- columnas obligatorias;
- filas vacías;
- formatos de fecha y texto;
- campos de selección;
- códigos con ceros iniciales;
- fórmulas o valores no calculados;
- duplicados;
- columnas de resultados que deben estar vacías;
- filas ya procesadas.

Los identificadores deben leerse como texto cuando exista riesgo de perder ceros iniciales. Los títulos y detalles deben conservarse literalmente, salvo que el proceso documentado permita una transformación.

Conserva dos archivos o estados:

1. el original de entrada, sin modificar;
2. una copia de resultados con estado, marcas de tiempo y datos devueltos por la aplicación.

## 7. Diseñar el flujo como una máquina de estados

Cada fila debe pasar por estados explícitos. Un modelo general es:

```text
PENDIENTE
  → VALIDADA
  → FORMULARIO_COMPLETADO
  → INTENCION_CONFIRMADA
  → GUARDADO_VERIFICADO
  → RESULTADO_DISPONIBLE
  → IMPRESION_COMPLETADA
  → FORMULARIO_LIMPIO
  → RESULTADOS_ACTUALIZADOS
```

Si ocurre una duda, se usa un estado de revisión:

```text
GUARDADO_INCIERTO / REPORTE_NO_LEIDO / IMPRESION_INCIERTA / REQUIERE_REVISION
```

Un estado incierto no debe convertirse en un reintento automático. El mayor riesgo de un RPA administrativo es duplicar una operación cuyo resultado sí se creó, pero cuya respuesta no llegó a tiempo.

El flujo general de una fila es:

1. leer la fila;
2. validar que puede procesarse;
3. comprobar que la aplicación está en la pantalla esperada;
4. limpiar o verificar el formulario;
5. completar los campos;
6. leer de vuelta los campos críticos;
7. comparar con la fila original;
8. guardar una intención antes de la acción irreversible;
9. guardar una sola vez;
10. esperar una evidencia real de éxito;
11. leer el resultado generado;
12. imprimir o abrir el reporte según el alcance;
13. cerrar el reporte;
14. comprobar que la pantalla está preparada;
15. actualizar la copia de resultados;
16. pasar a la siguiente fila.

## 8. Esperas y sincronización

Las esperas fijas ayudan cuando la aplicación es lenta, pero no bastan. Usa una combinación de:

- espera mínima entre acciones críticas;
- espera por aparición de una ventana;
- espera por habilitación de un botón;
- espera por desaparición de un indicador de carga;
- espera por mensaje o código de éxito;
- tiempo máximo por etapa;
- captura diagnóstica al vencer el tiempo máximo.

El valor de espera debe ser configurable. Comienza con un valor conservador y ajústalo con tiempos observados. Reporta por separado el tiempo de programación y el tiempo que realmente consumió la aplicación.

## 9. Credenciales y permisos

Las credenciales deben permanecer en memoria durante la sesión y nunca deben aparecer en:

- código fuente;
- archivos de configuración;
- argumentos de procesos;
- portapapeles;
- logs;
- capturas;
- archivos de resultados.

Para el primer piloto suele ser más seguro que la persona abra la aplicación e inicie sesión manualmente. El RPA valida que la sesión está disponible y trabaja desde una pantalla conocida.

La aplicación objetivo y el RPA deben ejecutarse con el mismo nivel de permisos. Una aplicación elevada y un robot sin elevación puede impedir que UIA o Win32 interactúen correctamente.

## 10. Impresión y resultados

La impresión debe tratarse como una etapa independiente del guardado. Identifica por separado:

- botón o acción que abre el reporte;
- indicador de reporte listo;
- código o identificador generado;
- campos de resultado;
- destino de impresión;
- botón de imprimir;
- indicador de impresión finalizada;
- cierre del reporte.

No escribas en el Excel solo porque se abrió una pantalla. Escribe los resultados cuando el código, los campos de salida y el estado de impresión cumplan las condiciones del proceso.

Si existe una revisión humana, define exactamente su momento y alcance. Puede ser una revisión del lote o una autorización inicial, pero no debe aparecer de forma accidental después de cada fila si ese no es el diseño acordado.

## 11. Reanudación y trazabilidad

Cada fila debe conservar:

- identificador de fila de origen;
- clave de negocio;
- estado actual;
- fecha y hora de cada etapa;
- resultado devuelto;
- error, si existe;
- versión del perfil de controles;
- versión del RPA.

El diario permite saber qué ocurrió sin volver a enviar una fila. La reanudación debe comenzar desde la primera fila pendiente o en revisión, nunca desde el inicio por defecto.

## 12. Pruebas por etapas

### Prueba A: instalación

Comprobar que la carpeta extraída contiene ejecutable, launcher, runtime, recursos y dependencias. Ejecutar el diagnóstico sin abrir ni leer datos de la aplicación objetivo.

### Prueba B: interfaz

Abrir la ventana nativa, seleccionar un archivo sintético y comprobar mensajes, botones, validaciones y botón de detener.

### Prueba C: lectura del archivo

Usar datos sintéticos para comprobar tipos, columnas, ceros iniciales, filas incompletas y duplicados. No tocar la aplicación objetivo.

### Prueba D: inspección de controles

Con la aplicación abierta, leer ventanas y controles sin escribir ni guardar. Generar el perfil local y documentar lo que no se pudo identificar.

### Prueba E: una fila autorizada

Usar una fila controlada. Verificar el ciclo completo y medir cada etapa. Confirmar que los resultados regresan al archivo de salida.

### Prueba F: tres filas consecutivas

Solo después de que la prueba de una fila funcione. Comprobar limpieza entre filas, ausencia de duplicados, lectura correcta de resultados y continuidad del lote.

### Prueba G: fallos controlados

Probar de forma segura ventana perdida, control ausente, tiempo agotado, mensaje de éxito no encontrado y resultado incierto. El robot debe detenerse y conservar evidencia, no continuar a ciegas.

Las pruebas unitarias con dobles verifican la lógica, pero no demuestran que la aplicación real funcione. La validación final siempre necesita una prueba observada en Windows.

## 13. Medición de tiempo y ROI

Usa un reloj monotónico para registrar:

- inicio y fin del lote;
- inicio y fin de cada fila;
- entrada de datos;
- guardado;
- respuesta de éxito;
- reporte;
- impresión;
- limpieza;
- actualización del archivo.

Para comparar con el proceso manual se necesitan datos observados:

- tiempo manual promedio por fila o lote;
- tiempo del RPA por fila o lote;
- minutos de intervención humana que siguen siendo necesarios;
- frecuencia del proceso;
- número de personas o áreas que lo realizan;
- costo horario utilizado por la organización;
- horas de levantamiento, desarrollo, pruebas, implementación y mantenimiento.

Una forma transparente de calcular el ahorro es:

```text
horas ahorradas por ciclo = horas manuales − horas de intervención humana con RPA
ahorro monetario por ciclo = horas ahorradas × costo horario
beneficio anual = ahorro monetario por ciclo × ciclos anuales
inversión = horas de desarrollo × costo horario de desarrollo + otros costos
ROI (%) = ((beneficio anual − inversión) / inversión) × 100
```

Si todavía no existe un tiempo real del RPA, presenta el cálculo como estimación y marca qué dato debe medirse en el piloto. No uses una duración programada como si fuera una medición observada.

## 14. Empaquetado y entrega

La entrega debe permitir que otra persona:

1. extraiga la carpeta completa;
2. ejecute el instalador o diagnóstico;
3. abra el `.exe` o `.bat`;
4. lea una guía breve;
5. prepare la aplicación objetivo;
6. seleccione el archivo;
7. ejecute el piloto;
8. encuentre resultados y logs.

Antes de entregar:

- verifica dependencias y arquitectura de Windows;
- incluye el icono y los recursos;
- excluye credenciales, perfiles privados y bases de datos de prueba;
- calcula hashes si el proyecto lo requiere;
- documenta versión y fecha;
- indica qué se probó realmente y qué queda pendiente.

No entregues un paquete que dependa de abrir Visual Studio Code o una página HTML para iniciar el flujo.

## 15. Errores habituales y su diagnóstico

### Se abre una página HTML

El launcher está apuntando a una interfaz antigua o a un servidor local. Revisa el punto de entrada y haz que el `.bat` invoque la aplicación nativa.

### El ejecutable no inicia en otra computadora

Probablemente se copió solo el `.exe`. Extrae la carpeta completa o genera un paquete con runtime y assets incluidos.

### El RPA no encuentra la aplicación

Comprueba título, PID, permisos, sesión, arquitectura, DPI y backend. Ejecuta el diagnóstico en la computadora objetivo.

### Encuentra la ventana pero no los campos

Inspecciona UIA y Win32. El control puede estar dentro de un diálogo, en otro proceso o expuesto con otra clase. No sustituyas el problema con coordenadas sin documentarlo.

### El robot duplica registros

Falta separar guardado verificado de guardado incierto o se reintentó después de un tiempo agotado. Añade estados persistentes y conciliación.

### El Excel pierde ceros o cambia títulos

El lector está tratando identificadores como números o transformando texto. Lee códigos como texto y valida una copia antes de operar.

## 16. Prompt reutilizable para Codex

El siguiente texto puede copiarse y adaptarse para otro RPA. Sustituye los campos entre corchetes.

```text
Trabaja dentro de [CARPETA DEL PROYECTO] en la laptop Windows donde está instalada y abierta [APLICACIÓN OBJETIVO].

Objetivo: construir un RPA local que lea [ARCHIVO/FUENTE DE ENTRADA], complete [PROCESO O FORMULARIO], espere el resultado, lea [DATOS DE SALIDA] y actualice una copia de resultados sin duplicar operaciones.

Lee primero:
1. AGENTS.md o las reglas locales del proyecto.
2. README y especificación.
3. Documentación del proceso observado.
4. Código de interfaz, controlador, workflow, lector de datos y pruebas.
5. Toda la documentación de validación existente.

Reglas:
- Trabaja en español y documenta cada decisión.
- No uses HTML como interfaz operativa.
- No inventes selectores, resultados ni tiempos.
- Inspecciona la aplicación real con UI Automation y Win32.
- Usa el mismo nivel de permisos para aplicación y RPA.
- No guardes credenciales en código, archivos, logs, argumentos ni portapapeles.
- Conserva el archivo original y escribe resultados en una copia.
- No reintentes una acción irreversible cuyo resultado sea incierto.
- Detén el proceso si un control no es único, no está disponible o no puede verificarse.

Fase 1: diagnóstico
1. Ejecuta las pruebas locales.
2. Comprueba que el paquete y el launcher funcionan.
3. Identifica ventana, proceso/PID, backend y permisos de [APLICACIÓN OBJETIVO].
4. Inspecciona controles en modo lectura, sin guardar información.
5. Construye un mapa con nombre funcional, backend, propiedades, acción y evidencia.

Fase 2: datos
1. Define columnas obligatorias y columnas de resultados.
2. Valida tipos, filas incompletas, duplicados y códigos con ceros iniciales.
3. Crea una copia de resultados y conserva el original.

Fase 3: flujo
Implementa estados explícitos:
PENDIENTE, VALIDADA, FORMULARIO_COMPLETADO, GUARDADO_VERIFICADO,
RESULTADO_DISPONIBLE, IMPRESION_COMPLETADA, LIMPIO,
RESULTADOS_ACTUALIZADOS y REQUIERE_REVISION.

Para cada fila:
1. valida la fila;
2. comprueba la pantalla esperada;
3. limpia o verifica el formulario;
4. completa campos;
5. lee de vuelta valores críticos;
6. registra la intención antes de guardar;
7. guarda una sola vez;
8. espera una evidencia real de éxito;
9. lee los resultados;
10. imprime o genera el reporte;
11. cierra el reporte;
12. verifica el estado limpio;
13. actualiza la copia de resultados;
14. continúa solo si el estado anterior está confirmado.

Fase 4: pruebas
1. diagnóstico sin escritura;
2. inspección de controles;
3. validación del archivo con datos sintéticos;
4. una fila real autorizada;
5. tres filas consecutivas;
6. fallos controlados y reanudación segura.

Mide tiempos con reloj monotónico para cada etapa. Distingue tiempo programado, tiempo de respuesta de la aplicación e intervención humana.

Actualiza documentación, pruebas y versión. Al finalizar informa:
- controles esperados, encontrados y pendientes;
- archivos modificados;
- pruebas ejecutadas;
- resultado de una fila y de tres filas;
- tiempos observados;
- filas actualizadas;
- errores y correcciones;
- limitaciones concretas;
- si el ciclo real quedó validado.

No afirmes que el RPA está listo para producción sin evidencia de la aplicación real.
```

## 17. Lista de entrega para la compañera

Antes de considerar terminado un caso, la persona que lo desarrolla debe poder responder afirmativamente:

- ¿El proceso humano está escrito y validado con su responsable?
- ¿El alcance del piloto está delimitado?
- ¿El archivo de entrada tiene columnas y reglas claras?
- ¿La aplicación real fue inspeccionada en la laptop donde se usará?
- ¿Cada control importante tiene un selector observado y documentado?
- ¿Las credenciales están protegidas?
- ¿Existe un estado seguro para los resultados inciertos?
- ¿El flujo fue probado con una fila real autorizada?
- ¿El flujo fue probado con varias filas consecutivas?
- ¿Se comprobó que no existen duplicados?
- ¿El resultado se escribió en una copia trazable?
- ¿Se midieron tiempos reales?
- ¿Se actualizaron las pruebas y la documentación?
- ¿El paquete puede abrirse sin herramientas de desarrollo?
- ¿El informe distingue evidencia real, estimaciones y pendientes?

Si una respuesta es no, el proyecto todavía tiene una tarea concreta antes de declararse listo.
