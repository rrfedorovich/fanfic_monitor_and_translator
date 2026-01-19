@echo off


:: Задайте относительный путь для виртуального окружения (папки с ним). Примеры:
:: - если виртуальное окружение .venv и находится в корне проекта, то: set "VENV_NAME=.venv"
:: - если виртуальное окружение with_gui находится в папке .venv в корне проекта, 
::   то: set "VENV_NAME=.venv\with_gui")
:: Для варианта без виртуального окружения оставить строчку ниже закомментированной.
:: set "VENV_NAME=.venv\with_gui"


chcp 65001 > nul

set "projectPath=%~dp0"
set "projectPath=%projectPath:~0,-1%"
set "venvPath=%projectPath%\%VENV_NAME%\Scripts\activate.bat"
set "pythonScriptPath=%projectPath%\src\gui.py"

if defined VENV_NAME (
    echo Пытаемся активировать виртуальное окружение: %VENV_NAME%...

    if exist "%venvPath%" (
        echo Активируем виртуальное окружение...
        call "%venvPath%"
    ) else (
        echo Ошибка: Виртуальное окружение "%venvPath%" не найдено!
        pause
        exit /b 1
    )
) else (
    echo Переменная VENV_NAME не задана. Виртуальное окружение не подключается.
)

if exist "%pythonScriptPath%" (
    echo Запускаем Python-скрипт...
    python "%pythonScriptPath%"
) else (
    echo Ошибка: Файл "%pythonScriptPath%" не найден!
    pause
    exit /b 1
)
