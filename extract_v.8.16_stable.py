import random
import json
import time
from datetime import datetime, timedelta
from colorama import Fore, Style, init

# Конфигурация
VERSION = "v.8.16.0_///_from_02.06.2025_by_rexamm1t"
SAVE_FILE = "users.json"
CRYPTO_SYMBOLS = {"EXTRACT": "₿", "BTC": "₿", "ETH": "Ξ", "LTC": "Ł"}
CURRENCY = "₿"
INITIAL_BALANCE = 1000.0

# Инициализация colorama
init(autoreset=True)

def dynamic_border(text, width=50, border_color=Fore.MAGENTA):
    lines = text.split('\n')
    bordered = []
    for line in lines:
        bordered.append(f"{border_color}║ {line.ljust(width-4)} {border_color}║")
    return f"{border_color}╔{'═'*(width-2)}╗\n" + '\n'.join(bordered) + f"\n{border_color}╚{'═'*(width-2)}╝"

def rainbow_text(text):
    colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
    return ''.join([colors[i % len(colors)] + char for i, char in enumerate(text)])

def gradient_text(text, colors):
    return ''.join([colors[i % len(colors)] + char for i, char in enumerate(text)])

def format_time(seconds):
    return str(timedelta(seconds=seconds)).split('.')[0]

def print_art():
    art = r"""
     _______      _                  _
    |  ____|    | |                | |
    | |__  __  _| |_ _ __ __ _  ___| |_
    |  __| \ \/ / __| '__/ _` |/ __| __|
    | |____ >  <| |_| | | (_| | (__| |_
    |______/_/\_\\__|_|  \__,_|\___|\__|
    """
    print(rainbow_text(art))
    print(Fore.RED + "By Rexamm1t, tg: @rexamm1t")
    print(Fore.BLUE + dynamic_border("Для получения списка команд введите help", 40, Fore.BLUE) + "\n")

class CryptoMarket:
    def __init__(self):
        self.rates = {
            "BTC": random.uniform(38000, 80000),
            "ETH": random.uniform(2800, 5000),
            "LTC": random.uniform(80, 800),
            "EXTRACT": 1.0
        }

    def update_rates(self):
        for coin in self.rates:
            if coin != "EXTRACT":
                change = random.uniform(-0.05, 0.05)
                self.rates[coin] = max(0.1, self.rates[coin] * (1 + change))

    def get_rate(self, coin):
        return self.rates.get(coin, 0.0)

class User:
    def __init__(self, username):
        self.username = username
        self.crypto_balance = {
            "EXTRACT": INITIAL_BALANCE,
            "BTC": 0.0,
            "ETH": 0.0,
            "LTC": 0.0
        }
        self.games_played = 0
        self.wins = 0
        self.losses = 0
        self.transactions = []
        self.play_time = 0.0
        self.session_start = None

    def to_dict(self):
        return {
            "username": self.username,
            "crypto_balance": self.crypto_balance,
            "games_played": self.games_played,
            "wins": self.wins,
            "losses": self.losses,
            "transactions": self.transactions,
            "play_time": self.play_time
        }

    @classmethod
    def from_dict(cls, data):
        user = cls(data["username"])
        user.crypto_balance = data.get("crypto_balance", {"EXTRACT": INITIAL_BALANCE})
        user.games_played = data.get("games_played", 0)
        user.wins = data.get("wins", 0)
        user.losses = data.get("losses", 0)
        user.transactions = data.get("transactions", [])
        user.play_time = data.get("play_time", 0.0)
        return user

    def start_session(self):
        self.session_start = time.time()

    def end_session(self):
        if self.session_start:
            self.play_time += time.time() - self.session_start
            self.session_start = None

    def update_stats(self, won):
        self.games_played += 1
        if won:
            self.wins += 1
        else:
            self.losses += 1

    def add_transaction(self, action, coin, amount, price):
        self.transactions.insert(0, {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
            "coin": coin,
            "amount": round(amount, 4),
            "total": round(price, 2)
        })
        self.transactions = self.transactions[:10]

    def win_loss_ratio(self):
        if self.games_played == 0:
            return 0.0
        return round(self.wins / self.games_played * 100, 1)

    def show_stats(self):
        content = [
            f"{Fore.CYAN}Баланс:",
            *[f"  {CRYPTO_SYMBOLS[coin]} {coin}: {amount:.4f}" 
              for coin, amount in self.crypto_balance.items()],
            "",
            f"{Fore.YELLOW}Игр: {self.games_played} | Побед: {self.wins} | Поражений: {self.losses}",
            f"{Fore.MAGENTA}WL Ratio: {self.win_loss_ratio()}%",
            f"{Fore.GREEN}Время в игре: {format_time(self.play_time)}",
            "",
            f"{Fore.CYAN}Последние транзакции:"
        ]
        
        for t in self.transactions[:5]:
            action_color = Fore.GREEN if t['action'] == 'buy' else Fore.RED
            content.append(
                f"  [{t['timestamp']}] {action_color}{t['action'].upper()} {t['amount']} {t['coin']} "
                f"{Fore.WHITE}за {t['total']}{CURRENCY}"
            )

        stats = '\n'.join(content)
        print(dynamic_border(f"{Fore.GREEN}Профиль {self.username}\n{stats}", 60))

