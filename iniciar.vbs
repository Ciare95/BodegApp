Dim shell
Set shell = CreateObject("WScript.Shell")

Dim base
base = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\") - 1)

' Backend (Django sirve el frontend por el puerto 8000)
shell.Run "cmd /c """ & base & "\iniciar_back.bat""", 0, False

' Esperar y abrir Chrome
WScript.Sleep 5000
shell.Run "chrome http://localhost:8000"
