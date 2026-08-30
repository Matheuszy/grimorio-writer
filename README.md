# O Grimório Errante — MVP

Projeto de visão computacional: um livro/grimório controlado por gestos das
mãos, com efeito de escrita mágica e virada de página.

## Estrutura

```
grimorio/
├── backend/
│   ├── hand_tracker.py     # captura webcam, detecta gestos, serve WebSocket
│   └── requirements.txt
└── frontend/
    ├── index.html          # só a estrutura da página
    ├── style.css           # aparência (livro, câmera, status)
    └── js/
        ├── book.js         # páginas do livro e navegação entre elas
        ├── drawing.js      # traço de tinta + teste manual com o mouse
        ├── keyboard.js     # atalhos de teclado (setas, C) para teste
        ├── connection.js   # WebSocket com o backend + status/câmera na tela
        └── main.js         # inicializa os módulos acima, nessa ordem
```

## Como testar

### 1. Só o visual (sem câmera, sem Python)

Abra `frontend/index.html` direto no navegador (duplo clique já funciona).

- Clique e arraste o mouse sobre a página para "escrever"
- Setas ← → para virar a página
- Tecla `C` para limpar a página atual

Isso valida o efeito visual (páginas, brilho da tinta, câmara circular)
antes mesmo de ligar a webcam.

### 2. Com detecção de mão de verdade

```bash
cd backend
pip install -r requirements.txt
python hand_tracker.py
```

Isso abre a webcam (nenhuma janela extra aparece — tudo é enviado por
WebSocket) e sobe o servidor em `ws://localhost:8765`. Com o script rodando,
abra (ou recarregue) `frontend/index.html`: o círculo dourado no canto
deve mostrar sua câmera com os pontos da mão desenhados, e o indicador
ao lado dele acende quando o "modo caneta" é reconhecido.

**Gestos:**
- **Escrever:** indicador esticado, outros dedos fechados (como se
  estivesse segurando uma pena)
- **Virar página:** mão aberta, mova-a rapidamente para o lado

## Calibração esperada no primeiro teste

Esse é um MVP — é bem provável que na primeira tentativa:
- O gesto de "modo caneta" dispare cedo demais ou não dispare (ajuste os
  limiares em `detect_pen_mode`, dentro de `hand_tracker.py`)
- O swipe de página precise de um gesto mais exagerado (ajuste
  `SWIPE_THRESHOLD` e `SWIPE_COOLDOWN` no topo do arquivo)
- A luz do ambiente afete a detecção do MediaPipe — teste num lugar bem
  iluminado primeiro

Depois de testar, me conta o que aconteceu (falso positivo, delay, gesto
não reconhecido etc.) que a gente ajusta os parâmetros juntos.

## Rodando com Docker

```bash
docker compose up --build
```

Isso builda e sobe os dois serviços: backend em `ws://localhost:8765` e
frontend em `http://localhost:8080`.

### ⚠️ Aviso sobre a webcam

Esse projeto depende de acesso direto à câmera física, e isso é o ponto
mais frágil de containerizar:

- **Linux**: `devices: - /dev/video0:/dev/video0` no `docker-compose.yml`
  geralmente funciona direto.
- **Windows (o seu caso)**: o Docker Desktop roda os containers dentro de
  uma VM Linux via WSL2, que **não tem acesso à webcam do Windows por
  padrão**. Existe um caminho via `usbipd-win` pra "emprestar" o
  dispositivo USB pro WSL2, mas é um processo manual, específico do
  dispositivo, e nem sempre estável para câmeras (funciona melhor pra
  dispositivos seriais simples).

**Recomendação prática:** para esse projeto especificamente, continue
rodando o `hand_tracker.py` nativamente no Windows (como já está
fazendo) — é onde a webcam funciona sem fricção. O Docker aqui serve
melhor pra containerizar o **frontend** (que não depende de hardware),
ou como material de estudo de como isso ficaria organizado num projeto
que não dependa de uma câmera física. Guarde o Docker pros próximos
projetos que sejam só código + rede — é aí que ele realmente compensa.