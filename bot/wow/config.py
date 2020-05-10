# 是否调试
debug = True

# 魔兽窗口句柄
hwnd = 0

# 获取当前屏幕分辨率
screenWidth, screenHeight = pyautogui.size()

# 标题栏和任务栏尺寸
titleHeight = 30
taskHeight = 40

# 截图额外调整参数(根据hwnd截图有额外的部分并非精确的窗口区域)
sc_offset_x = 8
sc_offset_y = 1
