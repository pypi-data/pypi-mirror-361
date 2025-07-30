from PyQt6.QtWidgets import QApplication
import os
import os
import sys

def _configure_qt_plugins():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    possible_plugin_paths = [
        os.path.join(base_dir),
        os.path.join(base_dir, "plugins")
    ]
    
    valid_plugin_path = None
    for path in possible_plugin_paths:
        platforms_path = os.path.join(path, "platforms")
        if os.path.exists(platforms_path) and os.path.exists(os.path.join(platforms_path, "qwindows.dll")):
            valid_plugin_path = path
            break
    
    if not valid_plugin_path:
        raise RuntimeError("Qt插件目录未找到! 请检查部署结构")
    
    os.environ["QT_PLUGIN_PATH"] = valid_plugin_path
    
    if sys.version_info >= (3, 8):
        os.add_dll_directory(base_dir)
        os.add_dll_directory(valid_plugin_path)
    
def HInit(argv):
    _configure_qt_plugins()
    return QApplication(argv)