"""Ensamblaje reproducible del Python embebido y wheels Windows ya descargados.

No mezcla código de la aplicación con el intérprete. Mantiene la versión anterior
en build/ si se reconstruye, sin tocar data/ ni los documentos de origen.
"""
import hashlib
import json
import shutil
import time
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
PYTHON_SHA256 = 'd1f04d990aee1253d8569e8e5104e30fa9f5fa830899f14843448872d936a2cf'
LIBRARIES = {'openpyxl', 'et_xmlfile', 'pywinauto', 'pywin32', 'comtypes', 'six'}


def install_wheel(wheel, destination):
    with zipfile.ZipFile(wheel) as archive:
        for info in archive.infolist():
            path = PurePosixPath(info.filename)
            if path.is_absolute() or '..' in path.parts:
                raise ValueError('Ruta inválida en wheel')
            if info.is_dir():
                continue
            parts = path.parts
            if parts[0].endswith('.data'):
                if parts[1] not in ('purelib', 'platlib'):
                    continue
                parts = parts[2:]
            target = destination.joinpath(*parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.read(info))


def main():
    source = ROOT / 'build' / 'python-3.13.15-embed-amd64.zip'
    if hashlib.sha256(source.read_bytes()).hexdigest() != PYTHON_SHA256:
        raise ValueError('El intérprete Windows no coincide con el hash esperado.')
    stage = ROOT / 'build' / ('native_runtime_' + str(time.time_ns()))
    stage.mkdir()
    with zipfile.ZipFile(source) as archive:
        archive.extractall(stage)
    wheels = [p for p in (ROOT / 'wheelhouse-desktop').glob('*.whl') if p.name.split('-')[0] in LIBRARIES]
    wheels += list((ROOT / 'build' / 'native-wheels').glob('*.whl'))
    names = {p.name.split('-')[0].lower() for p in wheels}
    if not LIBRARIES | {'pyside6_essentials', 'shiboken6', 'pytest', 'colorama'} <= names:
        raise ValueError('Faltan dependencias en los wheels descargados.')
    for wheel in sorted(wheels):
        install_wheel(wheel, stage / 'Lib' / 'site-packages')
    (stage / 'python313._pth').write_text('python313.zip\n.\n..\nLib/site-packages\nimport site\n', encoding='utf-8')
    manifest = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [source] + wheels}
    (stage / 'COMPONENTES_SHA256.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    destination = ROOT / 'runtime'
    if destination.exists():
        destination.rename(ROOT / 'build' / ('runtime_anterior_' + str(time.time_ns())))
    stage.rename(destination)
    print(f'Runtime Windows armado con {len(wheels)} wheels. Prueba de ejecución Windows pendiente.')


if __name__ == '__main__':
    main()
