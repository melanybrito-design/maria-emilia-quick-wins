# Alcance de la versión para GitHub

## Se incluye

- código fuente Python y recursos necesarios para mantener el proyecto;
- pruebas automatizadas;
- documentación técnica y operativa;
- prompts de implementación, inspección y validación;
- ejemplos sintéticos de Excel;
- scripts de diagnóstico, pruebas y empaquetado;
- reportes finales y materiales documentales seleccionados.

## Se excluye intencionalmente

- `CAFI_MVP/runtime/`, `build/`, `wheelhouse/` y `wheelhouse-desktop/`, porque son runtimes o dependencias pesadas generadas para una distribución concreta de Windows;
- `CAFI_MVP/.venv/`, cachés, archivos temporales y salidas de renderizado;
- `data/`, logs, bases de datos, locks y perfiles locales, porque pueden contener estado de ejecución o datos de la computadora;
- `CAFI_MVP 2/`, que es una copia duplicada del proyecto;
- paquetes ZIP y artefactos intermedios;
- credenciales, tokens y configuraciones privadas.

La carpeta completa para ejecutar el RPA en Windows se debe generar con el proceso documentado en `CAFI_MVP/tools/make_release.py`. El repositorio conserva el código y la configuración reproducible, pero no publica el estado privado de una laptop.
