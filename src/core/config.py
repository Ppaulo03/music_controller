import json
import logging
import os
from dataclasses import asdict, dataclass, field
from typing import Any, Dict

logger = logging.getLogger(__name__)


@dataclass
class AppConfig:
    """Estrutura de dados para as configurações do aplicativo."""

    volume_step: int = 5
    hud_display_time: int = 3
    # Atalhos Globais
    hotkeys: Dict[str, str] = field(
        default_factory=lambda: {
            "play_pause": "alt gr+p",
            "next_track": "alt gr+right",
            "previous_track": "alt gr+left",
            "volume_up": "alt gr+up",
            "volume_down": "alt gr+down",
            "mute": "alt gr+m",
        }
    )
    # Gatilhos para o HUD aparecer
    triggers: Dict[str, bool] = field(
        default_factory=lambda: {
            "volume": True,
            "metadata": True,
            "playback": True,
        }
    )


class ConfigManager:
    """Gerenciador de persistência para configurações em JSON."""

    def __init__(self, config_file: str = "settings.json") -> None:
        self.config_path = config_file
        self.config = self.load()

    def load(self) -> AppConfig:
        """Carrega configurações do arquivo ou cria padrões se não existir."""
        if not os.path.exists(self.config_path):
            logger.info("Arquivo de configurações não encontrado. Criando padrões...")
            default_cfg = AppConfig()
            # Salva os padrões imediatamente para criar o arquivo
            self.config = default_cfg
            self.save()
            return default_cfg

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return AppConfig(**data)
        except Exception as e:
            logger.error(f"Erro ao carregar configurações: {e}. Usando padrões.")
            return AppConfig()

    def save(self, config: AppConfig = None) -> None:
        """Salva o estado atual das configurações no arquivo JSON."""
        if config:
            self.config = config

        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(asdict(self.config), f, indent=4, ensure_ascii=False)
            logger.info(f"Configurações salvas em {self.config_path}")
        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {e}")

    def get_all(self) -> AppConfig:
        return self.config
