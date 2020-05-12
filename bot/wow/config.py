import pyautogui

# 是否调试
debug = True

# 是否单步调试
debug_step = True

# 魔兽窗口句柄
hwnd = 0

# 获取当前屏幕分辨率
screenWidth, screenHeight = pyautogui.size()

# 截图调整参数
# 截图额外调整参数(根据hwnd截图有额外的部分并非精确的窗口区域)
# 到新的机器需要检查调整
sc_offset_left = 7
sc_offset_top = 0
sc_offset_right = 7
sc_offset_bottom = 7
titleHeight = 30
frameSize = 1

# 是否杀中立怪
kill_neutral = True

def setHwnd(h):
    global hwnd
    hwnd = h
