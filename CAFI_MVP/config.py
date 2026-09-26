from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VERSION = '0.4.0'

@dataclass(frozen=True)
class Rules:
    # Parámetro de diagnóstico; no constituye regla institucional aprobada.
    code_length: int = 10
    sheet: str = 'Hoja 1'

    def __post_init__(self):
        if not 1 <= self.code_length <= 30:
            raise ValueError('La longitud debe estar entre 1 y 30.')
        if not self.sheet.strip():
            raise ValueError('Indique la hoja exacta.')
