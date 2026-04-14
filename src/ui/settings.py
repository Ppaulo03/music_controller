import flet as ft
from src.core.config import ConfigManager, AppConfig


def main(page: ft.Page):
    page.title = "Configurações - Music HUD"
    page.window.width = 400
    page.window.height = 600
    page.window.resizable = False
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20

    config_manager = ConfigManager()
    cfg = config_manager.load()

    # --- Controles de Volume e HUD ---
    volume_step = ft.Slider(
        min=1, max=20, divisions=19, label="{value}%", value=cfg.volume_step
    )
    hud_time = ft.Slider(
        min=1, max=10, divisions=9, label="{value}s", value=cfg.hud_display_time
    )

    # --- Hotkeys ---
    hk_play = ft.TextField(label="Play/Pause", value=cfg.hotkeys["play_pause"])
    hk_next = ft.TextField(label="Próxima", value=cfg.hotkeys["next_track"])
    hk_prev = ft.TextField(label="Anterior", value=cfg.hotkeys["previous_track"])
    hk_up = ft.TextField(label="Volume +", value=cfg.hotkeys["volume_up"])
    hk_down = ft.TextField(label="Volume -", value=cfg.hotkeys["volume_down"])
    hk_mute = ft.TextField(label="Mute", value=cfg.hotkeys["mute"])

    # --- Gatilhos (Triggers) ---
    t_vol = ft.Switch(label="Mudar Volume", value=cfg.triggers["volume"])
    t_meta = ft.Switch(label="Mudar Música", value=cfg.triggers["metadata"])
    t_play = ft.Switch(label="Pausar/Play", value=cfg.triggers["playback"])

    def save_settings(e):
        new_cfg = AppConfig(
            volume_step=int(volume_step.value),
            hud_display_time=int(hud_time.value),
            hotkeys={
                "play_pause": hk_play.value,
                "next_track": hk_next.value,
                "previous_track": hk_prev.value,
                "volume_up": hk_up.value,
                "volume_down": hk_down.value,
                "mute": hk_mute.value,
            },
            triggers={
                "volume": t_vol.value,
                "metadata": t_meta.value,
                "playback": t_play.value,
            },
        )
        config_manager.save(new_cfg)
        page.snack_bar = ft.SnackBar(ft.Text("Configurações salvas com sucesso!"))
        page.snack_bar.open = True
        page.update()

    page.add(
        ft.Text("Ajustes Gerais", size=20, weight=ft.FontWeight.BOLD),
        ft.Text("Passo do Volume (%)", size=12, color=ft.Colors.WHITE70),
        volume_step,
        ft.Text("Tempo HUD (segundos)", size=12, color=ft.Colors.WHITE70),
        hud_time,
        ft.Divider(),
        ft.Text("Atalhos de Teclado", size=20, weight=ft.FontWeight.BOLD),
        hk_play,
        ft.Row([hk_prev, hk_next]),
        ft.Row([hk_up, hk_down]),
        hk_mute,
        ft.Divider(),
        ft.Text("HUD Aparece Quando:", size=20, weight=ft.FontWeight.BOLD),
        t_vol,
        t_meta,
        t_play,
        ft.Container(height=20),
        ft.ElevatedButton(
            "Salvar Configurações", 
            on_click=save_settings, 
            icon=ft.Icons.SAVE,
            style=ft.ButtonStyle(bgcolor=ft.Colors.AMBER, color=ft.Colors.BLACK)
        ),
    )


if __name__ == "__main__":
    ft.app(target=main)
