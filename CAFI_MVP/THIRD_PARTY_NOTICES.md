# Componentes de terceros

El código de la aplicación se entrega editable. Las bibliotecas se distribuyen sin modificar y se cargan dinámicamente desde runtime/Lib/site-packages. Sus licencias y avisos originales se conservan dentro de las carpetas dist-info y del intérprete. El manifiesto runtime/COMPONENTES_SHA256.json identifica los archivos de origen usados en esta compilación.

- Python 3.13.15 embebido: licencia PSF, runtime/LICENSE.txt. https://www.python.org/downloads/
- PySide6-Essentials y shiboken6 6.10.2: Qt for Python, bibliotecas bajo LGPLv3/GPLv3 según componente. Se incluyen los avisos originales del wheel. No están enlazadas estáticamente; es posible sustituir las bibliotecas por versiones compatibles para ejercer los derechos de su licencia. Fuentes y licencias: https://code.qt.io/cgit/pyside/pyside-setup.git/ y https://www.qt.io/licensing/open-source-lgpl-obligations
- Qt 6.10.2: módulos binarios y plugins incluidos por el wheel de Qt for Python. Fuentes: https://download.qt.io/archive/qt/6.10/6.10.2/
- pywinauto 0.6.9 (BSD), pywin32 312 (licencia PSF), comtypes 1.4.16 (MIT), six 1.17.0 (MIT).
- openpyxl 3.1.5 y et-xmlfile 2.0.0 (MIT).
- pytest 8.4.2 y sus dependencias, para las pruebas locales; licencias incluidas en los respectivos dist-info.

Los gráficos CAFI aportados por la usuaria se conservan como identidad visual de la aplicación de trabajo. La interfaz se inspira en la captura UEES; no declara certificación oficial de marca. El ZIP de Panacea se consultó como referencia y no se redistribuye.
