# Proceso observado en el video: carga de trámites en CAFI

## Propósito y límites de esta evidencia

Este documento describe **solo lo visible** en el video de Drive `Grabación Prueba Quick Wins CAFI Consejo.mp4`, duración mostrada: 4:47. Fue revisado el 10 de septiembre de 2026.

No es un instructivo operativo autorizado ni una especificación de automatización. Las marcas de tiempo son aproximadas, porque se tomaron del reproductor. Las acciones de teclado, clics exactos, selectores de pantalla, permisos, reglas de negocio y resultados no visibles se indican como pendientes en vez de inferirse.

El video contiene datos de prueba. Por protección de datos, este documento no reproduce información identificable adicional a los valores técnicos necesarios para entender la demostración.

## Resumen de lo que sí demuestra

1. El video parte de un equipo Windows y de la aplicación **Sistema Académico UEES** ya abierta; no muestra el inicio de sesión.
2. En la ventana **Procesos**, se trabaja con el proceso **TRÁMITES ESTUDIANTE** y se abre la ventana **Ingreso de Procesos**.
3. Se ingresa un código de diez dígitos, que se resuelve visualmente a una descripción de facultad, no a un nombre de estudiante visible.
4. Se llenan título y detalle, se conserva la prioridad visible **Media**, se guarda y aparece una confirmación de éxito.
5. Tras el éxito se muestra una pantalla de impresión y luego un formulario con un código de proceso generado. Después, el formulario vuelve a quedar disponible para iniciar otra carga.
6. Se inicia una segunda carga, pero el video finaliza antes de mostrar su título, detalle, guardado o confirmación.

## Recorrido cronológico observado

### 00:00–00:30: punto de partida

- El video comienza en el escritorio de Windows.
- Se abre o ya está disponible la aplicación **Sistema Académico UEES – [Menú Principal]**.
- La pantalla visible corresponde a una ventana titulada **Procesos**. No se muestra cómo se ingresa al sistema ni cómo se llega inicialmente a este módulo.
- En la parte superior de la ventana se observa la sección **Criterios de consulta de Procesos**, con opciones como *Mis Tareas*, *Mis Procesos Activos*, *Mis Procesos Terminados*, *Todos*, un selector de facultad y filtros de fechas/trámite.
- Debajo aparece el árbol de procesos. También se observan secciones informativas inferiores, pero no se editan en esta demostración.

### 00:30–00:50: selección del tipo de proceso y apertura del formulario

- En el árbol de procesos se ve expandida la categoría **PROCESOS**.
- Entre los elementos visibles aparecen, entre otros, **ASIGNACIÓN BECAS DIFERENCIADAS**, **COMITÉ IMAGEN**, **COMPRAS GENERALES**, **RESERVACIONES PARA EVENTOS** y **TRÁMITES ESTUDIANTE**.
- Se selecciona visualmente **TRÁMITES ESTUDIANTE**.
- Se abre una ventana flotante titulada **Ingreso de Procesos**. El video no permite establecer con certeza el gesto exacto usado para abrirla (por ejemplo, clic derecho y opción de creación); únicamente permite confirmar que aparece tras seleccionar ese proceso.
- El formulario recién abierto muestra, entre otros, estos campos o valores visibles:
  - `Código` (vacío en ese instante).
  - `Fecha Inicio`, con fecha visible `08/09/2026`.
  - `Proceso` con valor `12` y descripción **TRÁMITES ESTUDIANTE**.
  - `# Días`, con valor `30`.
  - `Fecha Límite`.
  - `Cód. Alumno` y un campo descriptivo a la derecha.
  - `Colegio`.
  - `% Máximo Beca`.
  - `Título`.
  - `Detalle`, como área multilínea.
  - `Prioridad`, inicialmente visible como **Media**.
- No se observa que se modifiquen la fecha de inicio, el número de días, el proceso, colegio, porcentaje máximo de beca o prioridad.

