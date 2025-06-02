#for cfg file
import subprocess
import sys
from tqdm import tqdm
import time

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    try:
        with open('requirements.cfg', 'r') as file:
            packages = [line.strip() for line in file.readlines() if line.strip()]
        
        total_packages = len(packages)
        
        if total_packages == 0:
            print("Нет библиотек для установки.")
            return
        
        print("Начинаем установку зависимостей...")
        
        for package in tqdm(packages, desc="Установка библиотек", unit="библиотека"):
            install(package)
            time.sleep(0.1)  # Задержка для визуального эффекта прогресс-бара
            
        print("\nВсе зависимости успешно установлены! Теперь вы можете запустить Extract")
        
    except FileNotFoundError:
        print("Файл requirements.cfg не найден.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при установке {package}: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    main()
