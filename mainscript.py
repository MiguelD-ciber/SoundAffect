# main.py

import subprocess
import pygame
import os
import shutil
import json
import random
import sys
from datetime import datetime

# ------------------- Configurações / Paths -------------------
SAVE_FOLDER_NAME = "SavesFolder"
BASE_WORLD_FOLDER = "BaseWorldDirectores"
STATISTICS_FILE_PATH = os.path.join("Player", "statistics.json")
CLASSES_FILE_NAME = "classes.json"
SUCCESS_SOUND_FILE = "save_success.wav"
SEED_FILE_NAME = "seed.json"
CLASS_IMAGE_FOLDER = "classes" # Pasta onde estão as imagens das classes

# Recursos de mídia (podem faltar; temos fallback)
BACKGROUND_IMAGE_FILE = "menu_bg.png"
MUSIC_FILE = "menu_music.wav"
LOGO_FILE = "game_logo.png"
### ATUALIZAÇÃO: Adiciona o arquivo de som para hover (presumindo que exista)
HOVER_SOUND_FILE = "bubble_pop.mp3" 


# ------------------- Visual -------------------
TELA_LARGURA = 1920
TELA_ALTURA = 1080
COR_PRETA = (0, 0, 0)
COR_BRANCA = (255, 255, 255)
COR_DESTAQUE = (0, 148, 255)
COR_INPUT_BOX = (50, 50, 50)
COR_INPUT_BOX_ATIVA = (80, 80, 80)
COR_BOTAO = (40, 40, 40)
### ATUALIZAÇÃO: Nova cor roxa para a borda
COR_ROXA_HOVER = (150, 0, 255) 

GAME_VERSION = "Game Version 1.0.4"


UPDATE_LOG_TITLE = "Update Log Title"
UPDATE_LOG_TEXT = [
    "text text text text text text text text text text text text text",
    "text text text text text text text text text text text text text",
    "text text text text text text text text text text text text text",
    "text text text text text text text text text text text text text",
    "text text text text text text text text text text text text text",
    "text text text text text text text text text text text text text",
    "text text text text text text text text text text text text text",
    "text text text text text text text text text text text text text",
    "text text text text text text text text text text text text text",
    "text text text text text text text text text text text text text",
    "text text text text text text text text text text text text text",
    "text text text text text text text text text text text text text",
]


# ------------------- Estado Global -------------------
current_state = "MENU_PRINCIPAL"
player_responses = {
    "save_name": "",
    "char_name": "",
    "class_choice": "", # Índice da Classe (ex: 1 para Humano)
    "subclass_choice": "" # Índice da Subclasse/Tier dentro da Classe (ex: 2 para Guerreiro Adaptável)
}
class_data = None
current_active_input = "save_name"
class_images = {}

### ATUALIZAÇÃO: Variáveis globais para o som de hover e o controle de toque
hover_sound = None
# Dicionário para rastrear o estado de hover dos botões
# Chave: ID do botão (Rect), Valor: Booleano (True se já tocou o som)
hover_state_tracker = {} 


# ------------------- Utilitários -------------------

def generate_64bit_seed():
    return random.getrandbits(64)

def play_save_sound():
    try:
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except Exception:
                return
        if os.path.exists(SUCCESS_SOUND_FILE):
            sound = pygame.mixer.Sound(SUCCESS_SOUND_FILE)
            sound.play()
    except Exception:
        pass

### ATUALIZAÇÃO: Nova função para tocar o som de hover
def play_hover_sound():
    """Toca o som de hover se ele tiver sido carregado."""
    global hover_sound
    if hover_sound:
        # Usa um canal para não interromper outros sons (como a música)
        try:
            pygame.mixer.Channel(0).play(hover_sound)
        except Exception:
            pass

def load_music_and_play(file_path):
    """Carrega e toca a música em loop."""
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            
        if os.path.exists(file_path):
            pygame.mixer.music.load(file_path)
            # O parâmetro -1 faz a música tocar em loop infinito
            pygame.mixer.music.play(-1) 
            print(f"🎵 Música '{file_path}' iniciada em loop.")
        else:
            print(f"❌ Erro: Arquivo de música '{file_path}' não encontrado.")
    except Exception as e:
        print(f"❌ Erro ao inicializar ou tocar música: {e}")

