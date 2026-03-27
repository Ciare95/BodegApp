Dim shell
Set shell = CreateObject("WScript.Shell")

Dim base
base = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\") - 1)

' Liberar puerto 80
shell.Run "cmd /c for /f ""tokens=5"" %a in ('netstat -aon ^| findstr "":80 ""') do taskkill /PID %a /F", 0, True

' Backend
shell.Run "cmd /c """ & base & "\venv\Scripts\python.exe"" """ & base & "\manage.py"" runserver 0.0.0.0:8000", 0, False

' Frontend
shell.Run "cmd /c cd /d """ & base & "\frontend"" && npm run build && npm run preview -- --port 80", 0, False

' Esperar y abrir Chrome
WScript.Sleep 15000
shell.Run "chrome http://localhost"
