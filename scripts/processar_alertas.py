"""
CalibraCore Lab - Script de Processamento de Alertas
Execute este script diariamente via Agendador de Tarefas do Windows

Para configurar no Agendador:
1. Abra "Agendador de Tarefas" no Windows
2. Criar Tarefa Básica
3. Nome: "CalibraCore Lab - Alertas Diários"
4. Trigger: Diariamente às 08:00
5. Ação: Iniciar um programa
6. Programa: python
7. Argumentos: "C:\\...\\CalibraCore Lab\\scripts\\processar_alertas.py"
8. Iniciar em: "C:\\...\\CalibraCore Lab\\scripts"
"""
import sys
import os
import asyncio
import logging
from datetime import datetime

# Add backend to path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(os.path.dirname(script_dir), 'backend')
sys.path.insert(0, backend_dir)

# Configure logging
log_file = os.path.join(script_dir, 'alertas.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def main():
    """Process calibration alerts"""
    logger.info("=" * 60)
    logger.info("Iniciando processamento de alertas - CalibraCore Lab")
    logger.info(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    logger.info("=" * 60)
    
    try:
        # Import after path is set
        from app.database import SessionLocal, init_db
        from app.services.alerta_service import process_alerts
        
        # Initialize database
        init_db()
        
        # Create session
        db = SessionLocal()
        
        try:
            # Process alerts
            result = await process_alerts(db)
            
            logger.info("-" * 60)
            logger.info("RESULTADO DO PROCESSAMENTO:")
            logger.info(f"  Equipamentos processados: {result['processados']}")
            logger.info(f"  Alertas enviados: {result['alertas_enviados']}")
            logger.info(f"  Erros: {result['erros']}")
            
            if result['detalhes']:
                logger.info("-" * 60)
                logger.info("DETALHES:")
                for detalhe in result['detalhes']:
                    logger.info(f"  - {detalhe['equipamento']}: {detalhe['status']} ({detalhe['tipo_alerta']})")
            
            logger.info("-" * 60)
            logger.info("Processamento concluído com sucesso!")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Erro no processamento: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
