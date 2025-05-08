@echo off
set SERVER=root@5.129.196.118
set KEY=C:\Users\danya\.ssh\id_ed25519
set REMOTE_PORT=3000
set LOCAL_PORT=8000

:loop
echo Starting SSH tunnel...
ssh -i "%KEY%" -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -o ExitOnForwardFailure=yes -N -R 0.0.0.0:%REMOTE_PORT%:127.0.0.1:%LOCAL_PORT% %SERVER%

echo SSH tunnel disconnected. Reconnecting in 5 seconds...
timeout /t 5
goto loop