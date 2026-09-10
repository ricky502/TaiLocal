@echo off
REM TaiLocal Windows 一键打包 → dist/TaiLocal.exe
pip install pyinstaller -q
pyinstaller --onefile --noconsole --name TaiLocal tailocal.py
echo.
echo 打包完成！软件在 dist\TaiLocal.exe
pause
