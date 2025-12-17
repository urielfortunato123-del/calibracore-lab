"""
CalibraCore Lab - Script de Inicialização de Usuários
Este script adiciona os usuários iniciais ao sistema.
ATENÇÃO: Este arquivo contém credenciais sensíveis. Não deve ser versionado no GitHub público.
"""
from app.database import SessionLocal, engine, Base
from app.models import Usuario, UserRole
from app.auth import get_password_hash

# Criar todas as tabelas
Base.metadata.create_all(bind=engine)

# Usuários iniciais
USUARIOS_INICIAIS = [
    {
        "nome": "Letícia Silveira",
        "email": "leticia.silveira@motiva.com.br",
        "senha": "MotivaLeti9",
        "papel": UserRole.ADMIN,
        "laboratorio": "Motiva"
    },
    {
        "nome": "André Pereira",
        "email": "andre.pereira@motiva.com.br",
        "senha": "Andre@Motiva9",
        "papel": UserRole.ADMIN,
        "laboratorio": "Motiva"
    },
    {
        "nome": "Alan Silva",
        "email": "alan.silva@nucleoengenharia.com.br",
        "senha": "NucleoAlan88",
        "papel": UserRole.ADMIN,
        "laboratorio": "Núcleo Engenharia"
    },
    {
        "nome": "Fabiano Silva",
        "email": "fabiano.silva@nucleoengenharia.com.br",
        "senha": "Fabiano@Eng9",
        "papel": UserRole.ADMIN,
        "laboratorio": "Núcleo Engenharia"
    }
]


def init_users():
    """Inicializa os usuários no banco de dados"""
    db = SessionLocal()
    try:
        print("🔧 Iniciando criação de usuários...")
        
        for user_data in USUARIOS_INICIAIS:
            # Verificar se o usuário já existe
            existing_user = db.query(Usuario).filter(Usuario.email == user_data["email"]).first()
            
            if existing_user:
                print(f"⚠️  Usuário {user_data['email']} já existe. Pulando...")
                continue
            
            # Criar novo usuário
            novo_usuario = Usuario(
                nome=user_data["nome"],
                email=user_data["email"],
                senha_hash=get_password_hash(user_data["senha"]),
                papel=user_data["papel"],
                laboratorio=user_data["laboratorio"],
                ativo=True
            )
            
            db.add(novo_usuario)
            print(f"✅ Usuário criado: {user_data['nome']} ({user_data['email']})")
        
        db.commit()
        print("\n🎉 Todos os usuários foram criados com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro ao criar usuários: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_users()
