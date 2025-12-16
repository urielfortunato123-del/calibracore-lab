"""
CalibraCore Lab - Seed Equipment Data
Importa equipamentos baseado nas imagens enviadas pelo usuário
"""
import sys
import os
from datetime import date

# Add backend to path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(os.path.dirname(script_dir), 'backend')
sys.path.insert(0, backend_dir)

from app.database import SessionLocal, init_db
from app.models import Equipamento

# Equipment data from user's images
EQUIPAMENTOS = [
    # Balanças
    {"codigo": "Balança 0,01g", "categoria": "Balanças", "marca": "Marte", "certificado": "82512-25", "calibracao": "2025-08-18", "vencimento": "2026-08-18"},
    {"codigo": "Balança 0,001g", "categoria": "Balanças", "marca": "Shimadzu", "certificado": "82513-25", "calibracao": "2025-08-18", "vencimento": "2026-08-18"},
    {"codigo": "Balança 0,1g", "categoria": "Balanças", "marca": "Filizola", "certificado": "82514-25", "calibracao": "2025-08-18", "vencimento": "2026-08-18"},
    {"codigo": "Balança 50Kg", "categoria": "Balanças", "marca": "Filizola", "certificado": "82515-25", "calibracao": "2025-08-18", "vencimento": "2026-08-18"},
    
    # Termômetros
    {"codigo": "Termômetro Analógico", "categoria": "Termômetros", "marca": "Incoterm", "certificado": "1036/25", "calibracao": "2025-01-14", "vencimento": "2026-01-14"},
    {"codigo": "Termômetro Digital", "categoria": "Termômetros", "marca": "Incoterm", "certificado": "1037/25", "calibracao": "2025-01-14", "vencimento": "2026-01-14"},
    {"codigo": "Termômetro Mercúrio", "categoria": "Termômetros", "marca": "Incoterm", "certificado": "1038/25", "calibracao": "2025-01-14", "vencimento": "2026-01-14"},
    {"codigo": "Termômetro Infravermelho", "categoria": "Termômetros", "marca": "Minipa", "certificado": "1039/25", "calibracao": "2025-01-14", "vencimento": "2026-01-14"},
    
    # Peneiras (amostra das imagens)
    {"codigo": "Peneira #80", "categoria": "Peneiras", "marca": "Fort Minas", "certificado": "19631/25", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Peneira #3\"", "categoria": "Peneiras", "marca": "A bronzinox", "certificado": "19632/25", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Peneira #50", "categoria": "Peneiras", "marca": "Fort Minas", "certificado": "19633/25", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Peneira #200", "categoria": "Peneiras", "marca": "Fort Minas", "certificado": "19634/25", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Peneira #8", "categoria": "Peneiras", "marca": "Fort Minas", "certificado": "19629/25", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Peneira #1/2", "categoria": "Peneiras", "marca": "Fort Minas", "certificado": "19625/25", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Peneira #3", "categoria": "Peneiras", "marca": "Fort Minas", "certificado": "19626/25", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Peneira #4", "categoria": "Peneiras", "marca": "Fort Minas", "certificado": "19627/25", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Peneira #40", "categoria": "Peneiras", "marca": "Fort Minas", "certificado": "19628/25", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Peneira #3/4", "categoria": "Peneiras", "marca": "Fort Minas", "certificado": "19617/25", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Peneira #3/8", "categoria": "Peneiras", "marca": "Fort Minas", "certificado": "19618/25", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Peneira #10", "categoria": "Peneiras", "marca": "Fort Minas", "certificado": "19619/25", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Peneira #16", "categoria": "Peneiras", "marca": "Fort Minas", "certificado": "19621/25", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Peneira #14", "categoria": "Peneiras", "marca": "A bronzinox", "certificado": "19623/25", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Peneira #100", "categoria": "Peneiras", "marca": "Fort Minas", "certificado": "19613/25", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Peneira #18", "categoria": "Peneiras", "marca": "A bronzinox", "certificado": "Png-024-466693", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Peneira #1\"", "categoria": "Peneiras", "marca": "Fort Minas", "certificado": "Png-027-502484", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Peneira #5/8", "categoria": "Peneiras", "marca": "A bronzinox", "certificado": "Png-030-471038", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Peneira #30", "categoria": "Peneiras", "marca": "Fort Minas", "certificado": "Png-032-502795", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    
    # Provetas
    {"codigo": "Proveta Graduada 1000Ml", "categoria": "Provetas Graduadas", "marca": "Precision", "certificado": "20159/25", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Proveta Graduada 500Ml", "categoria": "Provetas Graduadas", "marca": "Precision", "certificado": "Pro-003", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Proveta Graduada 500Ml #2", "categoria": "Provetas Graduadas", "marca": "Precision", "certificado": "Pro-004", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Proveta Graduada 500Ml #3", "categoria": "Provetas Graduadas", "marca": "Nalgon", "certificado": "Pro-005", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Proveta Graduada 1000Ml #2", "categoria": "Provetas Graduadas", "marca": "Nalgon", "certificado": "Pro-006", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    
    # Beckers
    {"codigo": "Becker 50Ml", "categoria": "Beckers", "marca": "Fortest", "certificado": "Beq-001", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Becker 50Ml #2", "categoria": "Beckers", "marca": "Fortest", "certificado": "Beq-002", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Becker 500Ml", "categoria": "Beckers", "marca": "Precision", "certificado": "Beq-003", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Becker 500Ml #2", "categoria": "Beckers", "marca": "Precision", "certificado": "Beq-004", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Becker 250Ml", "categoria": "Beckers", "marca": "Precision", "certificado": "Beq-006", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Becker 1000Ml", "categoria": "Beckers", "marca": "Plena-Lab", "certificado": "Beq-010", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Becker 1000Ml #2", "categoria": "Beckers", "marca": "Plena-Lab", "certificado": "19596/25", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    
    # Picnômetros
    {"codigo": "Picnômetro 500Ml", "categoria": "Picnômetros", "marca": "-", "certificado": "19642/25", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Picnômetro 500Ml #2", "categoria": "Picnômetros", "marca": "-", "certificado": "20155/25", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Picnômetro 500Ml #3", "categoria": "Picnômetros", "marca": "-", "certificado": "19643/25", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    
    # Outros equipamentos
    {"codigo": "Ponto de Amolecimento", "categoria": "Outros", "marca": "Ionglass", "certificado": "-", "calibracao": "2025-05-04", "vencimento": "2026-05-04"},
    {"codigo": "Soxhlet", "categoria": "Outros", "marca": "Precision", "certificado": "Soxh-001", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Soxhlet #2", "categoria": "Outros", "marca": "Precision", "certificado": "Soxh-002", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Defectometro", "categoria": "Outros", "marca": "Easylux", "certificado": "Def-001", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Alambique de Femel", "categoria": "Outros", "marca": "Precision", "certificado": "Ala-001", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Pote termico", "categoria": "Outros", "marca": "Solotest", "certificado": "-", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Cilindro CBR (Completo)", "categoria": "Outros", "marca": "-", "certificado": "-", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Kit Slump", "categoria": "Outros", "marca": "-", "certificado": "-", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Molde Marshall", "categoria": "Outros", "marca": "-", "certificado": "-", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    {"codigo": "Faciadora de Concreto", "categoria": "Outros", "marca": "Fort Minas", "certificado": "-", "calibracao": "2025-11-01", "vencimento": "2026-11-01"},
    
    # Relógios Comparadores
    {"codigo": "Relógio Comparador", "categoria": "Relógios Comparadores", "marca": "Mitutoyo", "certificado": "RC-001", "calibracao": "2025-08-18", "vencimento": "2026-08-18"},
    {"codigo": "Relógio Comparador #2", "categoria": "Relógios Comparadores", "marca": "Mitutoyo", "certificado": "RC-002", "calibracao": "2025-08-18", "vencimento": "2026-08-18"},
    
    # Paquímetros
    {"codigo": "Paquímetro Digital", "categoria": "Paquímetros", "marca": "Mitutoyo", "certificado": "PAQ-001", "calibracao": "2025-08-18", "vencimento": "2026-08-18"},
]


def seed_equipamentos():
    """Insert equipment into database"""
    print("=" * 60)
    print("CalibraCore Lab - Seed de Equipamentos")
    print("=" * 60)
    
    init_db()
    db = SessionLocal()
    
    try:
        # Check if there are already equipment in the database
        existing = db.query(Equipamento).count()
        if existing > 0:
            print(f"Já existem {existing} equipamentos no banco.")
            print("Adicionando equipamentos que ainda não existem...")
        
        added = 0
        for eq in EQUIPAMENTOS:
            # Check if already exists
            exists = db.query(Equipamento).filter(
                Equipamento.codigo_interno == eq["codigo"]
            ).first()
            
            if exists:
                print(f"  [SKIP] {eq['codigo']} - já existe")
                continue
            
            equipamento = Equipamento(
                codigo_interno=eq["codigo"],
                descricao=eq["codigo"],
                categoria=eq["categoria"],
                marca=eq["marca"] if eq["marca"] != "-" else None,
                numero_certificado=eq["certificado"] if eq["certificado"] != "-" else None,
                laboratorio="Laboratório",
                data_ultima_calibracao=eq["calibracao"],
                data_vencimento=eq["vencimento"],
                ativo=True
            )
            db.add(equipamento)
            added += 1
            print(f"  [ADD] {eq['codigo']}")
        
        db.commit()
        print("-" * 60)
        print(f"Total: {added} equipamentos adicionados!")
        print("=" * 60)
        
    finally:
        db.close()


if __name__ == "__main__":
    seed_equipamentos()
