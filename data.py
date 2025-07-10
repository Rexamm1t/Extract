import random
import json
import time
import os
from datetime import datetime, timedelta
from colorama import Fore, Style, init

ADDINFO = "EXTRACT™ PLATFORM 2025"
INFO = "Extract Team (Rexamm1t, Wefol1x)"
VERSION = "EXTRACT 9.6.0"
VERSION_ALL = "EXTRACT 9.6.0 (9.7.25) (UNIX base)"
SAVE_PATH = "scripts/users.json"
KEYS_PATH = "scripts/keys.json"
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
INITIAL_BALANCE = 10000.0
LEVEL_BASE_XP = 200
SEASON_EVENTS = {
    12: {"name": "Зимний Ивент", "period": (1, 24.2),
         "effects": ["x2 бонусам", "Скидки 20%", "Новогодний джекпот"]},
    3: {"name": "Весенний Ивент", "period": (1.3, 30.5),
        "effects": ["+150% XP", "Бесплатные спины", "Цветочные бонусы"]},
    6: {"name": "Летний Ивент", "period": (1.6, 31.8),
        "effects": ["Кэшбэк 15%", "Пляжные бонусы", "Страховка ставок"]},
    9: {"name": "Осенний Ивент", "period": (1.9, 1.12),
        "effects": ["Урожай x2", "Бонусы за депозит", "Осенние скидки"]}
}
AUTOSAVE_INTERVAL = 300

init(autoreset=True)

def dynamic_border(text, border_color=Fore.MAGENTA, width=None):
    lines = text.split('\n')
    max_width = width if width else max(len(line) for line in lines) + 4
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
                                ,----,                                             ,----, 
                              ,/   .`|                                           ,/   .`| 
    ,---,. ,--,     ,--,    ,`   .'  :,-.----.      ,---,         ,----..      ,`   .'  : 
  ,'  .' | |'. \   / .`|  ;    ;     /\    /  \    '  .' \       /   /   \   ;    ;     / 
