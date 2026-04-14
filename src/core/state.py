import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine, List

from src.core.config import ConfigManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MediaMetadata:
    """Dados puros da mídia recebidos da extensão."""

    title: str = ""
    artist: str = ""
    album: str = ""
    cover: str = ""
    status: str = "Desconhecido"
    volume: int = 50
    duration: str = "0:00"
    position: str = "0:00"
    progress: float = 0.0  # 0.0 a 1.0


@dataclass
class AppState:
    """Estado global compartilhado da aplicação com suporte a observadores."""

    config: ConfigManager = field(default_factory=ConfigManager)
    metadata: MediaMetadata = field(default_factory=MediaMetadata)
    is_muted: bool = False
    last_non_zero_volume: int = 50
    active_connections: int = 0

    # Lista de callbacks assíncronos para notificar mudanças (categoria opcional)
    _listeners: List[Callable[[bool, str], Coroutine[Any, Any, None]]] = field(
        default_factory=list, repr=False
    )

    def on_update(self, callback: Callable[[bool, str], Coroutine[Any, Any, None]]) -> None:
        """Registra um observador para mudanças de estado."""
        self._listeners.append(callback)

    async def notify(self, major: bool = False, category: str = "") -> None:
        """Notifica os observadores. 'category' indica o que mudou (volume, metadata, playback)."""
        for callback in self._listeners:
            try:
                await callback(major, category)
            except Exception:
                pass
