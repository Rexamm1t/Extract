#!/bin/bash

# Конфигурация
readonly VENV_DIR="venv"
readonly LOG_FILE="eum-shared/eum.log"
readonly GIT_ERROR_FILE=".git_error.tmp"

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Логирование
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Очистка временных файлов
cleanup() {
    rm -f "$GIT_ERROR_FILE"
    log "Очистка временных файлов выполнена"
}

# Заголовок
print_header() {
    clear
    echo -e "${MAGENTA}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║               EXTRACT UPDATE MANAGER v2.1                  ║"
    echo "║     Professional update system for Extract Platform        ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    log "Отображение заголовка"
}

# Визуальные элементы
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

# Анимация процесса
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

# Проверка версии Python
check_python_version() {
    log "Проверка версии Python..."
    if ! command -v python3 &>/dev/null; then
        print_error "Python3 не установлен!"
        log "Критическая ошибка: Python3 не установлен"
        exit 1
    fi

    local required_major=3
    local required_minor=6
    local current_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null)

    if [ $? -ne 0 ]; then
        print_error "Не удалось определить версию Python"
        log "Ошибка определения версии Python"
        exit 1
    fi

    local current_major=$(echo "$current_version" | cut -d. -f1)
    local current_minor=$(echo "$current_version" | cut -d. -f2)

    if [ "$current_major" -lt "$required_major" ] || 
       { [ "$current_major" -eq "$required_major" ] && [ "$current_minor" -lt "$required_minor" ]; }; then
        print_error "Требуется Python ${required_major}.${required_minor}+ (установлено: $current_version)"
        log "Несовместимая версия Python: $current_version"
        exit 1
    fi

    print_success "Версия Python $current_version совместима"
    log "Проверка версии Python успешна: $current_version"
}

# Проверка Git репозитория
check_git_repository() {
    log "Проверка Git репозитория..."
    if [ ! -d ".git" ]; then
        print_error "Скрипт должен запускаться из корня Git-репозитория!"
        log "Ошибка: не найден .git каталог"
        exit 1
    fi
    print_success "Git репозиторий обнаружен"
}

# Проверка интернет соединения
check_internet_connection() {
    log "Проверка интернет соединения..."
    print_message "Проверка интернет-соединения..."

    local sites=("8.8.8.8" "google.com" "github.com")
    local connected=false

    for site in "${sites[@]}"; do
        if ping -c 1 -W 2 "$site" >/dev/null 2>&1; then
            print_success "  ✓ Соединение с $site установлено"
            log "Соединение с $site успешно"
            connected=true
            break
        fi
    done

    if ! $connected; then
        print_warning "  ✗ Не удалось установить соединение"
        log "Предупреждение: нет интернет соединения"
        return 1
    fi

    return 0
}

# Настройка виртуального окружения
setup_virtualenv() {
    log "Настройка виртуального окружения..."
    if [ ! -d "$VENV_DIR" ]; then
        print_message "Создание виртуального окружения..."
        if ! python3 -m venv "$VENV_DIR" >/dev/null 2>&1; then
            print_error "Не удалось создать виртуальное окружение"
            log "Ошибка создания виртуального окружения"
            exit 1
        fi
        print_success "  ✓ Виртуальное окружение создано"
        log "Виртуальное окружение успешно создано"

        # Первичная инициализация
        print_message "Первичная настройка системы..."
        progress_bar 0.05 "Инициализация платформы Extract..."
        log "Первичная инициализация выполнена"
    fi

    if ! source "${VENV_DIR}/bin/activate" >/dev/null 2>&1; then
        print_error "Не удалось активировать виртуальное окружение"
        log "Ошибка активации виртуального окружения"
        exit 1
    fi
    log "Виртуальное окружение активировано"

    # Установка зависимостей
    print_message "Установка python-зависимостей..."
    local dependencies=("colorama" "requests" "psutil")
    
    for dep in "${dependencies[@]}"; do
        if ! python3 -c "import $dep" 2>/dev/null; then
            if pip install "$dep" >/dev/null 2>&1; then
                print_success "  ✓ Успешно установлен: $dep"
                log "Установлена зависимость: $dep"
            else
                print_warning "  ✗ Не удалось установить: $dep"
                log "Предупреждение: не удалось установить $dep"
            fi
        else
            print_success "  ✓ Уже установлен: $dep"
        fi
    done
}