,---.'   | ; \ `\ /' / ;.'___,/    ,' ;   :    \  /  ;    '.    |   :     :.'___,/    ,'  
|   |   .' `. \  /  / .'|    :     |  |   | .\ : :  :       \   .   |  ;. /|    :     |   
:   :  |-,  \  \/  / ./ ;    |.';  ;  .   : |: | :  |   /\   \  .   ; /--` ;    |.';  ;   
:   |  ;/|   \  \.'  /  `----'  |  |  |   |  \ : |  :  ' ;.   : ;   | ;    `----'  |  |   
|   :   .'    \  ;  ;       '   :  ;  |   : .  / |  |  ;/  \   \|   : |        '   :  ;   
|   |  |-,   / \  \  \      |   |  '  ;   | |  \ '  :  | \  \ ,'.   | '___     |   |  '   
'   :  ;/|  ;  /\  \  \     '   :  |  |   | ;\  \|  |  '  '--'  '   ; : .'|    '   :  |   
|   |    \./__;  \  ;  \    ;   |.'   :   ' | \.'|  :  :        '   | '/  :    ;   |.'    
|   :   .'|   : / \  \  ;   '---'     :   : :-'  |  | ,'        |   :    /     '---'      
|   | ,'  ;   |/   \  ' |             |   |.'    `--''           \   \ .'                 
`----'    `---'     `--`              `---'                       `---`
    """
    print(gradient_text(art, [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]))

class CryptoMarket:
    def __init__(self):
        self.rates = {
            "BETASTD": random.uniform(7750100, 10000000),
            "DOGCOIN": random.uniform(1000000, 2000000),
            "EXRSD": random.uniform(328110, 400000),
            "BTC": random.uniform(25000, 110000),
            "ETH": random.uniform(1500, 6000),
            "LTC": random.uniform(60, 455),
            "BNB": random.uniform(200, 600),
            "ADA": random.uniform(200, 500),
            "SOL": random.uniform(20, 200),
            "XRP": random.uniform(50, 100),
            "DOT": random.uniform(4, 300),
            "DOGE": random.uniform(300, 500),
            "SHIB": random.uniform(1000, 20000),
            "AVAX": random.uniform(10, 100),
            "TRX": random.uniform(100, 200),
            "MATIC": random.uniform(14000, 16000),
            "ATOM": random.uniform(600, 1000),
            "NOT": random.uniform(0.05, 0.5),
            "TON": random.uniform(1.0, 6.5),
            "XYZ": random.uniform(0.01, 0.1),
            "ABC": random.uniform(10, 50),
            "DEF": random.uniform(100, 500),
            "GHI": random.uniform(5, 20),
            "JKL": random.uniform(0.001, 0.01),
            "MNO": random.uniform(0.5, 2),
            "PQR": random.uniform(1000, 5000),
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
        reward = self.level * 1000
        self.crypto_balance["EXTRACT"] += reward
        print(dynamic_border(
            f"{Fore.GREEN}🎉 Уровень Повышен! {self.level-1} => {self.level}\n"
            f"+{reward}{CURRENCY} - Ваш бонус за уровень!\n"
            f"Следующий уровень: {self.required_xp():.0f} XP",
            Fore.YELLOW
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
        print(dynamic_border(f"{Fore.GREEN}Профиль {self.username}\n{stats}", Fore.GREEN))

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
        print(dynamic_border('\n'.join(content), Fore.MAGENTA))

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

        print(dynamic_border(f"{Fore.CYAN}🎰 ИГРАЕМ В АВТОМАТЫ!", Fore.CYAN))
        self._update_balance(-bet)

        symbols = ["🍒", "🍊", "🍋", "💎", "7️⃣", "🔔"]
        results = [random.choice(symbols) for _ in range(3)]
        line = " | ".join(results)
        print(f"\n{line}\n")

        if results[0] == results[1] == results[2]:
            win = bet * 10
            print(dynamic_border(f"{Fore.GREEN}ДЖЕКПОТ! +{win}{CURRENCY}", Fore.GREEN))
        elif results[0] == results[1] or results[1] == results[2]:
            win = bet * 2
            print(dynamic_border(f"{Fore.YELLOW}Выигрыш! +{win}{CURRENCY}", Fore.YELLOW))
        else:
            win = 0
            print(dynamic_border(f"{Fore.RED}Проигрыш", Fore.RED))

        self._process_result(win, bet)

    def trade(self, command):
        if not self.current_user:
            print(f"{Fore.RED}Сначала выберите пользователя! add/login [ник]")
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
                self.current_user.crypto_balance[coin] += amount
                self.current_user.add_transaction('buy', coin, amount, cost)
                print(dynamic_border(f"{Fore.GREEN}Куплено {amount:.4f} {coin}", Fore.CYAN, 40))

            elif action == "sell":
                if self.current_user.crypto_balance.get(coin, 0) < amount:
                    print(f"{Fore.RED}Недостаточно {coin} для продажи!")
                    return
                value = amount * self.market.get_rate(coin) * 0.99
                self.current_user.crypto_balance[coin] -= amount
                self._update_balance(value)
                self.current_user.add_transaction('sell', coin, amount, value)
                print(dynamic_border(f"{Fore.GREEN}Продано {amount:.4f} {coin}", Fore.MAGENTA, 40))

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

        print(dynamic_border(f"{Fore.RED}🐉 ВСТУПАЕМ В БОЙ!", Fore.RED))
        self._update_balance(-bet)

        player_attack = random.randint(50, 150) + self.current_user.level * 2
        monster_attack = random.randint(50, 150)

        print(f"{Fore.CYAN}Ваша сила атаки: {player_attack}")
        print(f"{Fore.RED}Сила атаки монстра: {monster_attack}")

        if player_attack > monster_attack:
            win = bet * 3
            print(dynamic_border(f"{Fore.GREEN}ПОБЕДА! +{win}{CURRENCY}", Fore.GREEN))
        else:
            win = 0
            print(dynamic_border(f"{Fore.RED}ПОРАЖЕНИЕ", Fore.RED))

        self._process_result(win, bet)

    def dice(self, bet):
        if not self._validate_bet(bet):
            return

        print(dynamic_border(f"{Fore.YELLOW}🎲 БРОСАЕМ КОСТИ", Fore.YELLOW))
        self._update_balance(-bet)

        player_dice = sum(random.randint(1, 6) for _ in range(3))
        dealer_dice = sum(random.randint(1, 6) for _ in range(3))

        print(f"{Fore.CYAN}Ваши кости: {player_dice}")
        print(f"{Fore.RED}Кости дилера: {dealer_dice}")

        if player_dice > dealer_dice:
            win = bet * 2
            print(dynamic_border(f"{Fore.GREEN}ВЫИГРЫШ! +{win}{CURRENCY}", Fore.GREEN))
        else:
            win = 0
            print(dynamic_border(f"{Fore.RED}ПРОИГРЫШ", Fore.RED))

        self._process_result(win, bet)

    def high_low(self, bet):
        if not self._validate_bet(bet):
            return

        print(dynamic_border(f"{Fore.MAGENTA}🎴 ИГРА HIGH-LOW", Fore.MAGENTA))
        self._update_balance(-bet)

        current = random.randint(1, 200)
        print(f"Текущее число: {Fore.CYAN}{current}")

        choice = input(f"{Fore.YELLOW}Следующее будет выше (h) или ниже (l)? ").lower()

        next_num = random.randint(1, 200)
        print(f"Новое число: {Fore.CYAN}{next_num}")

        if (choice == 'h' and next_num > current) or (choice == 'l' and next_num < current):
            win = bet * 2
            print(dynamic_border(f"{Fore.GREEN}ПОБЕДА! +{win}{CURRENCY}", Fore.GREEN))
        else:
            win = 0
            print(dynamic_border(f"{Fore.RED}ПРОИГРЫШ", Fore.RED))

        self._process_result(win, bet)

    def show_rates(self):
        content = [f"{Fore.CYAN}Текущие курсы:"]
        for coin, rate in self.market.rates.items():
            if coin == "EXTRACT":
                continue
            content.append(
                f"{CRYPTO_SYMBOLS[coin]} 1 {coin} = {rate:.2f}{CURRENCY}"
            )
        print(dynamic_border('\n'.join(content), Fore.BLUE))

    def newnote_up(self):
        path_text = f"""
{Fore.CYAN}EXTRACT 9.6.0 (9.7.25)\n
{Fore.WHITE}1. 13 Новых крипто токенов
{Fore.WHITE}2. Патчноут
{Fore.WHITE}3. Глобальная переделка команд
{Fore.WHITE}4. Редизайн меню помощи
{Fore.WHITE}5. Изменения баланса в играх
{Fore.RED}___\n
        """
        print(dynamic_border(path_text.strip(), Fore.CYAN)) 

    def display_help(self):
        help_text = f"""
{Fore.CYAN}Доступные команды:
{Fore.WHITE}           ---Аккаунт---\n
{Fore.GREEN}add    [ник]                {Fore.WHITE}- Создать нового пользователя
{Fore.GREEN}login  [ник]                {Fore.WHITE}- Выбрать пользователя
{Fore.GREEN}all                         {Fore.WHITE}- Все профили
{Fore.GREEN}delete [ник]                {Fore.WHITE}- Удалить пользователя
{Fore.GREEN}show                        {Fore.WHITE}- Статистика профиля
{Fore.GREEN}exit -a                     {Fore.WHITE}- Выйти из аккаунта\n
{Fore.WHITE}             ---Игры---\n
{Fore.RED}slots [сумма]                 {Fore.WHITE}- Играть в автоматы
{Fore.RED}battle [сумма]                {Fore.WHITE}- Сразиться с монстром
{Fore.RED}dice [сумма]                  {Fore.WHITE}- Игра в кости
{Fore.RED}highlow [сумма]               {Fore.WHITE}- Игра High-Low\n
{Fore.WHITE}         ---Криптовалюта---\n
{Fore.BLUE}trade buy [монета] [кол-во]  {Fore.WHITE}- Купить крипту
{Fore.BLUE}trade sell [монета] [кол-во] {Fore.WHITE}- Продать крипту
{Fore.BLUE}rates                        {Fore.WHITE}- Показать курсы обмена
{Fore.BLUE}wal                          {Fore.WHITE}- Показать баланс всего кошелька\n
{Fore.WHITE}       ---Игровые события---\n
{Fore.YELLOW}season                     {Fore.WHITE}- Информация об ивентах
{Fore.YELLOW}promo [код]                {Fore.WHITE}- Активировать промокод\n
{Fore.WHITE}          ---Об Extract---\n
{Fore.CYAN}extract                      {Fore.WHITE}- Информация о версии
{Fore.CYAN}wnew                         {Fore.WHITE}- Патчноут\n
{Fore.WHITE}            ---Прочее---\n
{Fore.MAGENTA}exit                      {Fore.WHITE}- Выйти из игры
{Fore.MAGENTA}help                      {Fore.WHITE}- Справка по командам\n
        """
        print(dynamic_border(help_text.strip(), Fore.CYAN))

    def display_version(self):
        print_art()
        version_info = f"""
{Fore.YELLOW}{ADDINFO}
{Fore.YELLOW}{VERSION_ALL}\n
{Fore.RED}{INFO}
{Fore.RED}Авторы: Rexamm1t, Wefol1x
{Fore.RED}Telegram: @rexamm1t, @wefolix\n
{Fore.GREEN}Лицензия: MIT
        """
        print(dynamic_border(version_info.strip(), Fore.BLUE))

    def check_autosave(self):
        if time.time() - self.last_save > AUTOSAVE_INTERVAL:
            self.save_users()
            self.last_save = time.time()

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
                    f"{Fore.BLUE}╭─{username_gradient} - {VERSION}\n"
                    f"{Fore.BLUE}╰─{gradient_text('➤', [Fore.GREEN, Fore.YELLOW])} {Style.RESET_ALL}"
                )
            else:
                prompt = f"{Fore.BLUE}╭─{VERSION_ALL} - Нужна помощь? - help\n╰─➤ {Style.RESET_ALL}"

            try:
                action = input(prompt).strip()
                casino.last_command = action.split()[0] if action else ""

                if action.startswith("add "):
                    username = action.split(" ", 1)[1]
                    casino.create_user(username)

                elif action.startswith("login "):
                    username = action.split(" ", 1)[1]
                    casino.select_user(username)

                elif action.startswith("delete "):
                    username = action.split(" ", 1)[1]
                    casino.delete_user(username)

                elif action == "exit -a":
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
                        print(f"{Fore.RED}Используйте: dice [сумма]"
                          )
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

                elif action == "show":
                    if casino.current_user:
                        casino.current_user.show_stats()
                    else:
                        print(f"{Fore.RED}Пользователь не выбран! Загрузитесь в аккаунт.")

                elif action == "level":
                    if casino.current_user:
                        content = [
                            f"{Fore.CYAN}Уровень: {casino.current_user.level}",
                            f"{Fore.BLUE}Опыт: {casino.current_user.xp:.0f}/{casino.current_user.required_xp():.0f}",
                            casino.current_user.show_level_progress(),
                            f"{Fore.GREEN}Всего заработано: {casino.current_user.total_earned:.2f}{CURRENCY}"
                        ]
                        print(dynamic_border('\n'.join(content), Fore.YELLOW))
                    else:
                        print(f"{Fore.RED}Пользователь не выбран!")

                elif action == "season":
                    casino.check_season_event()

                elif action == "wal":
                    if casino.current_user:
                        casino.current_user.crywall()
                    else:
                        print(f"{Fore.RED}Пользователь не выбран!")

                elif action == "extract":
                    casino.display_version()

                elif action == "wnew":
                    casino.newnote_up()

                elif action == "help":
                    casino.display_help()

                elif action.startswith("promo "):
                    code = action.split(" ", 1)[1].strip()
                    casino.activate_promo(code)

                elif action == "all":
                    casino.show_all_profiles()

                elif action == "exit":
                    if casino.current_user:
                        casino.current_user.end_session()
                    casino.save_users()
                    print(gradient_text("\nДо встречи! Ваш прогресс сохранён.\n", [Fore.GREEN, Fore.BLUE]))
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
    if not os.path.exists('/etc'):
        os.makedirs('/etc', exist_ok=True)
    main()
