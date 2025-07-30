# Hwindow.pyi
from typing import Any, Callable, List, Optional, Tuple, Union

class HPoint:
    """表示二维空间中的一个点"""
    def __init__(self, x: float, y: float) -> None: 
        """初始化点坐标"""
    def x(self) -> float: 
        """获取X坐标"""
    def y(self) -> float: 
        """获取Y坐标"""
    def setX(self, x: float) -> None: 
        """设置X坐标"""
    def setY(self, y: float) -> None: 
        """设置Y坐标"""
    def distanceTo(self, other: 'HPoint') -> float: 
        """计算到另一个点的距离"""

class HRect:
    """表示二维矩形区域"""
    def __init__(self, x: float, y: float, width: float, height: float) -> None: 
        """初始化矩形位置和尺寸"""
    def area(self) -> float: 
        """计算矩形面积"""
    def contains(self, point: HPoint) -> bool: 
        """检查点是否在矩形内"""
    def united(self, other: 'HRect') -> 'HRect': 
        """返回与另一个矩形的并集区域"""

class HColor:
    """表示RGBA颜色"""
    def __init__(self, r: int = 0, g: int = 0, b: int = 0, a: int = 255) -> None: 
        """初始化颜色分量 (0-255)"""
    def red(self) -> int: 
        """获取红色分量"""
    def green(self) -> int: 
        """获取绿色分量"""
    def blue(self) -> int: 
        """获取蓝色分量"""
    def alpha(self) -> int: 
        """获取透明度分量"""
    def lighter(self) -> 'HColor': 
        """返回更亮的颜色"""
    def darker(self) -> 'HColor': 
        """返回更暗的颜色"""

class HIcon:
    """表示应用程序图标"""
    def __init__(self, path: str = "") -> None: 
        """从文件路径加载图标"""
    def isNull(self) -> bool: 
        """检查图标是否为空"""
    def load(self, path: str) -> None: 
        """从文件加载图标"""
    def path(self) -> str: 
        """获取图标文件路径"""

class HMenu:
    """表示菜单栏中的菜单"""
    def __init__(self, title: str = "") -> None: 
        """创建带标题的菜单"""
    def setTitle(self, title: str) -> None: 
        """设置菜单标题"""
    def title(self) -> str: 
        """获取菜单标题"""
    def addAction(self, text: str) -> 'HAction': 
        """添加菜单项并返回动作对象"""
    def addSeparator(self) -> None: 
        """添加分隔线"""

class HAction:
    """表示可触发的菜单动作"""
    def __init__(self, text: str) -> None: 
        """创建带文本的动作"""
    def setText(self, text: str) -> None: 
        """设置动作显示文本"""
    def text(self) -> str: 
        """获取动作显示文本"""
    def setShortcut(self, shortcut: str) -> None: 
        """设置快捷键"""
    def triggered(self, callback: Callable[[], None]) -> None: 
        """设置触发回调函数"""

class HStatusBar:
    """表示窗口状态栏"""
    def __init__(self) -> None: 
        """创建状态栏"""
    def showMessage(self, message: str, timeout: int = 0) -> None: 
        """显示临时消息（timeout=0表示永久）"""
    def clearMessage(self) -> None: 
        """清除临时消息"""
    def addPermanentWidget(self, text: str) -> None: 
        """添加永久性文本部件"""

class HButton:
    """表示可点击的按钮"""
    def __init__(self, text: str = "") -> None: 
        """创建带文本的按钮"""
    def setText(self, text: str) -> None: 
        """设置按钮文本"""
    def text(self) -> str: 
        """获取按钮文本"""
    def clicked(self, callback: Callable[[], None]) -> None: 
        """设置点击回调函数"""

class HLabel:
    """表示文本标签"""
    def __init__(self, text: str = "") -> None: 
        """创建带文本的标签"""
    def setText(self, text: str) -> None: 
        """设置标签文本"""
    def text(self) -> str: 
        """获取标签文本"""
    def setAlignment(self, alignment: int) -> None: 
        """设置文本对齐方式"""

