import os
import sys
from loguru import logger
from app.core.config import settings

# 1. Obter o diretório raiz do projeto (onde fica a pasta 'storage')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_PATH = os.path.join(BASE_DIR, "storage", "logs", "api_{time:YYYY-MM-DD}.log")

# 2. Configurar a Loguru
def setup_logger():
    # Remove a configuração padrão da Loguru (para podermos recriar do zero)
    logger.remove()

    # Formato padrão da mensagem
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    # 3. Adicionar saída para o Terminal (Console)
    logger.add(sys.stdout, format=log_format, level="INFO")

    # 4. Adicionar saída para Arquivo Rotativo na pasta storage/logs
    # Cria um novo arquivo todos os dias, e apaga os que tiverem mais de 30 dias.
    logger.add(
        LOG_PATH,
        format=log_format,
        level="INFO",
        rotation="00:00",       # Rotaciona o arquivo meia noite
        retention="30 days",    # Mantém logs por 30 dias
        compression="zip",      # Comprime logs antigos para economizar espaço
        enqueue=True            # Thread-safe para FastApi
    )

    return logger

# Inicializa o logger e o exporta para a aplicação toda usar
app_logger = setup_logger()
