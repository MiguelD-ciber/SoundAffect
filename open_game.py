import subprocess
import os
import sys

# --- Configurações Ajustadas ---

# Caminho RELATIVO para a pasta que contém o love.exe
LUA_FOLDER = "lua" 

# Nome da pasta do seu jogo (dentro de 'lua')
GAME_FOLDER = "gametest"

# Caminho COMPLETO para o executável do LÖVE
LOVE_EXE_PATH = os.path.join(LUA_FOLDER, "love.exe")

# Caminho COMPLETO para a pasta do jogo
GAME_PATH = os.path.join(LUA_FOLDER, GAME_FOLDER)

# --- Lógica de Execução ---

def run_love_game():
    """Tenta executar a pasta do jogo usando o executável do LÖVE nos caminhos definidos."""
    
    # 1. Verifica se a pasta do jogo (lua/gametest) existe
    if not os.path.isdir(GAME_PATH):
        print(f"❌ Erro: A pasta do jogo '{GAME_PATH}' não foi encontrada.")
        print("Certifique-se de que a pasta 'gametest' está dentro da pasta 'lua'.")
        sys.exit(1)
        
    # 2. Verifica se o executável do love.exe existe
    if not os.path.isfile(LOVE_EXE_PATH):
        print(f"\n❌ Erro: O executável do LÖVE ('{LOVE_EXE_PATH}') não foi encontrado.")
        print("Certifique-se de que 'love.exe' está dentro da pasta 'lua'.")
        sys.exit(1)

    try:
        # Comando a ser executado: lua/love.exe lua/gametest
        command = [LOVE_EXE_PATH, GAME_PATH]
        
        print(f"▶️ Tentando executar o comando: {' '.join(command)}")
        
        # Executa o comando
        subprocess.run(command, check=True)
        
        print("\n✅ Jogo encerrado com sucesso.")
        
    except subprocess.CalledProcessError as e:
        print(f"\n⚠️ O LÖVE retornou um erro: {e}")
        
    except Exception as e:
        print(f"\n❌ Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    run_love_game()