Dim shell
Set shell = CreateObject("WScript.Shell")

Dim base
base = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\") - 1)

' Liberar puerto 80
shell.Run "cmd /c for /f ""tokens=5"" %a in ('netstat -aon ^| findstr "":80 ""') do taskkill /PID %a /F", 0, True

' Backend y frontend via .bat auxiliares (evita problema de espacios en la ruta)
shell.Run "cmd /c """ & base & "\iniciar_back.bat""", 0, False
shell.Run "cmd /c """ & base & "\iniciar_front.bat""", 0, False

' Esperar y abrir Chrome
WScript.Sleep 15000
shell.Run "chrome http://localhost"
