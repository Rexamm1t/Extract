import random
import json
import time
import os
from datetime import datetime, timedelta
from colorama import Fore, Style, init

# Конфигурация
VERSION = "EXTRACT 9.2.1"
SAVE_PATH = "/etc/users.json"
KEYS_PATH = "/etc/keys.json"
CRYPTO_SYMBOLS = {
    "EXTRACT": "Ⓔ", "BTC": "₿", "ETH": "Ξ", "LTC": "Ł",
    "BNB": "Ɥ", "ADA": "𝔸", "SOL": "S", "XRP": "✕",
    "DOT": "●", "DOGE": "Ð", "SHIB": "SH", "AVAX": "AV",
    "TRX": "T", "MATIC": "M", "ATOM": "A"
}
CURRENCY = "Ⓔ"
INITIAL_BALANCE = 1000.0
LEVEL_BASE_XP = 200
SEASON_EVENTS = {
    12: {"name": "Зимний Ивент", "period": (1, 24.2),
         "effects": ["x2 бонусам", "Скидки 20%", "Новогодний джекпот"]},
    3: {"name": "Весенний Ивент", "period": (1, 30.5),
        "effects": ["+150% XP", "Бесплатные спины", "Цветочные бонусы"]},
    6: {"name": "Летний Ивент", "period": (1, 31.8),
        "effects": ["Кэшбэк 15%", "Пляжные бонусы", "Страховка ставок"]},
    9: {"name": "Осенний Ивент", "period": (1, 1.12),
        "effects": ["Урожай x2", "Бонусы за депозит", "Осенние скидки"]}
}
AUTOSAVE_INTERVAL = 300

init(autoreset=True)

def dynamic_border(text, border_color=Fore.MAGENTA):
    lines = text.split('\n')
    max_width = max(len(line) for line in lines) + 4
    border = '═' * (max_width - 2)
    bordered = [f"{border_color}╔{border}╗"]
    for line in lines:
        bordered.append(f"{border_color}║ {line.ljust(max_width - 4)} ║")
    bordered.append(f"{border_color}╚{border}╝")
    return '\n'.join(bordered)

def rainbow_text(text):
    colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
    return ''.join([colors[i % len(colors)] + char for i, char in enumerate(text)])

def gradient_text(text, colors):
    return ''.join([colors[i % len(colors)] + char for i, char in enumerate(text)])

def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(hours)}ч {int(minutes)}м {int(seconds)}с"

def print_art():
    art = r"""
     ____|\ \  /__ __|  _ \     \     ___|__ __| 
     __|   \  /    |   |   |   _ \   |       |  
     |        \    |   __ <   ___ \  |       | 
    _____| _/\_\  _|  _| \_\_/    _\\____|  _| 
    """
    print(gradient_text(art, [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]))
    print(Fore.RED + "By Rexamm1t, tg: @rexamm1t")
    print(Fore.BLUE + dynamic_border("Для получения списка команд введите help", 40, Fore.BLUE) + "\n")

class CryptoMarket:
    def __init__(self):
        self.rates = {
            "BTC": random.uniform(25000, 70000),
            "ETH": random.uniform(1500, 4000),
            "LTC": random.uniform(60, 300),
            "BNB": random.uniform(200, 600),
            "ADA": random.uniform(0.4, 2.5),
            "SOL": random.uniform(20, 200),
            "XRP": random.uniform(0.3, 1.5),
            "DOT": random.uniform(4, 30),
            "DOGE": random.uniform(0.05, 0.3),
            "SHIB": random.uniform(0.000001, 0.00003),
            "AVAX": random.uniform(10, 100),
            "TRX": random.uniform(0.05, 0.2),
            "MATIC": random.uniform(0.5, 3),
            "ATOM": random.uniform(8, 40),
            "EXTRACT": 1.0
        }

    def update_rates(self):
        for coin in self.rates:
            if coin != "EXTRACT":
                change = random.uniform(-0.07, 0.07)
                self.rates[coin] = max(0.01, self.rates[coin] * (1 + change))

    def get_rate(self, coin):
        return self.rates.get(coin, 0.0)

