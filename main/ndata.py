import socket
import threading
import json
import random
import time
from datetime import datetime, timedelta
from colorama import Fore, Style, init
import os
import textwrap

# Инициализация colorama
init(autoreset=True)

# Константы из data.py
CRYPTO_SYMBOLS = {
    "EXTRACT": "Ⓔ",
    "BETASTD": "β",
    "EXRSD": "Ē",
    "DOGCOIN": "DC",
    "BTC": "₿",
    "ETH": "Ξ",
    "LTC": "Ł",
    "BNB": "Ɥ",
    "ADA": "𝔸",
    "SOL": "S",
    "XRP": "✕",
    "DOT": "●",
    "DOGE": "Ð",
    "SHIB": "SH",
    "AVAX": "AV",
    "TRX": "T",
    "MATIC": "M",
    "ATOM": "A",
    "NOT": "▲",
    "TON": "▼",
    "XYZ": "Ÿ",
    "ABC": "✦",
    "DEF": "DT",
    "GHI": "Ğ",
    "JKL": "+",
    "MNO": "Ḿ",
    "PQR": "❖"
}
CURRENCY = "Ⓔ"
SAVE_PATH = "data/users.json"
VERSION = "EXTRACT P2P 1.0"

def dynamic_border(text, border_color=Fore.MAGENTA, width=None):
    lines = text.split('\n')
    max_width = width if width else max(len(line) for line in lines) + 4
    border = '═' * (max_width - 2)
    bordered = [f"{border_color}╔{border}╗"]
    for line in lines:
        bordered.append(f"{border_color}║ {line.ljust(max_width - 4)} ║")
    bordered.append(f"{border_color}╚{border}╝")
    return '\n'.join(bordered)

class User:
    def __init__(self, username):
        self.username = username
        self.crypto_balance = {coin: 0.0 for coin in CRYPTO_SYMBOLS}
        self.crypto_balance["EXTRACT"] = 10000.0  # Начальный баланс
        self.transactions = []
        self.last_login = datetime.now().strftime("%Y-%m-%d")

    def to_dict(self):
        return {
            "username": self.username,
            "crypto_balance": self.crypto_balance,
            "transactions": self.transactions,
            "last_login": self.last_login
        }

    @classmethod
    def from_dict(cls, data):
        user = cls(data["username"])
        user.crypto_balance = data.get("crypto_balance", {coin: 0.0 for coin in CRYPTO_SYMBOLS})
        user.transactions = data.get("transactions", [])
        user.last_login = data.get("last_login", datetime.now().strftime("%Y-%m-%d"))
        return user

    def add_transaction(self, action, coin, amount, total):
        self.transactions.insert(0, {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
            "coin": coin,
            "amount": amount,
            "total": total
        })
        self.transactions = self.transactions[:10]  # Храним только последние 10

    def show_stats(self):
        content = [
            f"{Fore.CYAN}╔{'═'*25}╦{'═'*15}╗",
            f"║ {'Username:'.ljust(24)} ║ {self.username.ljust(14)} ║",
            f"╠{'═'*25}╬{'═'*15}╣"
        ]
        
        # Балансы
        for coin, amount in self.crypto_balance.items():
            if amount > 0:
                content.append(f"║ {coin.ljust(10)} {CRYPTO_SYMBOLS.get(coin, '?')} ║ {amount:>12.4f} ║")
        
        content.append(f"╚{'═'*25}╩{'═'*15}╝")
        
        # Последние транзакции
        if self.transactions:
            content.append(f"\n{Fore.YELLOW}Последние транзакции:")
            for t in self.transactions[:3]:
                action = "Куплено" if t['action'] == 'buy' else "Продано"
                content.append(f"{t['timestamp'][11:16]} {action} {t['amount']:.4f} {t['coin']} за {t['total']:.2f}{CURRENCY}")
        
        print('\n'.join(content))

