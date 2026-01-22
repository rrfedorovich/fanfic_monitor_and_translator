import os
import shutil
import subprocess


def git_clone():
    """Клонирует репозиторий."""
    subprocess.call(
        "git clone https://github.com/rrfedorovich/fanfic_monitor_and_translator temp_dir",
        shell=True,
    )
    subprocess.call("mv temp_dir/* .", shell=True)
    subprocess.call("mv temp_dir/.* .", shell=True)
    subprocess.call("rm -rf temp_dir", shell=True)


def delete_reload_env():
    """Комментирует строку с перезагрузкой env из файла."""
    file_path = "./src/modules/env_handler/env_handler.py"
    with open(file_path, "r") as f_read:
        content = f_read.read()
    with open(file_path, "w") as f_write:
        content = content.replace(
            "load_dotenv(override=True)", "#load_dotenv(override=True)"
        )
        f_write.write(content)


def set_replit_setting():
    """Настройка команды запуска в Replit."""
    run_str: str = 'run = "python ./src/console.py"'

    with open(".replit", "r") as f_read:
        content = f_read.read()

    with open(".replit", "w") as file:
        if run_str not in content:
            content = run_str + "\n" + content
            file.write(content)


def main():
    set_replit_setting()
    git_clone()
    delete_reload_env()

    subprocess.call(
        "pip install -r requirements_console.txt --user --break-system-packages",
        shell=True,
    )

    if os.path.exists("setting/fanfics_example.csv"):
        shutil.move("setting/fanfics_example.csv", "setting/fanfics.csv")
    if os.path.exists("setting/.env_example"):
        os.remove("setting/.env_example")


if __name__ == "__main__":
    main()
