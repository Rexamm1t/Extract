#!/bin/sh

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    clear
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════╗"
    echo "║             EXTRACT UPDATE MANAGER v2.0          ║"
    echo "╚══════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_logs() {
    echo -e "✓ Подгрузка зависимостей"
    sleep 1
    echo -e "✓ Разрешение зависимостей"
    sleep 1
    echo -e "✓ Чтение"
    sleep 1
    echo -e "✓ Очистка"
}

print_message() {
    echo -e "${YELLOW}$1${NC}"
}

print_success() {
    echo -e "${GREEN}$1${NC}"
}

print_error() {
    echo -e "${RED}ОШИБКА: $1${NC}" >&2
}

progress_bar() {
    local duration=$1
    local message=$2
    local width=50
    local increment=$((100/$width))
    
    echo -ne "${BLUE}┌${YELLOW} $message\n${BLUE}└[${NC}"
    
    for ((i=0; i<=width; i++)); do
        echo -ne "${GREEN}#${NC}"
        sleep $duration
    done
    
    echo -e "${BLUE}]${NC}"
}

check_python_version() {
    if ! command -v python3 &>/dev/null; then
        print_error "Python3 не установлен!"
        exit 1
    fi

    required_major=3
    required_minor=6
    current_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null)
    
    if [ $? -ne 0 ]; then
        print_error "Не удалось определить версию Python"
        exit 1
    fi

    current_major=$(echo "$current_version" | cut -d. -f1)
    current_minor=$(echo "$current_version" | cut -d. -f2)

    if [ "$current_major" -lt "$required_major" ] || 
       { [ "$current_major" -eq "$required_major" ] && [ "$current_minor" -lt "$required_minor" ]; }; then
        print_error "Требуется Python ${required_major}.${required_minor}+ (установлено: $current_version)"
        exit 1
    fi
}

check_git_repository() {
    if [ ! -d ".git" ]; then
        print_error "Скрипт должен запускаться из корня Git-репозитория!"
        exit 1
    fi
}

check_internet_connection() {
    print_message "\nПроверка интернет-соединения..."
    
    if ping -c 1 -W 2 8.8.8.8 >/dev/null 2>&1; then
        print_success "  ✓ Интернет-соединение активно (ping)"
        return 0
    else
        print_error "  ✗ Отсутствует интернет-соединение (none-check)"
        return 1
    fi
}

setup_virtualenv() {
    VENV_DIR="venv"
    
    if [ ! -d "$VENV_DIR" ]; then
        print_message "\nСоздание виртуального окружения..."
        if ! python3 -m venv "$VENV_DIR" >/dev/null 2>&1; then
            print_error "Не удалось создать виртуальное окружение"
            exit 1
        fi
        print_success "  ✓ Виртуальное окружение создано"
        echo -e "${GREEN}[  ?  ]${CYAN} Начинается первичная проверка целостности репозитория (Это действие будет совершено только при первом запуске)"
        sleep 2
        clear
        echo -e "${GREEN}[  *  ]${CYAN} start extract platform"
        sleep 1
        echo -e "${GREEN}[  #  ]${CYAN} check filesystem"
        sleep 1
        echo -e "${GREEN}[  #  ]${CYAN} dm ! /"
        sleep 1
        echo -e "${GREEN}[  #  ]${CYAN} dm ! /LICENSE.md"
        sleep 1
        echo -e "${GREEN}[  #  ]${CYAN} dm ! /data.py"
        sleep 1
        echo -e "${GREEN}[  #  ]${CYAN} dm ! /eum.sh"
        sleep 1
        echo -e "${GREEN}[  #  ]${CYAN} dm ! /logs/receipts.json"
        sleep 1
        echo -e "${GREEN}[  #  ]${CYAN} dm ! /data/keys.json"
        sleep 1
        echo -e "${GREEN}[  #  ]${CYAN} dm ! /data/users.json"
        sleep 1
        echo -e "${GREEN}[  +  ]${CYAN} python run..."
        sleep 1
    fi
    
    if ! source "${VENV_DIR}/bin/activate" >/dev/null 2>&1; then
        print_error "Не удалось активировать виртуальное окружение"
        exit 1
    fi
    
    print_message "\nУстановка python-зависимостей..."
    if pip install colorama >/dev/null 2>&1; then
        print_success "  ✓ Зависимости успешно установлены"
    else
        print_error "Не удалось установить colorama"
        exit 1
    fi
}

check_for_updates() {
    if ! current_branch=$(git rev-parse --abbrev-ref HEAD 2>.git_error.tmp); then
        error_msg=$(cat .git_error.tmp)
        print_error "Ошибка Git: ${error_msg}"
        rm -f .git_error.tmp
        return 1
    fi

    git fetch >/dev/null 2>.git_error.tmp
    
    if [ $? -ne 0 ]; then
        error_msg=$(cat .git_error.tmp)
        print_error "Ошибка при получении данных: ${error_msg}"
        rm -f .git_error.tmp
        return 1
    fi

    local_sha=$(git rev-parse "$current_branch")
    remote_sha=$(git rev-parse "origin/$current_branch")

    if [ "$local_sha" != "$remote_sha" ]; then
        print_success "\n  ✓ Доступно новое обновление для Extract!"
        return 0
    else
        print_message "\n  ✓ Обновлений не найдено"
        return 1
    fi
}

update_repository() {
    print_message "\nПрименение обновлений..."
    if git pull --rebase 2>.git_error.tmp; then
        print_success "  ✓ Extract успешно обновлен!"
        return 0
    else
        error_msg=$(cat .git_error.tmp)
        print_error "Конфликт при обновлении: ${error_msg}"
        rm -f .git_error.tmp
        return 1
    fi
}

main() {
    print_header
    
    progress_bar 0.02 "Инициализация EUM..."
    echo -e "Первая загрузка или загрузка после обновления длиться всегда больше."
    print_logs
    progress_bar 0.02 "Подготовка..."
    check_python_version
    check_git_repository
    setup_virtualenv
    
    if check_internet_connection; then
        if check_for_updates; then
            echo -ne "${YELLOW}\nОбновить Extract? (y/n): ${NC}"
            read choice
            
            if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
                progress_bar 0.01 "Применение обновлений для Extract..."
                update_repository
            else
                print_message "\n  ✓ Обновление отменено"
            fi
        fi
    else
        print_message "\n  ✓ Проверка обновлений пропущена (нет интернета)"
    fi
    
    echo -ne "${CYAN}\nНажмите Enter для запуска Extract...${NC}"
    read
    clear
    python main/data.py
}

main
 
