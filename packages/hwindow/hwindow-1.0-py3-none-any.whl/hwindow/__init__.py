from data.Core.Hwindow import *
from data.Core.data import HInit
import typing, os, subprocess
import data.Core.Hwindow as hw
import sys
del HMainWindow

def getScreenSize():
    platform = sys.platform
    
    # Windows
    if platform == "win32":
        import ctypes
        user32 = ctypes.windll.user32
        return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    
    # macOS
    elif platform == "darwin":
        try:
            output = subprocess.check_output(
                ["system_profiler", "SPDisplaysDataType"]
            ).decode("utf-8")
            for line in output.splitlines():
                if "Resolution:" in line:
                    parts = line.split(":")
                    if len(parts) > 1:
                        resolution = parts[1].strip().split(" ")[0]
                        if "x" in resolution:
                            return tuple(map(int, resolution.split("x")))
        except:
            pass
    
    # Linux/Unix
    else:
        try:
            # 尝试读取虚拟帧缓冲区
            with open("/sys/class/graphics/fb0/virtual_size", "r") as f:
                data = f.read().strip().split(',')
                if len(data) == 2:
                    return int(data[0]), int(data[1])
        except:
            try:
                # 尝试使用xrandr
                output = subprocess.check_output(["xrandr"]).decode("utf-8")
                for line in output.splitlines():
                    if "*" in line:
                        resolution = line.split()[0]
                        return tuple(map(int, resolution.split("x")))
            except:
                pass
    
    # 默认分辨率
    return 1920, 1080

class HWindow(hw.HMainWindow):
    """自定义窗口类，继承自HMainWindow"""
    DEFAULT_ICON_PATH = os.path.dirname(os.path.realpath(__file__)) + r"\data\_image\icon.ico"  # 默认图标路径
    
    def __init__(
        self, 
        title: typing.Optional[str] = None, 
        icon_path: typing.Optional[str] = None,
        width: int = 800,
        height: int = 600,
        x: int = None,
        y: int = None
    ):
        super().__init__()
        
        if title is not None:
            self.setTitle(title)
        else:
            self.setTitle("HWindow - MainWindow")

        if x or y is not None:
            self.move(x,y)

        elif x and y is None:
            self.move(getScreenSize)

        self.resize(width, height)
        
        final_icon_path = icon_path or self.DEFAULT_ICON_PATH
        if os.path.exists(final_icon_path):
            self.setIcon(HIcon(final_icon_path))
        else:
            print(f"Warning: Icon file not found at {final_icon_path}")

del hw, typing, subprocess, os, sys