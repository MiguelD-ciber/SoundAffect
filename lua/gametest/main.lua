-- Variáveis globais para o círculo
local circleX = 400
local circleY = 300
local circleRadius = 20
local speed = 200 -- Velocidade em pixels por segundo

-- love.load() é chamado uma vez no início do jogo.
function love.load()
    -- Define o título da janela
    love.window.setTitle("Sound Affect Main Game")
    -- Define o modo de desenho para antialiasing para gráficos mais suaves (opcional)
    love.graphics.setLineStyle("smooth")
end

-- love.update(dt) é chamado em cada frame do jogo.
-- dt (delta time) é o tempo em segundos desde o último frame.
function love.update(dt)
    -- Lógica de Movimento:
    -- Multiplicamos a velocidade por dt para garantir que o movimento seja o mesmo,
    -- independentemente da taxa de quadros (FPS) do usuário.
    
    if love.keyboard.isDown("right") then
        circleX = circleX + speed * dt
    end
    if love.keyboard.isDown("left") then
        circleX = circleX - speed * dt
    end
    if love.keyboard.isDown("up") then
        circleY = circleY - speed * dt
    end
    if love.keyboard.isDown("down") then
        circleY = circleY + speed * dt
    end
    
    -- Lógica de Limite da Tela (opcional)
    local width, height = love.graphics.getDimensions()
    circleX = math.max(circleRadius, math.min(circleX, width - circleRadius))
    circleY = math.max(circleRadius, math.min(circleY, height - circleRadius))
end

-- love.draw() é chamado para desenhar coisas na tela.
function love.draw()
    -- 1. Desenha o fundo (opcional, mas bom para limpar o frame anterior)
    -- love.graphics.setColor(R, G, B, A) | 0 a 1
    love.graphics.setColor(0.2, 0.2, 0.3, 1) -- Um cinza/azul escuro
    love.graphics.rectangle("fill", 0, 0, love.graphics.getWidth(), love.graphics.getHeight())

    -- 2. Define a cor do objeto (vermelho)
    love.graphics.setColor(1, 0.2, 0.2, 1) -- Vermelho
    
    -- 3. Desenha o círculo
    -- love.graphics.circle("modo", x, y, raio)
    love.graphics.circle("fill", circleX, circleY, circleRadius)
    
    -- 4. Desenha texto para instruções (opcional)
    love.graphics.setColor(1, 1, 1, 1) -- Branco
    love.graphics.print("Use as setas para mover o círculo.", 10, 10)
    love.graphics.print("FPS: " .. love.timer.getFPS(), 10, 30)
end