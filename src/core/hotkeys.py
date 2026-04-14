import logging

import keyboard

from src.services.player_controller import PlayerController

logger = logging.getLogger(__name__)


class HotkeyManager:
    """Gerencia a configuração e registro de atalhos de teclado."""

    def __init__(self, controller: PlayerController) -> None:
        self.controller = controller

    def setup(self) -> None:
        """Registra os atalhos baseados na configuração persistente."""
        cfg = self.controller.state.config.load()
        hk = cfg.hotkeys

        # Limpa atalhos anteriores para evitar duplicatas ou conflitos
        keyboard.unhook_all()

        hotkey_map = {
            hk["play_pause"]: self.controller.play_pause,
            hk["next_track"]: self.controller.next_track,
            hk["previous_track"]: self.controller.previous_track,
            hk["volume_up"]: lambda: self.controller.adjust_volume(1), # +step
            hk["volume_down"]: lambda: self.controller.adjust_volume(-1), # -step
            hk["mute"]: self.controller.toggle_mute,
        }

        for shortcut, callback in hotkey_map.items():
            if shortcut:
                try:
                    keyboard.add_hotkey(shortcut, callback)
                    logger.info(f"Hotkey configurada: {shortcut}")
                except Exception as e:
                    logger.error(f"Erro ao registrar hotkey '{shortcut}': {e}")

        logger.info("Sistema de Hotkeys configurado com sucesso.")