### 00:50–01:40: ingreso y resolución del código

- Se escribe `0000000017` en **Cód. Alumno**. El valor se muestra con diez dígitos, incluidos los ceros iniciales.
- Mientras el sistema procesa el dato se aprecia un indicador de espera.
- Después de la resolución, el campo descriptivo a la derecha muestra **TRÁMITES FACULTAD COMUNICACION**.
- Esta evidencia muestra que, para ese código de prueba, el sistema devuelve una descripción de facultad. El video no prueba que sea un alumno, ni explica la regla de destinatario aplicable a cargas reales.

### 01:40–02:10: llenado del trámite y resultado de guardado

- Se ingresa en **Título**: `CONSIGNACIÓN DE NOTA`.
- Se ingresa en **Detalle** el texto visible: `EL ALUMNO SOLICITA LA CONSIGNACIÓN DE NOTA DE LA MATERIA USUARIO Y CONSUMIDOR`.
- La prioridad permanece en **Media**.
- Alrededor de 01:50 aparece momentáneamente un diálogo de error titulado **Error: Validación de Datos**. El mensaje visible es `FRM-41008: Undefined function key. Press CTRL+F1 for list of valid keys.`
  - El video no permite asociar con certeza ese mensaje a una acción determinada ni determina su causa.
  - No debe interpretarse como un error de los datos ingresados, porque el mensaje se refiere a una tecla de función no definida y luego se muestra un resultado exitoso.
- Alrededor de 02:10 aparece un diálogo **Información** con icono informativo y el texto visible `La Transacción se realizó Exitosamente...`.
- El diálogo ofrece el botón **OK**. Por lo tanto, el video proporciona evidencia visual de éxito para esta primera transacción demostrada.

### 02:10–03:30: salida posterior al éxito e impresión

- Después de la confirmación de éxito se abre un diálogo **Impresión**.
- En este diálogo se ven:
  - `Destino de Impresión`: **Pantalla**.
  - `Copias`: **1**.
  - Sección **Tipo archivo**, con opciones PDF, HTML y EXCEL; PDF aparece seleccionado visualmente.
  - Campo `Archivo`.
  - Botones **Cancelar** e **Impresión**.
- También se observa brevemente un cuadro de progreso de reporte (*Report Progress*) durante la generación.
- El video no muestra con suficiente claridad la acción exacta que abrió la impresión ni permite confirmar dónde se almacenó o visualizó el resultado impreso.
- Alrededor de 03:20 vuelve a verse el formulario con datos del trámite ya creado. En ese instante se aprecia un **Código** generado `10473`, `Fecha Límite` `21/10/2026`, el mismo título y detalle, y referencias visibles a `PGA CRED. APROB:0` dentro del área de detalle. Esto es evidencia de una pantalla posterior al registro, no una regla que deba fijarse en futuras cargas.
- Alrededor de 03:30 el formulario vuelve a mostrarse vacío, preparado para una nueva entrada; se mantienen los valores de contexto del proceso y la prioridad Media.

### 03:30–04:47: comienzo de una segunda carga y cierre del video

- Se empieza una segunda carga en el mismo formulario.
- Se vuelve a escribir `0000000017` en **Cód. Alumno** y se observa nuevamente el indicador de espera.
- Hacia el final, la grabación cambia a una hoja de cálculo de Google titulada **Prueba_AGENDA CONSEJO-CAFI**.
- La hoja visible contiene dos filas de prueba bajo las columnas `COD. ALUMNO`, `TITULO` y `DETALLE`:
  - primera fila: título `CONSIGNACIÓN DE NOTA`;
  - segunda fila: título `INCOMPLETO`;
  - ambas muestran el mismo código de diez dígitos y textos de detalle relacionados con la materia Usuario y Consumidor.
- La grabación termina sin evidencia de que la segunda fila haya sido completada, guardada, confirmada o impresa.

## Campos observados y tratamiento prudente

