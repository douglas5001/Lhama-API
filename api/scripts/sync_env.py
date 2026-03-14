import os
import sys

def sync_env():
    """Reads .env and generates .env.example with empty values."""
    # Defina os caminhos para .env e .env.example
    # Usa o diretório do script para encontrar o .env na raiz (diretório acima)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    api_dir = os.path.dirname(script_dir)
    env_path = os.path.join(api_dir, ".env")
    example_path = os.path.join(api_dir, ".env.example")
    
    if not os.path.exists(env_path):
        print("⚠️ O arquivo .env não existe. Nada a sincronizar.")
        sys.exit(0)

    with open(env_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    example_lines = []
    for line in lines:
        line = line.strip()
        # Se a linha estiver vazia ou for um comentário, mantém como está
        if not line or line.startswith("#"):
            example_lines.append(line + "\n")
            continue
            
        # Se for uma variável (possui o sinal de '='), limpa o valor
        if "=" in line:
            key = line.split("=", 1)[0]
            example_lines.append(f"{key}=\n")
        else:
            example_lines.append(line + "\n")

    with open(example_path, "w", encoding="utf-8") as f:
        f.writelines(example_lines)

    print(f"✅ Arquivo {example_path} atualizado com sucesso a partir de {env_path}.")

if __name__ == "__main__":
    sync_env()