class User:
    def __init__(self, username):
        self.username = username
        self.crypto_balance = {coin: 0.0 for coin in CRYPTO_SYMBOLS}
        self.crypto_balance["EXTRACT"] = INITIAL_BALANCE
        self.games_played = 0
        self.wins = 0
        self.losses = 0
        self.transactions = []
        self.play_time = 0.0
        self.session_start = None
        self.level = 1
        self.xp = 0
        self.total_earned = 0.0

    def to_dict(self):
        return {
            "username": self.username,
            "crypto_balance": self.crypto_balance,
            "games_played": self.games_played,
            "wins": self.wins,
            "losses": self.losses,
            "transactions": self.transactions,
            "play_time": self.play_time,
            "level": self.level,
            "xp": self.xp,
            "total_earned": self.total_earned
        }

    @classmethod
    def from_dict(cls, data):
        user = cls(data["username"])
        user.crypto_balance = {coin: data["crypto_balance"].get(coin, 0.0) for coin in CRYPTO_SYMBOLS}
        user.games_played = data.get("games_played", 0)
        user.wins = data.get("wins", 0)
        user.losses = data.get("losses", 0)
        user.transactions = data.get("transactions", [])
        user.play_time = data.get("play_time", 0.0)
        user.level = data.get("level", 1)
        user.xp = data.get("xp", 0)
        user.total_earned = data.get("total_earned", 0.0)
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

    def add_xp(self, amount):
        xp_gain = random.randint(100, 300) + self.level * 50
        self.xp += xp_gain
        while self.xp >= self.required_xp():
            self.xp -= self.required_xp()
            self.level_up()

    def required_xp(self):
        return LEVEL_BASE_XP * (1.2 ** (self.level - 1))

    def level_up(self):
        self.level += 1
        reward = self.level * 100
        self.crypto_balance["EXTRACT"] += reward
        print(dynamic_border(
            f"{Fore.GREEN}🎉 Уровень UP! {self.level-1} → {self.level}\n"
            f"+{reward}{CURRENCY} бонус\n"
            f"Следующий уровень: {self.required_xp():.0f} XP",
            50, Fore.YELLOW
        ))

    def show_level_progress(self):
        progress = self.xp / self.required_xp()
        bar = "▓" * int(progress * 20) + "░" * (20 - int(progress * 20))
        return f"{Fore.CYAN}Прогресс уровня: {bar} {progress*100:.1f}%"

    def crywall(self):
        content = [f"{Fore.CYAN}╔{'═'*25}╦{'═'*15}╗"]
        for coin, amount in self.crypto_balance.items():
            if amount <= 0: continue
            symbol = CRYPTO_SYMBOLS[coin]
            line = f"║ {symbol} {coin.ljust(10)} ║ {amount:>10.4f} ║"
            color = Fore.GREEN if coin == "EXTRACT" else Fore.YELLOW
            content.append(color + line)
        content.append(f"{Fore.CYAN}╚{'═'*25}╩{'═'*15}╝")
        print('\n'.join(content))

    def show_stats(self):
        content = [
            f"{Fore.CYAN}Баланс:",
            *[f"  {CRYPTO_SYMBOLS[coin]} {coin}: {amount:.4f}" 
              for coin, amount in self.crypto_balance.items() if amount > 0],
            "",
            f"{Fore.YELLOW}Игр: {self.games_played} | Побед: {self.wins} | Поражений: {self.losses}",
            f"{Fore.MAGENTA}WL Ratio: {self.win_loss_ratio()}%",
            f"{Fore.GREEN}Время в игре: {format_time(self.play_time)}",
            f"{Fore.BLUE}Уровень: {self.level} | XP: {self.xp:.0f}/{self.required_xp():.0f}",
            self.show_level_progress(),
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
        self.last_save = time.time()
        self.promo_codes = self._load_promocodes()
        self.load_users()

    def save_users(self):
        try:
            with open(SAVE_PATH, "w") as f:
                data = {un: user.to_dict() for un, user in self.users.items()}
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"{Fore.RED}Ошибка сохранения: {str(e)}")

    def load_users(self):
        try:
            with open(SAVE_PATH, "r") as f:
                data = json.load(f)
                self.users = {un: User.from_dict(user_data) for un, user_data in data.items()}
        except (FileNotFoundError, json.JSONDecodeError):
            self.users = {}
        except Exception as e:
            print(f"{Fore.RED}Ошибка загрузки: {str(e)}")

    def _load_promocodes(self):
        try:
            with open(KEYS_PATH, "r") as f:
                data = json.load(f)
                valid_codes = {}
                for code, details in data.items():
                    if isinstance(details, dict) and all(key in details for key in ['type', 'amount', 'used']):
                        if details['type'] == 'crypto' and 'coin' not in details:
                            continue
                        valid_codes[code.lower()] = details
                return valid_codes
        except FileNotFoundError:
            print(f"{Fore.YELLOW}Файл промокодов не найден по пути: {KEYS_PATH}")
            return {}
        except Exception as e:
            print(f"{Fore.RED}Ошибка загрузки промокодов: {str(e)}")
            return {}

    def _save_promocodes(self):
        try:
            with open(KEYS_PATH, "w") as f:
                json.dump(self.promo_codes, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"{Fore.RED}Ошибка сохранения промокодов: {str(e)}")

    def activate_promo(self, code):
        if not self.current_user:
            print(dynamic_border(f"{Fore.RED}Требуется авторизация!", Fore.RED))
            return

        code = code.lower()
        promo = self.promo_codes.get(code)

        if not promo:
            print(dynamic_border(f"{Fore.RED}Неверный промокод!", Fore.RED))
            return
            
        if promo["used"]:
            print(dynamic_border(f"{Fore.RED}Промокод уже использован!", Fore.RED))
            return

        if promo["type"] == "xp":
            self.current_user.add_xp(promo["amount"])
            msg = f"+{promo['amount']} XP"
        elif promo["type"] == "currency":
            self._update_balance(promo["amount"])
            msg = f"+{promo['amount']}{CURRENCY}"
        elif promo["type"] == "crypto":
            coin = promo["coin"]
            amount = promo["amount"]
            self.current_user.crypto_balance[coin] += amount
            msg = f"+{amount} {coin} {CRYPTO_SYMBOLS[coin]}"
        else:
            print(dynamic_border(f"{Fore.RED}Неизвестный тип промокода!", Fore.RED))
            return

        self.promo_codes[code]["used"] = True
        self._save_promocodes()
        
        print(dynamic_border(
            f"{Fore.GREEN}Успешная активация!\n"
            f"{Fore.CYAN}Награда: {msg}",
            Fore.GREEN
        ))

    def check_season_event(self):
        now = datetime.now()
        current_month = now.month
        day = now.day
        
        for month, event in SEASON_EVENTS.items():
            start_month, end_day = event["period"]
            if current_month == month and day <= end_day:
                self._print_season_info(event)
                return

    def _print_season_info(self, event):
        content = [
            f"{Fore.MAGENTA}{event['name']}",
            f"{Fore.CYAN}Активные эффекты:"
        ]
        for i, effect in enumerate(event["effects"], 1):
            content.append(f"{i}. {effect}")
        print(dynamic_border('\n'.join(content), 50, Fore.MAGENTA))

    def apply_event_effects(self, amount):
        now = datetime.now()
        for event in SEASON_EVENTS.values():
            start_month, end_day = event["period"]
            if start_month <= now.month <= (start_month + 2):
                if "x2" in event['effects'][0]:
                    amount *= 2
                elif "XP" in event['effects'][0]:
                    self.current_user.add_xp(amount * 0.5)
                elif "Кэшбэк" in event['effects'][0]:
                    self._update_balance(amount * 0.15)
        return amount

    def _check_balance(self, amount, currency="EXTRACT"):
        return self.current_user.crypto_balance.get(currency, 0) >= amount

    def _update_balance(self, amount, currency="EXTRACT"):
        self.current_user.crypto_balance[currency] += amount

    def _validate_bet(self, bet):
        if not self.current_user:
            print(f"{Fore.RED}Сначала выберите пользователя!")
            return False
        if bet <= 0:
            print(f"{Fore.RED}Ставка должна быть положительной!")
            return False
        if not self._check_balance(bet):
            print(f"{Fore.RED}Недостаточно средств!")
            return False
        return True

    def _process_result(self, win, bet):
        win = self.apply_event_effects(win)
        if win > 0:
            self._update_balance(win)
            self.current_user.update_stats(True)
            self.current_user.add_xp(win)
        else:
            self.current_user.update_stats(False)
            self.current_user.add_xp(bet * 0.1)
        self.current_user.total_earned += win
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

    def show_all_profiles(self):
        if not self.users:
            print(dynamic_border(f"{Fore.RED}Нет созданных пользователей!", Fore.RED))
            return
            
        profiles = [f"{i+1}. {un}" for i, un in enumerate(self.users.keys())]
        content = [f"{Fore.CYAN}Зарегистрированные пользователи:"] + profiles
        print(dynamic_border('\n'.join(content), Fore.BLUE))

