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
MacroID=b268ce04-d1db-4125-8243-ab347c5c664b
Description=京喜机器人
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
Dim x, y

Rem begin
Delay 100

// 获取京喜工厂窗口信息
jxWin = Plugin.Window.Find("Chrome_WidgetWin_0", "京喜")
If jxWin = 0 Then 
	MsgBox "没有运行京喜"
	ExitScript
End If
Plugin.Window.Active (jxWin)
winRect = Plugin.Window.GetClientRect(jxWin)
Dim winArray
winArray = Split(winRect, "|")
w_left = Clng(winArray(0))
w_top = Clng(winArray(1))
w_right = Clng(winArray(2))
w_bottom = Clng(winArray(3))
Delay 200

// 判定电力是否到达300
color1 = GetPixelColor(w_left + 188, w_bottom - 212)
TracePrint(color1)
If color1 = "00B1FF" Then
	// 已到300，点击
	MoveTo w_left + 188, w_bottom - 212
	LeftClick 1
	// 10分钟后再检查
	Delay 600000
Else 
	// 1分钟检查一次
	Delay 60000
End If

// 继续
Goto begin

