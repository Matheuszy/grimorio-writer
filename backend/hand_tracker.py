"""
Grimório Interativo — Backend de visão computacional
------------------------------------------------------
Captura a webcam, detecta a mão com MediaPipe, identifica dois gestos:
  - "modo caneta": indicador esticado, demais dedos fechados -> escreve
  - "virar página": movimento lateral rápido da mão aberta -> passa página

Envia tudo (frame com landmarks desenhados + eventos de gesto) via WebSocket
para o frontend (index.html) rodando no navegador.

Instalação:
    pip install -r requirements.txt

Execução:
    python hand_tracker.py

Depois é só abrir o frontend/index.html no navegador. Ele conecta
automaticamente em ws://localhost:8765
"""

import asyncio
import base64
import json
import time
from collections import deque

import cv2
import mediapipe as mp
import websockets

# ----------------------------- Configurações -----------------------------

CAM_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
JPEG_QUALITY = 60          # qualidade do frame enviado ao navegador (0-100)
SWIPE_HISTORY_SIZE = 8     # quantos frames usamos para detectar o swipe
SWIPE_THRESHOLD = 0.28     # deslocamento horizontal normalizado para virar página
SWIPE_COOLDOWN = 0.8       # segundos de espera entre uma virada de página e outra

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles


class HandGrimorio:
    def __init__(self):
        self.cap = cv2.VideoCapture(CAM_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

        self.hands = mp_hands.Hands(
            model_complexity=0,
            max_num_hands=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.5,
        )

        self.wrist_history = deque(maxlen=SWIPE_HISTORY_SIZE)
        self.last_swipe_time = 0.0
        self.clients = set()

    # ------------------------- Lógica de gestos -------------------------

    @staticmethod
    def _finger_extended(landmarks, tip_id, pip_id):
        # Em coordenadas de imagem, y cresce para baixo.
        # Dedo esticado -> ponta (tip) está acima da articulação (pip).
        return landmarks[tip_id].y < landmarks[pip_id].y

    def detect_pen_mode(self, landmarks):
        index_up = self._finger_extended(landmarks, 8, 6)
        middle_down = not self._finger_extended(landmarks, 12, 10)
        ring_down = not self._finger_extended(landmarks, 16, 14)
        pinky_down = not self._finger_extended(landmarks, 20, 18)
        return index_up and middle_down and ring_down and pinky_down

    def detect_open_hand(self, landmarks):
        fingers = [(8, 6), (12, 10), (16, 14), (20, 18)]
        return all(self._finger_extended(landmarks, t, p) for t, p in fingers)

    def detect_swipe(self, landmarks):
        wrist_x = landmarks[0].x
        now = time.time()
        self.wrist_history.append((now, wrist_x))

        if now - self.last_swipe_time < SWIPE_COOLDOWN:
            return None
        if len(self.wrist_history) < SWIPE_HISTORY_SIZE:
            return None
        if not self.detect_open_hand(landmarks):
            return None

        start_t, start_x = self.wrist_history[0]
        delta = wrist_x - start_x

        if abs(delta) >= SWIPE_THRESHOLD:
            self.last_swipe_time = now
            self.wrist_history.clear()
            # Câmera é espelhada no frontend, então invertemos o sinal
            # para casar com a percepção natural de "arrastar para a direita".
            return "next_page" if delta > 0 else "prev_page"
        return None

    # --------------------------- Loop principal --------------------------

    async def broadcast(self, message: dict):
        if not self.clients:
            return
        data = json.dumps(message)
        dead = set()
        for ws in self.clients:
            try:
                await ws.send(data)
            except websockets.exceptions.ConnectionClosed:
                dead.add(ws)
        self.clients -= dead

    async def camera_loop(self):
        while True:
            ok, frame = self.cap.read()
            if not ok:
                await asyncio.sleep(0.01)
                continue

            frame = cv2.flip(frame, 1)  # espelha, fica mais natural
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = self.hands.process(rgb)

            pen_mode = False
            fingertip = None
            gesture = None

            if result.multi_hand_landmarks:
                hand_landmarks = result.multi_hand_landmarks[0]
                landmarks = hand_landmarks.landmark

                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_styles.get_default_hand_landmarks_style(),
                    mp_styles.get_default_hand_connections_style(),
                )

                pen_mode = self.detect_pen_mode(landmarks)
                if pen_mode:
                    tip = landmarks[8]
                    fingertip = {"x": tip.x, "y": tip.y}

                gesture = self.detect_swipe(landmarks)

            # Codifica o frame como JPEG -> base64 para mandar ao navegador
            ok, buf = cv2.imencode(
                ".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY]
            )
            frame_b64 = base64.b64encode(buf).decode("utf-8") if ok else None

            payload = {
                "type": "update",
                "frame": frame_b64,
                "pen_mode": pen_mode,
                "fingertip": fingertip,
            }
            await self.broadcast(payload)

            if gesture:
                await self.broadcast({"type": "gesture", "action": gesture})

            await asyncio.sleep(1 / 30)  # ~30 fps

    async def handler(self, websocket):
        self.clients.add(websocket)
        print(f"[+] Frontend conectado ({len(self.clients)} cliente(s))")
        try:
            async for _ in websocket:
                pass  # não esperamos mensagens do frontend por enquanto
        finally:
            self.clients.discard(websocket)
            print(f"[-] Frontend desconectado ({len(self.clients)} cliente(s))")

    async def run(self):
        async with websockets.serve(self.handler, "localhost", 8765):
            print("Servidor WebSocket rodando em ws://localhost:8765")
            print("Abra frontend/index.html no navegador para ver o grimório.")
            await self.camera_loop()


if __name__ == "__main__":
    grimorio = HandGrimorio()
    try:
        asyncio.run(grimorio.run())
    except KeyboardInterrupt:
        print("\nEncerrando...")