import ctypes

def get_screen_info():
    user32 = ctypes.windll.user32
    w = user32.GetSystemMetrics(0)
    h = user32.GetSystemMetrics(1)
    print(f"Physical/Raw System Metrics: {w}x{h}")
    
    # get DPI
    hdc = user32.GetDC(0)
    dpiX = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88) # LOGPIXELSX
    ctypes.windll.user32.ReleaseDC(0, hdc)
    print(f"DPI: {dpiX} (Scale: {dpiX/96.0 * 100}%)")

if __name__ == '__main__':
    get_screen_info()
    
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        print("Set DPI Awareness ON")
    except: ...
    get_screen_info()