| Elemento visible | Acción demostrada | Conclusión válida |
|---|---|---|
| Cód. Alumno | Se introduce `0000000017` | Debe tratarse como texto para no perder ceros iniciales. |
| Descripción del código | El sistema devuelve `TRÁMITES FACULTAD COMUNICACION` | Hay una resolución en pantalla que debe validarse antes de guardar; su significado operativo está pendiente. |
| Título | Se llena para la primera fila | Se transfiere texto al formulario, pero el video no define límites ni catálogo. |
| Detalle | Se llena como texto multilínea | Debe conservarse el contenido, incluidos acentos y saltos, si los hubiera. |
| Prioridad | Permanece en Media | Media es un valor observado; el video no demuestra que sea obligatorio ni que aplique a todos los casos. |
| Guardar | Produce diálogo de éxito visible | La confirmación mostrada es la evidencia de éxito de esta demostración. |
| Código del proceso | Se muestra `10473` tras el registro | Es un valor generado observado en un caso de prueba, no un identificador reutilizable ni una secuencia garantizada. |
| Impresión | Se abre diálogo posterior | Es una acción observada, pero su necesidad y resultado requerido para el MVP siguen sin confirmar. |

## Controles y reglas que el video no confirma

- El inicio de sesión, usuarios, contraseñas, roles o permisos.
- El gesto exacto para abrir **Ingreso de Procesos** y los controles técnicos de la interfaz.
- La relación correcta entre código, destinatario, facultad y nombre de estudiante.
- Que `0000000017`, `30` días, las fechas observadas, `Media`, `10473`, colegio, porcentaje de beca o cualquier otro valor sean constantes para cargas reales.
- Los límites de longitud de título/detalle, el catálogo completo de prioridades y campos obligatorios.
- La consulta posterior que permita conciliar de forma segura una transacción en caso de resultado incierto.
- Que la impresión sea parte obligatoria del flujo, ni su archivo o destino final.
- La finalización de la segunda fila: no se observa éxito ni fallo de esa carga.
- Selectores, identificadores técnicos o coordenadas aptos para automatización. Esos controles deben inspeccionarse en el Windows donde se ejecuta SIAC.

## Implicación para el MVP RPA

El video, complementado por las voice notes F7, refuerza que una implementación debe: conservar el código como texto de diez dígitos, pulsar Enter y esperar la resolución del destinatario, comparar lo resuelto con una regla aprobada, leer los campos antes de guardar, pulsar Guardar una sola vez y marcar éxito únicamente tras observar la confirmación. Si aparece el diálogo `Undefined Function` al pegar, debe documentarse y manejarse solo según el comportamiento validado en el equipo real; no equivale por sí solo a que el trámite sea inválido.

Después de la impresión, el flujo conversado requiere Limpiar formulario, restablecer Proceso 12 y solo entonces iniciar la siguiente fila. La impresión individual, la lectura de código de trámite, GPA y créditos aprobados, y su devolución a la tabla siguen siendo aspectos que deben inspeccionarse y conciliarse antes de automatizarse.

La carga productiva sigue fuera de alcance de esta documentación. Antes de un piloto real aún se debe confirmar la regla de destinatario, el entorno de ejecución, el comportamiento de reapertura y la conciliación posterior.

## Medición incorporada del ciclo visible

| Hito | Marca aproximada | Tiempo desde formulario vacío |
|---|---:|---:|
| Formulario vacío disponible | 0:50 | — |
| Confirmación de éxito | 2:10 | 1 min 20 s |
| Formulario listo tras impresión | 3:30 | 2 min 40 s |

La usuaria confirmó posteriormente que la impresión sigue al guardado y que el código de trámite, GPA y créditos aprobados se devuelven al Google Sheet de origen. También confirmó que una discrepancia entre código, nombre o destinatario exige detener el lote para revisión manual. Estas decisiones no cambian los límites de la evidencia del video: la lectura de los tres valores y la actualización de la hoja deberán validarse en el equipo Windows.
