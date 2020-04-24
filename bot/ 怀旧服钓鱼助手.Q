[General]
SyntaxVersion=2
BeginHotkey=121
BeginHotkeyMod=0
PauseHotkey=0
PauseHotkeyMod=0
StopHotkey=123
StopHotkeyMod=0
RunOnce=1
EnableWindow=
MacroID=a1ea15e8-8d4a-41d9-8846-cfb1e37fb3a6
Description=怀旧服自动钓鱼
Enable=1
AutoRun=0
[Repeat]
Type=0
Number=1
[SetupUI]
Type=2
QUI=
[Relative]
SetupOCXFile=
[Comment]

[Script]
// 鼠标外观
Dim cursor_shape
// 鼠标位置
Dim cursor_x,cursor_y

// 鼠标形状
// 正常为手指 特征码 965986689
// 鱼漂为齿轮，特征码 1884068285

Rem begin
Delay 100
// ESC退出脚本
key = GetLastKey()
If key = 27 Then 
	ExitScript
End If

// 获取合成器窗口大小
soundWin = Plugin.Window.Find("#32770","音量合成器 - 扬声器 (Realtek High Definition Audio)")
If soundWin = 0 Then 
	MsgBox "没有打开音量合成器"
	ExitScript	
End If
soundRect = Plugin.Window.GetClientRect(soundWin)
Dim soundArray
soundArray = Split(soundRect, "|")
sw_left = Clng(soundArray(0))
sw_top = Clng(soundArray(1))
sw_right = Clng(soundArray(2))
sw_bottom = Clng(soundArray(3))
//Call fishSound

// 获取魔兽世界窗口信息
wowWin = Plugin.Window.Find("GxWindowClass", "魔兽世界")
If wowWin = 0 Then 
	MsgBox "没有运行魔兽世界"
	ExitScript
End If
Plugin.Window.Active (wowWin)
wowRect = Plugin.Window.GetClientRect(wowWin)
Dim wowArray
wowArray = Split(wowRect, "|")
ww_left = Clng(wowArray(0))
ww_top = Clng(wowArray(1))
ww_right = Clng(wowArray(2))
ww_bottom = Clng(wowArray(3))

// 计算水域(中上)
ww_size_w = ww_right - ww_left
ww_size_h = ww_bottom - ww_top
water_l = ww_left + ww_size_w / 5
water_r = ww_left + (ww_size_w / 5) * 4
water_t = ww_top
water_b = ww_top + ww_size_h / 2
Delay 100

// 甩钩
KeyPress "1", 1
Delay 200
Call mouse(water_l, water_r, water_t, water_b, 8, 25)

////////////////////////////////////////////////////////////////////
// 函数

// 刷屏寻找鱼漂鼠标位置
// 参数是滑动范围和滑动步距
Function mouse(left, right, top, bottom, stepx, stepy)
	mouse_x = left + 5
	mouse_y = bottom - 5
	While top < mouse_y and mouse_y < bottom
		While left < mouse_x and mouse_x < right
			// ESC退出脚本
			key = GetLastKey()
			If key = 27 Then 
				ExitScript
			End If
			MoveTo mouse_x, mouse_y
			If findFishMouse = 1 Then 
				Call fish
			End If
			Delay 8
			mouse_x = mouse_x + stepx
		Wend
		Delay 8
		mouse_y = mouse_y - stepy
		mouse_x = left + 1
	Wend
	Goto begin
End Function

// 判断鼠标是否在鱼漂上
Function findFishMouse()
	mouseShape = GetCursorShape(0)
	If mouseShape = 1884068285 Then 
		findFishMouse = 1
	Else 
		findFishMouse = 0
	End If
End Function

// 找到鱼漂调用此函数
// 18秒倒计时，每隔300毫秒进行一次声音判定
Function fish
	GetCursorPos x, y
	MoveTo x - 5, y
	Delay 100
	fishtime = 60
	While fishtime > 0
		If fishSound = 1 Then 
			RightClick 1
			Delay 1000
			Goto begin
		End If
		fishtime = fishtime - 1
		Delay 300
	Wend
	// 没有鱼上钩，重新下饵
	Goto begin
End Function

// 声音判定
Function fishSound()
	TracePrint "call fishSound"
	color1 = GetPixelColor(sw_left + 56, sw_bottom - 92)	
	IfColor sw_left + 56, sw_bottom - 92, "E7EAEA", 2 Then
		fishSound = 0
	Else 
		fishSound = 1
	End If
End Function
