#!/bin/bash
# TaiLocal Mac 一键打包 → dist/TaiLocal
pip3 install pyinstaller -q
pyinstaller --onefile --windowed --name TaiLocal tailocal.py
echo "打包完成！软件在 dist/TaiLocal"
