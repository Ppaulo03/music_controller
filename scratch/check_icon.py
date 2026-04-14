import flet as ft

def main(page: ft.Page):
    try:
        icon = ft.Icon(name=ft.icons.PLAY_ARROW)
        print("Icon with name= works")
    except Exception as e:
        print(f"Icon with name= failed: {e}")
    
    try:
        icon = ft.Icon(ft.icons.PLAY_ARROW)
        print("Icon positional works")
    except Exception as e:
        print(f"Icon positional failed: {e}")

    print("Icon attributes:")
    print(dir(ft.Icon))

ft.app(target=main)
