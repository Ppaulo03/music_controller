import asyncio
import logging
import sys

from src.core.hotkeys import HotkeyManager
from src.core.state import AppState
from src.core.websocket import MusicWebSocketServer
from src.services.player_controller import PlayerController

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """
    Ponto de entrada principal da aplicação.
    Orquestra a inicialização do estado, servidor websocket,
    lógica de controle e gerenciamento de atalhos.
    """

    state = AppState()
    server = MusicWebSocketServer(state, port=8975)
    controller = PlayerController(state, server)
    hotkeys = HotkeyManager(controller)
    hotkeys.setup()

    try:
        await server.start()
    except asyncio.CancelledError:
        logger.info("Servidor cancelado.")
    except Exception as e:
        logger.error(f"Erro inesperado no servidor: {e}")
    finally:
        logger.info("Encerrando controlador de música...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Processo interrompido pelo usuário.")
        sys.exit(0)
