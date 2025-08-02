import random
import json
import time
import os
import textwrap
from datetime import datetime, timedelta
from colorama import Fore, Style, init

ADDINFO = "EXTRACT™ PLATFORM 2025"
INFO = "Extract Team (Rexamm1t, Wefol1x)"
VERSION = "EXTRACT 10.2.6"
VERSION_ALL = "EXTRACT 10.2.6 (7.7.25)"

SAVE_PATH = "data/users.json"
KEYS_PATH = "data/keys.json"
RECEIPTS_PATH = "logs/receipts.json"
CS_LOG_PATH = "logs/cs_l.json"
FORUM_PATH = "forum/meta.json"

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
LEVEL_BASE_XP = 1000

AUTOSAVE_INTERVAL = 300

MONTHLY_EVENTS = {
    1: {
        "name": "❄️ Новогодний Разгон",
        "effects": {
            "slots_multiplier": 1.8,
            "free_daily_spins": 3,
            "level_up_bonus": 2000
        }
    },
    2: {
        "name": "💘 Битва Сердец",
        "effects": {
            "double_win_chance": True,
            "referral_bonus": 1.5,
            "loss_protection": 0.25
        }
    },
    3: {
        "name": "🌱 Весенний Рост",
        "effects": {
            "xp_boost": 2.0,
            "trade_xp_bonus": 3,
            "daily_interest": 0.01
        }
    },
    4: {
        "name": "🌸 Апрельский Лотес",
        "effects": {
            "jackpot_chance": 0.15,
            "insurance": 0.2,
            "daily_bonus": 1500
        }
    },
    5: {
        "name": "⚡ Майский Штурм",
        "effects": {
            "battle_xp": 1.8,
            "daily_gift": 1500,
            "free_spins": 2
        }
    },
    6: {
        "name": "🌞 Летний Круиз",
        "effects": {
            "trade_fee": 0.7,
            "slots_bonus": 3000,
            "xp_multiplier": 1.4
        }
    },
    7: {
        "name": "🔥 Жаркий Удар",
        "effects": {
            "xp_multiplier": 1.4,
            "free_spins": 3,
            "daily_interest": 0.015
        }
    },
    8: {
        "name": "🌪️ Августовский Ветер",
        "effects": {
            "win_multiplier": 1.25,
            "insurance": 0.25,
            "trade_bonus": 1.1
        }
    },
    9: {
        "name": "🍂 Осенний Урожай",
        "effects": {
            "trade_bonus": 1.3,
            "daily_gift": 2000,
            "xp_boost": 1.5
        }
    },
    10: {
        "name": "🎃 Хеллоуин Спешиал",
        "effects": {
            "jackpot_chance": 0.2,
            "battle_xp": 2.0,
            "mystery_gift": True
        }
    },
    11: {
        "name": "🌧️ Ноябрьский Шторм",
        "effects": {
            "xp_multiplier": 1.6,
            "slots_bonus": 4000,
            "loss_protection": 0.3
        }
    },
    12: {
        "name": "🎄 Зимнее Чудо",
        "effects": {
            "win_multiplier": 1.5,
            "year_end_special": True,
            "unlimited_withdrawals": True
        }
    }
}

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
      ___           ___           ___           ___           ___           ___           ___     
     /\  \         |\__\         /\  \         /\  \         /\  \         /\  \         /\  \    
    /::\  \        |:|  |        \:\  \       /::\  \       /::\  \       /::\  \        \:\  \   
   /:/\:\  \       |:|  |         \:\  \     /:/\:\  \     /:/\:\  \     /:/\:\  \        \:\  \  
  /::\~\:\  \      |:|__|__       /::\  \   /::\~\:\  \   /::\~\:\  \   /:/  \:\  \       /::\  \ 
 /:/\:\ \:\__\ ____/::::\__\     /:/\:\__\ /:/\:\ \:\__\ /:/\:\ \:\__\ /:/__/ \:\__\     /:/\:\__\
 \:\~\:\ \/__/ \::::/~~/~       /:/  \/__/ \/_|::\/:/  / \/__\:\/:/  / \:\  \  \/__/    /:/  \/__/
  \:\ \:\__\    ~~|:|~~|       /:/  /         |:|::/  /       \::/  /   \:\  \         /:/  /     
   \:\ \/__/      |:|  |       \/__/          |:|\/__/        /:/  /     \:\  \        \/__/      
    \:\__\        |:|  |                      |:|  |         /:/  /       \:\__\                  
     \/__/         \|__|                       \|__|         \/__/         \/__/                  
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

    def save_rates(self):
        try:
            os.makedirs(os.path.dirname(CS_LOG_PATH), exist_ok=True)
            with open(CS_LOG_PATH, "w") as f:
                json.dump(self.rates, f, indent=4)
        except Exception as e:
            print(f"{Fore.YELLOW}Не удалось сохранить курсы: {str(e)}")

    def update_rates(self):
        old_rates = self.rates.copy()
        for coin in self.rates:
            if coin != "EXTRACT":
                change = random.uniform(-0.07, 0.07)
                self.rates[coin] = max(0.01, self.rates[coin] * (1 + change))
        self.save_rates()
        return old_rates

class Forum:
    def __init__(self):
        self.messages = []
        self.load_messages()

    def load_messages(self):
        try:
            os.makedirs(os.path.dirname(FORUM_PATH), exist_ok=True)
            if not os.path.exists(FORUM_PATH):
                default_messages = [{
                    "id": 1,
                    "title": "Добро пожаловать в EXTRACT!",
                    "content": "Это официальный форум платформы. Здесь будут появляться важные объявления.",
                    "author": "Extract Team",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "pinned": True
                }]
                with open(FORUM_PATH, 'w', encoding='utf-8') as f:
                    json.dump(default_messages, f, indent=4)
            
            with open(FORUM_PATH, 'r', encoding='utf-8') as f:
                self.messages = json.load(f)
        except Exception as e:
            print(f"{Fore.YELLOW}Ошибка загрузки форума: {str(e)}")
            self.messages = []

    def show_forum(self, limit=5):
        pinned = [m for m in self.messages if m.get("pinned", False)]
        regular = [m for m in self.messages if not m.get("pinned", False)]
        messages = (pinned + regular)[:limit]
        
        if not messages:
            print(dynamic_border(f"{Fore.YELLOW}На форуме пока нет сообщений", Fore.YELLOW))
            return

        content = [
            f"{Fore.RED}╔{'═'*50}╗",
            f"║{'EXTRAFORUM'.center(50)}║",
            f"╠{'═'*50}╣"
        ]

        for msg in messages:
            pin = "📌 " if msg.get("pinned", False) else ""
            content.append(f"║ {pin}{Fore.YELLOW}{msg['title'].ljust(48)}║")
            content.append(f"║ {Fore.WHITE}Автор: {msg.get('author', 'Extract Team')} | Дата: {msg.get('date', 'N/A')} ║")
            content.append(f"╠{'─'*50}╣")
            
            # Разбиваем текст на строки по 48 символов
            for line in textwrap.wrap(msg['content'], width=48):
                content.append(f"║ {Fore.GREEN}{line.ljust(48)}║")
            
            content.append(f"╠{'═'*50}╣")

        print('\n'.join(content))

