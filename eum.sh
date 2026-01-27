#!/bin/bash

readonly VENV_DIR="venv"
readonly LOG_FILE="eum-shared/eum.log"
readonly GIT_ERROR_FILE=".git_error.tmp"
readonly PROTECTED_FILES=("data/users.json" "eum-shared/config.ini")

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m'

fade_art() {
    local art=(" ____    __   __   __    ____    ______  ____    ______   
/\  _`\ /\ \ /\ \ /\ \__/\  _`\ /\  _  \/\  _`\ /\__  _\  
\ \ \L\_\ `\`\/'/'\ \ ,_\ \ \L\ \ \ \L\ \ \ \/\_\/_/\ \/  
 \ \  _\L`\/ > <   \ \ \/\ \ ,  /\ \  __ \ \ \/_/_ \ \ \  
  \ \ \L\ \ \/'/\`\ \ \ \_\ \ \\ \\ \ \/\ \ \ \L\ \ \ \ \ 
   \ \____/ /\_\\ \_\\ \__\\ \_\ \_\ \_\ \_\ \____/  \ \_\
    \/___/  \/_/ \/_/ \/__/ \/_/\/ /\/_/\/_/\/___/    \/_/                  ")
    local colors=("36" "36;1" "36;2" "36;1" "36" "34;1" "34" "34;2" "34;1" "34" "36")
    for i in {0..10}; do
        clear
        for line in "${art[@]}"; do
            echo -ne "\033[${colors[$i]}m$line\033[0m\n"
        done
        sleep 0.1
    done
    clear
    for line in "${art[@]}"; do
        echo -e "${MAGENTA}$line${NC}"
    done
    sleep 0.5
}

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

cleanup() {
    rm -f "$GIT_ERROR_FILE"
    log "Очистка временных файлов выполнена"
}

print_header() {
    clear
    fade_art
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗"
    echo -e "║ При первом запуске, Extract загружается дольше чем обычно  ║"
    echo -e "╚════════════════════════════════════════════════════════════╝${NC}"
    log "Отображение заголовка"
}

print_separator() {
    echo -e "${BLUE}──────────────────────────────────────────────────────────────${NC}"
}

print_message() {
    echo -e "${YELLOW}[i] $1${NC}"
    log "MESSAGE: $1"
}

print_success() {
    echo -e "${GREEN} [✓] $1${NC}"
    log "SUCCESS: $1"
}

print_error() {
    echo -e "${RED}   [✗] ОШИБКА: $1${NC}" >&2
    log "ERROR: $1"
}

print_warning() {
    echo -e "${YELLOW} [!] ВНИМАНИЕ: $1${NC}"
    log "WARNING: $1"
}

progress_bar() {
    local duration=$1
    local message=$2
    echo -ne "${BLUE}┌${CYAN} $message\n${BLUE}└[${NC}"
    for ((i=0; i<=50; i++)); do
        echo -ne "${GREEN}■${NC}"
        sleep $duration
    done
    echo -e "${BLUE}]${NC}"
    log "Прогресс бар завершен: $message"
}

check_python_version() {
    log "Проверка версии Python..."
    if ! command -v python3 &>/dev/null; then
        print_error "Python3 не установлен!"
        exit 1
    fi
    local required_major=3
    local required_minor=6
    local current_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null)
    if [ $? -ne 0 ]; then
        print_error "Не удалось определить версию Python"
        exit 1
    fi
    local current_major=$(echo "$current_version" | cut -d. -f1)
    local current_minor=$(echo "$current_version" | cut -d. -f2)
    if [ "$current_major" -lt "$required_major" ] || { [ "$current_major" -eq "$required_major" ] && [ "$current_minor" -lt "$required_minor" ]; }; then
        print_error "Требуется Python ${required_major}.${required_minor}+ (установлено: $current_version)"
        exit 1
    fi
    print_success "Версия Python $current_version совместима"
}

check_git_repository() {
    log "Проверка Git репозитория..."
    if [ ! -d ".git" ]; then
        print_error "Скрипт должен запускаться из корня Git-репозитория!"
        exit 1
    fi
    print_success "Git репозиторий обнаружен"
}

check_internet_connection() {
    log "Проверка интернет соединения..."
    print_message "Проверка интернет-соединения..."
    if ping -c 1 -W 2 8.8.8.8 >/dev/null 2>&1 || ping -c 1 -W 2 google.com >/dev/null 2>&1 || ping -c 1 -W 2 github.com >/dev/null 2>&1; then
        print_success "  ✓ Интернет-соединение установлено"
        return 0
    else
        print_warning "  ✗ Не удалось установить соединение"
        return 1
    fi
}

setup_virtualenv() {
    log "Настройка виртуального окружения..."
    if [ ! -d "$VENV_DIR" ]; then
        print_message "Создание виртуального окружения..."
        if ! python3 -m venv "$VENV_DIR" >/dev/null 2>&1; then
            print_error "Не удалось создать виртуальное окружение"
            exit 1
        fi
        print_success "  ✓ Виртуальное окружение создано"
    fi
    if ! source "${VENV_DIR}/bin/activate" >/dev/null 2>&1; then
        print_error "Не удалось активировать виртуальное окружение"
        exit 1
    fi
    print_message "Проверка python-зависимостей..."
    local dependencies=("colorama" "requests")
    local all_ok=true
    for dep in "${dependencies[@]}"; do
        if ! python3 -c "import $dep" 2>/dev/null; then
            if pip install "$dep" >/dev/null 2>&1; then
                print_success "  ✓ Установлен: $dep"
            else
                print_warning "  ✗ Не удалось установить: $dep"
                all_ok=false
            fi
        else
            print_success "  ✓ Уже установлен: $dep"
        fi
    done
    if ! $all_ok; then
        print_warning "Некоторые зависимости не установлены"
    fi
}