class Casino:
    def __init__(self):
        self.users = {}
        self.current_user = None
        self.market = CryptoMarket()
        self.last_command = ""
        self.load_users()

    def save_users(self):
        with open(SAVE_FILE, "w") as f:
            data = {un: user.to_dict() for un, user in self.users.items()}
            json.dump(data, f, indent=4)

    def load_users(self):
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
                self.users = {un: User.from_dict(user_data) for un, user_data in data.items()}
        except (FileNotFoundError, json.JSONDecodeError):
            self.users = {}

    def _check_balance(self, amount, currency="EXTRACT"):
        if self.current_user.crypto_balance.get(currency, 0) >= amount:
            return True
        print(f"{Fore.RED}Недостаточно {CRYPTO_SYMBOLS[currency]}! Требуется: {amount:.2f}")
        return False

    def _update_balance(self, amount, currency="EXTRACT"):
        self.current_user.crypto_balance[currency] += amount
        self.save_users()

    def create_user(self, username):
        if username in self.users:
            print(f"{Fore.RED}Пользователь {username} уже существует!")
            return
        self.users[username] = User(username)
        self.current_user = self.users[username]
        self.save_users()
        print(f"{gradient_text(f'Пользователь {username} создан!', [Fore.GREEN, Fore.LIGHTGREEN_EX])}")

    def select_user(self, username):
        if username in self.users:
            if self.current_user:
                self.current_user.end_session()
            self.current_user = self.users[username]
            self.current_user.start_session()
            print(f"{Fore.GREEN}Выбран пользователь: {rainbow_text(username)}")
        else:
            print(f"{Fore.RED}Пользователь не найден!")

    def delete_user(self, username):
        if username in self.users:
            if self.current_user and self.current_user.username == username:
                self.current_user.end_session()
                self.current_user = None
            del self.users[username]
            self.save_users()
            print(f"{Fore.GREEN}Пользователь {username} удалён!")
        else:
            print(f"{Fore.RED}Пользователь не найден!")

    def slots(self, bet):
        if not self.current_user:
            print(f"{Fore.RED}Сначала выберите пользователя!")
            return

        if not self._check_balance(bet):
            return

        self._update_balance(-bet)

        symbols = ["🍒", "💎", "7", "★", "🍀", "💰"]
        result = []

        print(dynamic_border(f"{Fore.YELLOW}🌀 Запуск слот-машины...", 40, Fore.YELLOW))
        for i in range(5):
            print("\r" + " | ".join(random.choice(symbols) for _ in range(3)), end="")
            time.sleep(0.1 * (i + 1))

        result = [random.choice(symbols) for _ in range(3)]
        print(f"\r{' | '.join(result)}")

        if all(x == "7" for x in result):
            win = bet * 50
        elif len(set(result)) == 1:
            win = bet * 10
        elif result[0] == result[1] or result[1] == result[2]:
            win = bet * 2
        else:
            win = 0

        if win > 0:
            print(dynamic_border(f"{Fore.GREEN}Выигрыш! +{win:.2f}{CURRENCY}", 30, Fore.GREEN))
            self._update_balance(win)
            self.current_user.update_stats(True)
        else:
            print(dynamic_border(f"{Fore.RED}Повезёт в следующий раз!", 30, Fore.RED))
            self.current_user.update_stats(False)

    def trade(self, command):
        if not self.current_user:
            print(f"{Fore.RED}Сначала выберите пользователя!")
            return

        try:
            parts = command.split()
            action = parts[0].lower()
            coin = parts[1].upper()
            amount = float(parts[2])

            if coin not in self.market.rates:
                print(f"{Fore.RED}Неизвестная валюта: {coin}")
                return

            if action == "buy":
                cost = amount * self.market.get_rate(coin) * 1.01
                if not self._check_balance(cost):
                    return
                self._update_balance(-cost)
                self._update_balance(amount, coin)
                self.current_user.add_transaction('buy', coin, amount, cost)
                print(dynamic_border(f"{Fore.GREEN}Куплено {amount:.4f} {coin}", 40, Fore.CYAN))

            elif action == "sell":
                if not self._check_balance(amount, coin):
                    return
                value = amount * self.market.get_rate(coin) * 0.99
                self._update_balance(-amount, coin)
                self._update_balance(value)
                self.current_user.add_transaction('sell', coin, amount, value)
                print(dynamic_border(f"{Fore.GREEN}Продано {amount:.4f} {coin}", 40, Fore.MAGENTA))

            self.market.update_rates()

        except Exception as e:
            print(f"{Fore.RED}Ошибка команды: trade [buy/sell] [монета] [количество]")

    def monster_battle(self, bet):
        if not self.current_user:
            print(f"{Fore.RED}Сначала выберите пользователя!")
            return

        if not self._check_balance(bet):
            return

        self._update_balance(-bet)

        monsters = ["🐉 Дракон", "🤖 Голем", "👹 Демон", "🦖 Тиранозавр"]
        player_monster = random.choice(monsters)
        enemy_monster = random.choice(monsters)

        print(dynamic_border(f"{Fore.YELLOW}⚔️ {player_monster} vs {enemy_monster} ⚔️", 45, Fore.RED))

        for _ in range(3):
            print(f"{Fore.RED}💥 Удар!", end="")
            time.sleep(0.3)
            print(f"{Fore.BLUE} 🛡️ Блок!", end="\r")
            time.sleep(0.3)

        win_chance = 0.45 + (len(player_monster) - len(enemy_monster)) * 0.05
        win = random.random() < win_chance

        if win:
            prize = bet * 2.5
            self._update_balance(prize)
            print(dynamic_border(f"{Fore.GREEN}🏆 Победа! +{prize:.2f}{CURRENCY}", 35, Fore.GREEN))
            self.current_user.update_stats(True)
        else:
            print(dynamic_border(f"{Fore.RED}💀 Поражение! -{bet:.2f}{CURRENCY}", 35, Fore.RED))
            self.current_user.update_stats(False)

    def dice(self, bet):
        if not self.current_user:
            print(f"{Fore.RED}Сначала выберите пользователя!")
            return

        if not self._check_balance(bet):
            return

        self._update_balance(-bet)

        dice = [random.randint(1, 6), random.randint(1, 6)]
        total = sum(dice)

        print(dynamic_border(f"{Fore.YELLOW}🎲 Результат: {dice[0]} + {dice[1]} = {total}", 30, Fore.BLUE))

        if total == 7:
            win = bet * 3
        elif total in [11, 12]:
            win = bet * 2
        elif total % 2 == 0:
            win = bet * 1.5
        else:
            win = 0

        if win > 0:
            self._update_balance(win)
            print(dynamic_border(f"{Fore.GREEN}🎉 Выигрыш! +{win:.2f}{CURRENCY}", 30, Fore.GREEN))
            self.current_user.update_stats(True)
        else:
            print(dynamic_border(f"{Fore.RED}😢 Проигрыш!", 30, Fore.RED))
            self.current_user.update_stats(False)

    def high_low(self, bet):
        if not self.current_user:
            print(f"{Fore.RED}Сначала выберите пользователя!")
            return

        if not self._check_balance(bet):
            return

        self._update_balance(-bet)
        
        current_num = random.randint(0, 200)
        next_num = random.randint(0, 200)
        
        print("\n"*2)
        print(dynamic_border(f"{Fore.MAGENTA}   CRYPTO HIGH/LOW   ", 45, Fore.MAGENTA))
        
        content = [
            f"{Fore.CYAN}Ставка: {Fore.WHITE}{bet:.2f}{CURRENCY}",
            f"{Fore.CYAN}Баланс: {Fore.WHITE}{self.current_user.crypto_balance['EXTRACT']:.2f}{CURRENCY}"
        ]
        print(dynamic_border('\n'.join(content), 45, Fore.CYAN))

        print(dynamic_border(f"{Fore.YELLOW}Генерация чисел...", 45, Fore.YELLOW))
        
        # Анимация первого числа
        print(f"{Fore.YELLOW}Текущее число: ", end="")
        for _ in range(8):
            print(f"{Fore.YELLOW}⌛ {random.randint(0, 200):03d}", end="\r")
            time.sleep(0.08)
        print(f"{Fore.GREEN}▶ {current_num:03d} ◀")

        print(dynamic_border(f"{Fore.BLUE}Выберите действие:", 45, Fore.BLUE))
        choice = None
        while choice not in ['h', 'l']:
            choice = input(f"{Fore.GREEN}➤ Ваш выбор (H/L): ").strip().lower()

        # Анимация результата
        print(dynamic_border(f"{Fore.YELLOW}Результат...", 45, Fore.YELLOW))
        result_color = Fore.LIGHTGREEN_EX if (next_num > current_num and choice == 'h') or (next_num < current_num and choice == 'l') else Fore.RED
        result = f"{current_num:03d} {'>' if next_num > current_num else '<' if next_num < current_num else '='} {next_num:03d}"
        print(dynamic_border(f"{result_color}{result}", 20, result_color))

        if current_num == next_num:
            win = bet
            status = f"{Fore.CYAN}⏣ Ничья! Ставка возвращена ⏣"
        elif (choice == 'h' and next_num > current_num) or (choice == 'l' and next_num < current_num):
            win = bet * 2
            status = f"{Fore.GREEN}★ Выигрыш: {win:.2f}{CURRENCY} ★"
        else:
            win = 0
            status = f"{Fore.RED}✖ Потеряно: {bet:.2f}{CURRENCY} ✖"

        print(dynamic_border(status, 40, Fore.WHITE if win else Fore.RED))
        
        if win > 0:
            self._update_balance(win)
            self.current_user.update_stats(True)
            for _ in range(3):
                print(f"{Fore.YELLOW}💰", end=" ")
                time.sleep(0.2)
            print()
        else:
            self.current_user.update_stats(False)

        if random.random() < 0.1:
            self.market_crash()

    def market_crash(self):
        print(dynamic_border(f"{Fore.RED}💣 НАЧАЛСЯ ОБВАЛ РЫНКА!", 50, Fore.RED))
        for i in range(1, 6):
            print(f"{Fore.RED}{'▼' * i * 10}", end="\r")
            time.sleep(0.2)
        
        for coin in self.market.rates:
            if coin != "EXTRACT":
                crash_factor = random.uniform(0.3, 0.6)
                self.market.rates[coin] *= crash_factor
                print(f"{Fore.RED}▏ {coin}: -{int((1 - crash_factor)*100)}% ", end="")
                time.sleep(0.3)
        
        print(f"\n{Fore.RED}💥 Рынок восстановился после обвала!")
        self.show_rates()

    def show_rates(self):
        content = [f"{Fore.YELLOW}1 {coin} = {rate:.2f}{CURRENCY}" 
                  for coin, rate in self.market.rates.items() if coin != "EXTRACT"]
        print(dynamic_border(f"{Fore.CYAN}Текущие курсы\n" + '\n'.join(content), 40))

    def display_help(self):
        help_content = f"""
{Fore.CYAN}Основные:
  create [имя]      - Создать пользователя
  switch [имя]      - Переключить пользователя
  delete [имя]      - Удалить пользователя
  exit -un          - Выйти из аккаунта
  help              - Показать помощь

{Fore.MAGENTA}Игры:
  slots [сумма]     - Слот-машина
  battle [сумма]    - Битва монстров
  dice [сумма]      - Игра в кости
  highlow [сумма]   - Больше/Меньше

{Fore.GREEN}Трейдинг:
  trade buy [монета] [кол-во]  - Купить
  trade sell [монета] [кол-во] - Продать
  rates              - Курсы валют

{Fore.YELLOW}Прочее:
  s                 - Статистика
  verinf            - Версия
  exit              - Выход
"""
        print(dynamic_border(help_content, 50, Fore.BLUE))

    def display_version(self):
        version_art = f"""
{Fore.MAGENTA}╔{'═'*35}╗
║ {rainbow_text('Extract Casino Platform')} ║
║ {Fore.CYAN}Версия: {VERSION.ljust(24)} ║
╚{'═'*35}╝
        """
        print(version_art)

