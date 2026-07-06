@echo off
cd /d G:\workbuddy\2026-06-28-23-34-20\silver-pulse
echo === Silver Pulse 每日更新 ===
echo [%date% %time%] 开始采集RSS...
C:\Users\shuan\.workbuddy\binaries\python\envs\silver-pulse\Scripts\python collector.py
echo [%date% %time%] 生成资讯看板...
C:\Users\shuan\.workbuddy\binaries\python\envs\silver-pulse\Scripts\python generator.py
echo [%date% %time%] 生成企业库...
C:\Users\shuan\.workbuddy\binaries\python\envs\silver-pulse\Scripts\python gen_enterprise.py
echo [%date% %time%] 完成！打开 output\index.html 查看
pause