def slots(self, bet):
        if not self._validate_bet(bet):
            return

        self._update_balance(-bet)

        symbols = ["♦", "♠", "♥", "♣", "★", "‡", "Ω"]
        
        print(dynamic_border(f"{Fore.YELLOW}🌀 Запуск слот-машины...", 40, Fore.YELLOW))
        
        for i in range(12):
            frame = [random.choice(symbols) for _ in range(3)]
            print("\r" + " | ".join(frame), end="")
            time.sleep(0.08 * (i**0.5))

        result = [random.choice(symbols) for _ in range(3)]
        print(f"\r{' | '.join(result)}")

        if all(x == "★" for x in result):
            win = bet * 50
        elif len(set(result)) == 1:
            win = bet * 10
        elif result[0] == result[1] or result[1] == result[2]:
            win = bet * 2
        else:
            win = 0

        self._process_result(win, bet)

        if win > 0:
            print(dynamic_border(f"{Fore.GREEN}Выигрыш! +{win:.2f}{CURRENCY}", 30, Fore.GREEN))
        else:
            print(dynamic_border(f"{Fore.RED}Повезёт в следующий раз!", 30, Fore.RED))

    def trade(self, command):
        if not self.current_user:
            print(f"{Fore.RED}Сначала выберите пользователя!")
                return

        try:
            parts = command.split()
            if len(parts) < 3:
                raise ValueError
            action = parts[0].lower()
            coin = parts[1].upper()
            amount = float(parts[2])

            if amount <= 0:
                print(f"{Fore.RED}Количество должно быть положительным!")
                return

            if coin not in self.market.rates:
                print(f"{Fore.RED}Неизвестная валюта: {coin}")
                return

            if action == "buy":
                cost = amount * self.market.get_rate(coin) * 1.01
                if not self._check_balance(cost):
                    print(f"{Fore.RED}Недостаточно средств!")
                    return
                self._update_balance(-cost)
                self._update_balance(amount, coin)
                self.current_user.add_transaction('buy', coin, amount, cost)
                print(dynamic_border(f"{Fore.GREEN}Куплено {amount:.4f} {coin}", 40, Fore.CYAN))

            elif action == "sell":
                if not self._check_balance(amount, coin):
                    print(f"{Fore.RED}Недостаточно {coin} для продажи!")
                    return
                value = amount * self.market.get_rate(coin) * 0.99
                self._update_balance(-amount, coin)
                self._update_balance(value)
                self.current_user.add_transaction('sell', coin, amount, value)
                print(dynamic_border(f"{Fore.GREEN}Продано {amount:.4f} {coin}", 40, Fore.MAGENTA))

            else:
                print(f"{Fore.RED}Неизвестное действие: {action}")
                return

            self.market.update_rates()
            self.save_users()

        except (IndexError, ValueError):
            print(f"{Fore.RED}Ошибка команды: trade [buy/sell] [монета] [количество]")

    def monster_battle(self, bet):
        if not self._validate_bet(bet):
            return

        self._update_balance(-bet)

        monsters = ["Дракон", "Голем", "Демон", "Титан"]
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

        self._process_result(bet * 2.5 if win else 0, bet)

    def dice(self, bet):
        if not self._validate_bet(bet):
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

        self._process_result(win, bet)

    def high_low(self, bet):
        if not self._validate_bet(bet):
            return

        self._update_balance(-bet)
        
        current_num = random.randint(0, 200)
        next_num = random.randint(0, 200)
        
        print(dynamic_border(f"{Fore.MAGENTA}   CRYPTO HIGH/LOW   ", 45, Fore.MAGENTA))
        
        content = [
            f"{Fore.CYAN}Ставка: {Fore.WHITE}{bet:.2f}{CURRENCY}",
            f"{Fore.CYAN}Баланс: {Fore.WHITE}{self.current_user.crypto_balance['EXTRACT']:.2f}{CURRENCY}"
        ]
        print(dynamic_border('\n'.join(content), 45, Fore.CYAN))

        print(dynamic_border(f"{Fore.YELLOW}Генерация чисел...", 45, Fore.YELLOW))
        
        print(f"{Fore.YELLOW}Текущее число: ", end="")
        for _ in range(8):
            print(f"{Fore.YELLOW}⌛ {random.randint(0, 200):03d}", end="\r")
            time.sleep(0.08)
        print(f"{Fore.GREEN}▶ {current_num:03d} ◀")

        choice = None
        while choice not in ['h', 'l']:
            choice = input(f"{Fore.GREEN}➤ Ваш выбор (H/L): ").strip().lower()

        print(dynamic_border(f"{Fore.YELLOW}Результат...", 45, Fore.YELLOW))
        result_color = Fore.LIGHTGREEN_EX if (next_num > current_num and choice == 'h') or (next_num < current_num and choice == 'l') else Fore.RED
        result = f"{current_num:03d} {'>' if next_num > current_num else '<' if next_num < current_num else '='} {next_num:03d}"
        print(dynamic_border(f"{result_color}{result}", 20, result_color))

        if current_num == next_num:
            win = bet
        elif (choice == 'h' and next_num > current_num) or (choice == 'l' and next_num < current_num):
            win = bet * 2
        else:
            win = 0

        self._process_result(win, bet)

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
  level             - Информация об уровне
  season            - Текущее событие
  crywall           - Крипто-баланс
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

    def check_autosave(self):
        if time.time() - self.last_save > AUTOSAVE_INTERVAL:
            self.save_users()
            self.last_save = time.time()
            print(f"{Fore.GREEN}Автосохранение выполнено!")

