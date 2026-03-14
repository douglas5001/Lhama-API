import asyncio
from fastapi import APIRouter, Request, HTTPException, status
from app.database.connections.redis_connection import get_redis
from app.core.logger import app_logger

router = APIRouter(prefix="/test-redis", tags=["Testes Redis"])

# --- 1. Sistema de Cache Clássico ---
@router.get("/cache")
async def test_redis_cache():
    """ Simula uma consulta lenta no Postgres salvando o valor temporariamente. """
    redis_client = get_redis()
    val = await redis_client.get('relatorio_vendas_do_mes')
    
    if val:
        return {"data": val, "source": "redis_cache", "message": "Veio em 0.005s!"}
    
    await asyncio.sleep(5)  # 5s simulando gargalo no BD
    resultado_demorado = "Faturamento Total: R$ 500.000,00"
    await redis_client.setex('relatorio_vendas_do_mes', 30, resultado_demorado) # Expira em 30s
    return {"data": resultado_demorado, "source": "postgres_simulado", "message": "Demorou 5 segundos"}

# --- 2. Rate Limiting Avançado ---
@router.get("/rate-limit")
async def test_redis_rate_limit(request: Request):
    """ Impede que o mesmo IP abuse dessa rota mais de 5 vezes a cada minuto. """
    redis_client = get_redis()
    client_ip = request.client.host
    rate_limit_key = f"rate_limit:{client_ip}"
    
    # Incrementa +1 pro IP atual
    tentativas = await redis_client.incr(rate_limit_key)
    
    if tentativas == 1:
        # Se for o primeiro request do minuto, liga o timer de 60 segundos
        await redis_client.expire(rate_limit_key, 60)
        
    if tentativas > 5:
        raise HTTPException(status_code=429, detail="Too Many Requests! Você estourou seu limite do minuto.")
        
    return {"message": "Acesso Liberado!", "tentativas_usadas": tentativas, "limite_maximo": 5}

# --- 3. Fila de Tarefas Assíncronas (Messageria) ---
@router.post("/queue")
async def test_redis_queue_producer(tarefa: str):
    """ Simula o FastAPI colocando um trabalho de PDF pesadíssimo na fila. """
    redis_client = get_redis()
    
    # Adiciona a tarefa na esquerda (LPUSH) da lista 'processamento_fila'
    await redis_client.lpush("minhas_tarefas_pendentes", tarefa)
    
    fila_tamanho = await redis_client.llen("minhas_tarefas_pendentes")
    return {"message": f"A tarefa '{tarefa}' foi posta na fila do Redis!", "tarefas_na_fila": fila_tamanho}

@router.get("/queue/worker")
async def test_redis_queue_consumer():
    """ Simula o Servidor Worker lendo a mensagem do Redis depois para não travar a API """
    redis_client = get_redis()
    
    # Pega (RPOP) a tarefa mais antiga da lista
    tarefa = await redis_client.rpop("minhas_tarefas_pendentes")
    if not tarefa:
        return {"message": "Nenhuma fila para processar no momento!"}
        
    return {"message": f"Executando CPU 100% na Tarefa: {tarefa}"}

# --- 4. Controle de Sessão (DenyList/Loggout) ---
@router.post("/session/revoke")
async def test_redis_revoke_token(token: str):
    """ Coloca o token JWT na DenyList da Memória para ninguém conseguir usar mais. """
    redis_client = get_redis()
    # Adiciona o Token bloqueado por 15 minutos (Tempo do nosso AccessToken)
    await redis_client.setex(f"denylist:{token}", 15 * 60, "revogado")
    return {"message": f"Token JWT revogado instantâneamente."}

@router.get("/session/check")
async def test_redis_check_token(token: str):
    """ Simula a leitura que nosso get_current_user faria a cada rota protegida """
    redis_client = get_redis()
    is_blocked = await redis_client.get(f"denylist:{token}")
    
    if is_blocked:
        raise HTTPException(status_code=401, detail="Seu Token foi revogado antes do prazo (Usuário deu Loggout).")
    return {"message": "Acesso autorizado, token ainda é seguro."}

# --- 5. Leaderboards (Rankings em Tempo Real) ---
@router.post("/leaderboard")
async def test_redis_add_pontuacao(jogador: str, pontos: int):
    """ Insere um score de um jogador rankeando na nuvem. """
    redis_client = get_redis()
    # ZADD (Key, Mapping {jogador: pontos})
    await redis_client.zadd("placar_do_jogo", {jogador: pontos})
    return {"message": f"{jogador} salvou os seus {pontos} pontos no Placar em 0.003ms"}

@router.get("/leaderboard")
async def test_redis_get_top3():
    """ Retorna o placar global instantaneamente sem envolver SQL/Postgres. """
    redis_client = get_redis()
    # ZREVRANGE: Do maior pro menor valor (0 ao 2 = Top 3). Withscores=True para trazer os pontos tbm
    top3 = await redis_client.zrevrange("placar_do_jogo", 0, 2, withscores=True)
    
    ranking = [{"posicao": i+1, "jogador": p[0], "pontos": p[1]} for i, p in enumerate(top3)]
    return {"top_3_jogadores": ranking}
