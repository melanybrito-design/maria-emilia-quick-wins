# Maria Emilia · Quick Wins RPA UEES

Proyecto de automatización local para una aplicación administrativa de Windows. El núcleo del proyecto se encuentra en [`CAFI_MVP/`](CAFI_MVP/), con una interfaz nativa, controlador de UI Automation/Win32, lectura de Excel, trazabilidad y pruebas.

## Contenido

- `CAFI_MVP/`: código fuente, pruebas, documentación, prompts, ejemplos y recursos del RPA.
- `CAFI_MVP/docs/`: validación, inspección de Windows y guía general para construir otros RPAs.
- `CAFI_MVP/tools/`: herramientas de prueba, generación de ejemplos y empaquetado.
- `CAFI_MVP/ejemplos/`: archivos sintéticos para probar la lectura y validación del Excel.
- `Prompt_Maestro_Slides_Quickwins_UEES.md`: prompt de referencia para los materiales del proyecto.
- Reportes PDF/DOCX finales: entregables documentales del proyecto.

## Ejecución del RPA en Windows

El paquete operativo de Windows se genera localmente con el runtime y las dependencias indicadas en `CAFI_MVP/requirements-windows.txt`. Para la ejecución diaria se utiliza `CAFI.exe` o `INICIAR_CAFI.bat` dentro de un paquete completo; ambos abren la ventana nativa del RPA.

El repositorio no contiene runtimes, entornos virtuales, bases de datos de ejecución, perfiles locales de controles ni credenciales. Esto mantiene el repositorio ligero y evita publicar información específica de una computadora. Consulta `CAFI_MVP/README.md` y `CAFI_MVP/LEEME_WINDOWS.md` para preparar el paquete Windows.

## Pruebas

Desde `CAFI_MVP/`:

```bash
python -m pytest tests -q
```

Las pruebas locales verifican la lógica y los contratos del controlador. La conexión con una aplicación real de Windows debe validarse en la computadora donde está instalada y con un perfil de controles observado allí.

## Estado de validación

La evidencia y las limitaciones conocidas están en [`CAFI_MVP/docs/VALIDACION.md`](CAFI_MVP/docs/VALIDACION.md). No se deben interpretar las pruebas con dobles como evidencia de una ejecución real en Windows.