def main():
    print_art()
    casino = Casino()
    casino.check_season_event()

    try:
        while True:
            casino.check_autosave()
            
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

            try:
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

                elif action == "level":
                    if casino.current_user:
                        content = [
                            f"{Fore.CYAN}Уровень: {casino.current_user.level}",
                            f"{Fore.BLUE}Опыт: {casino.current_user.xp:.0f}/{casino.current_user.required_xp():.0f}",
                            casino.current_user.show_level_progress(),
                            f"{Fore.GREEN}Всего заработано: {casino.current_user.total_earned:.2f}{CURRENCY}"
                        ]
                        print(dynamic_border('\n'.join(content), 40, Fore.YELLOW))
                    else:
                        print(f"{Fore.RED}Пользователь не выбран!")

                elif action == "season":
                    casino.check_season_event()

                elif action == "crywall":
                    if casino.current_user:
                        casino.current_user.crywall()
                    else:
                        print(f"{Fore.RED}Пользователь не выбран!")

                elif action == "verinf":
                    casino.display_version()

                elif action == "help":
                    casino.display_help()

                elif action.startswith("promo "):
                    code = action.split(" ", 1)[1].strip()
                    casino.activate_promo(code)

                elif action == "all profiles":
                    casino.show_all_profiles()

                elif action == "exit":
                    if casino.current_user:
                        casino.current_user.end_session()
                    casino.save_users()
                    print(f"{gradient_text('\nДо встречи! Ваш прогресс сохранён.\n', [Fore.GREEN, Fore.BLUE])}")
                    break
                
                else:
                    print(f"{Fore.RED}Неизвестная команда. Введите 'help' для помощи")

            except (IndexError, ValueError) as e:
                print(f"{Fore.RED}Ошибка ввода: {str(e)}")
            except Exception as e:
                print(f"{Fore.RED}Неизвестная ошибка: {str(e)}")

    except KeyboardInterrupt:
        print(f"{Fore.RED}\nСрочное сохранение...")
        if casino.current_user:
            casino.current_user.end_session()
        casino.save_users()
        exit()

if __name__ == "__main__":
    # Проверка существования директории /etc
    if not os.path.exists('/etc'):
        os.makedirs('/etc', exist_ok=True)
    main()