class User:
    def __init__(self, username):
        self.username = username
        self.crypto_balance = {coin: 0.0 for coin in CRYPTO_SYMBOLS}
        self.crypto_balance["EXTRACT"] = INITIAL_BALANCE
        self.games_played = 0
        self.wins = 0
        self.losses = 0
        self.transactions = []
        self.total_earned = 0.0
        self.play_time = 0.0
        self.session_start = None
        self.level = 1
        self.xp = 0
        self.total_earned = 0.0
        self.subscription = {"type": "none", "expires_at": None, "autorenew": False}
        self.last_login = None
        self.free_spins = 0
        self.consecutive_wins = 0
        self.last_action_time = None

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
            "total_earned": self.total_earned,
            "subscription": self.subscription,
            "last_login": self.last_login,
            "free_spins": self.free_spins,
            "consecutive_wins": self.consecutive_wins
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
        user.subscription = data.get("subscription", {"type": "none", "expires_at": None, "autorenew": False})
        user.last_login = data.get("last_login", None)
        user.free_spins = data.get("free_spins", 0)
        user.consecutive_wins = data.get("consecutive_wins", 0)
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
        xp_gain = amount
        if self.subscription["type"] == "eup":
            xp_gain *= 1.2
        elif self.subscription["type"] == "eup_plus":
            xp_gain *= 1.5

        self.xp += xp_gain
        while self.xp >= self.required_xp():
            self.xp -= self.required_xp()
            self.level_up()

    def required_xp(self):
        base = LEVEL_BASE_XP * 5
        return int(base * (self.level ** 2.2 + self.level * 8))

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
        req = self.required_xp()
        progress = min(1.0, self.xp / req)
        gradient = [Fore.RED, Fore.YELLOW, Fore.GREEN]
        color = gradient[min(2, int(progress * 3))]
        
        bar = "▓" * int(progress * 20) + "░" * (20 - int(progress * 20))
        return f"{Fore.CYAN}{bar} {progress*100:.1f}%"

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
        THEME = {
            'eup': Fore.CYAN,
            'eup_plus': Fore.YELLOW,
            'base': Fore.GREEN,
            'stats': Fore.MAGENTA,
            'transactions': Fore.WHITE
        }

        if self.has_active_subscription():
            expiry_date = datetime.strptime(self.subscription["expires_at"], "%Y-%m-%d")
            days_left = (expiry_date - datetime.now()).days
            sub_icon = "🔷" if self.subscription["type"] == "eup" else "🔶"
            sub_color = THEME[self.subscription["type"]]
    
            sub_header = f"{sub_icon} {sub_color}{self.subscription['type'].upper()}"
            sub_details = [
                f"  {sub_color}Действует до: {expiry_date.strftime('%d.%m.%Y')}",
                f"  {sub_color}Осталось: {days_left} дней",
                f"  {sub_color}Бонусы: +{25 if self.subscription['type'] == 'eup_plus' else 10}% выигрыши, "
                f"{20 if self.subscription['type'] == 'eup_plus' else 10}% страховка"
            ]
        else:
            sub_header = f"⚪ {Fore.RED}БЕЗ ПОДПИСКИ"
            sub_details = [
                f"  {Fore.RED}Доступные подписки:",
                f"> {Fore.CYAN}EUP  - 10 BTC/день",
                f"> {Fore.YELLOW}EUP+ - 15 BTC/день + бонусы"
            ]

        profile = [
            f"{THEME['base']}╭─────────────────────────────────╮",
            f"│        {Fore.WHITE}    Подписка             {THEME['base']}│",
            f"├─────────────────────────────────|",
            f"    {sub_header.ljust(30)}{THEME['base']}",
            *sub_details,
            f"{THEME['base']}╭─────────────────────────────────╮",
            f"│        {Fore.WHITE}   Статистика            {THEME['base']}│",
            f"├─────────────────────────────────|",
            f"  {Fore.YELLOW}Баланс: {self.crypto_balance['EXTRACT']:,.2f} {CURRENCY}\n",
            f"  {THEME['stats']}WLR: {self.win_loss_ratio()}%           ",
            f"  {THEME['stats']}Игр: {self.games_played}  🏆 {self.wins}  💀 {self.losses}\n",
            f"{THEME['base']} ───────────────────────────────── \n",
            f"  {THEME['stats']}Уровень: {self.level:<2}\n",
            f"  {THEME['stats']}{self.show_level_progress()}\n"
        ]

        top_coins = sorted(
            [(k, v) for k, v in self.crypto_balance.items() if v > 0 and k != "EXTRACT"],
            key=lambda x: x[1],
            reverse=True
        )[:3]

        if top_coins:
            profile.extend([
                f"{THEME['base']}╭─────────────────────────────────╮",
                f"│        {Fore.WHITE}   Топ активы            {THEME['base']}│",
                f"├─────────────────────────────────|",
            ])
            for coin, amount in top_coins:
                profile.append(f"  {THEME['stats']}  {CRYPTO_SYMBOLS[coin]} {coin}: {amount:>12.2f}  {THEME['base']} ")

        if self.transactions:
            profile.extend([
                f"{THEME['base']}╭─────────────────────────────────╮",
                f"│       {Fore.WHITE}Последние транзакции      {THEME['base']}│",
                f"├─────────────────────────────────|",
            ])
            for t in self.transactions[:6]:
                if t['action'] in ['buy', 'sell']:
                    action_icon = "+" if t['action'] == 'buy' else "-"
                    action_color = Fore.GREEN if t['action'] == 'buy' else Fore.RED
                    profile.append(
                        f"  {action_icon} {t['timestamp'][5:16]} "
                        f"{action_color}{t['action'].upper()} {t['amount']:.2f} {t['coin']} "
                        f"{THEME['transactions']}за {t['total']}{CURRENCY} {THEME['base']} "
                    )
                elif t['action'] == 'transfer_in':
                    profile.append(
                        f"  + {t['timestamp'][5:16]} "
                        f"{Fore.GREEN}Получено (перевод) {t['amount']:.2f} {t['coin']} "
                        f"{THEME['transactions']}от {t['from']} {THEME['base']} "
                    )
                elif t['action'] == 'transfer_out':
                    profile.append(
                        f"  - {t['timestamp'][5:16]} "
                        f"{Fore.RED}Переведено {t['amount']:.2f} {t['coin']} "
                        f"{THEME['transactions']}комиссия: {t['commission']:.2f} {THEME['base']} "
                    )

        profile.append(f" ───────────────────────────────── ")
        print('\n'.join(profile))

    def has_active_subscription(self):
        if self.subscription["type"] == "none":
            return False
        if self.subscription["expires_at"] is None:
            return False
        expiry_date = datetime.strptime(self.subscription["expires_at"], "%Y-%m-%d")
        return datetime.now() <= expiry_date
    
    def get_styled_username(self):
        if not self.has_active_subscription():
            return self.username
        if self.subscription["type"] == "eup":
            return f"{Style.BRIGHT}{Fore.CYAN}{self.username}{Style.RESET_ALL}"
        return f"{Style.BRIGHT}{Fore.YELLOW}{self.username}{Style.RESET_ALL}"
    
    def give_daily_bonus(self):
        today = datetime.now().strftime("%Y-%m-%d")
        if self.last_login == today:
            return
        
        self.last_login = today
        
        if self.subscription["type"] == "eup":
            bonus = 1000000
            self.crypto_balance["EXTRACT"] += bonus
            print(dynamic_border(f"{Fore.CYAN}Ежедневный бонус EUP: +1,000,000Ⓔ", Fore.CYAN))
        
        elif self.subscription["type"] == "eup_plus":
            bonus = 10000000
            self.crypto_balance["EXTRACT"] += bonus
            print(dynamic_border(f"{Fore.YELLOW}Ежедневный бонус EUP+: +2,000,000Ⓔ", Fore.YELLOW))
            
            if random.random() < 0.05:
                btc_bonus = 10.0
                self.crypto_balance["BTC"] = self.crypto_balance.get("BTC", 0) + btc_bonus
                print(dynamic_border(f"{Fore.GREEN}СУПЕРБОНУС! +10 ₿", Fore.GREEN))
    
    def check_subscription(self):
        if not self.has_active_subscription():
            self.subscription = {"type": "none", "expires_at": None, "autorenew": False}
    
    def buy_eup(self, days):
        if not 1 <= days <= 365:
            print(f"{Fore.RED}Ошибка: можно купить от 1 до 365 дней! Не больше одного года.")
            return
        
        cost = 10 * days
        print(dynamic_border(
            f"{Fore.BLUE}EUP base -------------------- Base\n"
            f"{Fore.CYAN}Подтвердите покупку EUP на {days} дней\n"
            f"Стоимость: {cost} ₿\n"
            f"Ваш баланс BTC: {self.crypto_balance.get('BTC', 0):.8f} ₿\n\n"
            f"{Fore.YELLOW}Введите 'yes' для оплаты:",
            Fore.CYAN
        ))
        
        confirm = input(">>> ").lower()
        if confirm == "yes":
            if self.crypto_balance.get("BTC", 0) >= cost:
                self.crypto_balance["BTC"] -= cost
                expiry_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
                self.subscription = {"type": "eup", "expires_at": expiry_date, "autorenew": True}
                print(dynamic_border(
                    f"{Fore.GREEN}Оплачено! EUP активна до {expiry_date}\n"
                    f"{Fore.BLUE}Благодарим за покупку!\n"
                    f"Новый баланс BTC: {self.crypto_balance['BTC']:.8f} ₿",
                    Fore.GREEN
                ))
            else:
                print(f"{Fore.RED}Недостаточно BTC!")
        else:
            print(f"{Fore.YELLOW}Отменено.")
    
    def buy_eup_plus(self, days):
        if not 1 <= days <= 365:
            print(f"{Fore.RED}Ошибка: можно купить от 1 до 365 дней! Не больше одного года")
            return
        
        cost = 15 * days
        print(dynamic_border(
            f"{Fore.YELLOW}EUP plus -------------------- Plus\n"
            f"{Fore.YELLOW}Покупка EUP+ на {days} дней\n"
            f"Стоимость: {cost} ₿\n"
            f"Ваш баланс: {self.crypto_balance.get('BTC', 0):.8f} ₿\n"
            f"{Fore.CYAN}Введите 'yes' для подтверждения:",
            Fore.YELLOW
        ))
        
        if input(">>> ").lower() != "yes":
            print(f"{Fore.YELLOW}Отменено.")
            return
        
        if self.crypto_balance.get("BTC", 0) < cost:
            print(f"{Fore.RED}Недостаточно BTC. Нужно: {cost} ₿")
            return
        
        self.crypto_balance["BTC"] -= cost
        expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        self.subscription = {
            "type": "eup_plus",
            "expires_at": expiry,
            "autorenew": False
        }
        
        bonus = 2000000
        self.crypto_balance["EXTRACT"] += bonus
        
        print(dynamic_border(
            f"{Fore.GREEN}EUP+ активирована до {expiry}!\n"
            f"+{bonus}Ⓔ бонус за покупку. Благодарим за покупку!\n"
            f"Новый баланс BTC: {self.crypto_balance['BTC']:.8f} ₿",
            Fore.GREEN
        ))
    
    def eup_status(self):
        if not self.has_active_subscription():
            print(f"{Fore.RED}У вас нет никаких активных подписок.")
            return
        
        remaining = (datetime.strptime(self.subscription["expires_at"], "%Y-%m-%d") - datetime.now()).days
        print(dynamic_border(
            f"{Fore.CYAN}Статус Подписки\n"
            f"Действует до: {self.subscription['expires_at']}\n"
            f"Осталось дней: {remaining}\n"
            f"Автопродление: {'вкл' if self.subscription.get('autorenew', False) else 'выкл'}\n",
            Fore.CYAN
        ))
    
    def eup_autonone(self):
        if not self.has_active_subscription():
            print(f"{Fore.RED}У вас нет активной подписки!")
            return
        
        self.subscription["autorenew"] = False
        print(f"{Fore.GREEN}Автопродление подписок отключено. Действующая подписка истечёт {self.subscription['expires_at']}.")

