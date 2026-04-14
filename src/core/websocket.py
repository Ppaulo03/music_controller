import asyncio
import json
import logging
from typing import Optional, Set

import websockets
from websockets.server import ServerConnection

from src.core.state import AppState, MediaMetadata

logger = logging.getLogger(__name__)


class MusicWebSocketServer:
    """Gerencia o servidor WebSocket e a comunicação com a extensão."""

    def __init__(self, state: AppState, host: str = "127.0.0.1", port: int = 8975) -> None:
        self.state = state
        self.host = host
        self.port = port
        self.clients: Set[ServerConnection] = set()
        self.command_queue: asyncio.Queue[str] = asyncio.Queue()
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    async def start(self) -> None:
        """Inicia o servidor e o loop de broadcast."""
        self._loop = asyncio.get_running_loop()
        async with websockets.serve(self.handler, self.host, self.port):
            logger.info(f"Servidor WebSocket ouvindo em ws://{self.host}:{self.port}")
            await self._broadcast_loop()

    async def handler(self, websocket: ServerConnection) -> None:
        """Handler para conexões de entrada."""
        self.clients.add(websocket)
        self.state.active_connections = len(self.clients)
        logger.info(f"Extensão conectada! (Conexões ativas: {self.state.active_connections})")

        try:
            async for message in websocket:
                if isinstance(message, str):
                    self._parse_message(message)
        except websockets.ConnectionClosed:
            pass
        finally:
            self.clients.remove(websocket)
            self.state.active_connections = len(self.clients)
            logger.info(f"Extensão desconectada. (Conexões ativas: {self.state.active_connections})")

    def _parse_message(self, message: str) -> None:
        """Processa as mensagens JSON recebidas da extensão."""
        try:
            data = json.loads(message)
            status_code = data.get("playerStatus")
            status_text = (
                "Tocando" if status_code == 1 else "Pausado" if status_code == 2 else "Desconhecido"
            )

            raw_vol = data.get("volume", self.state.metadata.volume)
            volume = int(raw_vol if raw_vol > 1 else raw_vol * 100)

            new_metadata = MediaMetadata(
                title=data.get("title", self.state.metadata.title),
                artist=data.get("artist", self.state.metadata.artist),
                album=data.get("album", self.state.metadata.album),
                cover=data.get("cover", self.state.metadata.cover),
                status=status_text,
                volume=volume,
            )

            if new_metadata != self.state.metadata:
                self.state.metadata = new_metadata
                # Sincroniza estado de mute com o volume real
                if self.state.metadata.volume == 0:
                    self.state.is_muted = True
                elif self.state.metadata.volume > 0 and self.state.is_muted:
                    self.state.is_muted = False

                logger.info(
                    f"META: {self.state.metadata.title} - {self.state.metadata.artist} "
                    f"({self.state.metadata.status}) | Vol: {self.state.metadata.volume}%"
                )
        except json.JSONDecodeError:
            pass

    async def _broadcast_loop(self) -> None:
        """Envia comandos da fila para todos os clientes conectados."""
        while True:
            command = await self.command_queue.get()
            if self.clients:
                for client in self.clients:
                    try:
                        logger.info(f"Enviando comando: {command}")
                        await client.send(command)
                    except Exception as e:
                        logger.error(f"Erro ao enviar {command}: {e}")
            self.command_queue.task_done()

    def enqueue_command(self, command: str) -> None:
        """Adiciona um comando à fila de forma thread-safe."""
        if self._loop:
            self._loop.call_soon_threadsafe(self.command_queue.put_nowait, command)