def load_classes():
    """Carrega classes.json com tratamento de erro e retorna o dict."""
    global class_data
    try:
        with open(CLASSES_FILE_NAME, 'r', encoding='utf-8') as f:
            data = json.load(f)
            class_data = data
            # validações mínimas
            if not isinstance(class_data, dict) or "Classes" not in class_data:
                raise ValueError("Formato inválido do classes.json: 'Classes' ausente.")
            return class_data
    except Exception as e:
        print(f"ERRO ao carregar {CLASSES_FILE_NAME}: {e}")
        # fallback seguro (Nova Estrutura)
        fallback = {
            "Classes": [
                {
                    "Classe": "Guerreiro", 
                    "Subclasse": [{"Nome": "Guerreiro", "Descricao": "Classe base de combate."}]
                }
            ],
            "MagiasUniversais": {}
        }
        class_data = fallback
        return class_data

def load_class_images():
    """Carrega as imagens das classes para o cache global."""
    global class_images
    class_images = {}
    IMAGE_SIZE = (200, 200)
    
    if not os.path.exists(CLASS_IMAGE_FOLDER):
        print(f"Aviso: Pasta de imagens de classes '{CLASS_IMAGE_FOLDER}' não encontrada.")
        return

    # Carrega imagens de classes base e subclasses (que agora estão aninhadas)
    if class_data and "Classes" in class_data:
        # Percorre Classes Base
        for class_info in class_data["Classes"]:
            class_base_name = class_info.get("Classe")
            if class_base_name:
                
                # Tenta carregar a imagem da Classe Base
                class_names_to_check = [class_base_name]
                
                # Adiciona todos os nomes de Subclasse (Tiers) para carregar
                for sub_info in class_info.get("Subclasse", []):
                    sub_name = sub_info.get("Nome")
                    if sub_name and sub_name != class_base_name:
                        class_names_to_check.append(sub_name)

                for name in class_names_to_check:
                    # Tenta carregar .png e .jpeg, priorizando o .png
                    img_path = os.path.join(CLASS_IMAGE_FOLDER, f"{name}.png")
                    if not os.path.exists(img_path):
                        img_path = os.path.join(CLASS_IMAGE_FOLDER, f"{name}.jpeg")
                    
                    if os.path.exists(img_path) and name not in class_images:
                        try:
                            img = pygame.image.load(img_path).convert_alpha()
                            class_images[name] = pygame.transform.scale(img, IMAGE_SIZE)
                        except Exception as e:
                            print(f"Aviso: Não foi possível carregar ou escalar imagem para {name}: {e}")
                    elif name not in class_images:
                        # print(f"Aviso: Imagem para a classe/subclasse '{name}' não encontrada.") # Comentei para evitar spam
                        pass