class Casino:
    def __init__(self):
        self.users = {}
        self.current_user = None
        self.market = CryptoMarket()
        self.last_command = ""
        self.last_save = time.time()
        self.promo_codes = self._load_promocodes()
        self.forum = Forum()
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
        elif promo["type"] == "eup":
            expiry_date = (datetime.now() + timedelta(days=promo['amount'])).strftime("%Y-%m-%d")
            self.current_user.subscription = {
                "type": "eup",
                "expires_at": expiry_date,
                "autorenew": False
            }
            msg = f"EUP подписка на {promo['amount']} дней"

        elif promo["type"] == "eup_plus":
            expiry_date = (datetime.now() + timedelta(days=promo['amount'])).strftime("%Y-%m-%d")
            self.current_user.subscription = {
                "type": "eup_plus",
                "expires_at": expiry_date,
                "autorenew": False
            }
            msg = f"EUP+ подписка на {promo['amount']} дней"

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

    def get_current_event(self):
        current_month = datetime.now().month
        event = MONTHLY_EVENTS.get(current_month, {}).copy()
        if event:
            event["active"] = True
            return event
        return None

    def apply_event_bonus(self, bonus_type, base_value):
        event = self.get_current_event()
        if not event or "effects" not in event:
            return base_value
            
        bonus = event["effects"].get(bonus_type, 1.0)
        
        if isinstance(bonus, (int, float)):
            return base_value * bonus
        elif isinstance(bonus, int):
            return base_value + bonus
        return base_value

    def show_monthly_event(self):
        event = self.get_current_event()
        if not event:
            print(dynamic_border(f"{Fore.YELLOW}В этом месяце нет активных событий", Fore.YELLOW))
            return
        
        month_name = datetime.now().strftime("%B")
        days_left = (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1) - datetime.now()
        
        content = [
            f"{Fore.MAGENTA}📅 {month_name} - {event['name']}",
            f"{Fore.CYAN}Осталось: {days_left.days} дней",
            f"{Fore.GREEN}Действующие бонусы:",
        ]
        
        bonus_icons = {
            "multiplier": "📈",
            "bonus": "🎁", 
            "special": "✨",
            "protection": "🛡️"
        }
        
        for effect, value in event["effects"].items():
            icon = bonus_icons.get(effect.split('_')[-1], "▪️")
            if isinstance(value, bool):
                content.append(f"{icon} {effect}: {'Активен' if value else 'Неактивен'}")
            elif isinstance(value, float):
                content.append(f"{icon} {effect}: x{value}")
            else:
                content.append(f"{icon} {effect}: +{value}")
        
        print(dynamic_border('\n'.join(content), Fore.MAGENTA))

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
        win = self.apply_event_bonus("win_multiplier", win)
        if win > 0:
            self._update_balance(win)
            self.current_user.update_stats(True)
            self.current_user.add_xp(win)
        else:
            self.current_user.update_stats(False)
            self.current_user.add_xp(bet * 0.1)
        self.current_user.total_earned += win
        self.save_users()
    
    def _apply_subscription_bonus(self, win):
        if self.current_user.subscription["type"] == "eup":
            return win * 1.10
        elif self.current_user.subscription["type"] == "eup_plus":
            return win * 1.25
        return win
    
    def _apply_subscription_refund(self, bet):
        if not self.current_user.has_active_subscription():
            return 0
        
        if self.current_user.subscription["type"] == "eup":
            refund = bet * 0.10
            self._update_balance(refund)
            return refund
        
        if self.current_user.subscription["type"] == "eup_plus":
            refund = bet * 0.20
            self._update_balance(refund)
            return refund
        
        return 0

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
            self.current_user.check_subscription()
            self.current_user.give_daily_bonus()
            print(f"{Fore.GREEN}Выбран пользователь: {self.current_user.get_styled_username()}")
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
            
        profiles = [f"{i+1}. {self.users[un].get_styled_username()}" for i, un in enumerate(self.users.keys())]
        content = [f"{Fore.CYAN}Зарегистрированные пользователи:"] + profiles
        print(dynamic_border('\n'.join(content), Fore.BLUE))

    def slots(self, bet):
        if not self._validate_bet(bet):
            return

        actual_bet = bet
        used_free_spin = False
    
        if self.current_user.free_spins > 0:
            print(f"{Fore.GREEN}Использован бесплатный спин (осталось: {self.current_user.free_spins-1})\n")
            self.current_user.free_spins -= 1
            actual_bet = bet
            used_free_spin = True
        else:
            self._update_balance(-bet)

        print(dynamic_border(f"{Fore.CYAN}EXTRACT SLOTS", Fore.CYAN))

        symbols = [
            ("🍒", 0.3),
            ("🍊", 0.25),
            ("🍋", 0.2),
            ("🔔", 0.15),
            ("⭐", 0.07),
            ("💎", 0.03)
        ]
    
        def spin_animation():
            for _ in range(10):
                temp = random.choices([s[0] for s in symbols],
                                      weights=[s[1] for s in symbols],
                                    k=3)
                print("\r" + " | ".join(temp), end='', flush=True)
                time.sleep(0.1)
    
        print("Вращение...")
        spin_animation()
    
        results = random.choices([s[0] for s in symbols], 
                                weights=[s[1] for s in symbols], 
                                k=3)
    
        print(" \r" + " | ".join(results) + "   ")
    
        win = 0
        free_spins_won = 0
    
        if results.count("💎") == 3:
            win = bet * 50
            free_spins_won = 5
            print(dynamic_border(f"{Fore.GREEN}✨ ДЖЕКПОТ! 3 АЛМАЗА! ✨ +{win}{CURRENCY} + {free_spins_won} ФРИСПИНОВ", Fore.GREEN))
    
        elif results[0] == results[1] == results[2]:
            multiplier = 10
            if results[0] == "🔔": multiplier = 15
            if results[0] == "⭐": multiplier = 20
            win = bet * multiplier
            free_spins_won = 2
            print(dynamic_border(f"{Fore.GREEN}🎉 СУПЕР! 3 {results[0]}! +{win}{CURRENCY} + {free_spins_won} ФРИСПИНА", Fore.GREEN))
    
        elif results[0] == results[1]:
            win = bet * 3
            if results[0] == "💎": 
                win = bet * 10
                free_spins_won = 1
            print(dynamic_border(f"{Fore.YELLOW}Выигрыш по линии! +{win}{CURRENCY}" + 
                                 (f" + {free_spins_won} ФРИСПИН" if free_spins_won else ""), 
                                 Fore.YELLOW))
    
        elif used_free_spin:
            if random.random() < 0.3:
                free_spins_won = 1
                print(dynamic_border(f"{Fore.BLUE}Удача в следующий раз! 🍀 +1 ФРИСПИН", Fore.BLUE))
            else:
                print(dynamic_border(f"{Fore.RED}Проигрыш", Fore.RED))
    
        else:
            refund = self._apply_subscription_refund(bet)
            if refund > 0:
                print(dynamic_border(f"{Fore.RED}Проигрыш {Fore.YELLOW}(Возврат: +{refund}{CURRENCY})", Fore.RED))
            else:
                print(dynamic_border(f"{Fore.RED}Проигрыш", Fore.RED))

        if win > 0:
            win = self._apply_subscription_bonus(win)
            win = self.apply_event_bonus("slots_multiplier", win)
            self._update_balance(win)
    
        if free_spins_won > 0:
            self.current_user.free_spins += free_spins_won
            print(f"{Fore.CYAN}Теперь у вас {self.current_user.free_spins} фриспинов!")

        self._process_result(win, actual_bet)

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
                cost = self.apply_event_bonus("trade_fee", cost)
                if not self._check_balance(cost):
                    print(f"{Fore.RED}Недостаточно средств!")
                    return
                self._update_balance(-cost)
                self.current_user.crypto_balance[coin] += amount
                self.current_user.add_transaction('buy', coin, amount, cost)
                if "trade_xp_bonus" in self.get_current_event().get("effects", {}):
                    self.current_user.add_xp("trade", self.get_current_event()["effects"]["trade_xp_bonus"])
                print(dynamic_border(f"{Fore.GREEN}Куплено {amount:.4f} {coin}", Fore.CYAN, 40))

            elif action == "sell":
                if self.current_user.crypto_balance.get(coin, 0) < amount:
                    print(f"{Fore.RED}Недостаточно {coin} для продажи!")
                    return
                value = amount * self.market.get_rate(coin) * 0.99
                value = self.apply_event_bonus("trade_bonus", value)
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

        print(dynamic_border(f"{Fore.RED}EXTRACT BATTLES", Fore.RED))
        self._update_balance(-bet)

        player_attack = random.randint(50, 150) + self.current_user.level * 2
        monster_attack = random.randint(50, 150)

        print(f"{Fore.CYAN}Ваша сила атаки: {player_attack}")
        print(f"{Fore.RED}Сила атаки монстра: {monster_attack}")

        if player_attack > monster_attack:
            win = bet * 3
            win = self._apply_subscription_bonus(win)
            win = self.apply_event_bonus("battle_xp", win)
            print(dynamic_border(f"{Fore.GREEN}ПОБЕДА! +{win}{CURRENCY}", Fore.GREEN))
        else:
            win = 0
            refund = self._apply_subscription_refund(bet)
            if refund > 0:
                print(dynamic_border(f"{Fore.RED}ПОРАЖЕНИЕ {Fore.YELLOW}(Возврат: +{refund}{CURRENCY})", Fore.RED))
            else:
                print(dynamic_border(f"{Fore.RED}ПОРАЖЕНИЕ", Fore.RED))

        self._process_result(win, bet)

    def dice(self, bet):
        if not self._validate_bet(bet):
            return

        print(dynamic_border(f"{Fore.YELLOW}EXTRACT DICE", Fore.YELLOW))
        self._update_balance(-bet)

        player_dice = sum(random.randint(1, 6) for _ in range(3))
        dealer_dice = sum(random.randint(1, 6) for _ in range(3))

        print(f"{Fore.CYAN}Ваши кости: {player_dice}")
        print(f"{Fore.RED}Кости дилера: {dealer_dice}")

        if player_dice > dealer_dice:
            win = bet * 2
            win = self._apply_subscription_bonus(win)
            print(dynamic_border(f"{Fore.GREEN}ВЫИГРЫШ! +{win}{CURRENCY}", Fore.GREEN))
        else:
            win = 0
            refund = self._apply_subscription_refund(bet)
            if refund > 0:
                print(dynamic_border(f"{Fore.RED}ПРОИГРЫШ {Fore.YELLOW}(Возврат: +{refund}{CURRENCY})", Fore.RED))
            else:
                print(dynamic_border(f"{Fore.RED}ПРОИГРЫШ", Fore.RED))

        self._process_result(win, bet)

    def high_low(self, bet):
        if not self._validate_bet(bet):
            return

        print(dynamic_border(f"{Fore.MAGENTA}EXTRACT HIGH-LOW", Fore.MAGENTA))
        self._update_balance(-bet)

        current = random.randint(1, 200)
        print(f"Текущее число: {Fore.CYAN}{current}")

        choice = input(f"{Fore.YELLOW}Следующее будет выше (h) или ниже (l)? ").lower()
        next_num = random.randint(1, 200)
        print(f"Новое число: {Fore.CYAN}{next_num}")

        won = (choice == 'h' and next_num > current) or (choice == 'l' and next_num < current)
        
        if won:
            base_win = bet * 2
            win = self._apply_subscription_bonus(base_win)
            win = self.apply_event_bonus("win_multiplier", win)
            print(dynamic_border(f"{Fore.GREEN}ПОБЕДА! +{win}{CURRENCY}", Fore.GREEN))
            self._process_result(win, bet)
        else:
            win = 0
            refund = self._apply_subscription_refund(bet)
            if refund > 0:
                print(dynamic_border(f"{Fore.RED}ПРОИГРЫШ {Fore.YELLOW}(Возврат: +{refund}{CURRENCY})", Fore.RED))
            else:
                print(dynamic_border(f"{Fore.RED}ПРОИГРЫШ", Fore.RED))
            self._process_result(0, bet)

    def show_rates(self):
        try:
            with open(CS_LOG_PATH, "r") as f:
                old_rates = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            old_rates = self.market.rates.copy()

        content = [f"{Fore.CYAN}Текущие курсы:"]
        for coin, rate in self.market.rates.items():
            if coin == "EXTRACT":
                continue
            
            old_rate = old_rates.get(coin, rate)
            change = ((rate - old_rate) / old_rate) * 100 if old_rate != 0 else 0
        
            color = Fore.GREEN if change >= 0 else Fore.RED
            change_text = f"{color}({change:+.2f}%){Style.RESET_ALL}"
        
            content.append(
                f"{CRYPTO_SYMBOLS[coin]} 1 {coin} = {rate:.2f}{CURRENCY} {change_text}"
            )
    
        print(dynamic_border('\n'.join(content), Fore.BLUE))

    def rename_account(self, current_name, new_name):
        if current_name not in self.users:
            print(f"{Fore.RED}Ошибка: пользователь '{current_name}' не найден!")
            return False

        if new_name in self.users:
            print(f"{Fore.RED}Ошибка: имя '{new_name}' уже занято!")
            return False

        if not (new_name.isalnum() and 3 <= len(new_name) <= 16):
            print(f"{Fore.RED}Ошибка: новое имя должно быть 3-16 символов (только буквы/цифры)!")
            return False

        confirm = input(
            f"{Fore.RED}Переименовать '{current_name}' → '{new_name}'? (y/n): "
        ).strip().lower()

        if confirm != "y":
            print(f"{Fore.YELLOW}Отменено.")
            return False

        user_data = self.users.pop(current_name)
        user_data.username = new_name
        self.users[new_name] = user_data

        if self.current_user and self.current_user.username == current_name:
            self.current_user = user_data

        self.save_users()
        print(f"{Fore.GREEN}Успех: '{current_name}' переименован в '{new_name}'!")
        return True

    def transfer(self, sender, receiver, currency, amount):
        if not isinstance(sender, str) or not isinstance(receiver, str) or not isinstance(currency, str):
            print(f"{Fore.RED}Ошибка: неверный формат параметров")
            return False

        currency = currency.upper()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if sender not in self.users:
            print(f"{Fore.RED}Ошибка: отправитель '{sender}' не найден!")
            return False
            
        if receiver not in self.users:
            print(f"{Fore.RED}Ошибка: получатель '{receiver}' не найден!")
            return False
            
        if currency not in CRYPTO_SYMBOLS:
            print(f"{Fore.RED}Ошибка: валюта '{currency}' не поддерживается!")
            return False

        try:
            amount = round(float(amount), 8)
            if amount <= 0:
                print(f"{Fore.RED}Ошибка: сумма должна быть больше 0!")
                return False
        except (ValueError, TypeError):
            print(f"{Fore.RED}Ошибка: неверный формат суммы!")
            return False

        sender_balance = round(self.users[sender].crypto_balance.get(currency, 0), 8)
        if sender_balance < amount:
            print(f"{Fore.RED}Ошибка: недостаточно средств! Доступно: {sender_balance:.8f}{CRYPTO_SYMBOLS[currency]}")
            return False

        commission_rate = 0.00 if self.users[sender].has_active_subscription() else 0.05
        commission = round(amount * commission_rate, 8)
        received_amount = round(amount - commission, 8)

        confirm_text = f"""
{Fore.CYAN}{"═"*50}
{Fore.YELLOW}ПОДТВЕРЖДЕНИЕ ПЕРЕВОДА
{Fore.CYAN}{"."*50}
{Fore.WHITE}▪ От: {Fore.GREEN}{sender:<44}
{Fore.WHITE}▪ Кому: {Fore.GREEN}{receiver:<42}
{Fore.WHITE}▪ Валюта: {Fore.GREEN}{currency} {CRYPTO_SYMBOLS[currency]:<36}
{Fore.CYAN}{"═"*50}
{Fore.WHITE}▪ Сумма: {Fore.GREEN}{amount:.8f}
{Fore.WHITE}▪ Комиссия: {Fore.RED}{commission:.8f} ({commission_rate*100}%){" [Без комиссии]" if commission_rate == 0 else ""}
{Fore.WHITE}▪ Получит: {Fore.YELLOW}{received_amount:.8f}
{Fore.CYAN}{"^"*50}
{Style.BRIGHT}Подтвердить перевод? (yes/no): {Style.RESET_ALL}"""
        
        print(confirm_text)
        confirm = input(">>> ").strip().lower()
        
        if confirm != 'yes':
            print(f"{Fore.YELLOW}❌ Перевод отменён")
            return False

        self.users[sender].crypto_balance[currency] = round(self.users[sender].crypto_balance.get(currency, 0) - amount, 8)
        self.users[receiver].crypto_balance[currency] = round(self.users[receiver].crypto_balance.get(currency, 0) + received_amount, 8)

        if not hasattr(self.users[sender], 'transactions'):
            self.users[sender].transactions = []
        if not hasattr(self.users[receiver], 'transactions'):
            self.users[receiver].transactions = []
            
        self.users[sender].transactions.insert(0, {
            "timestamp": timestamp,
            "action": "transfer_out",
            "coin": currency,
            "amount": -amount,
            "total": amount,
            "to": receiver,
            "commission": commission
        })
        
        self.users[receiver].transactions.insert(0, {
            "timestamp": timestamp,
            "action": "transfer_in",
            "coin": currency,
            "amount": received_amount,
            "total": received_amount,
            "from": sender
        })
        
        self.users[sender].transactions = self.users[sender].transactions[:20]
        self.users[receiver].transactions = self.users[receiver].transactions[:20]
        
        self._save_receipt({
            "timestamp": timestamp,
            "sender": sender,
            "receiver": receiver,
            "currency": currency,
            "amount": amount,
            "commission": commission,
            "received": received_amount
        })
        
        self.save_users()
        print(f"{Fore.GREEN}✅ Успешно: {received_amount:.8f}{CRYPTO_SYMBOLS[currency]} → {receiver}")
        return True

    def show_receipts(self):
        try:
            if not os.path.exists(RECEIPTS_PATH):
                print(dynamic_border(f"{Fore.YELLOW}История переводов пуста", Fore.YELLOW))
                return

            with open(RECEIPTS_PATH, 'r', encoding='utf-8') as f:
                receipts = json.load(f)

            if not receipts:
                print(dynamic_border(f"{Fore.YELLOW}История переводов пуста", Fore.YELLOW))
                return

            content = [f"{Fore.CYAN}Последние переводы:"]
            for i, receipt in enumerate(receipts[:5], 1):
                content.append(
                    f"{Fore.WHITE}{i}. {receipt['timestamp'][:16]} "
                    f"{Fore.YELLOW}{receipt['sender']} → {receipt['receiver']} "
                    f"{Fore.GREEN}{receipt['amount']:.8f}{CRYPTO_SYMBOLS.get(receipt['currency'], '?')} "
                    f"{Fore.RED}(комиссия: {receipt['commission']:.8f})"
                )

            print(dynamic_border('\n'.join(content), Fore.BLUE))

        except Exception as e:
            print(dynamic_border(f"{Fore.RED}Ошибка загрузки истории переводов: {str(e)}", Fore.RED))

    def _save_receipt(self, receipt_data):
        try:
            os.makedirs(os.path.dirname(RECEIPTS_PATH), exist_ok=True)
            receipts = []
        
            if os.path.exists(RECEIPTS_PATH):
                try:
                    with open(RECEIPTS_PATH, 'r', encoding='utf-8') as f:
                        receipts = json.load(f)
                        if not isinstance(receipts, list):
                            receipts = []
                except (json.JSONDecodeError, IOError):
                    receipts = []
        
            receipts.insert(0, receipt_data)
            receipts = receipts[:10]
        
            with open(RECEIPTS_PATH, 'w', encoding='utf-8') as f:
                json.dump(receipts, f, indent=4, ensure_ascii=False, sort_keys=True)
            
        except Exception as e:
            print(f"{Fore.YELLOW}⚠ Ошибка сохранения чека: {str(e)}")

    def check_user(self, username):
        if username not in self.users:
            print(f"{Fore.RED}Пользователь '{username}' не найден!")
            return
    
        user = self.users[username]
        content = [
            f"{Fore.CYAN}Информация о пользователе: {user.get_styled_username()}",
            f"{Fore.GREEN}Баланс: {user.crypto_balance.get('EXTRACT', 0):.2f} {CURRENCY}",
            f"{Fore.BLUE}Уровень: {user.level}",
            f"{Fore.YELLOW}Опыт: {user.xp}/{user.required_xp()} ({user.show_level_progress()})"
        ]
    
        top_coins = sorted(
            [(k, v) for k, v in user.crypto_balance.items() if v > 0 and k != "EXTRACT"],
            key=lambda x: x[1],
            reverse=True
        )[:3]
    
        if top_coins:
            content.append(f"{Fore.MAGENTA}Топ активы:")
            for coin, amount in top_coins:
                content.append(f"  {CRYPTO_SYMBOLS[coin]} {coin}: {amount:.4f}")
    
        print(dynamic_border('\n'.join(content), Fore.CYAN))

    def global_stats(self):
        total_balance = sum(u.crypto_balance.get("EXTRACT", 0) for u in self.users.values())
        print(dynamic_border(
            f"👥 Пользователей: {len(self.users)}\n"
            f"💰 Общий баланс: {total_balance:,} {CURRENCY}\n"
            f"🎮 Всего игр: {sum(u.games_played for u in self.users.values())}",
            Fore.CYAN
        ))

    def show_eup_info(self):
        info = f"""
    {Fore.CYAN}╔{'═'*35}╗
    ║{'ИНФОРМАЦИЯ О ПОДПИСКАХ'.center(35)}║
    ╠{'═'*35}╣
    ║ {Fore.BLUE}EUP (Extract User Privilege){Fore.CYAN}      ║
    ║ ▪ Цена: 10 BTC/день               ║
    ║ ▪ Бонусы:                         ║
    ║   +10% к выигрышам                ║
    ║   +10% страховка при проигрыше    ║
    ║   Ежедневный бонус 1,000,000Ⓔ     ║
    ╠{'─'*35}╣
    ║ {Fore.YELLOW}EUP+ (Extract User Privilege+){Fore.CYAN}    ║
    ║ ▪ Цена: 15 BTC/день               ║
    ║ ▪ Бонусы:                         ║
    ║   +25% к выигрышам                ║
    ║   +20% страховка при проигрыше    ║
    ║   Ежедневный бонус 2,000,000Ⓔ     ║
    ║   Шанс получить 10 BTC            ║
    ╚{'═'*35}╝
    {Style.RESET_ALL}
    {Fore.CYAN}Для покупки используйте:
    {Fore.BLUE}eup buy [дни]      - купить EUP
    {Fore.CYAN}или
    {Fore.YELLOW}eup_plus buy [дни] - купить EUP+
    """
        print(info)

    def newnote_up(self):
        path_text = f"""
{Fore.CYAN}{VERSION_ALL}\n
{Fore.WHITE}1. Анимации в слотах.
{Fore.WHITE}2. Фриспины (Слоты).
{Fore.WHITE}3. Исправление багов в сезонах.
{Fore.WHITE}4. Обновили отображение курса валют.
{Fore.WHITE}5. Добавили форум.
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
{Fore.GREEN}rename [старый ник] [новый ник]{Fore.WHITE}- Переименовывает пользователя
{Fore.GREEN}transfer [отправитель] [получатель] [валюта] [сумма] - Совершает перевод
{Fore.GREEN}receipts                    {Fore.WHITE}- показывает последние переводы
{Fore.GREEN}delete [ник]                {Fore.WHITE}- Удалить пользователя
{Fore.GREEN}check [ник]                 {Fore.WHITE}- Информация о выбранном пользователе
{Fore.GREEN}show                        {Fore.WHITE}- Статистика профиля
{Fore.GREEN}level                       {Fore.WHITE}- Детальная информация об уровне
{Fore.GREEN}exit -a                     {Fore.WHITE}- Выйти из аккаунта\n
{Fore.WHITE}      ---Покупка и статус EUP---\n
{Fore.YELLOW}eup buy [дни]              {Fore.WHITE}- Купить подписку EUP
{Fore.YELLOW}eup_plus buy [дни]         {Fore.WHITE}- Купить подписку EUP+
{Fore.YELLOW}eup status                 {Fore.WHITE}- Статус подписки
{Fore.YELLOW}eup info                   {Fore.WHITE}- Актуальная информация об подписках
{Fore.YELLOW}eup autonone               {Fore.WHITE}- Отключить автопродление\n
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
{Fore.WHITE}monthly                     {Fore.WHITE}- Текущее месячное событие
{Fore.WHITE}promo [код]                {Fore.WHITE}- Активировать промокод\n
{Fore.WHITE}          ---Об Extract---\n
{Fore.CYAN}extract                      {Fore.WHITE}- Информация о версии
{Fore.CYAN}wnew                         {Fore.WHITE}- Патчноут
{Fore.CYAN}forum                        {Fore.WHITE}- Открывает форум\n
{Fore.WHITE}            ---Прочее---\n
{Fore.MAGENTA}global                    {Fore.WHITE}- Общая статистика всех аккаунтов
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

    try:
        while True:
            casino.check_autosave()
            current_time = datetime.now().strftime("%H:%M:%S")
            
            if casino.current_user:
                username = casino.current_user.get_styled_username()
                balance = casino.current_user.crypto_balance.get("EXTRACT", 0)
                prompt = (
                    f"{Fore.BLUE}╭─{Fore.BLUE}[{current_time}] - {username}{Fore.BLUE} - {Fore.GREEN}{balance:.2f} {CURRENCY}\n"
                    f"{Fore.BLUE}╰─{gradient_text('➤', [Fore.GREEN, Fore.YELLOW])} {Style.RESET_ALL}"
                )
            else:
                prompt = f"{Fore.BLUE}╭─[{current_time}] - {VERSION_ALL} - Нужна помощь? - help\n╰─➤ {Style.RESET_ALL}"

            try:
                action = input(prompt).strip()
                casino.last_command = action.split()[0] if action else ""

                if action.startswith("add "):
                    username = action.split(" ", 1)[1]
                    casino.create_user(username)

                elif action.startswith("login "):
                    username = action.split(" ", 1)[1]
                    casino.select_user(username)

                elif action.startswith("check "):
                    try:
                        username = action.split(" ", 1)[1]
                        casino.check_user(username)
                    except:
                        print(f"{Fore.RED}Используйте: check [ник]")

                elif action.startswith("transfer "):
                    try:
                        parts = action.split()
                        if len(parts) != 5:
                            raise ValueError
                        
                        sender = parts[1]
                        receiver = parts[2]
                        currency = parts[3].upper()
                        amount = parts[4]
                    
                        if not casino.transfer(sender, receiver, currency, amount):
                            print(f"{Fore.YELLOW}Перевод не выполнен")
                        
                    except ValueError:
                        print(f"{Fore.RED}Ошибка: используйте 'transfer <отправитель> <получатель> <валюта> <сумма>'")

                elif action == "receipts":
                    casino.show_receipts()

                elif action.startswith("rename "):
                    parts = action.split()
                    if len(parts) != 3:
                        print(f"{Fore.RED}Ошибка: используйте `rename <старое_имя> <новое_имя>`")
                        continue
        
                    current_name = parts[1]
                    new_name = parts[2]

                    if current_name == new_name:
                        print(f"{Fore.YELLOW}Ошибка: новое имя не должно совпадать со старым!")
                        continue
        
                    if not (current_name.isprintable() and new_name.isprintable()):
                        print(f"{Fore.RED}Ошибка: имена содержат недопустимые символы!")
                        continue
        
                    casino.rename_account(current_name, new_name)

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
                        print(f"{Fore.RED}Используйте: dice [сумма]")

                elif action.startswith("highlow"):
                    try:
                        bet = float(action.split()[1])
                        casino.high_low(bet)
                    except:
                        print(f"{Fore.RED}Используйте: highlow [сумма]")

                elif action.startswith("trade"):
                    casino.trade(action[5:])

                elif action == "global":
                    casino.global_stats()

                elif action == "eup info":
                    casino.show_eup_info()

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

                elif action == "monthly":
                    casino.show_monthly_event()

                elif action == "wal":
                    if casino.current_user:
                        casino.current_user.crywall()
                    else:
                        print(f"{Fore.RED}Пользователь не выбран!")

                elif action == "extract":
                    casino.display_version()

                elif action == "forum":
                    casino.forum.show_forum()

                elif action == "wnew":
                    casino.newnote_up()

                elif action == "help":
                    casino.display_help()

                elif action.startswith("promo "):
                    code = action.split(" ", 1)[1].strip()
                    casino.activate_promo(code)

                elif action == "all":
                    casino.show_all_profiles()

                elif action.startswith("eup buy"):
                    try:
                        days = int(action.split()[2])
                        if casino.current_user:
                            casino.current_user.buy_eup(days)
                        else:
                            print(f"{Fore.RED}Сначала войдите в аккаунт!")
                    except:
                        print(f"{Fore.RED}Используйте: eup buy [дни]")

                elif action.startswith("eup_plus buy"):
                    try:
                        days = int(action.split()[2])
                        if casino.current_user:
                            casino.current_user.buy_eup_plus(days)
                        else:
                            print(f"{Fore.RED}Сначала войдите в аккаунт!")
                    except:
                        print(f"{Fore.RED}Используйте: eup_plus buy [дни]")

                elif action == "eup status":
                    if casino.current_user:
                        casino.current_user.eup_status()
                    else:
                        print(f"{Fore.RED}Пользователь не выбран!")

                elif action == "eup autonone":
                    if casino.current_user:
                        casino.current_user.eup_autonone()
                    else:
                        print(f"{Fore.RED}Пользователь не выбран!")

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