class HProgressBar:
    """表示进度条"""
    def __init__(self) -> None: 
        """创建进度条"""
    def setRange(self, min: int, max: int) -> None: 
        """设置进度范围"""
    def setValue(self, value: int) -> None: 
        """设置当前进度值"""
    def value(self) -> int: 
        """获取当前进度值"""
    def setFormat(self, format: str) -> None: 
        """设置显示格式"""

class HMainWindow:
    """表示应用程序主窗口"""
    def __init__(self) -> None: 
        """创建主窗口"""
    def setTitle(self, title: str) -> None: 
        """设置窗口标题"""
    def title(self) -> str: 
        """获取窗口标题"""
    def resize(self, width: int, height: int) -> None: 
        """调整窗口尺寸"""
    def move(self, x: int, y: int) -> None: 
        """移动窗口位置"""
    def show(self) -> None: 
        """显示窗口"""
    def close(self) -> None: 
        """关闭窗口"""
    def setIcon(self, icon: HIcon) -> None: 
        """设置窗口图标"""
    def createMenu(self, title: str) -> HMenu: 
        """创建菜单并返回"""
    def addMenu(self, menu: HMenu) -> None: 
        """添加菜单到菜单栏"""
    def setStatusBar(self, status_bar: HStatusBar) -> None: 
        """设置状态栏"""
    def statusBar(self) -> HStatusBar: 
        """获取当前状态栏"""
    def addWidget(self, widget: Any) -> None: 
        """添加部件到窗口"""

# 数学函数
def hSin(angle: float) -> float: 
    """计算角度的正弦值（角度制）"""
def hCos(angle: float) -> float: 
    """计算角度的余弦值（角度制）"""
def hTan(angle: float) -> float: 
    """计算角度的正切值（角度制）"""
def hDegreesToRadians(degrees: float) -> float: 
    """角度转弧度"""
def hRadiansToDegrees(radians: float) -> float: 
    """弧度转角度"""
def hHypotenuse(a: float, b: float) -> float: 
    """计算直角三角形的斜边长度"""
def hRandom(min: float, max: float) -> float: 
    """生成指定范围内的随机浮点数"""

# 字符串操作
def hToUpper(s: str) -> str: 
    """将字符串转换为大写"""
def hToLower(s: str) -> str: 
    """将字符串转换为小写"""
def hSplit(s: str, delimiter: str = "") -> List[str]: 
    """分割字符串（默认按空白字符分割）"""
def hJoin(strings: List[str], delimiter: str) -> str: 
    """连接字符串列表"""
def hStartsWith(s: str, prefix: str) -> bool: 
    """检查字符串是否以指定前缀开头"""

# 系统函数
def hCurrentTimeMillis() -> int: 
    """获取当前时间戳（毫秒）"""
def hSleep(milliseconds: int) -> None: 
    """线程休眠指定毫秒数"""
def hOsName() -> str: 
    """获取操作系统名称"""
def hClipboardText() -> str: 
    """获取剪贴板文本内容"""
def hSetClipboardText(text: str) -> None: 
    """设置剪贴板文本内容"""
def hShowMessage(title: str, message: str) -> None: 
    """显示消息对话框"""
def hOpenUrl(url: str) -> bool: 
    """用默认浏览器打开URL（返回是否成功）"""
def hFileExists(path: str) -> bool: 
    """检查文件是否存在"""
def hDirectoryExists(path: str) -> bool: 
    """检查目录是否存在"""
def hCurrentPath() -> str: 
    """获取当前工作目录"""
def hSetCurrentPath(path: str) -> bool: 
    """设置当前工作目录（返回是否成功）"""
def hFileSize(path: str) -> int: 
    """获取文件大小（字节）"""
def hAfter(milliseconds: int, callback: Callable[[], None]) -> None: 
    """延迟执行回调函数（毫秒）"""