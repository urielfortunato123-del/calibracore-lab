"""
CalibraCore Lab - FastAPI Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import logging

from app.config import settings
from app.database import init_db, SessionLocal
from app.models import Usuario, UserRole
from app.auth import get_password_hash
from app.routers import auth, equipamentos, usuarios, dashboard, alertas, audit

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Sistema Inteligente de Controle de Vencimento de Calibração de Equipamentos",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database and create default admin user"""
    logger.info(f"Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Initialize database
    init_db()
    logger.info("Banco de dados inicializado")
    
    # Create default admin user if not exists
    db = SessionLocal()
    try:
        # Default Admin
        admin = db.query(Usuario).filter(Usuario.email == settings.ADMIN_EMAIL).first()
        if not admin:
            admin = Usuario(
                nome=settings.ADMIN_NAME,
                email=settings.ADMIN_EMAIL,
                senha_hash=get_password_hash(settings.ADMIN_PASSWORD),
                papel=UserRole.ADMIN,
                ativo=True
            )
            db.add(admin)
            db.commit()
            logger.info(f"Usuário admin criado: {settings.ADMIN_EMAIL}")
        else:
            logger.info("Usuário admin já existe")

        # Additional Users
        additional_users = [
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

        for user_data in additional_users:
            existing_user = db.query(Usuario).filter(Usuario.email == user_data["email"]).first()
            if not existing_user:
                new_user = Usuario(
                    nome=user_data["nome"],
                    email=user_data["email"],
                    senha_hash=get_password_hash(user_data["senha"]),
                    papel=user_data["papel"],
                    laboratorio=user_data["laboratorio"],
                    ativo=True
                )
                db.add(new_user)
                logger.info(f"Usuário criado: {user_data['email']}")
            else:
                logger.info(f"Usuário já existe: {user_data['email']}")
        
        db.commit()
    except Exception as e:
        logger.error(f"Erro ao inicializar usuários: {e}")
        db.rollback()
    finally:
        db.close()


# Include routers
app.include_router(auth.router)
app.include_router(equipamentos.router)
app.include_router(usuarios.router)
app.include_router(dashboard.router)
app.include_router(alertas.router)
app.include_router(audit.router)


# Serve frontend static files
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")

if os.path.exists(frontend_path):
    app.mount("/css", StaticFiles(directory=os.path.join(frontend_path, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(frontend_path, "js")), name="js")
    app.mount("/img", StaticFiles(directory=os.path.join(frontend_path, "img")), name="img")
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")


@app.api_route("/", methods=["GET", "HEAD"])
async def serve_index():
    """Serve login page"""
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": f"Bem-vindo ao {settings.APP_NAME}!", "docs": "/api/docs"}


@app.api_route("/dashboard", methods=["GET", "HEAD"])
async def serve_dashboard():
    """Serve dashboard page"""
    dashboard_path = os.path.join(frontend_path, "dashboard.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    return {"message": "Dashboard", "error": "Frontend not found"}


@app.get("/equipamentos")
async def serve_equipamentos():
    """Serve equipment management page"""
    eq_path = os.path.join(frontend_path, "equipamentos.html")
    if os.path.exists(eq_path):
        return FileResponse(eq_path)
    return {"message": "Equipamentos", "error": "Frontend not found"}


@app.get("/usuarios")
async def serve_usuarios():
    """Serve users management page"""
    users_path = os.path.join(frontend_path, "usuarios.html")
    if os.path.exists(users_path):
        return FileResponse(users_path)
    return {"message": "Usuários", "error": "Frontend not found"}


@app.get("/audit.html")
async def serve_audit():
    """Serve audit page"""
    audit_path = os.path.join(frontend_path, "audit.html")
    if os.path.exists(audit_path):
        return FileResponse(audit_path)
    return {"message": "Audit", "error": "Frontend not found"}


@app.api_route("/health", methods=["GET", "HEAD"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "app": settings.APP_NAME, "version": settings.APP_VERSION}
