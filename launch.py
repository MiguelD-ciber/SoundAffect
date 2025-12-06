# -- INEXVI_PYGAME.PY --
print("Iniciando inexvi_pygame.py")

import pygame
import os
import subprocess
import sys
import time

# --- Configurações ---
IMAGE_PATH = "dragonpulse.png"  # Nome da imagem
SEGUNDO_SCRIPT_PATH = "mainscript.py" # Caminho para o script principal
SOUND_PATH = "dragonpulse.wav"  # Caminho para o arquivo de som
FADE_DURATION = 2000  # Duração do fade-in e fade-out em milissegundos (2 segundos)
PAUSE_DURATION = 1500  # Duração da pausa em milissegundos (1.5 segundos)

# Inicializa todos os módulos Pygame
pygame.init()

class PygameFadeApp:
    def __init__(self):
        # 1. Configuração da Tela
        info = pygame.display.Info()
        self.screen_width = info.current_w
        self.screen_height = info.current_h
        # Configurar a tela em modo FULLSCREEN
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        pygame.display.set_caption("Efeito Fade Pygame")
        self.clock = pygame.time.Clock()
        self.running = True

        # 2. Carregar e preparar a imagem
        try:
            original_image = pygame.image.load(IMAGE_PATH).convert_alpha()
        except pygame.error as e:
            print(f"Erro ao carregar a imagem '{IMAGE_PATH}': {e}")
            self.running = False
            return

        # 2a. Cálculo do redimensionamento (Mantém a proporção)
        original_width, original_height = original_image.get_size()
        width_ratio = self.screen_width / original_width
        height_ratio = self.screen_height / original_height
        scale_factor = min(width_ratio, height_ratio)
        
        # 2b. Calcular as dimensões e redimensionar
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
        
        self.base_image = pygame.transform.smoothscale(original_image, (new_width, new_height))
        
        # 2c. Centralizar a imagem
        self.image_rect = self.base_image.get_rect(center=(self.screen_width // 2, self.screen_height // 2))

        # 3. Estado do Fade
        self.start_time = pygame.time.get_ticks()
        self.state = 'IN'  # IN, PAUSE, OUT, DONE
        
        # 4. Iniciar Áudio
        self.play_sound_if_available()

    def play_sound_if_available(self):
        """Inicializa e toca o som."""
        try:
            # Tenta inicializar o mixer (se já estiver inicializado, não faz nada)
            if not pygame.mixer.get_init():
                 # Tenta inicializar com configurações específicas se necessário, senão usa as padrão
                pygame.mixer.init()
            
            pygame.mixer.music.load(SOUND_PATH)
            pygame.mixer.music.play()
            print(f"Áudio '{SOUND_PATH}' iniciado via Pygame.")
        except pygame.error as e:
            print(f"Não foi possível tocar o som com Pygame: {e}")

    def update(self):
        """Calcula o valor do alpha (transparência) com base no estado e tempo."""
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.start_time
        
        if self.state == 'IN':
            # Fade-in (Alpha de 255 -> 0. O alpha de um Surface de Cobertura!)
            progress = min(1.0, elapsed_time / FADE_DURATION)
            # O alpha da superfície de cobertura vai de 255 (totalmente opaca, escondendo a imagem) a 0 (totalmente transparente, mostrando a imagem)
            self.alpha = int(255 * (1 - progress)) 
            if progress >= 1.0:
                self.state = 'PAUSE'
                self.start_time = current_time # Reinicia o cronômetro para a pausa
                self.alpha = 0
                
        elif self.state == 'PAUSE':
            if elapsed_time >= PAUSE_DURATION:
                self.state = 'OUT'
                self.start_time = current_time # Reinicia o cronômetro para o fade-out
                
        elif self.state == 'OUT':
            # Fade-out (Alpha de 0 -> 255. O alpha da superfície de Cobertura!)
            progress = min(1.0, elapsed_time / FADE_DURATION)
            # O alpha da superfície de cobertura vai de 0 (transparente) a 255 (opaco, cor preta cobrindo a imagem)
            self.alpha = int(255 * progress)
            if progress >= 1.0:
                self.state = 'DONE'
                self.running = False
                self.alpha = 255
                
        # Mantém o alpha dentro do limite [0, 255]
        self.alpha = max(0, min(255, self.alpha))

    def draw(self):
        """Desenha a imagem e o efeito de cobertura na tela."""
        self.screen.fill((0, 0, 0)) # Fundo preto
        
        if self.state != 'OUT' or self.alpha < 255:
            # 1. Desenha a imagem na posição central
            self.screen.blit(self.base_image, self.image_rect)
            
            # 2. Cria e desenha a Superfície de Cobertura (preta)
            # Ela precisa ter o alpha ajustado para dar o efeito de fade-in/out
            if self.alpha > 0:
                # Cria uma superfície preta do tamanho da tela
                cover_surface = pygame.Surface((self.screen_width, self.screen_height))
                cover_surface.fill((0, 0, 0))
                # Define a transparência (Alpha)
                cover_surface.set_alpha(self.alpha)
                # Desenha a superfície de cobertura (preta) sobre a tela
                self.screen.blit(cover_surface, (0, 0))

        pygame.display.flip()

    def execute_next_script(self):
        try:
            # Garante que o executável python do ambiente virtual ou PATH seja usado
            subprocess.run([sys.executable, SEGUNDO_SCRIPT_PATH], check=True)
        except FileNotFoundError:
            print(f"Erro: O arquivo '{SEGUNDO_SCRIPT_PATH}' não foi encontrado.")
        except Exception as e:
            print(f"Ocorreu um erro ao executar o script: {e}")

    def run(self):
        """Loop principal do jogo."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False

            self.update()
            self.draw()
            self.clock.tick(60) # Limita a taxa de quadros (FPS)
  
        self.execute_next_script()
        time.sleep(2)
        pygame.quit()

if __name__ == "__main__":
    app = PygameFadeApp()
    if app.running:
        app.run()