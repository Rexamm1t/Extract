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

# ... (все предыдущие функции остаются без изменений до функции update_repository)

update_repository() {
    log "Попытка обновления репозитория..."
    print_message "Применение обновлений..."

    # Проверяем наличие изменений
    local changes_exist=false
    if ! git diff-index --quiet HEAD --; then
        changes_exist=true
        print_message "Обнаружены незакоммиченные изменения"
    fi

    # Если есть изменения, предлагаем пользователю выбор
    if $changes_exist; then
        print_separator
        echo -e "${YELLOW}Обнаружены незакоммиченные изменения:${NC}"
        git status --short
        echo -e "${YELLOW}Выберите действие:${NC}"
        echo -e "  1) Сохранить изменения (stash) и обновить"
        echo -e "  2) Отменить все изменения и обновить"
        echo -e "  3) Отменить обновление"
        echo