def update_seed_file(save_name, seed):
    save_path = os.path.join(SAVE_FOLDER_NAME, save_name)
    seed_file_path = os.path.join(save_path, SEED_FILE_NAME)

    data = {}
    try:
        if os.path.exists(seed_file_path):
            with open(seed_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
    except Exception:
        data = {}

    data['seed'] = str(seed)

    try:
        os.makedirs(os.path.dirname(seed_file_path), exist_ok=True)
        with open(seed_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar seed.json: {e}")
        return False

def update_statistics_file(save_name, player_data):
    """
    Atualiza statistics.json com dados básicos do jogador.
    Usa ClasseBase e Subclasse/Tier para o registro.
    """
    save_path = os.path.join(SAVE_FOLDER_NAME, save_name)
    stats_file_path = os.path.join(save_path, STATISTICS_FILE_PATH)

    base_stats = {"Velocidade": 10, "Hp": 100, "Stamina": 50, "Level": 1}

    player_data_keys = {
        "Nome": player_data.get("Nome", "SemNome"),
        "ClasseBase": player_data.get("ClasseBase", "Indefinida"),
        # Subclasse aqui se refere ao Tier/Variação escolhida
        "Subclasse": player_data.get("Subclasse", "Tier Base"), 
        "ClasseFinal": player_data.get("Subclasse", player_data.get("ClasseBase", "Indefinida"))
    }
    final_stats = {**player_data_keys, **base_stats}

    try:
        os.makedirs(os.path.dirname(stats_file_path), exist_ok=True)
        with open(stats_file_path, 'w', encoding='utf-8') as f:
            json.dump(final_stats, f, indent=4, ensure_ascii=False)
        print("📊 Estatísticas salvas com sucesso.")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar statistics.json: {e}")
        return False

def create_save_directory(save_name, player_data):
    destination_path = os.path.join(SAVE_FOLDER_NAME, save_name)
    source_path = BASE_WORLD_FOLDER

    try:
        if not os.path.exists(source_path):
            print(f"ERRO: Pasta base '{source_path}' não encontrada. Impossível criar save.")
            return False
        
        if os.path.exists(destination_path):
            print(f"ERRO: Já existe um save com o nome '{save_name}'.")
            return False

        shutil.copytree(source_path, destination_path, dirs_exist_ok=True)

        new_seed = generate_64bit_seed()
        seed_updated = update_seed_file(save_name, new_seed)
        stats_updated = update_statistics_file(save_name, player_data)

        if seed_updated and stats_updated:
            print(f"\n🎉 Personagem '{player_data['Nome']}' criado com sucesso!")
            play_save_sound()
            return True
        else:
            return False

    except Exception as e:
        print(f"ERRO FATAL NA CRIAÇÃO DE SAVE: {e}")
        return False

# ------------------- UI Helpers -------------------

def draw_button(tela, fonte, rect, text, mouse_pos):
    global hover_state_tracker
    
    is_hovered = rect.collidepoint(mouse_pos)
    
    # ATUALIZAÇÃO CRÍTICA: Cria uma tupla hashable (imutável) a partir do Rect.
    # Usaremos (x, y, largura, altura) como ID único.
    button_id = rect.topleft + rect.size 
    
    if is_hovered:
        if button_id not in hover_state_tracker or not hover_state_tracker[button_id]:
            # Se não está no tracker ou o estado é False (acabou de entrar)
            play_hover_sound()
            hover_state_tracker[button_id] = True # Marca como True (som já tocou)
    else:
        # Quando o mouse sai, resetamos o estado do botão
        if button_id in hover_state_tracker and hover_state_tracker[button_id]:
            hover_state_tracker[button_id] = False

    cor_padrao = COR_BOTAO
    cor_hover = (60, 60, 60)
    cor_fundo = cor_hover if is_hovered else cor_padrao

    # Desenha o fundo
    pygame.draw.rect(tela, cor_fundo, rect, 0, 10)
    
    # Desenha a borda normal (COR_DESTAQUE)
    pygame.draw.rect(tela, COR_DESTAQUE, rect, 3, 10)


    if is_hovered:
 
        
        # Para desenhar a borda roxa por cima da azul (com 3px de largura)
        pygame.draw.rect(tela, COR_ROXA_HOVER, rect, 3, 10) 


    text_surf = fonte.render(text, True, COR_BRANCA)
    tela.blit(text_surf, (rect.centerx - text_surf.get_width()//2, rect.centery - text_surf.get_height()//2))

def draw_input_box(tela, fonte, rect, label, text, is_active):
    cor_borda = COR_DESTAQUE if is_active else COR_INPUT_BOX
    cor_fundo = COR_INPUT_BOX_ATIVA if is_active else COR_INPUT_BOX

    # Desenha o rótulo
    label_surf = fonte.render(label, True, COR_BRANCA)
    tela.blit(label_surf, (rect.x, rect.y - 30))

    # Desenha a caixa de input
    pygame.draw.rect(tela, cor_fundo, rect, 0, 5)
    pygame.draw.rect(tela, cor_borda, rect, 2, 5)

    texto_para_exibir = text
    # Truncar visualmente se maior que a caixa
    while fonte.size(texto_para_exibir + '...')[0] > rect.width - 20 and len(texto_para_exibir) > 0:
        texto_para_exibir = texto_para_exibir[:-1]
    if texto_para_exibir != text:
        texto_para_exibir += '...'

    text_surf = fonte.render(texto_para_exibir, True, COR_BRANCA)
    tela.blit(text_surf, (rect.x + 10, rect.y + (rect.height - text_surf.get_height())//2))

def get_class_options():
    """Retorna uma lista de objetos de classe base (com nomes e subclasses) e a contagem total."""
    if class_data is None or "Classes" not in class_data:
        return [], 0
    
    # Retorna a lista de objetos de classe base
    return class_data["Classes"], len(class_data["Classes"])

def get_subclass_options(class_choice_index):
    """Retorna lista de subclasses (tiers) e a contagem máxima para a classe base escolhida."""
    class_list, max_classes = get_class_options()
    
    # Verifica se o índice da classe base é válido
    if not (0 <= class_choice_index < max_classes):
        return [], 0, "N/A"
    
    selected_class = class_list[class_choice_index]
    class_base_name = selected_class.get("Classe", "SemNome")
    
    # Pega a lista de subclasses (tiers) diretamente da classe base
    subclasses = selected_class.get("Subclasse", [])
    
    return subclasses, len(subclasses), class_base_name

# NOVO: Função para desenhar o log de atualização
def draw_update_log(tela, update_log_title, update_log_text):
    fonte_titulo = pygame.font.Font(None, 45)
    fonte_texto = pygame.font.Font(None,30)
    
    # Dimensões do painel de logs (ajustado para caber na imagem)
    LOG_W = 750
    LOG_H = 700
    LOG_X = TELA_LARGURA - LOG_W - 100 # Posição mais à direita
    LOG_Y = TELA_ALTURA // 2 - LOG_H // 2
    
    log_rect = pygame.Rect(LOG_X, LOG_Y, LOG_W, LOG_H)
    
    # Desenha o fundo do log (preto com transparência)
    log_surface = pygame.Surface((LOG_W, LOG_H), pygame.SRCALPHA)
    log_surface.fill((0, 0, 0, 150)) # Preto com 150 de transparência
    tela.blit(log_surface, log_rect.topleft)
    
    # Desenha o título
    title_surf = fonte_titulo.render(update_log_title, True, COR_BRANCA)
    title_rect = title_surf.get_rect(center=(log_rect.centerx, LOG_Y + 40))
    tela.blit(title_surf, title_rect)
    
    # Desenha o texto do log
    text_start_y = LOG_Y + 80
    line_spacing = fonte_texto.get_linesize()
    #Altera a posição da descrição do UpdateLog no eixo X
    text_x = LOG_X + 90
    
    for i, line in enumerate(update_log_text):
        if text_start_y + i * line_spacing < LOG_Y + LOG_H - 30: # Limita para não sair do painel
            line_surf = fonte_texto.render(line, True, COR_BRANCA)
            tela.blit(line_surf, (text_x, text_start_y + i * line_spacing))


# ------------------- Telas -------------------

def main_menu(tela, relogio, background_img, game_logo):
    global current_state
    fonte_botao = pygame.font.Font(None, 48)
    fonte_versao = pygame.font.Font(None, 24) # Fonte para a versão
    logo_y_center = TELA_ALTURA // 3.
    altura_inicial = TELA_ALTURA // 2 + 50
    
    # Posições ajustadas para centralizar os botões à esquerda (como na imagem)
    BTN_X_CENTER = TELA_LARGURA // 4 # Aproximadamente 1/4 da tela para os botões
    BTN_W = 500
    
    btn_new_game_rect = pygame.Rect(BTN_X_CENTER - BTN_W // 2, altura_inicial, BTN_W, 90)
    btn_load_game_rect = pygame.Rect(BTN_X_CENTER - BTN_W // 2, altura_inicial + 110, BTN_W, 90)
    btn_exit_rect = pygame.Rect(BTN_X_CENTER - BTN_W // 2, altura_inicial + 220, BTN_W, 90)

    running = True
    while running and current_state == "MENU_PRINCIPAL":
        mouse_pos = pygame.mouse.get_pos()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if btn_new_game_rect.collidepoint(evento.pos):
                    # Reinicia inputs e entra no novo estado de janela única
                    global player_responses, current_active_input
                    player_responses = {"save_name": "", "char_name": "", "class_choice": "", "subclass_choice": ""}
                    current_active_input = "save_name"
                    current_state = "NEW_SAVE_WINDOW"
                    return
                elif btn_load_game_rect.collidepoint(evento.pos):
                    print("Ação: Carregar Jogo (Ainda não implementado)")
                elif btn_exit_rect.collidepoint(evento.pos):
                    pygame.quit(); sys.exit()

        tela.blit(background_img, (0, 0))
        overlay = pygame.Surface((TELA_LARGURA, TELA_ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        tela.blit(overlay, (0, 0))

        # Ajusta a posição do logo para o centro dos botões
        logo_rect = game_logo.get_rect()
        logo_rect.center = (BTN_X_CENTER, logo_y_center)
        tela.blit(game_logo, logo_rect)

        draw_button(tela, fonte_botao, btn_new_game_rect, "NOVO JOGO", mouse_pos)
        draw_button(tela, fonte_botao, btn_load_game_rect, "CARREGAR JOGO", mouse_pos)
        draw_button(tela, fonte_botao, btn_exit_rect, "SAIR", mouse_pos)

        # NOVO: Desenha a tela de Update Log
        draw_update_log(tela, UPDATE_LOG_TITLE, UPDATE_LOG_TEXT)

        # NOVO: Desenha a versão do jogo (ajustado para a parte inferior direita do painel de logs)
        version_surf = fonte_versao.render(GAME_VERSION, True, COR_BRANCA)
        
        # Posição da versão no canto inferior do painel de logs
        # O painel de logs começa em TELA_LARGURA - LOG_W - 100, e tem largura LOG_W
        LOG_W = 750
        LOG_X = TELA_LARGURA - LOG_W - 100
        
        # Centraliza a versão na parte inferior da tela, alinhado com o painel de logs (como na imagem)
        version_rect = version_surf.get_rect(center=(LOG_X + LOG_W // 2, TELA_ALTURA - 20))
        tela.blit(version_surf, version_rect)

        pygame.display.flip()
        relogio.tick(30)


def new_save_window(tela, relogio, background_img):
    """
    Janela para coletar inputs de criação de personagem, baseada na nova estrutura de classes.
    """
    global current_state, player_responses, current_active_input
    
    FONT_SIZE = 36
    fonte_texto = pygame.font.Font(None, FONT_SIZE)
    fonte_titulo = pygame.font.Font(None, 60)
    
    INPUT_W, INPUT_H = 500, 40
    # O input agora está centralizado na mesma coluna dos botões do menu
    INPUT_X = TELA_LARGURA // 4 - INPUT_W // 2 
    TITLE_Y = 80
    INPUT_START_Y = 150
    INPUT_SPACING = 100
    
    # Definição das caixas de input
    input_fields = {
        "save_name": {"label": "Nome do Save:", "rect": pygame.Rect(INPUT_X, INPUT_START_Y + 0 * INPUT_SPACING, INPUT_W, INPUT_H)},
        "char_name": {"label": "Nome do Personagem:", "rect": pygame.Rect(INPUT_X, INPUT_START_Y + 1 * INPUT_SPACING, INPUT_W, INPUT_H)},
        # Aqui, class_choice é o índice da classe base (Humano, Gato, Tank...)
        "class_choice": {"label": "Classe Base (Digite o número):", "rect": pygame.Rect(INPUT_X, INPUT_START_Y + 2 * INPUT_SPACING, INPUT_W, INPUT_H)}, 
        # subclass_choice é o índice do Tier/Variação dentro da Classe Base
        "subclass_choice": {"label": "Variação de Classe/Tier (Digite o número):", "rect": pygame.Rect(INPUT_X, INPUT_START_Y + 3 * INPUT_SPACING, INPUT_W, INPUT_H)}, 
    }
    
    # Posições para os bonecos
    IMAGE_X = input_fields["class_choice"]["rect"].right + 50
    
    BTN_HEIGHT = 70
    BTN_MARGIN_BOTTOM = 100
    # Botões centralizados na mesma coluna
    btn_create_rect = pygame.Rect(INPUT_X + INPUT_W // 2 + 50, TELA_ALTURA - BTN_MARGIN_BOTTOM, 200, BTN_HEIGHT)
    btn_cancel_rect = pygame.Rect(INPUT_X + INPUT_W // 2 - 250, TELA_ALTURA - BTN_MARGIN_BOTTOM, 200, BTN_HEIGHT)
    
    field_order = list(input_fields.keys())
    
    def validate_and_create():
        global current_state
        
        # 1. Validação básica de preenchimento (exceto Subclasse/Tier, que pode ser 1 por padrão)
        if not player_responses["save_name"].strip() or not player_responses["char_name"].strip():
            print("Erro: Nome do Save e Nome do Personagem são obrigatórios.")
            return False
        
        # 2. Validação de Classe Base
        class_list, max_classes = get_class_options()
        try:
            class_index = int(player_responses["class_choice"]) - 1
            if not (0 <= class_index < max_classes):
                print(f"Erro: Número da Classe Base deve estar entre 1 e {max_classes}.")
                return False
            chosen_class_info = class_list[class_index]
            chosen_class_name = chosen_class_info.get("Classe", "Indefinida")
        except ValueError:
            print("Erro: O input de Classe Base deve ser um número.")
            return False

        # 3. Validação de Subclasse/Tier
        subclasses, max_subs, class_base_name = get_subclass_options(class_index)
        
        try:
            # Se não digitou nada para subclasse, assume o primeiro tier (índice 0)
            if not player_responses["subclass_choice"].strip():
                subclass_index = 0
            else:
                subclass_index = int(player_responses["subclass_choice"]) - 1
            
            if not (0 <= subclass_index < max_subs):
                print(f"Erro: Número da Variação/Tier deve estar entre 1 e {max_subs}.")
                return False
            
            chosen_subclass_info = subclasses[subclass_index]
            chosen_subclass_name = chosen_subclass_info.get("Nome", "Tier Base")
            
        except ValueError:
            print("Erro: O input de Variação/Tier deve ser um número.")
            return False

        # 4. Monta player_info e cria o save
        player_info = {
            "Nome": player_responses.get("char_name", "SemNome"),
            "ClasseBase": chosen_class_name,
            "Subclasse": chosen_subclass_name, # O nome do Tier/Variação é usado como Subclasse
        }
        
        save_name = player_responses.get("save_name", "default_save")
        if create_save_directory(save_name, player_info):
            current_state = "GAMEPLAY"
            return save_name
        else:
            return False

    # Variáveis para a lista de opções
    class_list, max_classes = get_class_options()
    
    while current_state == "NEW_SAVE_WINDOW":
        mouse_pos = pygame.mouse.get_pos()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if evento.type == pygame.MOUSEBUTTONDOWN:
                # Checa qual input box foi clicada
                current_active_input = None
                for field_key, field_data in input_fields.items():
                    if field_data["rect"].collidepoint(evento.pos):
                        current_active_input = field_key
                
                # Botões
                if btn_cancel_rect.collidepoint(evento.pos):
                    current_state = "MENU_PRINCIPAL"
                    return None
                elif btn_create_rect.collidepoint(evento.pos):
                    result = validate_and_create()
                    if isinstance(result, str):
                        return result
                    elif result is False:
                        pass
                        
            if evento.type == pygame.KEYDOWN and current_active_input:
                if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    # Avança para o próximo campo na ordem
                    try:
                        current_index = field_order.index(current_active_input)
                        next_index = (current_index + 1) % len(field_order)
                        current_active_input = field_order[next_index]
                    except ValueError:
                        current_active_input = field_order[0]
                elif evento.key == pygame.K_BACKSPACE:
                    player_responses[current_active_input] = player_responses[current_active_input][:-1]
                else:
                    # Limitação de input
                    if current_active_input in ["class_choice", "subclass_choice"]:
                        if evento.unicode.isdigit() and len(player_responses[current_active_input]) < 3: # Apenas números para índices
                            player_responses[current_active_input] += evento.unicode
                    elif len(player_responses[current_active_input]) < 64: 
                        player_responses[current_active_input] += evento.unicode

        # --- Desenho ---
        tela.blit(background_img, (0, 0))
        overlay = pygame.Surface((TELA_LARGURA, TELA_ALTURA), pygame.SRCALPHA); overlay.fill((0, 0, 0, 180))
        tela.blit(overlay, (0, 0))

        titulo_surf = fonte_titulo.render("NOVO JOGO - CRIAÇÃO DE PERSONAGEM", True, COR_DESTAQUE)
        tela.blit(titulo_surf, (TELA_LARGURA // 2 - titulo_surf.get_width() // 2, TITLE_Y))

        # Desenha os campos de input
        for key, data in input_fields.items():
            draw_input_box(tela, fonte_texto, data["rect"], data["label"], player_responses[key], key == current_active_input)
            
        # --- Desenho dos Bonecos (Imagens de Classe/Subclasse) ---

        # 1. Desenha a imagem da CLASSE BASE (ou Subclasse) escolhida
        class_index = -1
        subclass_index = -1
        try:
            # Tenta obter o índice da classe base
            if player_responses["class_choice"].isdigit():
                class_index = int(player_responses["class_choice"]) - 1
            
            # Se a classe base for válida, tenta obter a Subclasse (Tier)
            if 0 <= class_index < max_classes:
                subclasses, max_subs, class_base_name = get_subclass_options(class_index)
                
                # Tenta obter o índice do tier/subclasse
                if player_responses["subclass_choice"].isdigit():
                    subclass_index = int(player_responses["subclass_choice"]) - 1
                elif not player_responses["subclass_choice"].strip():
                    subclass_index = 0 # Assume o primeiro tier se o campo estiver vazio
                    
                # Escolhe o nome da imagem a ser exibida: Subclasse se for válida, senão Classe Base
                image_name_to_display = None
                if 0 <= subclass_index < max_subs:
                    image_name_to_display = subclasses[subclass_index].get("Nome")
                else:
                    image_name_to_display = class_base_name

                if image_name_to_display in class_images:
                    img_to_display = class_images[image_name_to_display]
                    # Centraliza verticalmente no meio das caixas de classe/subclasse
                    mid_y = (input_fields["class_choice"]["rect"].centery + input_fields["subclass_choice"]["rect"].centery) // 2
                    img_rect = img_to_display.get_rect(midleft=(IMAGE_X, mid_y))
                    tela.blit(img_to_display, img_rect)
                    
        except ValueError:
            pass 
        except IndexError:
            pass

        # --- FIM do NOVO Desenho ---
            
        # Desenha opções de Classe
        y_offset = INPUT_START_Y + 4 * INPUT_SPACING
        tela.blit(fonte_texto.render("Classes Base Disponíveis:", True, COR_DESTAQUE), (INPUT_X, y_offset))
        y_offset += FONT_SIZE
        
        for i, class_info in enumerate(class_list):
            name = class_info.get("Classe", "SemNome")
            tela.blit(fonte_texto.render(f" {i+1}: {name}", True, COR_BRANCA), (INPUT_X, y_offset))
            y_offset += FONT_SIZE - 5

        # Desenha opções de Subclasse (apenas se a classe for válida)
        try:
            if 0 <= class_index < max_classes:
                subclasses, max_subs, class_base_name = get_subclass_options(class_index)
                y_offset += FONT_SIZE + 10 
                tela.blit(fonte_texto.render(f"Variações/Tiers para {class_base_name}:", True, COR_DESTAQUE), (INPUT_X, y_offset))
                y_offset += FONT_SIZE
                
                if max_subs == 0:
                    tela.blit(fonte_texto.render(" Nenhuma variação disponível.", True, COR_BRANCA), (INPUT_X, y_offset))
                else:
                    for i, sub in enumerate(subclasses):
                        nome_sub = sub.get("Nome", "SemNome")
                        descricao = sub.get("Descricao", "...")
                        tela.blit(fonte_texto.render(f" {i+1}: {nome_sub} ({descricao})", True, COR_BRANCA), (INPUT_X, y_offset))
                        y_offset += FONT_SIZE - 5
            
        except (ValueError, IndexError):
            # Classe não digitada ou inválida: não mostra subclasses
            pass

        draw_button(tela, fonte_titulo, btn_create_rect, "CRIAR", mouse_pos)
        draw_button(tela, fonte_titulo, btn_cancel_rect, "CANCELAR", mouse_pos)

        pygame.display.flip()
        relogio.tick(30)


# ------------------- Função Principal -------------------

def main():
    global current_state, class_data, player_responses, background_img, game_logo, relogio, tela, hover_sound

    pygame.init()
    # Inicializa mixer com cuidado
    try:
        pygame.mixer.init()
    except Exception:
        pass

    # Garante diretórios mínimos
    os.makedirs(SAVE_FOLDER_NAME, exist_ok=True)
    os.makedirs(CLASS_IMAGE_FOLDER, exist_ok=True)
    player_path = os.path.join(BASE_WORLD_FOLDER, "Player")
    os.makedirs(player_path, exist_ok=True)
    
    # cria arquivos básicos se não existirem
    try:
        stats_file = os.path.join(player_path, "statistics.json")
        if not os.path.exists(stats_file):
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump({}, f)
        base_seed_file = os.path.join(BASE_WORLD_FOLDER, SEED_FILE_NAME)
        if not os.path.exists(base_seed_file):
            with open(base_seed_file, 'w', encoding='utf-8') as f:
                json.dump({"seed": 0}, f)
    except Exception as e:
        print("Aviso: não foi possível criar arquivos iniciais:", e)

    # Garante que classes.json exista (cria um default se necessário, usando a NOVA estrutura)
    if not os.path.exists(CLASSES_FILE_NAME):
        NEW_USER_CLASSES_JSON = {
            "Classes": [
                {
                    "Classe": "Humano",
                    "Subclasse": [
                        {"Nome": "Humano", "Descricao": "Versátil."},
                        {"Nome": "Guerreiro Adaptável", "Descricao": "Armas de diferentes épocas."},
                    ]
                },
                {
                    "Classe": "Mago",
                    "Subclasse": [
                        {"Nome": "Mago", "Descricao": "Manipula energia temporal básica."},
                        {"Nome": "Arquimago", "Descricao": "Combina elementos com distorção."},
                    ]
                },
            ],
            "MagiasUniversais": {}
        }
        try:
            with open(CLASSES_FILE_NAME, 'w', encoding='utf-8') as f:
                json.dump(NEW_USER_CLASSES_JSON, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print("Erro ao criar classes.json default:", e)

    # CARREGA classes.json antes de entrar no menu (fix crítico)
    class_data = load_classes()
    
    # NOVO: Carrega as imagens das classes
    load_class_images()

    # Configura tela
    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    pygame.display.set_caption("Sound Affect")
    relogio = pygame.time.Clock()

    # Carrega mídias com fallbacks
    try:
        background_img = pygame.image.load(BACKGROUND_IMAGE_FILE).convert()
        background_img = pygame.transform.scale(background_img, (TELA_LARGURA, TELA_ALTURA))
    except Exception:
        background_img = pygame.Surface((TELA_LARGURA, TELA_ALTURA))
        background_img.fill(COR_PRETA)

    try:
        game_logo = pygame.image.load(LOGO_FILE).convert_alpha()
        game_logo = pygame.transform.scale(game_logo, (307, 265))
    except Exception:
        game_logo = pygame.Surface((307, 265), pygame.SRCALPHA)

    ### ATUALIZAÇÃO: Carrega o som de hover
    try:
        if os.path.exists(HOVER_SOUND_FILE):
            hover_sound = pygame.mixer.Sound(HOVER_SOUND_FILE)
            print(f"🔊 Som de hover '{HOVER_SOUND_FILE}' carregado.")
        else:
            print(f"❌ Aviso: Arquivo de som de hover '{HOVER_SOUND_FILE}' não encontrado.")
    except Exception as e:
        print(f"❌ Erro ao carregar som de hover: {e}")
        hover_sound = None
    
    while True:
        if current_state == "MENU_PRINCIPAL":
            main_menu(tela, relogio, background_img, game_logo)
        elif current_state == "NEW_SAVE_WINDOW":
            save_name = new_save_window(tela, relogio, background_img)
            # Após criar o save, se for bem-sucedido, o estado muda para 'GAMEPLAY'
            # Se for cancelado, o estado volta para 'MENU_PRINCIPAL' (dentro de new_save_window)
        elif current_state == "GAMEPLAY":
            # Aqui você chamaria sua função de loop de jogo
            print(f"Iniciando Jogo... Save: {player_responses['save_name']}")
            # Execução do jogo principal
            subprocess.run(["python", "open_game.py"])
            pygame.quit()
            sys.exit()
        
        # Mantém a taxa de atualização
        relogio.tick(30)

if __name__ == '__main__':
    main()