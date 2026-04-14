import ctypes
from dataclasses import dataclass
from ctypes import wintypes
from typing import Callable


@dataclass(frozen=True)
class MonitorArea:
    """Representa um monitor e sua work area no Windows."""

    index: int
    label: str
    left: int
    top: int
    right: int
    bottom: int
    work_left: int
    work_top: int
    work_right: int
    work_bottom: int

    @property
    def width(self) -> int:
        return self.work_right - self.work_left

    @property
    def height(self) -> int:
        return self.work_bottom - self.work_top


HUD_POSITION_PRESETS: dict[str, str] = {
    "bottom_right": "Inferior direita",
    "bottom_left": "Inferior esquerda",
    "top_right": "Superior direita",
    "top_left": "Superior esquerda",
    "top_center": "Superior central",
    "bottom_center": "Inferior central",
    "center": "Centralizado",
}


class _MonitorInfo(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", wintypes.RECT),
        ("rcWork", wintypes.RECT),
        ("dwFlags", wintypes.DWORD),
    ]


def _fallback_monitor() -> list[MonitorArea]:
    user32 = ctypes.windll.user32
    screen_w = user32.GetSystemMetrics(0)
    screen_h = user32.GetSystemMetrics(1)
    return [
        MonitorArea(
            index=0,
            label=f"Tela 1 ({screen_w}x{screen_h})",
            left=0,
            top=0,
            right=screen_w,
            bottom=screen_h,
            work_left=0,
            work_top=0,
            work_right=screen_w,
            work_bottom=screen_h,
        )
    ]


def list_monitors() -> list[MonitorArea]:
    """Lista os monitores disponíveis e suas áreas úteis."""
    try:
        monitors: list[MonitorArea] = []
        user32 = ctypes.windll.user32

        monitor_enum_proc = ctypes.WINFUNCTYPE(
            ctypes.c_bool,
            wintypes.HANDLE,
            wintypes.HDC,
            ctypes.POINTER(wintypes.RECT),
            wintypes.LPARAM,
        )

        def _callback(hmonitor, _hdc, _rect, _lparam):
            info = _MonitorInfo()
            info.cbSize = ctypes.sizeof(_MonitorInfo)
            if user32.GetMonitorInfoW(hmonitor, ctypes.byref(info)):
                index = len(monitors)
                monitor_rect = info.rcMonitor
                work_rect = info.rcWork
                monitors.append(
                    MonitorArea(
                        index=index,
                        label=f"Tela {index + 1} ({work_rect.right - work_rect.left}x{work_rect.bottom - work_rect.top})",
                        left=monitor_rect.left,
                        top=monitor_rect.top,
                        right=monitor_rect.right,
                        bottom=monitor_rect.bottom,
                        work_left=work_rect.left,
                        work_top=work_rect.top,
                        work_right=work_rect.right,
                        work_bottom=work_rect.bottom,
                    )
                )
            return True

        callback = monitor_enum_proc(_callback)
        success = user32.EnumDisplayMonitors(0, 0, callback, 0)
        if success and monitors:
            return monitors
    except Exception:
        pass

    return _fallback_monitor()


def get_monitor_by_index(index: int) -> MonitorArea:
    """Retorna o monitor solicitado ou o primeiro monitor disponível."""
    monitors = list_monitors()
    if index < 0 or index >= len(monitors):
        return monitors[0]
    return monitors[index]


def resolve_hud_position(
    monitor: MonitorArea,
    preset: str,
    hud_width: int,
    hud_height: int,
    margin: int = 20,
) -> tuple[int, int]:
    """Resolve coordenadas da janela do HUD com base no monitor e preset."""
    left = monitor.work_left
    top = monitor.work_top
    right = monitor.work_right
    bottom = monitor.work_bottom

    max_left = max(left + 8, right - hud_width - 8)
    max_top = max(top + 8, bottom - hud_height - 8)

    if preset == "bottom_left":
        target_left = left + margin
        target_top = bottom - hud_height - margin
    elif preset == "top_right":
        target_left = right - hud_width - margin
        target_top = top + margin
    elif preset == "top_left":
        target_left = left + margin
        target_top = top + margin
    elif preset == "top_center":
        target_left = left + (monitor.width - hud_width) // 2
        target_top = top + margin
    elif preset == "bottom_center":
        target_left = left + (monitor.width - hud_width) // 2
        target_top = bottom - hud_height - margin
    elif preset == "center":
        target_left = left + (monitor.width - hud_width) // 2
        target_top = top + (monitor.height - hud_height) // 2
    else:
        target_left = right - hud_width - margin
        target_top = bottom - hud_height - margin

    return max(left + 8, min(target_left, max_left)), max(top + 8, min(target_top, max_top))
