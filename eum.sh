#!/bin/bash

readonly VENV_DIR="venv"
readonly LOG_FILE="eum-shared/eum.log"
readonly GIT_ERROR_FILE=".git_error.tmp"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m'

fade_art() {
    local art=(
        "     --- Start EUM-class"
    )

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
    local width=50
    local increment=$((100/$width))

    echo -ne "${BLUE}┌${CYAN} $message\n${BLUE}└[${NC}"

    for ((i=0; i<=width; i++)); do
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
    local dependencies=("colorama" "requests" "psutil")
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
        print_success "  ✓ Локальная копия актуальна"
        return 1
    elif [ "$local_commit" = "$base_commit" ]; then
        print_success "Доступны новые обновления!"
        print_message "Локальная версия: ${local_commit:0:7}"
        print_message "Удалённая версия: ${remote_commit:0:7}"
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
    log "Попытка обновления репозитория..."
    print_message "Применение обновлений..."

    print_message "1. Сохранение локальных изменений..."
    if ! git diff-index --quiet HEAD --; then
        git stash push -m "EUM auto-stash" >/dev/null 2>"$GIT_ERROR_FILE" && {
            print_success "  ✓ Локальные изменения сохранены (stash)"
            local has_stash=true
        } || {
            error_msg=$(cat "$GIT_ERROR_FILE")
            print_warning "  ✗ Не удалось сохранить изменения: ${error_msg}"
            local has_stash=false
        }
    else
        local has_stash=false
    fi

    print_message "2. Получение обновлений..."
    if git pull --rebase 2>"$GIT_ERROR_FILE"; then
        print_success "  ✓ Обновление успешно завершено"

        if $has_stash; then
            print_message "3. Восстановление локальных изменений..."
            if git stash pop >/dev/null 2>"$GIT_ERROR_FILE"; then
                print_success "  ✓ Локальные изменения восстановлены"
            else
                print_warning "  ✗ Не удалось восстановить изменения"
                print_message "   Используйте 'git stash pop' вручную для восстановления"
            fi
        fi

        print_message "4. Обновление зависимостей..."
        setup_virtualenv

        return 0
    else
        error_msg=$(cat "$GIT_ERROR_FILE")
        print_error "  ✗ Ошибка при обновлении: ${error_msg}"

        if $has_stash; then
            git stash pop >/dev/null 2>&1
        fi

        print_separator
        print_message "Рекомендуемые действия:"
        print_message "1. Проверьте статус: git status"
        print_message "2. Разрешите конфликты вручную"
        print_message "3. Повторите попытку обновления"
        print_separator

        return 1
    fi
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

            if [[ "$choice" =~ ^[YyДд]$ ]]; then
                if update_repository; then
                    print_success "Обновление успешно завершено!"
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