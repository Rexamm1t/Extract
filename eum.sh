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
        " --- Start EUM-class √ "
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
    echo -e "║     При первом запуске, Extract загружается дольше чем обычно        ║"
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
    echo -e "${GREEN}[✓] $1${NC}"
    log "SUCCESS: $1"
}

print_error() {
    echo -e "${RED}[✗] ОШИБКА: $1${NC}" >&2
    log "ERROR: $1"
}

print_warning() {
    echo -e "${YELLOW}[!] ВНИМАНИЕ: $1${NC}"
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

    local sites=("8.8.8.8" "google.com" "github.com")
    local connected=false

    for site in "${sites[@]}"; do
        if ping -c 1 -W 2 "$site" >/dev/null 2>&1; then
            print_success "  ✓ Соединение с $site установлено"
            connected=true
            break
        fi
    done

    if ! $connected; then
        print_warning "  ✗ Не удалось установить соединение"
        return 1
    fi

    return 0
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
        print_message "Первичная настройка системы..."
        progress_bar 0.05 "Инициализация платформы Extract..."
    fi

    if ! source "${VENV_DIR}/bin/activate" >/dev/null 2>&1; then
        print_error "Не удалось активировать виртуальное окружение"
        exit 1
    fi

    print_message "Установка python-зависимостей..."
    local dependencies=("colorama" "requests" "psutil")
    
    for dep in "${dependencies[@]}"; do
        if ! python3 -c "import $dep" 2>/dev/null; then
            if pip install "$dep" >/dev/null 2>&1; then
                print_success "  ✓ Успешно установлен: $dep"
            else
                print_warning "  ✗ Не удалось установить: $dep"
            fi
        else
            print_success "  ✓ Уже установлен: $dep"
        fi
    done
}

check_for_updates() {
    log "Проверка обновлений..."
    if ! current_branch=$(git rev-parse --abbrev-ref HEAD 2>"$GIT_ERROR_FILE"); then
        error_msg=$(cat "$GIT_ERROR_FILE")
        print_error "Ошибка Git: ${error_msg}"
        return 1
    fi

    print_message "Проверка обновлений на ветке: $current_branch"

    if ! git fetch >/dev/null 2>"$GIT_ERROR_FILE"; then
        error_msg=$(cat "$GIT_ERROR_FILE")
        print_error "Ошибка при получении данных: ${error_msg}"
        return 1
    fi

    local local_sha=$(git rev-parse "$current_branch")
    local remote_sha=$(git rev-parse "origin/$current_branch")

    if [ "$local_sha" != "$remote_sha" ]; then
        print_success "Доступно новое обновление для Extract!"
        print_message "Локальная версия: ${local_sha:0:7}"
        print_message "Удалённая версия: ${remote_sha:0:7}"
        return 0
    else
        print_success "  ✓ Extract актуален (версия: ${local_sha:0:7})"
        return 1
    fi
}

update_repository() {
    log "Попытка обновления репозитория..."
    print_message "Применение обновлений..."
    
    print_message "1/4 Подготовка рабочей директории..."
    git reset --hard >/dev/null 2>"$GIT_ERROR_FILE" || {
        print_warning "Не удалось выполнить soft reset, продолжаем..."
    }

    print_message "2/4 Очистка неотслеживаемых файлов..."
    git clean -fd 2>"$GIT_ERROR_FILE" || {
        error_msg=$(cat "$GIT_ERROR_FILE")
        print_warning "Частичная очистка не удалась: ${error_msg}"
    }

    print_message "3/4 Сохранение локальных изменений..."
    if ! git diff-index --quiet HEAD --; then
        git stash push -m "EUM auto-stash" >/dev/null 2>"$GIT_ERROR_FILE"
        print_success "  ✓ Локальные изменения временно сохранены (stash)"
    fi

    print_message "4/4 Получение обновлений..."
    if git pull --rebase 2>"$GIT_ERROR_FILE"; then
        print_success "Extract успешно обновлен!"
        
        if git stash list | grep -q "EUM auto-stash"; then
            if git stash pop >/dev/null 2>"$GIT_ERROR_FILE"; then
                print_success "  ✓ Локальные изменения восстановлены"
            else
                print_warning "  ✗ Не удалось автоматически восстановить изменения"
                print_message "  Используйте 'git stash pop' вручную для восстановления"
            fi
        fi
        
        print_message "Проверка зависимостей после обновления..."
        setup_virtualenv
        
        if ! source "${VENV_DIR}/bin/activate" >/dev/null 2>&1; then
            print_error "Не удалось активировать виртуальное окружение после обновления"
            exit 1
        fi
        
        return 0
    else
        error_msg=$(cat "$GIT_ERROR_FILE")
        print_error "Ошибка при обновлении: ${error_msg}"
        
        if git stash list | grep -q "EUM auto-stash"; then
            git stash pop >/dev/null 2>&1
        fi
        
        print_separator
        print_message "Рекомендуемые действия:"
        print_message "1. Проверьте конфликтующие файлы: git status"
        print_message "2. Вручную удалите или сохраните файлы, указанные в ошибке"
        print_message "3. Повторите попытку обновления"
        print_message "Или выполните команды вручную:"
        print_message "   git reset --hard"
        print_message "   git clean -fd"
        print_message "   git pull"
        print_separator
        
        return 1
    fi
}

main() {
    print_header
    progress_bar 0.02 "Инициализация системы обновления..."
    
    check_python_version
    check_git_repository
    setup_virtualenv

    if check_internet_connection; then
        if check_for_updates; then
            print_separator
            echo -ne "${YELLOW}Установить доступное обновление? [y/N]: ${NC}"
            read -r choice
            
            if [[ "$choice" =~ ^[YyДд]$ ]]; then
                progress_bar 0.01 "Применение обновлений..."
                if update_repository; then
                    print_success "Обновление успешно завершено!"
                else
                    print_warning "Обновление завершено с проблемами"
                fi
            else
                print_message "Обновление отменено пользователем"
            fi
        fi
    else
        print_warning "Проверка обновлений пропущена (нет интернет-соединения)"
    fi

    if ! source "${VENV_DIR}/bin/activate" >/dev/null 2>&1; then
        print_error "Не удалось активировать виртуальное окружение перед запуском"
        exit 1
    fi

    print_separator
    echo -e "${CYAN}Готово! Система подготовлена к работе.${NC}"
    echo -e "${MAGENTA}Нажмите Enter для запуска Extract...${NC}"
    read -r
    clear
    
    python3 main/data.py
}

trap cleanup EXIT
main