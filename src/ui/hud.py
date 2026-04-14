import asyncio
import ctypes
import logging
from typing import Optional

import flet as ft

from src.core.display import get_monitor_by_index, resolve_hud_position
from src.core.state import AppState

logger = logging.getLogger(__name__)


class MusicHUD:
    """Interface visual (HUD) completa com status de reprodução, progresso e volume."""

    def __init__(self, state: AppState) -> None:
        self.state = state
        self.page: Optional[ft.Page] = None
        self._hide_task: Optional[asyncio.Task] = None
        self._window_width: int = 380
        self._window_height: int = 120

    def _calculate_window_size(self, monitor_width: int) -> tuple[int, int]:
        """Calcula tamanho seguro do HUD para não sair da tela."""

        # Mantem um HUD compacto e reduz em telas menores.
        max_width = max(300, monitor_width - 40)
        width = min(380, max_width)
        # Altura um pouco maior para comportar ultima linha (tempo/volume) sem recorte.
        height = 138
        return width, height

    def _force_window_stealth(self) -> None:
        """Arranca a barra de título e bordas via Win32 API."""
        try:
            hwnd = ctypes.windll.user32.FindWindowW(None, "Music HUD")
            if hwnd:
                style = ctypes.windll.user32.GetWindowLongW(hwnd, -16)
                new_style = style & ~0x00C00000 
                new_style = new_style & ~0x00040000 
                new_style = new_style & ~0x00080000 
                ctypes.windll.user32.SetWindowLongW(hwnd, -16, new_style)
                
                ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
                ctypes.windll.user32.SetWindowLongW(hwnd, -20, ex_style | 0x00000080 | 0x00000008)
                
                ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x0020 | 0x0002 | 0x0001 | 0x0004)
        except Exception as e:
            logger.warning(f"Win32 Brute Force Error: {e}")

    def _ensure_topmost(self) -> None:
        """Reforça topmost no nível Win32 para evitar perda de prioridade."""
        try:
            hwnd = ctypes.windll.user32.FindWindowW(None, "Music HUD")
            if not hwnd:
                return

            HWND_TOPMOST = -1
            SWP_NOMOVE = 0x0002
            SWP_NOSIZE = 0x0001
            SWP_NOACTIVATE = 0x0010
            SWP_NOOWNERZORDER = 0x0200
            SWP_SHOWWINDOW = 0x0040

            ctypes.windll.user32.SetWindowPos(
                hwnd,
                HWND_TOPMOST,
                0,
                0,
                0,
                0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_NOOWNERZORDER | SWP_SHOWWINDOW,
            )
        except Exception as e:
            logger.warning(f"Erro ao reforcar topmost: {e}")

    def _get_layout(self) -> tuple[int, int, int, int]:
        """Resolve monitor selecionado e posição do HUD a partir da configuração."""
        cfg = self.state.config.load()
        monitor = get_monitor_by_index(cfg.hud_monitor)
        width, height = self._calculate_window_size(monitor.width)
        left, top = resolve_hud_position(monitor, cfg.hud_position, width, height)
        return width, height, left, top

    def apply_layout(self) -> None:
        """Aplica tamanho e posição atuais do HUD conforme a configuração."""
        if not self.page:
            return

        width, height, target_left, target_top = self._get_layout()
        self._window_width = width
        self._window_height = height
        self.page.window.width = width
        self.page.window.height = height
        self.page.window.left = target_left
        self.page.window.top = target_top
        self.page.update()

    async def main(self, page: ft.Page) -> None:
        """Configuração da página Flet com todos os indicadores visuais."""
        self.page = page
        self.page.title = "Music HUD"
        self.page.window.left = -32000
        self.page.window.top = -32000
        self.page.window.visible = False
        self.page.window.opacity = 0.0
        
        self.page.window.bgcolor = "#00000000"
        self.page.bgcolor = "#00000000"
        
        self.page.window.frameless = True
        self.page.window.always_on_top = True
        self.page.window.skip_task_bar = True
        self.page.window.resizable = False
        # Configurações de tamanho inicial (responsivo)
        self.apply_layout()

        self.page.update()


        # --- Elementos da UI ---
        self.cover = ft.Image(
            src=self.state.metadata.cover or "https://via.placeholder.com/80",
            width=70,  # Reduzido
            height=70, # Reduzido
            border_radius=10,
            fit=ft.BoxFit.COVER,
        )

        self.title = ft.Text(
            self.state.metadata.title or "Nenhuma música",
            size=16, # Reduzido
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE,
            overflow=ft.TextOverflow.ELLIPSIS,
            max_lines=1,
        )

        self.artist = ft.Text(
            self.state.metadata.artist or "Aguardando player...",
            size=13, # Reduzido
            color=ft.Colors.WHITE70,
            overflow=ft.TextOverflow.ELLIPSIS,
            max_lines=1,
        )

        progress_width = max(180, self._window_width - 140)
        self.track_progress_bar = ft.ProgressBar(
            value=self.state.metadata.progress,
            width=progress_width,
            color=ft.Colors.AMBER,
            bgcolor=ft.Colors.WHITE10,
        )


        self.time_text = ft.Text(
            f"{self.state.metadata.position} / {self.state.metadata.duration}",
            size=12,
            color=ft.Colors.WHITE54,
        )

        self.status_icon = ft.Icon(
            ft.Icons.PLAY_ARROW if self.state.metadata.status == "Tocando" else ft.Icons.PAUSE,
            size=16,
            color=ft.Colors.AMBER if self.state.metadata.status == "Tocando" else ft.Colors.WHITE54,
        )

        self.volume_indicator = ft.Row(
            [
                ft.Icon(ft.Icons.VOLUME_UP, size=12, color=ft.Colors.WHITE54),
                ft.Text(f"{self.state.metadata.volume}%", size=12, color=ft.Colors.WHITE54),
            ],
            spacing=5,
        )

        self.container = ft.Container(
            content=ft.Row(
                [
                    self.cover,
                    ft.VerticalDivider(width=10, color=ft.Colors.TRANSPARENT),
                    ft.Column(
                        [
                            self.title,
                            self.artist,
                            ft.Container(height=5),
                            self.track_progress_bar,
                            ft.Row(
                                [
                                    self.status_icon,
                                    self.time_text,
                                    ft.Container(expand=True),
                                    self.volume_indicator,
                                ],
                                alignment=ft.MainAxisAlignment.START,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=10,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=4,
                        expand=True,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=ft.padding.symmetric(horizontal=15, vertical=10),
            bgcolor="#E6050505",
            border_radius=15,
            border=ft.border.all(1, ft.Colors.WHITE10),
        )

        self.page.add(self.container)
        self.state.on_update(self.update_ui)
        
        self.page.update()

        await asyncio.sleep(0.5)
        self._force_window_stealth()
        self._ensure_topmost()

    async def update_ui(self, major: bool = False, category: str = "") -> None:
        """Sincroniza UI. Respeita triggers e tempo de HUD configurados."""
        if not self.page:
            return

        cfg = self.state.config.load()
        
        self.title.value = self.state.metadata.title or "Nenhuma música"
        self.artist.value = self.state.metadata.artist or "Desconhecido"
        self.cover.src = self.state.metadata.cover or "https://via.placeholder.com/80"
        
        # Atualiza Status de Play/Pause
        is_playing = self.state.metadata.status == "Tocando"
        self.status_icon.name = ft.Icons.PLAY_ARROW if is_playing else ft.Icons.PAUSE
        self.status_icon.color = ft.Colors.AMBER if is_playing else ft.Colors.WHITE54

        # Atualiza Tempo e Progresso (Atualização silenciosa)
        self.track_progress_bar.value = self.state.metadata.progress or 0.0
        self.time_text.value = f"{self.state.metadata.position} / {self.state.metadata.duration}"
        
        # Atualiza Volume
        self.volume_indicator.controls[1].value = f"{self.state.metadata.volume}%"
        self.volume_indicator.controls[0].color = ft.Colors.RED if self.state.is_muted else ft.Colors.WHITE54

        # Determina se o HUD deve "acordar" com base nos triggers configurados
        should_show = False
        if major:
            if category == "volume" and cfg.triggers.get("volume", True):
                should_show = True
            elif category == "metadata" and cfg.triggers.get("metadata", True):
                should_show = True
            elif category == "playback" and cfg.triggers.get("playback", True):
                should_show = True

        if should_show:
            await self.show_hud(display_time=cfg.hud_display_time)
        else:
            self.page.update()

    async def show_hud(self, display_time: int = 3) -> None:
        """Exibe o HUD por um tempo determinado."""
        if not self.page:
            return

        if self._hide_task:
            self._hide_task.cancel()

        # Evita flash central: torna visivel fora da tela e reposiciona no mesmo ciclo.
        self.page.window.left = -32000
        self.page.window.top = -32000
        self.page.window.visible = True
        self.page.window.opacity = 0.0
        self.apply_layout()
        self.page.window.opacity = 1.0
        self.page.update()
        self._ensure_topmost()
        
        self._hide_task = asyncio.create_task(self._hide_after_delay(display_time))

    async def _hide_after_delay(self, seconds: int) -> None:

        """Fade out."""
        try:
            await asyncio.sleep(seconds)
            if self.page:
                steps = 10
                for i in range(steps, -1, -1):
                    self.page.window.opacity = i / steps
                    self.page.update()
                    await asyncio.sleep(0.01)
                self.page.window.visible = False
                self.page.update()
        except asyncio.CancelledError:
            pass