class P2PCasino:
    def __init__(self):
        self.users = {}
        self.current_user = None
        self.peers = {}
        self.connections = {}
        self.server_socket = None
        self.running = False
        self.peer_id = self._generate_peer_id()
        self.load_users()

    def _generate_peer_id(self):
        return f"peer_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000,9999)}"

    def load_users(self):
        try:
            os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
            if os.path.exists(SAVE_PATH):
                with open(SAVE_PATH, "r") as f:
                    data = json.load(f)
                    self.users = {un: User.from_dict(user_data) for un, user_data in data.items()}
        except Exception as e:
            print(f"{Fore.RED}Ошибка загрузки пользователей: {str(e)}")

    def save_users(self):
        try:
            with open(SAVE_PATH, "w") as f:
                data = {un: user.to_dict() for un, user in self.users.items()}
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"{Fore.RED}Ошибка сохранения пользователей: {str(e)}")

    def start_server(self, port=5555):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('0.0.0.0', port))
        self.server_socket.listen(5)
        self.running = True
        print(f"{Fore.GREEN}P2P сервер запущен на порту {port}")
        
        accept_thread = threading.Thread(target=self._accept_connections)
        accept_thread.start()

    def _accept_connections(self):
        while self.running:
            try:
                conn, addr = self.server_socket.accept()
                peer_thread = threading.Thread(target=self._handle_peer, args=(conn, addr))
                peer_thread.start()
            except Exception as e:
                if self.running:
                    print(f"{Fore.RED}Ошибка при принятии соединения: {str(e)}")

    def _handle_peer(self, conn, addr):
        peer_id = None
        try:
            data = conn.recv(4096).decode()
            if not data:
                return
                
            message = json.loads(data)
            if message.get('type') == 'handshake':
                peer_id = message['peer_id']
                self.peers[peer_id] = (addr[0], addr[1])
                self.connections[peer_id] = conn
                print(f"{Fore.CYAN}Подключен пир: {peer_id} ({addr[0]}:{addr[1]})")
                
                # Отправляем подтверждение
                conn.send(json.dumps({
                    'type': 'handshake_ack',
                    'peer_id': self.peer_id,
                    'status': 'success'
                }).encode())
                
                # Обработка сообщений
                while self.running:
                    data = conn.recv(4096)
                    if not data:
                        break
                    self._process_message(peer_id, json.loads(data.decode()))
                    
        except Exception as e:
            print(f"{Fore.RED}Ошибка в соединении с пиром: {str(e)}")
        finally:
            if peer_id in self.connections:
                del self.connections[peer_id]
            conn.close()

    def _process_message(self, peer_id, message):
        msg_type = message.get('type')
        
        if msg_type == 'transfer':
            self._process_transfer(peer_id, message)
        elif msg_type == 'game_result':
            self._process_game_result(message)

    def _process_transfer(self, peer_id, message):
        if not self.current_user:
            return
            
        currency = message['currency'].upper()
        amount = float(message['amount'])
        
        if currency not in CRYPTO_SYMBOLS:
            return
            
        self.current_user.crypto_balance[currency] += amount
        self.current_user.add_transaction('transfer', currency, amount, amount)
        print(f"{Fore.GREEN}Получен перевод: {amount:.4f}{CRYPTO_SYMBOLS[currency]} от {peer_id}")

    def connect_to_peer(self, ip, port):
        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect((ip, port))
            
            # Отправляем handshake
            conn.send(json.dumps({
                'type': 'handshake',
                'peer_id': self.peer_id,
                'version': VERSION
            }).encode())
            
            # Получаем подтверждение
            data = conn.recv(4096).decode()
            response = json.loads(data)
            
            if response.get('status') == 'success':
                peer_id = response['peer_id']
                self.peers[peer_id] = (ip, port)
                self.connections[peer_id] = conn
                
                # Запускаем обработчик
                peer_thread = threading.Thread(target=self._handle_peer, args=(conn, (ip, port)))
                peer_thread.start()
                
                print(f"{Fore.GREEN}Успешно подключено к {peer_id}")
                return True
                
        except Exception as e:
            print(f"{Fore.RED}Ошибка подключения: {str(e)}")
            return False

    def send_transfer(self, peer_id, amount, currency):
        if not self.current_user or currency not in self.current_user.crypto_balance:
            print(f"{Fore.RED}Ошибка: неверная валюта или пользователь не выбран")
            return False
            
        if self.current_user.crypto_balance[currency] < amount:
            print(f"{Fore.RED}Недостаточно средств")
            return False
            
        if peer_id not in self.connections:
            print(f"{Fore.RED}Пир не подключен")
            return False
            
        try:
            self.current_user.crypto_balance[currency] -= amount
            self.current_user.add_transaction('transfer', currency, -amount, amount)
            
            message = {
                'type': 'transfer',
                'from': self.peer_id,
                'currency': currency,
                'amount': amount,
                'timestamp': datetime.now().isoformat()
            }
            
            self.connections[peer_id].send(json.dumps(message).encode())
            print(f"{Fore.GREEN}Перевод {amount:.4f}{CRYPTO_SYMBOLS[currency]} отправлен к {peer_id}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}Ошибка при отправке: {str(e)}")
            return False

    def create_user(self, username):
        if username in self.users:
            print(f"{Fore.RED}Пользователь уже существует")
            return False
            
        self.users[username] = User(username)
        self.save_users()
        print(f"{Fore.GREEN}Пользователь {username} создан")
        return True

    def login(self, username):
        if username in self.users:
            self.current_user = self.users[username]
            print(f"{Fore.GREEN}Вы вошли как {username}")
            return True
        print(f"{Fore.RED}Пользователь не найден")
        return False

    def slots(self, bet):
        if not self.current_user:
            print(f"{Fore.RED}Сначала войдите в аккаунт")
            return
            
        try:
            bet = float(bet)
            if bet <= 0:
                print(f"{Fore.RED}Ставка должна быть положительной")
                return
                
            if self.current_user.crypto_balance['EXTRACT'] < bet:
                print(f"{Fore.RED}Недостаточно средств")
                return
                
            self.current_user.crypto_balance['EXTRACT'] -= bet
            
            symbols = ["🍒", "🍊", "🍋", "🔔", "⭐", "💎"]
            results = [random.choice(symbols) for _ in range(3)]
            
            print(f"\n{' | '.join(results)}\n")
            
            # Простые правила выигрыша
            if results[0] == results[1] == results[2]:
                win = bet * 10
                print(f"{Fore.GREEN}ДЖЕКПОТ! Вы выиграли {win}{CURRENCY}")
            elif results[0] == results[1] or results[1] == results[2]:
                win = bet * 3
                print(f"{Fore.YELLOW}Вы выиграли {win}{CURRENCY}")
            else:
                win = 0
                print(f"{Fore.RED}Вы проиграли")
                
            self.current_user.crypto_balance['EXTRACT'] += win
            self.current_user.add_transaction('slots', 'EXTRACT', win - bet, bet)
            self.save_users()
            
        except ValueError:
            print(f"{Fore.RED}Неверная сумма ставки")

    def dice(self, bet):
        if not self.current_user:
            print(f"{Fore.RED}Сначала войдите в аккаунт")
            return
            
        try:
            bet = float(bet)
            if bet <= 0:
                print(f"{Fore.RED}Ставка должна быть положительной")
                return
                
            if self.current_user.crypto_balance['EXTRACT'] < bet:
                print(f"{Fore.RED}Недостаточно средств")
                return
                
            self.current_user.crypto_balance['EXTRACT'] -= bet
            
            player_roll = sum(random.randint(1, 6) for _ in range(3))
            dealer_roll = sum(random.randint(1, 6) for _ in range(3))
            
            print(f"{Fore.CYAN}Ваши кости: {player_roll}")
            print(f"{Fore.RED}Кости дилера: {dealer_roll}")
            
            if player_roll > dealer_roll:
                win = bet * 2
                print(f"{Fore.GREEN}Вы выиграли {win}{CURRENCY}")
                self.current_user.crypto_balance['EXTRACT'] += win
            else:
                win = -bet
                print(f"{Fore.RED}Вы проиграли")
                
            self.current_user.add_transaction('dice', 'EXTRACT', win, bet)
            self.save_users()
            
        except ValueError:
            print(f"{Fore.RED}Неверная сумма ставки")

    def show_version(self):
        print(dynamic_border(
            f"{Fore.CYAN}EXTRACT P2P Версия {VERSION}\n"
            f"Децентрализованная казино-платформа\n"
            f"Поддержка: @extract_support",
            Fore.BLUE
        ))

    def show_updates(self):
        print(dynamic_border(
            f"{Fore.YELLOW}Последние обновления:\n"
            f"- Добавлена P2P сеть\n"
            f"- Новые игры: Слоты и Кости\n"
            f"- Улучшена безопасность транзакций",
            Fore.YELLOW
        ))

    def stop_server(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        for conn in self.connections.values():
            conn.close()
        self.save_users()
        print(f"{Fore.YELLOW}Сервер остановлен")

def main():
    casino = P2PCasino()
    
    # Запускаем сервер в фоновом режиме
    server_thread = threading.Thread(target=casino.start_server)
    server_thread.daemon = True
    server_thread.start()
    
    print(dynamic_border(
        f"{Fore.CYAN}Добро пожаловать в EXTRACT P2P!\n"
        f"Ваш Peer ID: {casino.peer_id}\n"
        f"Введите 'help' для списка команд",
        Fore.MAGENTA
    ))
    
    try:
        while True:
            cmd = input(f"{Fore.BLUE}P2P> {Style.RESET_ALL}").strip().split()
            if not cmd:
                continue
                
            if cmd[0] == 'help':
                print(dynamic_border(
                    f"{Fore.CYAN}Доступные команды:\n"
                    f"{Fore.GREEN}help        {Fore.WHITE}- Справка по командам\n"
                    f"{Fore.GREEN}create [ник]{Fore.WHITE}- Создать пользователя\n"
                    f"{Fore.GREEN}login [ник] {Fore.WHITE}- Войти в аккаунт\n"
                    f"{Fore.GREEN}show        {Fore.WHITE}- Показать статистику\n"
                    f"{Fore.GREEN}connect [ip] [port] {Fore.WHITE}- Подключиться к пиру\n"
                    f"{Fore.GREEN}transfer [peer_id] [amount] [currency] {Fore.WHITE}- Перевести средства\n"
                    f"{Fore.GREEN}slots [ставка] {Fore.WHITE}- Играть в слоты\n"
                    f"{Fore.GREEN}dice [ставка] {Fore.WHITE}- Играть в кости\n"
                    f"{Fore.GREEN}extract     {Fore.WHITE}- Информация о версии\n"
                    f"{Fore.GREEN}wnew        {Fore.WHITE}- Последние обновления\n"
                    f"{Fore.GREEN}exit        {Fore.WHITE}- Выйти из программы",
                    Fore.CYAN
                ))
                
            elif cmd[0] == 'create' and len(cmd) > 1:
                casino.create_user(cmd[1])
                
            elif cmd[0] == 'login' and len(cmd) > 1:
                casino.login(cmd[1])
                
            elif cmd[0] == 'show':
                if casino.current_user:
                    casino.current_user.show_stats()
                else:
                    print(f"{Fore.RED}Сначала войдите в аккаунт")
                    
            elif cmd[0] == 'connect' and len(cmd) > 2:
                casino.connect_to_peer(cmd[1], int(cmd[2]))
                
            elif cmd[0] == 'transfer' and len(cmd) > 3:
                casino.send_transfer(cmd[1], float(cmd[2]), cmd[3].upper())
                
            elif cmd[0] == 'slots' and len(cmd) > 1:
                casino.slots(cmd[1])
                
            elif cmd[0] == 'dice' and len(cmd) > 1:
                casino.dice(cmd[1])
                
            elif cmd[0] == 'extract':
                casino.show_version()
                
            elif cmd[0] == 'wnew':
                casino.show_updates()
                
            elif cmd[0] == 'exit':
                casino.stop_server()
                break
                
            else:
                print(f"{Fore.RED}Неизвестная команда. Введите 'help' для справки")
                
    except KeyboardInterrupt:
        casino.stop_server()
        print(f"\n{Fore.YELLOW}Завершение работы...")

if __name__ == "__main__":
    main()