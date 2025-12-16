"""
CalibraCore Lab - Simple Seed Equipment Script
"""
import sys
import os
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

from app.database import SessionLocal, init_db
from app.models import Equipamento

init_db()
db = SessionLocal()

equipamentos = [
    ("Balança 0,01g", "Balanças", "Marte", "82512-25", date(2025, 8, 18), date(2026, 8, 18)),
    ("Balança 0,001g", "Balanças", "Shimadzu", "82513-25", date(2025, 8, 18), date(2026, 8, 18)),
    ("Balança 0,1g", "Balanças", "Filizola", "82514-25", date(2025, 8, 18), date(2026, 8, 18)),
    ("Balança 50Kg", "Balanças", "Filizola", "82515-25", date(2025, 8, 18), date(2026, 8, 18)),
    ("Termômetro Analógico", "Termômetros", "Incoterm", "1036/25", date(2025, 1, 14), date(2026, 1, 14)),
    ("Termômetro Digital", "Termômetros", "Incoterm", "1037/25", date(2025, 1, 14), date(2026, 1, 14)),
    ("Termômetro Mercúrio", "Termômetros", "Incoterm", "1038/25", date(2025, 1, 14), date(2026, 1, 14)),
    ("Termômetro Infravermelho", "Termômetros", "Minipa", "1039/25", date(2025, 1, 14), date(2026, 1, 14)),
    ("Peneira #80", "Peneiras", "Fort Minas", "19631/25", date(2025, 11, 1), date(2026, 11, 1)),
    ("Peneira #3pol", "Peneiras", "A bronzinox", "19632/25", date(2025, 11, 1), date(2026, 11, 1)),
    ("Peneira #50", "Peneiras", "Fort Minas", "19633/25", date(2025, 11, 1), date(2026, 11, 1)),
    ("Peneira #200", "Peneiras", "Fort Minas", "19634/25", date(2025, 11, 1), date(2026, 11, 1)),
    ("Peneira #8", "Peneiras", "Fort Minas", "19629/25", date(2025, 11, 1), date(2026, 11, 1)),
    ("Peneira #1/2", "Peneiras", "Fort Minas", "19625/25", date(2025, 11, 1), date(2026, 11, 1)),
    ("Peneira #3", "Peneiras", "Fort Minas", "19626/25", date(2025, 11, 1), date(2026, 11, 1)),
    ("Peneira #4", "Peneiras", "Fort Minas", "19627/25", date(2025, 11, 1), date(2026, 11, 1)),
    ("Peneira #40", "Peneiras", "Fort Minas", "19628/25", date(2025, 11, 1), date(2026, 11, 1)),
    ("Peneira #3/4", "Peneiras", "Fort Minas", "19617/25", date(2025, 11, 1), date(2026, 11, 1)),
    ("Peneira #3/8", "Peneiras", "Fort Minas", "19618/25", date(2025, 11, 1), date(2026, 11, 1)),
    ("Peneira #10", "Peneiras", "Fort Minas", "19619/25", date(2025, 11, 1), date(2026, 11, 1)),
    ("Peneira #16", "Peneiras", "Fort Minas", "19621/25", date(2025, 11, 1), date(2026, 11, 1)),
    ("Peneira #14", "Peneiras", "A bronzinox", "19623/25", date(2025, 11, 1), date(2026, 11, 1)),
    ("Peneira #100", "Peneiras", "Fort Minas", "19613/25", date(2025, 11, 1), date(2026, 11, 1)),
    ("Peneira #18", "Peneiras", "A bronzinox", "Png-024", date(2025, 11, 1), date(2026, 11, 1)),
    ("Peneira #1pol", "Peneiras", "Fort Minas", "Png-027", date(2025, 11, 1), date(2026, 11, 1)),
    ("Peneira #5/8", "Peneiras", "A bronzinox", "Png-030", date(2025, 11, 1), date(2026, 11, 1)),
    ("Peneira #30", "Peneiras", "Fort Minas", "Png-032", date(2025, 11, 1), date(2026, 11, 1)),
    ("Proveta Graduada 1000Ml", "Provetas", "Precision", "20159/25", date(2025, 11, 1), date(2026, 11, 1)),
    ("Proveta Graduada 500Ml", "Provetas", "Precision", "Pro-003", date(2025, 11, 1), date(2026, 11, 1)),
    ("Proveta Graduada 500Ml #2", "Provetas", "Nalgon", "Pro-005", date(2025, 11, 1), date(2026, 11, 1)),
    ("Proveta Graduada 1000Ml #2", "Provetas", "Nalgon", "Pro-006", date(2025, 11, 1), date(2026, 11, 1)),
    ("Becker 50Ml", "Beckers", "Fortest", "Beq-001", date(2025, 11, 1), date(2026, 11, 1)),
    ("Becker 50Ml #2", "Beckers", "Fortest", "Beq-002", date(2025, 11, 1), date(2026, 11, 1)),
    ("Becker 500Ml", "Beckers", "Precision", "Beq-003", date(2025, 11, 1), date(2026, 11, 1)),
    ("Becker 250Ml", "Beckers", "Precision", "Beq-006", date(2025, 11, 1), date(2026, 11, 1)),
    ("Becker 1000Ml", "Beckers", "Plena-Lab", "Beq-010", date(2025, 11, 1), date(2026, 11, 1)),
    ("Picnometro 500Ml", "Picnometros", None, "19642/25", date(2025, 11, 1), date(2026, 11, 1)),
    ("Picnometro 500Ml #2", "Picnometros", None, "20155/25", date(2025, 11, 1), date(2026, 11, 1)),
    ("Picnometro 500Ml #3", "Picnometros", None, "19643/25", date(2025, 11, 1), date(2026, 11, 1)),
    ("Ponto de Amolecimento", "Outros", "Ionglass", None, date(2025, 5, 4), date(2026, 5, 4)),
    ("Relogio Comparador", "Relogios Comparadores", "Mitutoyo", "RC-001", date(2025, 8, 18), date(2026, 8, 18)),
    ("Paquimetro Digital", "Paquimetros", "Mitutoyo", "PAQ-001", date(2025, 8, 18), date(2026, 8, 18)),
]

print("Importando equipamentos...")
count = 0
for eq in equipamentos:
    novo = Equipamento(
        codigo_interno=eq[0],
        descricao=eq[0],
        categoria=eq[1],
        marca=eq[2],
        numero_certificado=eq[3],
        laboratorio="Laboratorio",
        data_ultima_calibracao=eq[4],
        data_vencimento=eq[5],
        ativo=True
    )
    db.add(novo)
    count += 1
    print(f"  + {eq[0]}")

db.commit()
db.close()
print(f"\nTotal: {count} equipamentos importados!")
