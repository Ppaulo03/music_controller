from dataclasses import dataclass, field


@dataclass(frozen=True)
class MediaMetadata:
    """Dados puros da mídia recebidos da extensão."""

    title: str = ""
    artist: str = ""
    album: str = ""
    cover: str = ""
    status: str = "Desconhecido"
    volume: int = 50


@dataclass
class AppState:
    """Estado global compartilhado da aplicação."""

    metadata: MediaMetadata = field(default_factory=MediaMetadata)
    is_muted: bool = False
    last_non_zero_volume: int = 50
    active_connections: int = 0