check_for_updates() {
    log "Проверка обновлений..."
    if ! current_branch=$(git rev-parse --abbrev-ref HEAD 2>"$GIT_ERROR_FILE"); then
        error_msg=$(cat "$GIT_ERROR_FILE")
        print_error "Ошибка Git: ${error_msg}"
        return 1
    fi
    print_message "Текущая ветка: $current_branch"
    git remote update >/dev/null 2>"$GIT_ERROR_FILE" || {
        error_msg=$(cat "$GIT_ERROR_FILE")
        print_error "Ошибка при обновлении информации о репозитории: ${error_msg}"
        return 1
    }
    local local_commit=$(git rev-parse @)
    local remote_commit=$(git rev-parse "@{u}")
    local base_commit=$(git merge-base @ "@{u}")
    if [ "$local_commit" = "$remote_commit" ]; then
        print_success "  ✓ Установлена последняя версия Extract:"
    print_message "local  - (${local_commit:0:7}) | ExtraHost"
    print_message "remote - (${remote_commit:0:7}) | GitHub"
        return 1
    elif [ "$local_commit" = "$base_commit" ]; then
        print_success "Доступны новое обновление!"
        print_message "Локальный индификатор: ${local_commit:0:7}"
        print_message "Удалённый индификатор: ${remote_commit:0:7}"
        return 0
    elif [ "$remote_commit" = "$base_commit" ]; then
        print_warning "Есть неотправленные локальные изменения"
        return 1
    else
        print_warning "Разошлись истории коммитов"
        return 1
    fi
}


update_repository() {
    log "Начало процесса обновления..."
    print_message "Подготовка к обновлению..."

    local backup_time=$(date +"%Y%m%d_%H%M%S")
    local backup_dir="$HOME/eum_backup_$backup_time"
    mkdir -p "$backup_dir"
    
    if [ -f "data/users.json" ]; then
        cp -a "data/users.json" "$backup_dir/" || {
            print_error "Не удалось создать резервную копию users.json"
            return 1
        }
    fi
    
    if [ -f "eum-shared/config.ini" ]; then
        cp -a "eum-shared/config.ini" "$backup_dir/" || {
            print_error "Не удалось создать резервную копию config.ini"
            return 1
        }
    fi
    
    print_success "Копирование пользовательских данных..."
    print_message "Подключение к серверу | ExtraHost -> GitHub"
    print_success "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

    print_message "Загрузка обновлений с сервера..."
    if git fetch origin && git reset --hard origin/$(git rev-parse --abbrev-ref HEAD); then
        print_success "Extract успешно обновлен"
    else
        print_error "Ошибка при обновлении Extract"
        return 1
    fi

    print_message "Восстановление пользовательских данных..."
    if [ -f "$backup_dir/users.json" ]; then
        mkdir -p "data"
        cp -a "$backup_dir/users.json" "data/" || {
            print_error "Не удалось восстановить users.json"
            return 1
        }
    fi
    
    if [ -f "$backup_dir/config.ini" ]; then
        mkdir -p "eum-shared"
        cp -a "$backup_dir/config.ini" "eum-shared/" || {
            print_error "Не удалось восстановить config.ini"
            return 1
        }
    fi
    
    print_success "Очистка временных файлов"

    print_message "Обновление ключевых токенов..."
    setup_virtualenv

    if [ ! -f "data/users.json" ]; then
        print_error "Файл users.json отсутствует после восстановления!"
        print_message "Попытка восстановить из резервной копии..."
        if [ -f "$backup_dir/users.json" ]; then
            cp -a "$backup_dir/users.json" "data/" && print_success "Файл users.json восстановлен"
        else
            print_error "Резервная копия users.json не найдена"
            echo "{}" > "data/users.json"
            print_success "сброс - % - user#0"
        fi
    fi

    print_message "Итоговая отчистка..."
    rm -rf "$backup_dir" || print_warning "Не удалось удалить резервную копию"
    
    print_success "Обновление завершено успешно!"
    return 0
}

main() {
    print_header
    progress_bar 0.02 "Инициализация системы..."

    check_python_version
    check_git_repository
    setup_virtualenv

    if check_internet_connection; then
        if check_for_updates; then
            print_separator
            echo -ne "${YELLOW}Установить обновление? [y/n]: ${NC}"
            read -r choice
            progress_bar 0.01 "Проверка ключей..."

            if [[ "$choice" =~ ^[YyДд]$ ]]; then
                if update_repository; then
                    print_success "run Extract..."
                else
                    print_warning "Обновление не было применено"
                fi
            else
                print_message "Обновление отменено пользователем"
            fi
        fi
    else
        print_warning "Проверка обновлений пропущена (нет интернет-соединения)"
    fi

    if ! source "${VENV_DIR}/bin/activate" >/dev/null 2>&1; then
        print_error "Не удалось активировать виртуальное окружение"
        exit 1
    fi

    print_separator
    echo -e "${CYAN} - Готово! Вы подготовлены к работе.${NC}"
    echo -e "${MAGENTA}Нажмите Enter для запуска Extract...${NC}"
    read -r
    clear

    python main/data.py
}

trap cleanup EXIT
main