def main():
    print_art()
    casino = Casino()

    try:
        while True:
            if casino.current_user:
                username = casino.current_user.username
                colors = [Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTMAGENTA_EX]
                username_gradient = gradient_text(username, colors)
                prompt = (
                    f"{Fore.BLUE}╭─{username_gradient}\n"
                    f"{Fore.BLUE}╰─{gradient_text('➤', [Fore.GREEN, Fore.YELLOW])} {Style.RESET_ALL}"
                )
            else:
                prompt = f"{Fore.BLUE}╭─Гость\n╰─➤ {Style.RESET_ALL}"

            action = input(prompt).strip()
            casino.last_command = action.split()[0] if action else ""

            if action.startswith("create "):
                username = action.split(" ", 1)[1]
                casino.create_user(username)

            elif action.startswith("switch "):
                username = action.split(" ", 1)[1]
                casino.select_user(username)

            elif action.startswith("delete "):
                username = action.split(" ", 1)[1]
                casino.delete_user(username)

            elif action == "exit -un":
                if casino.current_user:
                    casino.current_user.end_session()
                casino.current_user = None
                print(f"{Fore.GREEN}Вы вышли из аккаунта")

            elif action.startswith("slots"):
                try:
                    bet = float(action.split()[1])
                    casino.slots(bet)
                except:
                    print(f"{Fore.RED}Используйте: slots [сумма]")

            elif action.startswith("battle"):
                try:
                    bet = float(action.split()[1])
                    casino.monster_battle(bet)
                except:
                    print(f"{Fore.RED}Используйте: battle [сумма]")

            elif action.startswith("dice"):
                try:
                    bet = float(action.split()[1])
                    casino.dice(bet)
                except:
                    print(f"{Fore.RED}Используйте: dice [сумма]")

            elif action.startswith("highlow"):
                try:
                    bet = float(action.split()[1])
                    casino.high_low(bet)
                except:
                    print(f"{Fore.RED}Используйте: highlow [сумма]")

            elif action.startswith("trade"):
                casino.trade(action[5:])

            elif action == "rates":
                casino.show_rates()

            elif action == "s":
                if casino.current_user:
                    casino.current_user.show_stats()
                else:
                    print(f"{Fore.RED}Пользователь не выбран!")

            elif action == "verinf":
                casino.display_version()

            elif action == "help":
                casino.display_help()

            elif action == "exit":
                if casino.current_user:
                    casino.current_user.end_session()
                casino.save_users()
                print(f"{gradient_text('\nДо встречи! Ваш прогресс сохранён.\n', [Fore.GREEN, Fore.BLUE])}")
                break
            
            else:
                print(f"{Fore.RED}Неизвестная команда. Введите 'help' для помощи")

    except KeyboardInterrupt:
        print(f"{Fore.RED}\nСрочное сохранение...")
        if casino.current_user:
            casino.current_user.end_session()
        casino.save_users()
        exit()

if __name__ == "__main__":
    main()