# Проверка обновлений
check_for_updates() {
    log "Проверка обновлений..."
    if ! current_branch=$(git rev-parse --abbrev-ref HEAD 2>"$GIT_ERROR_FILE"); then
        error_msg=$(cat "$GIT_ERROR_FILE")
        print_error "Ошибка Git: ${error_msg}"
        log "Ошибка Git при проверке ветки: ${error_msg}"
        return 1
    fi

    print_message "Проверка обновлений на ветке: $current_branch"
    log "Текущая ветка: $current_branch"

    if ! git fetch >/dev/null 2>"$GIT_ERROR_FILE"; then
        error_msg=$(cat "$GIT_ERROR_FILE")
        print_error "Ошибка при получении данных: ${error_msg}"
        log "Ошибка Git fetch: ${error_msg}"
        return 1
    fi

    local local_sha=$(git rev-parse "$current_branch")
    local remote_sha=$(git rev-parse "origin/$current_branch")

    if [ "$local_sha" != "$remote_sha" ]; then
        print_success "Доступно новое обновление для Extract!"
        print_message "Локальная версия: ${local_sha:0:7}"
        print_message "Удалённая версия: ${remote_sha:0:7}"
        log "Обнаружено обновление: local=$local_sha, remote=$remote_sha"
        return 0
    else
        print_success "  ✓ Extract актуален (версия: ${local_sha:0:7})"
        log "Обновлений не найдено"
        return 1
    fi
}

# Обновление репозитория
update_repository() {
    log "Попытка обновления репозитория..."
    print_message "Применение обновлений..."
    
    # Сбрасываем все локальные изменения
    if ! git reset --hard >/dev/null 2>"$GIT_ERROR_FILE"; then
        error_msg=$(cat "$GIT_ERROR_FILE")
        print_error "Ошибка сброса изменений: ${error_msg}"
        log "Ошибка git reset: ${error_msg}"
        return 1
    fi

    # Обновление кода
    if git pull 2>"$GIT_ERROR_FILE"; then
        print_success "Extract успешно обновлен!"
        log "Репозиторий успешно обновлен"
        
        # Переустановка зависимостей после обновления
        print_message "Проверка зависимостей после обновления..."
        setup_virtualenv
        
        return 0
    else
        error_msg=$(cat "$GIT_ERROR_FILE")
        print_error "Ошибка при обновлении: ${error_msg}"
        print_message "Рекомендуемые действия:"
        print_message "1. Сохраните свои изменения: git stash"
        print_message "2. Попробуйте обновить вручную: git pull"
        log "Ошибка git pull: ${error_msg}"
        return 1
    fi
}

# Основная функция
main() {
    print_header
    progress_bar 0.02 "Инициализация системы обновления..."
    
    # Проверки
    check_python_version
    check_git_repository
    setup_virtualenv

    # Проверка обновлений
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
                log "Пользователь отменил обновление"
            fi
        fi
    else
        print_warning "Проверка обновлений пропущена (нет интернет-соединения)"
        log "Пропуск проверки обновлений - нет интернета"
    fi

    # Запуск приложения
    print_separator
    echo -e "${CYAN}Готово! Система подготовлена к работе.${NC}"
    echo -e "${MAGENTA}Нажмите Enter для запуска Extract...${NC}"
    read -r
    clear
    
    log "Запуск основного приложения..."
    python3 main/data.py
}

# Очистка и запуск
trap cleanup EXIT
main