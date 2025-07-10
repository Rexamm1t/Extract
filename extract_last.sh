#!/bin/sh

clear
echo "Запуск Extract Update Manager"
echo
echo "Установка необходимых зависимостей..."
echo
sleep 2
clear

pip install colorama

print_message() {
    echo -e "\n$1\n"
}

check_for_updates() {
    current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
    if [ $? -ne 0 ]; then
        print_message "Ошибка при получении обновления."
        return 1
    fi

    git fetch 2>/dev/null
    if [ $? -ne 0 ]; then
        print_message "Ошибка при выполнении обновления."
        return 1
    fi

    local_sha=$(git rev-parse "$current_branch" 2>/dev/null)
    remote_sha=$(git rev-parse "origin/$current_branch" 2>/dev/null)

    [ "$local_sha" != "$remote_sha" ]
}

update_repository() {
    print_message "Обновление Extract..."
    git pull
    if [ $? -ne 0 ]; then
        print_message "Ошибка при обновлении."
    else
        print_message "Обновление завершено."
    fi
}

main() {
    clear
    print_message "Проверка наличия обновлений..."
    if check_for_updates; then
        echo -n "Обновления найдены. Хотите обновить? (y/n): "
        read choice
        if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
            update_repository
        else
            print_message "Обновление пропущено."
        fi
    else
        print_message "Обновлений пока нет.."
    fi
    echo -n "Нажмите Enter для продолжения..."
    read
    clear
    python data.py
}

main