import random
import json
import time
import os
import textwrap
import hashlib
import secrets
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
from decimal import Decimal, ROUND_DOWN
from datetime import datetime, timedelta
from colorama import Fore, Style, init

init(autoreset=True)

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/extract.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

ADDINFO = "EXTRACT™ PLATFORM 2026"
INFO = "Extract Team (Rexamm1t, Wefol1x)"
VERSION = "EXTRACT 12.0.0"
VERSION_ALL = "EXTRACT 12.0.0 (5.0.0)"
SAVE_PATH = "data/users.json"
KEYS_PATH = "data/keys.json"
RECEIPTS_PATH = "logs/receipts.json"
CS_LOG_PATH = "logs/cs_l.json"
FORUM_PATH = "forum/meta.json"
ACHIEVEMENTS_PATH = "data/achievements.json"
RATES_HISTORY_PATH = "data/rates_history.json"
PREV_RATES_PATH = "data/previous_rates.json"

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
INITIAL_BALANCE = Decimal('10000.0')
LEVEL_BASE_XP = 1000
AUTOSAVE_INTERVAL = 300

class SubscriptionType(Enum):
    NONE = "none"
    EUP = "eup"
    EUP_PLUS = "eup_plus"

@dataclass
class Transaction:
    timestamp: str
    action: str
    coin: str
    amount: Decimal
    total: Decimal
    from_user: Optional[str] = None
    to_user: Optional[str] = None
    commission: Decimal = Decimal('0.0')
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "action": self.action,
            "coin": self.coin,
            "amount": float(self.amount),
            "total": float(self.total),
            "from_user": self.from_user,
            "to_user": self.to_user,
            "commission": float(self.commission)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        return cls(
            timestamp=data["timestamp"],
            action=data["action"],
            coin=data["coin"],
            amount=Decimal(str(data["amount"])),
            total=Decimal(str(data["total"])),
            from_user=data.get("from_user"),
            to_user=data.get("to_user"),
            commission=Decimal(str(data.get("commission", 0.0)))
        )

@dataclass
class Subscription:
    type: SubscriptionType = SubscriptionType.NONE
    expires_at: Optional[str] = None
    autorenew: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "expires_at": self.expires_at,
            "autorenew": self.autorenew
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Subscription':
        return cls(
            type=SubscriptionType(data.get("type", "none")),
            expires_at=data.get("expires_at"),
            autorenew=data.get("autorenew", False)
        )

@dataclass
class UserData:
    username: str
    crypto_balance: Dict[str, Decimal] = field(default_factory=dict)
    games_played: int = 0
    wins: int = 0
    losses: int = 0
    transactions: List[Transaction] = field(default_factory=list)
    play_time: float = 0.0
    level: int = 1
    xp: int = 0
    total_earned: Decimal = Decimal('0.0')
    subscription: Subscription = field(default_factory=Subscription)
    last_login: Optional[str] = None
    free_spins: int = 0
    consecutive_wins: int = 0
    achievements: List[str] = field(default_factory=list)

class HistoryTracker:
    def __init__(self):
        self.history = []
        self.load_history()
    
    def load_history(self):
        try:
            os.makedirs(os.path.dirname(RATES_HISTORY_PATH), exist_ok=True)
            if os.path.exists(RATES_HISTORY_PATH):
                with open(RATES_HISTORY_PATH, 'r') as f:
                    self.history = json.load(f)
            else:
                self.history = []
                self.save_history()
        except Exception as e:
            logger.error(f"Error loading rates history: {e}")
            self.history = []
    
    def save_history(self):
        try:
            with open(RATES_HISTORY_PATH, 'w') as f:
                json.dump(self.history[-1000:], f, indent=2)
        except Exception as e:
            logger.error(f"Error saving rates history: {e}")
    
    def add_record(self, rates: Dict[str, float]):
        record = {
            "timestamp": datetime.now().isoformat(),
            "rates": rates.copy()
        }
        self.history.append(record)
        self.save_history()
    
    def get_coin_history(self, coin: str, limit: int = 30) -> List[float]:
        history = []
        for record in self.history[-limit:]:
            if coin in record["rates"]:
                history.append(record["rates"][coin])
        return history

class CryptoMarket:
    def __init__(self):
        self.rates = self._generate_initial_rates()
        self.previous_rates = self._load_previous_rates()
        self.history_tracker = HistoryTracker()
        self._load_saved_rates()
    
    def _generate_initial_rates(self) -> Dict[str, Decimal]:
        return {
            "BETASTD": Decimal(str(random.uniform(7750100, 10000000))),
            "DOGCOIN": Decimal(str(random.uniform(1000000, 2000000))),
            "EXRSD": Decimal(str(random.uniform(328110, 400000))),
            "BTC": Decimal(str(random.uniform(25000, 110000))),
            "ETH": Decimal(str(random.uniform(1500, 6000))),
            "LTC": Decimal(str(random.uniform(60, 455))),
            "BNB": Decimal(str(random.uniform(200, 600))),
            "ADA": Decimal(str(random.uniform(200, 500))),
            "SOL": Decimal(str(random.uniform(20, 200))),
            "XRP": Decimal(str(random.uniform(50, 100))),
            "DOT": Decimal(str(random.uniform(4, 300))),
            "DOGE": Decimal(str(random.uniform(300, 500))),
            "SHIB": Decimal(str(random.uniform(1000, 20000))),
            "AVAX": Decimal(str(random.uniform(10, 100))),
            "TRX": Decimal(str(random.uniform(100, 200))),
            "MATIC": Decimal(str(random.uniform(14000, 16000))),
            "ATOM": Decimal(str(random.uniform(600, 1000))),
            "NOT": Decimal(str(random.uniform(0.05, 0.5))),
            "TON": Decimal(str(random.uniform(1.0, 6.5))),
            "XYZ": Decimal(str(random.uniform(0.01, 0.1))),
            "ABC": Decimal(str(random.uniform(10, 50))),
            "DEF": Decimal(str(random.uniform(100, 500))),
            "GHI": Decimal(str(random.uniform(5, 20))),
            "JKL": Decimal(str(random.uniform(0.001, 0.01))),
            "MNO": Decimal(str(random.uniform(0.5, 2))),
            "PQR": Decimal(str(random.uniform(1000, 5000))),
            "EXTRACT": Decimal('1.0')
        }
    
    def _load_previous_rates(self) -> Dict[str, Decimal]:
        try:
            os.makedirs(os.path.dirname(PREV_RATES_PATH), exist_ok=True)
            if os.path.exists(PREV_RATES_PATH):
                with open(PREV_RATES_PATH, 'r') as f:
                    prev_rates = json.load(f)
                    return {coin: Decimal(str(rate)) for coin, rate in prev_rates.items()}
            else:
                return self.rates.copy()
        except Exception as e:
            logger.error(f"Error loading previous rates: {e}")
            return self.rates.copy()
    
    def _save_previous_rates(self):
        try:
            rates_float = {coin: float(rate) for coin, rate in self.previous_rates.items()}
            with open(PREV_RATES_PATH, 'w') as f:
                json.dump(rates_float, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving previous rates: {e}")
    
    def _load_saved_rates(self):
        try:
            if os.path.exists(CS_LOG_PATH):
                with open(CS_LOG_PATH, "r") as f:
                    saved_rates = json.load(f)
                    for coin, rate in saved_rates.items():
                        if coin in self.rates:
                            self.rates[coin] = Decimal(str(rate))
        except Exception as e:
            logger.error(f"Failed to load saved rates: {e}")
    
    def update_rates(self):
        self.previous_rates = self.rates.copy()
        
        for coin in self.rates:
            if coin != "EXTRACT":
                change = Decimal(str(random.uniform(-0.07, 0.07)))
                new_rate = self.rates[coin] * (Decimal('1') + change)
                self.rates[coin] = max(Decimal('0.01'), new_rate)
        
        self.save_rates()
        self._save_previous_rates()
        rates_float = {coin: float(rate) for coin, rate in self.rates.items()}
        self.history_tracker.add_record(rates_float)
    
    def get_rate(self, coin: str) -> Decimal:
        return self.rates.get(coin, Decimal('0.0'))
    
    def get_rate_change(self, coin: str) -> float:
        if coin not in self.previous_rates or coin not in self.rates:
            return 0.0
        prev = float(self.previous_rates[coin])
        curr = float(self.rates[coin])
        if prev == 0:
            return 0.0
        return ((curr - prev) / prev) * 100
    
    def save_rates(self):
        try:
            os.makedirs(os.path.dirname(CS_LOG_PATH), exist_ok=True)
            rates_float = {coin: float(rate) for coin, rate in self.rates.items()}
            with open(CS_LOG_PATH, "w") as f:
                json.dump(rates_float, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save rates: {e}")
    
    def print_chart(self, coin: str, height: int = 12, width: int = 50):
        history = self.history_tracker.get_coin_history(coin, limit=100)
        if len(history) < 2:
            print(f"{Fore.YELLOW}Недостаточно данных для построения графика {coin}")
            print(f"{Fore.CYAN}Выполните несколько транзакций для накопления истории")
            return
        
        current = history[-1]
        avg = sum(history) / len(history)
        min_val = min(history)
        max_val = max(history)
        
        if max_val - min_val <= 0:
            normalized = [height // 2] * min(len(history), width)
        else:
            normalized = [int((h - min_val) / (max_val - min_val) * (height - 1)) for h in history[-width:]]
        
        chart = []
        for y in range(height - 1, -1, -1):
            row = []
            for val in normalized:
                if val >= y:
                    row.append("█")
                else:
                    row.append(" ")
            chart.append("".join(row))
        
        price_scale = []
        if height > 1:
            step = (max_val - min_val) / (height - 1)
            for i in range(height):
                price_scale.append(min_val + i * step)
        else:
            price_scale = [current]
        
        print(f"\n{Fore.CYAN}{'═' * 60}")
        print(f"{Fore.YELLOW}{coin} График курса - последние {len(normalized)} обновлений")
        print(f"{Fore.GREEN}Текущий: {current:.4f} {CURRENCY}")
        print(f"{Fore.BLUE}Средний: {avg:.4f} | Мин: {min_val:.4f} | Макс: {max_val:.4f}")
        change = self.get_rate_change(coin)
        change_color = Fore.GREEN if change >= 0 else Fore.RED
        print(f"{change_color}Изменение: {change:+.2f}%")
        print(f"{Fore.CYAN}{'─' * 60}")
        
        for i, (price, line) in enumerate(zip(price_scale, chart)):
            color = Fore.GREEN if price <= current else Fore.RED
            print(f"{Fore.WHITE}{price:8.2f} {color}{line}")
        
        print(f"{Fore.CYAN}{'═' * 60}")

MONTHLY_EVENTS = {
    1: {"name": "❄️ Новогодний Разгон", "effects": {"slots_multiplier": 1.8, "free_daily_spins": 3, "level_up_bonus": 2000}},
    2: {"name": "💘 Битва Сердец", "effects": {"double_win_chance": True, "referral_bonus": 1.5, "loss_protection": 0.25}},
    3: {"name": "🌱 Весенний Рост", "effects": {"xp_boost": 2.0, "trade_xp_bonus": 3, "daily_interest": 0.01}},
    4: {"name": "🌸 Апрельский Лотес", "effects": {"jackpot_chance": 0.15, "insurance": 0.2, "daily_bonus": 1500}},
    5: {"name": "⚡ Майский Штурм", "effects": {"battle_xp": 1.8, "daily_gift": 1500, "free_spins": 2}},
    6: {"name": "🌞 Летний Круиз", "effects": {"trade_fee": 0.7, "slots_bonus": 3000, "xp_multiplier": 1.4}},
    7: {"name": "🔥 Жаркий Удар", "effects": {"xp_multiplier": 1.4, "free_spins": 3, "daily_interest": 0.015}},
    8: {"name": "🌪️ Августовский Ветер", "effects": {"win_multiplier": 1.25, "insurance": 0.25, "trade_bonus": 1.1}},
    9: {"name": "🍂 Осенний Урожай", "effects": {"trade_bonus": 1.3, "daily_gift": 2000, "xp_boost": 1.5}},
    10: {"name": "🎃 Хеллоуин Спешиал", "effects": {"jackpot_chance": 0.2, "battle_xp": 2.0, "mystery_gift": True}},
    11: {"name": "🌧️ Ноябрьский Шторм", "effects": {"xp_multiplier": 1.6, "slots_bonus": 4000, "loss_protection": 0.3}},
    12: {"name": "🎄 Зимнее Чудо", "effects": {"win_multiplier": 1.5, "year_end_special": True, "unlimited_withdrawals": True}}
}

ACHIEVEMENTS = {
    "first_win": {"name": "Первый Выигрыш", "description": "Выиграйте свою первую игру", "xp_reward": 100},
    "level_10": {"name": "Десятый Уровень", "description": "Достигните 10 уровня", "xp_reward": 500},
    "millionaire": {"name": "Миллионер", "description": "Накопите 1,000,000 Ⓔ", "xp_reward": 1000},
    "slots_master": {"name": "Мастер Слотов", "description": "Выиграйте в слотах 100 раз", "xp_reward": 300},
    "trader": {"name": "Трейдер", "description": "Совершите 50 сделок", "xp_reward": 200}
}

def dynamic_border(text: str, border_color=Fore.MAGENTA, width=None) -> str:
    lines = text.split('\n')
    max_width = width if width else max((len(line) for line in lines), default=0) + 4
    border = '═' * (max_width - 2)
    bordered = [f"{border_color}╔{border}╗"]
    for line in lines:
        bordered.append(f"{border_color}║ {line.ljust(max_width - 4)} ║")
    bordered.append(f"{border_color}╚{border}╝")
    return '\n'.join(bordered)

def rainbow_text(text: str) -> str:
    colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
    return ''.join([colors[i % len(colors)] + char for i, char in enumerate(text)])

def gradient_text(text: str, colors: List[str]) -> str:
    return ''.join([colors[i % len(colors)] + char for i, char in enumerate(text)])

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

class User:
    def __init__(self, username: str):
        self.data = UserData(username=username)
        self.data.crypto_balance = {coin: Decimal('0.0') for coin in CRYPTO_SYMBOLS}
        self.data.crypto_balance["EXTRACT"] = INITIAL_BALANCE
        self.session_start: Optional[float] = None
    
    @property
    def username(self) -> str:
        return self.data.username
    
    @username.setter
    def username(self, value: str):
        self.data.username = value
    
    def to_dict(self) -> Dict[str, Any]:
        data_dict = asdict(self.data)
        data_dict["crypto_balance"] = {k: float(v) for k, v in self.data.crypto_balance.items()}
        data_dict["transactions"] = [t.to_dict() for t in self.data.transactions]
        data_dict["subscription"] = self.data.subscription.to_dict()
        data_dict["total_earned"] = float(self.data.total_earned)
        return data_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        user = cls(data["username"])
        user.data.crypto_balance = {coin: Decimal(str(amount)) for coin, amount in data.get("crypto_balance", {}).items()}
        user.data.games_played = data.get("games_played", 0)
        user.data.wins = data.get("wins", 0)
        user.data.losses = data.get("losses", 0)
        user.data.transactions = [Transaction.from_dict(t) for t in data.get("transactions", [])]
        user.data.play_time = data.get("play_time", 0.0)
        user.data.level = data.get("level", 1)
        user.data.xp = data.get("xp", 0)
        user.data.total_earned = Decimal(str(data.get("total_earned", 0.0)))
        user.data.subscription = Subscription.from_dict(data.get("subscription", {}))
        user.data.last_login = data.get("last_login")
        user.data.free_spins = data.get("free_spins", 0)
        user.data.consecutive_wins = data.get("consecutive_wins", 0)
        user.data.achievements = data.get("achievements", [])
        return user
    
    def start_session(self):
        self.session_start = time.time()
    
    def end_session(self):
        if self.session_start:
            self.data.play_time += time.time() - self.session_start
            self.session_start = None
    
    def update_stats(self, won: bool):
        self.data.games_played += 1
        if won:
            self.data.wins += 1
            self.data.consecutive_wins += 1
        else:
            self.data.losses += 1
            self.data.consecutive_wins = 0
    
    def add_transaction(self, action: str, coin: str, amount: Decimal, price: Decimal):
        transaction = Transaction(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            action=action,
            coin=coin,
            amount=amount,
            total=price
        )
        self.data.transactions.insert(0, transaction)
        self.data.transactions = self.data.transactions[:10]
    
    def win_loss_ratio(self) -> float:
        if self.data.games_played == 0:
            return 0.0
        return round(self.data.wins / self.data.games_played * 100, 1)
    
    def add_xp(self, amount: int):
        xp_gain = Decimal(str(amount))
        if self.data.subscription.type == SubscriptionType.EUP:
            xp_gain *= Decimal('1.2')
        elif self.data.subscription.type == SubscriptionType.EUP_PLUS:
            xp_gain *= Decimal('1.5')
        self.data.xp += int(xp_gain)
        while self.data.xp >= self.required_xp():
            self.data.xp -= self.required_xp()
            self.level_up()
    
    def required_xp(self) -> int:
        base = LEVEL_BASE_XP * 5
        return int(base * (self.data.level ** 2.2 + self.data.level * 8))
    
    def level_up(self):
        self.data.level += 1
        reward = self.data.level * 1000
        self.data.crypto_balance["EXTRACT"] += Decimal(str(reward))
        print(dynamic_border(
            f"{Fore.GREEN}🎉 Уровень Повышен! {self.data.level-1} => {self.data.level}\n"
            f"+{reward}{CURRENCY} - Ваш бонус за уровень!\n"
            f"Следующий уровень: {self.required_xp():.0f} XP",
            Fore.YELLOW
        ))
    
    def show_level_progress(self) -> str:
        req = self.required_xp()
        progress = min(1.0, self.data.xp / req) if req > 0 else 0
        gradient = [Fore.RED, Fore.YELLOW, Fore.GREEN]
        color = gradient[min(2, int(progress * 3))]
        bar_len = int(progress * 20)
        bar = "▓" * bar_len + "░" * (20 - bar_len)
        return f"{Fore.CYAN}{bar} {progress*100:.1f}%"
    
    def crywall(self):
        content = [f"{Fore.CYAN}╔{'═'*25}╦{'═'*15}╗"]
        for coin, amount in self.data.crypto_balance.items():
            if amount <= Decimal('0'):
                continue
            symbol = CRYPTO_SYMBOLS[coin]
            line = f"║ {symbol} {coin.ljust(10)} ║ {float(amount):>10.4f} ║"
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
            try:
                expiry_date = datetime.strptime(self.data.subscription.expires_at, "%Y-%m-%d")
                days_left = (expiry_date - datetime.now()).days
                sub_icon = "🔷" if self.data.subscription.type == SubscriptionType.EUP else "🔶"
                sub_color = THEME['eup'] if self.data.subscription.type == SubscriptionType.EUP else THEME['eup_plus']
                sub_header = f"{sub_icon} {sub_color}{self.data.subscription.type.value.upper()}"
                sub_details = [
                    f"  {sub_color}Действует до: {expiry_date.strftime('%d.%m.%Y')}",
                    f"  {sub_color}Осталось: {days_left} дней",
                    f"  {sub_color}Бонусы: +{25 if self.data.subscription.type == SubscriptionType.EUP_PLUS else 10}% выигрыши, "
                    f"{20 if self.data.subscription.type == SubscriptionType.EUP_PLUS else 10}% страховка"
                ]
            except:
                sub_header = f"⚪ {Fore.RED}ОШИБКА ПОДПИСКИ"
                sub_details = [f"  {Fore.RED}Ошибка в данных подписки"]
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
            f"├─────────────────────────────────┤",
            f"    {sub_header.ljust(30)}{THEME['base']}"
        ]
        profile.extend(sub_details)
        profile.extend([
            f"{THEME['base']}╭─────────────────────────────────╮",
            f"│        {Fore.WHITE}   Статистика            {THEME['base']}│",
            f"├─────────────────────────────────┤",
            f"  {Fore.YELLOW}Баланс: {float(self.data.crypto_balance['EXTRACT']):,.2f} {CURRENCY}",
            f"  {THEME['stats']}WLR: {self.win_loss_ratio()}%",
            f"  {THEME['stats']}Игр: {self.data.games_played}  🏆 {self.data.wins}  💀 {self.data.losses}",
            f"{THEME['base']} ───────────────────────────────── ",
            f"  {THEME['stats']}Уровень: {self.data.level}",
            f"  {THEME['stats']}{self.show_level_progress()}"
        ])
        
        top_coins = sorted(
            [(k, v) for k, v in self.data.crypto_balance.items() if v > Decimal('0') and k != "EXTRACT"],
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        if top_coins:
            profile.extend([
                f"{THEME['base']}╭─────────────────────────────────╮",
                f"│        {Fore.WHITE}   Топ активы            {THEME['base']}│",
                f"├─────────────────────────────────┤",
            ])
            for coin, amount in top_coins:
                profile.append(f"  {THEME['stats']}{CRYPTO_SYMBOLS[coin]} {coin}: {float(amount):>12.2f}")
        
        if self.data.transactions:
            profile.extend([
                f"{THEME['base']}╭─────────────────────────────────╮",
                f"│       {Fore.WHITE}Последние транзакции      {THEME['base']}│",
                f"├─────────────────────────────────┤",
            ])
            for t in self.data.transactions[:6]:
                if t.action in ['buy', 'sell']:
                    action_icon = "+" if t.action == 'buy' else "-"
                    action_color = Fore.GREEN if t.action == 'buy' else Fore.RED
                    profile.append(
                        f"  {action_icon} {t.timestamp[5:16]} "
                        f"{action_color}{t.action.upper()} {float(t.amount):.2f} {t.coin} "
                        f"{THEME['transactions']}за {float(t.total)}{CURRENCY}"
                    )
                elif t.action == 'transfer_in':
                    profile.append(
                        f"  + {t.timestamp[5:16]} "
                        f"{Fore.GREEN}Получено (перевод) {float(t.amount):.2f} {t.coin} "
                        f"{THEME['transactions']}от {t.from_user}"
                    )
                elif t.action == 'transfer_out':
                    profile.append(
                        f"  - {t.timestamp[5:16]} "
                        f"{Fore.RED}Переведено {float(t.amount):.2f} {t.coin} "
                        f"{THEME['transactions']}комиссия: {float(t.commission):.2f}"
                    )
        
        profile.append(f"{THEME['base']} ───────────────────────────────── ")
        print('\n'.join(profile))
    
    def has_active_subscription(self) -> bool:
        if self.data.subscription.type == SubscriptionType.NONE:
            return False
        if self.data.subscription.expires_at is None:
            return False
        try:
            expiry_date = datetime.strptime(self.data.subscription.expires_at, "%Y-%m-%d")
            return datetime.now() <= expiry_date
        except:
            return False
    
    def get_styled_username(self) -> str:
        if not self.has_active_subscription():
            return self.data.username
        if self.data.subscription.type == SubscriptionType.EUP:
            return f"{Style.BRIGHT}{Fore.CYAN}{self.data.username}{Style.RESET_ALL}"
        return f"{Style.BRIGHT}{Fore.YELLOW}{self.data.username}{Style.RESET_ALL}"
    
    def give_daily_bonus(self):
        today = datetime.now().strftime("%Y-%m-%d")
        if self.data.last_login == today:
            return
        self.data.last_login = today
        if self.data.subscription.type == SubscriptionType.EUP:
            bonus = Decimal('1000000')
            self.data.crypto_balance["EXTRACT"] += bonus
            print(dynamic_border(f"{Fore.CYAN}Ежедневный бонус EUP: +1,000,000Ⓔ", Fore.CYAN))
        elif self.data.subscription.type == SubscriptionType.EUP_PLUS:
            bonus = Decimal('10000000')
            self.data.crypto_balance["EXTRACT"] += bonus
            print(dynamic_border(f"{Fore.YELLOW}Ежедневный бонус EUP+: +2,000,000Ⓔ", Fore.YELLOW))
            if secrets.randbelow(100) < 5:
                btc_bonus = Decimal('10.0')
                self.data.crypto_balance["BTC"] = self.data.crypto_balance.get("BTC", Decimal('0')) + btc_bonus
                print(dynamic_border(f"{Fore.GREEN}СУПЕРБОНУС! +10 ₿", Fore.GREEN))
    
    def check_subscription(self):
        if not self.has_active_subscription():
            self.data.subscription = Subscription()
    
    def buy_eup(self, days: int):
        if not 1 <= days <= 365:
            print(f"{Fore.RED}Ошибка: можно купить от 1 до 365 дней!")
            return
        cost = Decimal('10') * days
        print(dynamic_border(
            f"{Fore.BLUE}EUP base -------------------- Base\n"
            f"{Fore.CYAN}Подтвердите покупку EUP на {days} дней\n"
            f"Стоимость: {float(cost)} ₿\n"
            f"Ваш баланс BTC: {float(self.data.crypto_balance.get('BTC', Decimal('0'))):.8f} ₿\n"
            f"{Fore.YELLOW}Введите 'yes' для оплаты:",
            Fore.CYAN
        ))
        confirm = input(">>> ").lower()
        if confirm == "yes":
            if self.data.crypto_balance.get("BTC", Decimal('0')) >= cost:
                self.data.crypto_balance["BTC"] -= cost
                expiry_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
                self.data.subscription = Subscription(
                    type=SubscriptionType.EUP,
                    expires_at=expiry_date,
                    autorenew=True
                )
                print(dynamic_border(
                    f"{Fore.GREEN}Оплачено! EUP активна до {expiry_date}\n"
                    f"{Fore.BLUE}Благодарим за покупку!\n"
                    f"Новый баланс BTC: {float(self.data.crypto_balance['BTC']):.8f} ₿",
                    Fore.GREEN
                ))
            else:
                print(f"{Fore.RED}Недостаточно BTC!")
        else:
            print(f"{Fore.YELLOW}Отменено.")
    
    def buy_eup_plus(self, days: int):
        if not 1 <= days <= 365:
            print(f"{Fore.RED}Ошибка: можно купить от 1 до 365 дней!")
            return
        cost = Decimal('15') * days
        print(dynamic_border(
            f"{Fore.YELLOW}EUP plus -------------------- Plus\n"
            f"{Fore.YELLOW}Покупка EUP+ на {days} дней\n"
            f"Стоимость: {float(cost)} ₿\n"
            f"Ваш баланс: {float(self.data.crypto_balance.get('BTC', Decimal('0'))):.8f} ₿\n"
            f"{Fore.CYAN}Введите 'yes' для подтверждения:",
            Fore.YELLOW
        ))
        if input(">>> ").lower() != "yes":
            print(f"{Fore.YELLOW}Отменено.")
            return
        if self.data.crypto_balance.get("BTC", Decimal('0')) < cost:
            print(f"{Fore.RED}Недостаточно BTC. Нужно: {float(cost)} ₿")
            return
        self.data.crypto_balance["BTC"] -= cost
        expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        self.data.subscription = Subscription(
            type=SubscriptionType.EUP_PLUS,
            expires_at=expiry,
            autorenew=False
        )
        bonus = Decimal('2000000')
        self.data.crypto_balance["EXTRACT"] += bonus
        print(dynamic_border(
            f"{Fore.GREEN}EUP+ активирована до {expiry}!\n"
            f"+{float(bonus)}Ⓔ бонус за покупку. Благодарим за покупку!\n"
            f"Новый баланс BTC: {float(self.data.crypto_balance['BTC']):.8f} ₿",
            Fore.GREEN
        ))
    
    def eup_status(self):
        if not self.has_active_subscription():
            print(f"{Fore.RED}У вас нет активных подписок.")
            return
        try:
            remaining = (datetime.strptime(self.data.subscription.expires_at, "%Y-%m-%d") - datetime.now()).days
            print(dynamic_border(
                f"{Fore.CYAN}Статус Подписки\n"
                f"Действует до: {self.data.subscription.expires_at}\n"
                f"Осталось дней: {remaining}\n"
                f"Автопродление: {'вкл' if self.data.subscription.autorenew else 'выкл'}",
                Fore.CYAN
            ))
        except:
            print(f"{Fore.RED}Ошибка в данных подписки")
    
    def eup_autonone(self):
        if not self.has_active_subscription():
            print(f"{Fore.RED}У вас нет активной подписки!")
            return
        self.data.subscription.autorenew = False
        print(f"{Fore.GREEN}Автопродление подписок отключено. Действующая подписка истечёт {self.data.subscription.expires_at}.")

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
            logger.error(f"Ошибка загрузки форума: {e}")
            self.messages = []
    
    def show_forum(self, limit: int = 5):
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
            for line in textwrap.wrap(msg['content'], width=48):
                content.append(f"║ {Fore.GREEN}{line.ljust(48)}║")
            content.append(f"╠{'═'*50}╣")
        
        print('\n'.join(content))

class Achievements:
    def __init__(self):
        self.achievements = ACHIEVEMENTS
        self.user_achievements = self.load_achievements()
    
    def load_achievements(self) -> Dict[str, List[str]]:
        try:
            os.makedirs(os.path.dirname(ACHIEVEMENTS_PATH), exist_ok=True)
            if os.path.exists(ACHIEVEMENTS_PATH):
                with open(ACHIEVEMENTS_PATH, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading achievements: {e}")
        return {}
    
    def save_achievements(self):
        try:
            with open(ACHIEVEMENTS_PATH, 'w') as f:
                json.dump(self.user_achievements, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving achievements: {e}")
    
    def unlock_achievement(self, username: str, achievement_key: str, user: 'User'):
        if username not in self.user_achievements:
            self.user_achievements[username] = []
        
        if achievement_key not in self.user_achievements[username]:
            self.user_achievements[username].append(achievement_key)
            user.add_xp(self.achievements[achievement_key]["xp_reward"])
            print(dynamic_border(
                f"{Fore.GREEN}🎉 Новое достижение!\n"
                f"{self.achievements[achievement_key]['name']}\n"
                f"{self.achievements[achievement_key]['description']}\n"
                f"+{self.achievements[achievement_key]['xp_reward']} XP",
                Fore.YELLOW
            ))
            self.save_achievements()
    
    def show_achievements(self, username: str):
        user_achs = self.user_achievements.get(username, [])
        content = [f"{Fore.CYAN}Ваши достижения:"]
        
        for ach_key in user_achs:
            if ach_key in self.achievements:
                ach = self.achievements[ach_key]
                content.append(f"{Fore.GREEN}✓ {ach['name']} - {ach['description']}")
        
        unlocked_count = len(user_achs)
        total_count = len(self.achievements)
        content.append(f"{Fore.YELLOW}Прогресс: {unlocked_count}/{total_count}")
        
        print(dynamic_border('\n'.join(content), Fore.BLUE))

class Casino:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.current_user: Optional[User] = None
        self.market = CryptoMarket()
        self.last_command = ""
        self.last_save = time.time()
        self.promo_codes = self._load_promocodes()
        self.forum = Forum()
        self.achievements = Achievements()
        self.load_users()
    
    def save_users(self):
        try:
            os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
            data = {un: user.to_dict() for un, user in self.users.items()}
            with open(SAVE_PATH, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Ошибка сохранения: {e}")
    
    def load_users(self):
        try:
            if os.path.exists(SAVE_PATH):
                with open(SAVE_PATH, "r") as f:
                    data = json.load(f)
                    self.users = {un: User.from_dict(user_data) for un, user_data in data.items()}
        except FileNotFoundError:
            self.users = {}
        except Exception as e:
            logger.error(f"Ошибка загрузки: {e}")
            self.users = {}
    
    def _load_promocodes(self) -> Dict[str, Any]:
        try:
            os.makedirs(os.path.dirname(KEYS_PATH), exist_ok=True)
            if os.path.exists(KEYS_PATH):
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
            return {}
        except Exception as e:
            logger.error(f"Ошибка загрузки промокодов: {e}")
            return {}
    
    def _save_promocodes(self):
        try:
            with open(KEYS_PATH, "w") as f:
                json.dump(self.promo_codes, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Ошибка сохранения промокодов: {e}")
    
    def activate_promo(self, code: str):
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
            self.current_user.data.crypto_balance["EXTRACT"] += Decimal(str(promo["amount"]))
            msg = f"+{promo['amount']}{CURRENCY}"
        elif promo["type"] == "eup":
            expiry_date = (datetime.now() + timedelta(days=promo['amount'])).strftime("%Y-%m-%d")
            self.current_user.data.subscription = Subscription(
                type=SubscriptionType.EUP,
                expires_at=expiry_date,
                autorenew=False
            )
            msg = f"EUP подписка на {promo['amount']} дней"
        elif promo["type"] == "eup_plus":
            expiry_date = (datetime.now() + timedelta(days=promo['amount'])).strftime("%Y-%m-%d")
            self.current_user.data.subscription = Subscription(
                type=SubscriptionType.EUP_PLUS,
                expires_at=expiry_date,
                autorenew=False
            )
            msg = f"EUP+ подписка на {promo['amount']} дней"
        elif promo["type"] == "crypto":
            coin = promo["coin"]
            amount = Decimal(str(promo["amount"]))
            self.current_user.data.crypto_balance[coin] += amount
            msg = f"+{float(amount)} {coin} {CRYPTO_SYMBOLS[coin]}"
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
    
    def get_current_event(self) -> Optional[Dict[str, Any]]:
        current_month = datetime.now().month
        event = MONTHLY_EVENTS.get(current_month, {}).copy()
        if event:
            event["active"] = True
            return event
        return None
    
    def apply_event_bonus(self, bonus_type: str, base_value: Decimal) -> Decimal:
        event = self.get_current_event()
        if not event or "effects" not in event:
            return base_value
        bonus = event["effects"].get(bonus_type, 1.0)
        if isinstance(bonus, (int, float)):
            return base_value * Decimal(str(bonus))
        return base_value
    
    def show_monthly_event(self):
        event = self.get_current_event()
        if not event:
            print(dynamic_border(f"{Fore.YELLOW}В этом месяце нет активных событий", Fore.YELLOW))
            return
        month_name = datetime.now().strftime("%B")
        next_month = datetime.now().replace(day=28) + timedelta(days=4)
        days_left = (next_month.replace(day=1) - datetime.now()).days
        content = [
            f"{Fore.MAGENTA}📅 {month_name} - {event['name']}",
            f"{Fore.CYAN}Осталось: {days_left} дней",
            f"{Fore.GREEN}Действующие бонусы:",
        ]
        for effect, value in event["effects"].items():
            icon = "▪️"
            if isinstance(value, bool):
                content.append(f"{icon} {effect}: {'Активен' if value else 'Неактивен'}")
            elif isinstance(value, float):
                content.append(f"{icon} {effect}: x{value}")
            else:
                content.append(f"{icon} {effect}: +{value}")
        print(dynamic_border('\n'.join(content), Fore.MAGENTA))
    
    def _validate_bet(self, bet: Decimal) -> bool:
        if not self.current_user:
            print(f"{Fore.RED}Сначала выберите пользователя!")
            return False
        if bet <= Decimal('0'):
            print(f"{Fore.RED}Ставка должна быть положительной!")
            return False
        if self.current_user.data.crypto_balance.get("EXTRACT", Decimal('0')) < bet:
            print(f"{Fore.RED}Недостаточно средств!")
            return False
        return True
    
    def _process_result(self, win: Decimal, bet: Decimal):
        win_decimal = win
        bet_decimal = bet
        
        win_value = self.apply_event_bonus("win_multiplier", win_decimal)
        
        if win_decimal > Decimal('0'):
            self.current_user.data.crypto_balance["EXTRACT"] += win_decimal
            self.current_user.update_stats(True)
            self.current_user.add_xp(int(win_decimal))
            if self.current_user.data.wins == 1:
                self.achievements.unlock_achievement(self.current_user.username, "first_win", self.current_user)
            if self.current_user.data.games_played >= 100:
                self.achievements.unlock_achievement(self.current_user.username, "slots_master", self.current_user)
        else:
            self.current_user.update_stats(False)
            self.current_user.add_xp(int(bet_decimal * Decimal('0.1')))
        
        self.current_user.data.total_earned += win_decimal
        self.save_users()
    
    def _apply_subscription_bonus(self, win: Decimal) -> Decimal:
        if self.current_user.data.subscription.type == SubscriptionType.EUP:
            return win * Decimal('1.10')
        elif self.current_user.data.subscription.type == SubscriptionType.EUP_PLUS:
            return win * Decimal('1.25')
        return win
    
    def _apply_subscription_refund(self, bet: Decimal) -> Decimal:
        if not self.current_user.has_active_subscription():
            return Decimal('0')
        if self.current_user.data.subscription.type == SubscriptionType.EUP:
            refund = bet * Decimal('0.10')
            self.current_user.data.crypto_balance["EXTRACT"] += refund
            return refund
        if self.current_user.data.subscription.type == SubscriptionType.EUP_PLUS:
            refund = bet * Decimal('0.20')
            self.current_user.data.crypto_balance["EXTRACT"] += refund
            return refund
        return Decimal('0')
    
    def create_user(self, username: str):
        if username in self.users:
            print(f"{Fore.RED}Пользователь {username} уже существует!")
            return
        self.users[username] = User(username)
        self.current_user = self.users[username]
        self.save_users()
        print(f"{gradient_text(f'Пользователь {username} создан!', [Fore.GREEN, Fore.LIGHTGREEN_EX])}")
    
    def select_user(self, username: str):
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
    
    def delete_user(self, username: str):
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
        
        print(f"{Fore.CYAN}╔{'═'*60}╗")
        print(f"{Fore.CYAN}║{'ЗАРЕГИСТРИРОВАННЫЕ ПОЛЬЗОВАТЕЛИ':^60}║")
        print(f"{Fore.CYAN}╠{'═'*60}╣")
        
        for i, (username, user) in enumerate(self.users.items(), 1):
            balance = float(user.data.crypto_balance.get('EXTRACT', Decimal('0')))
            print(f"{Fore.CYAN}║ {i:2}. {user.get_styled_username():<30} Баланс: {balance:>12.2f} {CURRENCY} ║")
        
        print(f"{Fore.CYAN}╚{'═'*60}╝")
    
    def slots(self, bet_amount: float):
        bet = Decimal(str(bet_amount))
        if not self._validate_bet(bet):
            return
        
        actual_bet = bet
        used_free_spin = False
        
        if self.current_user.data.free_spins > 0:
            print(f"{Fore.GREEN}Использован бесплатный спин (осталось: {self.current_user.data.free_spins-1})\n")
            self.current_user.data.free_spins -= 1
            used_free_spin = True
        else:
            self.current_user.data.crypto_balance["EXTRACT"] -= bet
        
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
                temp = secrets.SystemRandom().choices([s[0] for s in symbols], weights=[s[1] for s in symbols], k=3)
                print("\r" + " | ".join(temp), end='', flush=True)
                time.sleep(0.1)
        
        print("Вращение...")
        spin_animation()
        
        results = secrets.SystemRandom().choices([s[0] for s in symbols], weights=[s[1] for s in symbols], k=3)
        print(" \r" + " | ".join(results) + "   ")
        
        win = Decimal('0')
        free_spins_won = 0
        
        if results.count("💎") == 3:
            win = bet * Decimal('50')
            free_spins_won = 5
            print(dynamic_border(f"{Fore.GREEN}✨ ДЖЕКПОТ! 3 АЛМАЗА! ✨ +{float(win)}{CURRENCY} + {free_spins_won} ФРИСПИНОВ", Fore.GREEN))
        elif results[0] == results[1] == results[2]:
            multiplier = Decimal('10')
            if results[0] == "🔔":
                multiplier = Decimal('15')
            if results[0] == "⭐":
                multiplier = Decimal('20')
            win = bet * multiplier
            free_spins_won = 2
            print(dynamic_border(f"{Fore.GREEN}🎉 СУПЕР! 3 {results[0]}! +{float(win)}{CURRENCY} + {free_spins_won} ФРИСПИНА", Fore.GREEN))
        elif results[0] == results[1]:
            win = bet * Decimal('3')
            if results[0] == "💎":
                win = bet * Decimal('10')
                free_spins_won = 1
            print(dynamic_border(f"{Fore.YELLOW}Выигрыш по линии! +{float(win)}{CURRENCY}" +
                                 (f" + {free_spins_won} ФРИСПИН" if free_spins_won else ""),
                                 Fore.YELLOW))
        elif used_free_spin:
            if secrets.randbelow(100) < 30:
                free_spins_won = 1
                print(dynamic_border(f"{Fore.BLUE}Удача в следующий раз! 🍀 +1 ФРИСПИН", Fore.BLUE))
            else:
                print(dynamic_border(f"{Fore.RED}Проигрыш", Fore.RED))
        else:
            refund = self._apply_subscription_refund(bet)
            if refund > Decimal('0'):
                print(dynamic_border(f"{Fore.RED}Проигрыш {Fore.YELLOW}(Возврат: +{float(refund)}{CURRENCY})", Fore.RED))
            else:
                print(dynamic_border(f"{Fore.RED}Проигрыш", Fore.RED))
        
        if win > Decimal('0'):
            win = self._apply_subscription_bonus(win)
            win_multiplier = self.apply_event_bonus("slots_multiplier", Decimal('1.0'))
            win *= win_multiplier
            self.current_user.data.crypto_balance["EXTRACT"] += win
        
        if free_spins_won > 0:
            self.current_user.data.free_spins += free_spins_won
            print(f"{Fore.CYAN}Теперь у вас {self.current_user.data.free_spins} фриспинов!")
        
        self._process_result(win, actual_bet)
    
    def trade(self, command: str):
        if not self.current_user:
            print(f"{Fore.RED}Сначала выберите пользователя! add/login [ник]")
            return
        
        try:
            parts = command.split()
            if len(parts) < 3:
                raise ValueError
            action = parts[0].lower()
            coin = parts[1].upper()
            amount = Decimal(str(parts[2]))
            
            if amount <= Decimal('0'):
                print(f"{Fore.RED}Количество должно быть положительным!")
                return
            
            if coin not in self.market.rates:
                print(f"{Fore.RED}Неизвестная валюта: {coin}")
                return
            
            rate = self.market.get_rate(coin)
            
            if action == "buy":
                cost = amount * rate * Decimal('1.01')
                cost_multiplier = self.apply_event_bonus("trade_fee", Decimal('1.0'))
                cost *= cost_multiplier
                
                if self.current_user.data.crypto_balance.get("EXTRACT", Decimal('0')) < cost:
                    print(f"{Fore.RED}Недостаточно средств!")
                    return
                
                self.current_user.data.crypto_balance["EXTRACT"] -= cost
                current_balance = self.current_user.data.crypto_balance.get(coin, Decimal('0'))
                self.current_user.data.crypto_balance[coin] = current_balance + amount
                self.current_user.add_transaction('buy', coin, amount, cost)
                
                event = self.get_current_event()
                if event and "trade_xp_bonus" in event.get("effects", {}):
                    self.current_user.add_xp(event["effects"]["trade_xp_bonus"])
                
                trade_count = len([t for t in self.current_user.data.transactions if t.action in ['buy', 'sell']])
                if trade_count >= 50:
                    self.achievements.unlock_achievement(self.current_user.username, "trader", self.current_user)
                
                print(dynamic_border(f"{Fore.GREEN}Куплено {float(amount):.4f} {coin}", Fore.CYAN, 40))
            
            elif action == "sell":
                current_balance = self.current_user.data.crypto_balance.get(coin, Decimal('0'))
                if current_balance < amount:
                    print(f"{Fore.RED}Недостаточно {coin} для продажи!")
                    return
                
                value = amount * rate * Decimal('0.99')
                value_multiplier = self.apply_event_bonus("trade_bonus", Decimal('1.0'))
                value *= value_multiplier
                
                self.current_user.data.crypto_balance[coin] = current_balance - amount
                self.current_user.data.crypto_balance["EXTRACT"] += value
                self.current_user.add_transaction('sell', coin, amount, value)
                
                trade_count = len([t for t in self.current_user.data.transactions if t.action in ['buy', 'sell']])
                if trade_count >= 50:
                    self.achievements.unlock_achievement(self.current_user.username, "trader", self.current_user)
                
                print(dynamic_border(f"{Fore.GREEN}Продано {float(amount):.4f} {coin}", Fore.MAGENTA, 40))
            else:
                print(f"{Fore.RED}Неизвестное действие: {action}")
                return
            
            self.market.update_rates()
            self.save_users()
        
        except (IndexError, ValueError) as e:
            logger.error(f"Trade error: {e}")
            print(f"{Fore.RED}Ошибка команды: trade [buy/sell] [монета] [количество]")
    
    def monster_battle(self, bet_amount: float):
        bet = Decimal(str(bet_amount))
        if not self._validate_bet(bet):
            return
        
        print(dynamic_border(f"{Fore.RED}EXTRACT BATTLES", Fore.RED))
        self.current_user.data.crypto_balance["EXTRACT"] -= bet
        
        player_attack = secrets.randbelow(101) + 50 + self.current_user.data.level * 2
        monster_attack = secrets.randbelow(101) + 50
        
        print(f"{Fore.CYAN}Ваша сила атаки: {player_attack}")
        print(f"{Fore.RED}Сила атаки монстра: {monster_attack}")
        
        if player_attack > monster_attack:
            win = bet * Decimal('3')
            win = self._apply_subscription_bonus(win)
            win_multiplier = self.apply_event_bonus("battle_xp", Decimal('1.0'))
            win *= win_multiplier
            print(dynamic_border(f"{Fore.GREEN}ПОБЕДА! +{float(win)}{CURRENCY}", Fore.GREEN))
        else:
            win = Decimal('0')
            refund = self._apply_subscription_refund(bet)
            if refund > Decimal('0'):
                print(dynamic_border(f"{Fore.RED}ПОРАЖЕНИЕ {Fore.YELLOW}(Возврат: +{float(refund)}{CURRENCY})", Fore.RED))
            else:
                print(dynamic_border(f"{Fore.RED}ПОРАЖЕНИЕ", Fore.RED))
        
        self._process_result(win, bet)
    
    def dice(self, bet_amount: float):
        bet = Decimal(str(bet_amount))
        if not self._validate_bet(bet):
            return
        
        print(dynamic_border(f"{Fore.YELLOW}EXTRACT DICE", Fore.YELLOW))
        self.current_user.data.crypto_balance["EXTRACT"] -= bet
        
        player_dice = sum(secrets.randbelow(6) + 1 for _ in range(3))
        dealer_dice = sum(secrets.randbelow(6) + 1 for _ in range(3))
        
        print(f"{Fore.CYAN}Ваши кости: {player_dice}")
        print(f"{Fore.RED}Кости дилера: {dealer_dice}")
        
        if player_dice > dealer_dice:
            win = bet * Decimal('2')
            win = self._apply_subscription_bonus(win)
            print(dynamic_border(f"{Fore.GREEN}ВЫИГРЫШ! +{float(win)}{CURRENCY}", Fore.GREEN))
        else:
            win = Decimal('0')
            refund = self._apply_subscription_refund(bet)
            if refund > Decimal('0'):
                print(dynamic_border(f"{Fore.RED}ПРОИГРЫШ {Fore.YELLOW}(Возврат: +{float(refund)}{CURRENCY})", Fore.RED))
            else:
                print(dynamic_border(f"{Fore.RED}ПРОИГРЫШ", Fore.RED))
        
        self._process_result(win, bet)
    
    def high_low(self, bet_amount: float):
        bet = Decimal(str(bet_amount))
        if not self._validate_bet(bet):
            return
        
        print(dynamic_border(f"{Fore.MAGENTA}EXTRACT HIGH-LOW", Fore.MAGENTA))
        self.current_user.data.crypto_balance["EXTRACT"] -= bet
        
        current = secrets.randbelow(200) + 1
        print(f"Текущее число: {Fore.CYAN}{current}")
        
        choice = input(f"{Fore.YELLOW}Следующее будет выше (h) или ниже (l)? ").lower()
        next_num = secrets.randbelow(200) + 1
        
        print(f"Новое число: {Fore.CYAN}{next_num}")
        
        won = (choice == 'h' and next_num > current) or (choice == 'l' and next_num < current)
        
        if won:
            base_win = bet * Decimal('2')
            win = self._apply_subscription_bonus(base_win)
            win_multiplier = self.apply_event_bonus("win_multiplier", Decimal('1.0'))
            win *= win_multiplier
            print(dynamic_border(f"{Fore.GREEN}ПОБЕДА! +{float(win)}{CURRENCY}", Fore.GREEN))
            self._process_result(win, bet)
        else:
            win = Decimal('0')
            refund = self._apply_subscription_refund(bet)
            if refund > Decimal('0'):
                print(dynamic_border(f"{Fore.RED}ПРОИГРЫШ {Fore.YELLOW}(Возврат: +{float(refund)}{CURRENCY})", Fore.RED))
            else:
                print(dynamic_border(f"{Fore.RED}ПРОИГРЫШ", Fore.RED))
            self._process_result(Decimal('0'), bet)
    
    def roulette(self, bet_amount: float):
        bet = Decimal(str(bet_amount))
        if not self._validate_bet(bet):
            return
        
        print(dynamic_border(f"{Fore.RED}EXTRACT ROULETTE", Fore.RED))
        self.current_user.data.crypto_balance["EXTRACT"] -= bet
        
        print(f"{Fore.YELLOW}Выберите цвет:")
        print(f"{Fore.RED}1. Красное (x2)")
        print(f"{Fore.BLACK}2. Черное (x2)")
        print(f"{Fore.GREEN}3. Зеленое (x14)")
        
        try:
            choice = int(input("Ваш выбор (1-3): "))
            if choice not in [1, 2, 3]:
                print(f"{Fore.RED}Неверный выбор!")
                self.current_user.data.crypto_balance["EXTRACT"] += bet
                return
        except ValueError:
            print(f"{Fore.RED}Неверный ввод!")
            self.current_user.data.crypto_balance["EXTRACT"] += bet
            return
        
        result = secrets.randbelow(37)
        if result == 0:
            color = 3
        elif result % 2 == 0:
            color = 1
        else:
            color = 2
        
        print(f"Выпало: {result}")
        if color == 1:
            print(f"{Fore.RED}Красное!")
        elif color == 2:
            print(f"{Fore.BLACK}Черное!")
        else:
            print(f"{Fore.GREEN}Зеленое!")
        
        if choice == color:
            if color == 3:
                win = bet * Decimal('14')
            else:
                win = bet * Decimal('2')
            win = self._apply_subscription_bonus(win)
            print(dynamic_border(f"{Fore.GREEN}ВЫИГРЫШ! +{float(win)}{CURRENCY}", Fore.GREEN))
        else:
            win = Decimal('0')
            refund = self._apply_subscription_refund(bet)
            if refund > Decimal('0'):
                print(dynamic_border(f"{Fore.RED}ПРОИГРЫШ {Fore.YELLOW}(Возврат: +{float(refund)}{CURRENCY})", Fore.RED))
            else:
                print(dynamic_border(f"{Fore.RED}ПРОИГРЫШ", Fore.RED))
        
        self._process_result(win, bet)
    
    def blackjack(self, bet_amount: float):
        bet = Decimal(str(bet_amount))
        if not self._validate_bet(bet):
            return
        
        print(dynamic_border(f"{Fore.BLUE}EXTRACT BLACKJACK", Fore.BLUE))
        self.current_user.data.crypto_balance["EXTRACT"] -= bet
        
        deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4
        secrets.SystemRandom().shuffle(deck)
        
        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]
        
        print(f"{Fore.CYAN}Ваши карты: {player_hand} (Сумма: {sum(player_hand)})")
        print(f"{Fore.RED}Карта дилера: {dealer_hand[0]}")
        
        while sum(player_hand) < 21:
            action = input(f"{Fore.YELLOW}Еще карту? (y/n): ").lower()
            if action == 'y':
                player_hand.append(deck.pop())
                print(f"{Fore.CYAN}Ваши карты: {player_hand} (Сумма: {sum(player_hand)})")
                if sum(player_hand) > 21:
                    if 11 in player_hand:
                        player_hand[player_hand.index(11)] = 1
                        print(f"{Fore.CYAN}Ваши карты: {player_hand} (Сумма: {sum(player_hand)})")
                    else:
                        print(dynamic_border(f"{Fore.RED}Перебор! Вы проиграли.", Fore.RED))
                        self._process_result(Decimal('0'), bet)
                        return
            else:
                break
        
        while sum(dealer_hand) < 17:
            dealer_hand.append(deck.pop())
        
        print(f"{Fore.RED}Карты дилера: {dealer_hand} (Сумма: {sum(dealer_hand)})")
        
        player_sum = sum(player_hand)
        dealer_sum = sum(dealer_hand)
        
        if dealer_sum > 21 or player_sum > dealer_sum:
            win = bet * Decimal('2')
            win = self._apply_subscription_bonus(win)
            print(dynamic_border(f"{Fore.GREEN}ВЫИГРЫШ! +{float(win)}{CURRENCY}", Fore.GREEN))
        elif player_sum == dealer_sum:
            print(dynamic_border(f"{Fore.YELLOW}Ничья! Ставка возвращена.", Fore.YELLOW))
            self.current_user.data.crypto_balance["EXTRACT"] += bet
            return
        else:
            win = Decimal('0')
            refund = self._apply_subscription_refund(bet)
            if refund > Decimal('0'):
                print(dynamic_border(f"{Fore.RED}ПРОИГРЫШ {Fore.YELLOW}(Возврат: +{float(refund)}{CURRENCY})", Fore.RED))
            else:
                print(dynamic_border(f"{Fore.RED}ПРОИГРЫШ", Fore.RED))
        
        self._process_result(win, bet)
    
    def show_rates(self):
        print(f"{Fore.CYAN}╔{'═'*80}╗")
        print(f"{Fore.CYAN}║{'ТЕКУЩИЕ КУРСЫ КРИПТОВАЛЮТ':^80}║")
        print(f"{Fore.CYAN}╠{'═'*80}╣")
        
        for coin, rate in self.market.rates.items():
            if coin == "EXTRACT":
                continue
            
            change = self.market.get_rate_change(coin)
            color = Fore.GREEN if change >= 0 else Fore.RED
            change_text = f"{color}({change:+.2f}%){Style.RESET_ALL}"
            
            print(f"{Fore.CYAN}║ {CRYPTO_SYMBOLS[coin]:<2} {coin:<10} 1 {coin} = {float(rate):>12.2f}{CURRENCY} {change_text:<20} ║")
        
        print(f"{Fore.CYAN}╚{'═'*80}╝")
    
    def rename_account(self, current_name: str, new_name: str) -> bool:
        if current_name not in self.users:
            print(f"{Fore.RED}Ошибка: пользователь '{current_name}' не найден!")
            return False
        if new_name in self.users:
            print(f"{Fore.RED}Ошибка: имя '{new_name}' уже занято!")
            return False
        if not (new_name.isalnum() and 3 <= len(new_name) <= 16):
            print(f"{Fore.RED}Ошибка: новое имя должно быть 3-16 символов (только буквы/цифры)!")
            return False
        
        confirm = input(f"{Fore.RED}Переименовать '{current_name}' → '{new_name}'? (y/n): ").strip().lower()
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
    
    def transfer(self, sender: str, receiver: str, currency: str, amount_str: str) -> bool:
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
            amount = Decimal(str(amount_str))
            amount = amount.quantize(Decimal('0.00000001'), rounding=ROUND_DOWN)
            if amount <= Decimal('0'):
                print(f"{Fore.RED}Ошибка: сумма должна быть больше 0!")
                return False
        except Exception:
            print(f"{Fore.RED}Ошибка: неверный формат суммы!")
            return False
        
        sender_balance = self.users[sender].data.crypto_balance.get(currency, Decimal('0'))
        if sender_balance < amount:
            print(f"{Fore.RED}Ошибка: недостаточно средств! Доступно: {float(sender_balance):.8f}{CRYPTO_SYMBOLS[currency]}")
            return False
        
        commission_rate = Decimal('0.00') if self.users[sender].has_active_subscription() else Decimal('0.05')
        commission = (amount * commission_rate).quantize(Decimal('0.00000001'), rounding=ROUND_DOWN)
        received_amount = (amount - commission).quantize(Decimal('0.00000001'), rounding=ROUND_DOWN)
        
        confirm_text = f"""
{Fore.CYAN}{"═"*50}
{Fore.YELLOW}ПОДТВЕРЖДЕНИЕ ПЕРЕВОДА
{Fore.CYAN}{"."*50}
{Fore.WHITE}▪ От: {Fore.GREEN}{sender:<44}
{Fore.WHITE}▪ Кому: {Fore.GREEN}{receiver:<42}
{Fore.WHITE}▪ Валюта: {Fore.GREEN}{currency} {CRYPTO_SYMBOLS[currency]:<36}
{Fore.CYAN}{"═"*50}
{Fore.WHITE}▪ Сумма: {Fore.GREEN}{float(amount):.8f}
{Fore.WHITE}▪ Комиссия: {Fore.RED}{float(commission):.8f} ({float(commission_rate*Decimal("100"))}%){" [Без комиссии]" if commission_rate == Decimal('0') else ""}
{Fore.WHITE}▪ Получит: {Fore.YELLOW}{float(received_amount):.8f}
{Fore.CYAN}{"^"*50}
{Style.BRIGHT}Подтвердить перевод? (yes/no): {Style.RESET_ALL}"""
        
        print(confirm_text)
        confirm = input(">>> ").strip().lower()
        if confirm != 'yes':
            print(f"{Fore.YELLOW}❌ Перевод отменён")
            return False
        
        self.users[sender].data.crypto_balance[currency] = sender_balance - amount
        receiver_balance = self.users[receiver].data.crypto_balance.get(currency, Decimal('0'))
        self.users[receiver].data.crypto_balance[currency] = receiver_balance + received_amount
        
        self.users[sender].data.transactions.insert(0, Transaction(
            timestamp=timestamp,
            action="transfer_out",
            coin=currency,
            amount=-amount,
            total=amount,
            to_user=receiver,
            commission=commission
        ))
        
        self.users[receiver].data.transactions.insert(0, Transaction(
            timestamp=timestamp,
            action="transfer_in",
            coin=currency,
            amount=received_amount,
            total=received_amount,
            from_user=sender
        ))
        
        self.users[sender].data.transactions = self.users[sender].data.transactions[:20]
        self.users[receiver].data.transactions = self.users[receiver].data.transactions[:20]
        
        self._save_receipt({
            "timestamp": timestamp,
            "sender": sender,
            "receiver": receiver,
            "currency": currency,
            "amount": float(amount),
            "commission": float(commission),
            "received": float(received_amount)
        })
        
        self.save_users()
        print(f"{Fore.GREEN}✅ Успешно: {float(received_amount):.8f}{CRYPTO_SYMBOLS[currency]} → {receiver}")
        return True
    
    def show_receipts(self):
        try:
            os.makedirs(os.path.dirname(RECEIPTS_PATH), exist_ok=True)
            if not os.path.exists(RECEIPTS_PATH):
                print(dynamic_border(f"{Fore.YELLOW}История переводов пуста", Fore.YELLOW))
                return
            
            with open(RECEIPTS_PATH, 'r', encoding='utf-8') as f:
                receipts = json.load(f)
            
            if not receipts:
                print(dynamic_border(f"{Fore.YELLOW}История переводов пуста", Fore.YELLOW))
                return
            
            print(f"{Fore.CYAN}╔{'═'*100}╗")
            print(f"{Fore.CYAN}║{'ПОСЛЕДНИЕ ПЕРЕВОДЫ':^100}║")
            print(f"{Fore.CYAN}╠{'═'*100}╣")
            
            for i, receipt in enumerate(receipts[:10], 1):
                print(f"{Fore.CYAN}║ {i:2}. {receipt['timestamp'][:16]} {receipt['sender']:>15} → {receipt['receiver']:<15} "
                      f"{receipt['amount']:>12.8f}{CRYPTO_SYMBOLS.get(receipt['currency'], '?')} "
                      f"комиссия: {receipt['commission']:>10.8f} ║")
            
            print(f"{Fore.CYAN}╚{'═'*100}╝")
        
        except Exception as e:
            logger.error(f"Error loading receipts: {e}")
            print(dynamic_border(f"{Fore.RED}Ошибка загрузки истории переводов", Fore.RED))
    
    def _save_receipt(self, receipt_data: Dict[str, Any]):
        try:
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
            receipts = receipts[:50]
            
            with open(RECEIPTS_PATH, 'w', encoding='utf-8') as f:
                json.dump(receipts, f, indent=4, ensure_ascii=False, sort_keys=True)
        
        except Exception as e:
            logger.error(f"Error saving receipt: {e}")
    
    def check_user(self, username: str):
        if username not in self.users:
            print(f"{Fore.RED}Пользователь '{username}' не найден!")
            return
        
        user = self.users[username]
        content = [
            f"{Fore.CYAN}Информация о пользователе: {user.get_styled_username()}",
            f"{Fore.GREEN}Баланс: {float(user.data.crypto_balance.get('EXTRACT', Decimal('0'))):.2f} {CURRENCY}",
            f"{Fore.BLUE}Уровень: {user.data.level}",
            f"{Fore.YELLOW}Опыт: {user.data.xp}/{user.required_xp()} ({user.show_level_progress()})"
        ]
        
        top_coins = sorted(
            [(k, v) for k, v in user.data.crypto_balance.items() if v > Decimal('0') and k != "EXTRACT"],
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        if top_coins:
            content.append(f"{Fore.MAGENTA}Топ активы:")
            for coin, amount in top_coins:
                content.append(f"  {CRYPTO_SYMBOLS[coin]} {coin}: {float(amount):.4f}")
        
        print(dynamic_border('\n'.join(content), Fore.CYAN))
    
    def global_stats(self):
        total_balance = sum(float(user.data.crypto_balance.get("EXTRACT", Decimal('0'))) for user in self.users.values())
        total_games = sum(user.data.games_played for user in self.users.values())
        total_users = len(self.users)
        
        print(f"{Fore.CYAN}╔{'═'*60}╗")
        print(f"{Fore.CYAN}║{'ГЛОБАЛЬНАЯ СТАТИСТИКА':^60}║")
        print(f"{Fore.CYAN}╠{'═'*60}╣")
        print(f"{Fore.CYAN}║ 👥  Пользователей: {total_users:>40} ║")
        print(f"{Fore.CYAN}║ 💰  Общий баланс: {total_balance:>38.2f} {CURRENCY} ║")
        print(f"{Fore.CYAN}║ 🎮  Всего игр: {total_games:>42} ║")
        print(f"{Fore.CYAN}║ 🏆  Общих побед: {sum(user.data.wins for user in self.users.values()):>40} ║")
        print(f"{Fore.CYAN}║ 💀  Общих поражений: {sum(user.data.losses for user in self.users.values()):>36} ║")
        print(f"{Fore.CYAN}╚{'═'*60}╝")
    
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
{Fore.CYAN}{VERSION_ALL}
{Fore.WHITE}1. Обновление до версии 12.0.0
{Fore.WHITE}2. Добавлена безопасная генерация (secrets)
{Fore.WHITE}3. Добавлена история курсов валют
{Fore.WHITE}4. Добавлен ASCII график курсов (команда chart)
{Fore.WHITE}5. Улучшена типизация данных
{Fore.WHITE}6. Исправлены ошибки округления
{Fore.WHITE}7. Добавлено логирование
{Fore.WHITE}8. Удалены проблемные библиотеки
{Fore.RED}___
        """
        print(dynamic_border(path_text.strip(), Fore.CYAN))
    
    def display_help(self):
        help_text = f"""
{Fore.CYAN}Доступные команды:
{Fore.WHITE}           ---Аккаунт---
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
{Fore.GREEN}achievements                {Fore.WHITE}- Показать достижения
{Fore.GREEN}exit -a                     {Fore.WHITE}- Выйти из аккаунта
{Fore.WHITE}      ---Покупка и статус EUP---
{Fore.YELLOW}eup buy [дни]              {Fore.WHITE}- Купить подписку EUP
{Fore.YELLOW}eup_plus buy [дни]         {Fore.WHITE}- Купить подписку EUP+
{Fore.YELLOW}eup status                 {Fore.WHITE}- Статус подписки
{Fore.YELLOW}eup info                   {Fore.WHITE}- Актуальная информация об подписках
{Fore.YELLOW}eup autonone               {Fore.WHITE}- Отключить автопродление
{Fore.WHITE}             ---Игры---
{Fore.RED}slots [сумма]                 {Fore.WHITE}- Играть в автоматы
{Fore.RED}battle [сумма]                {Fore.WHITE}- Сразиться с монстром
{Fore.RED}dice [сумма]                  {Fore.WHITE}- Игра в кости
{Fore.RED}highlow [сумма]               {Fore.WHITE}- Игра High-Low
{Fore.RED}roulette [сумма]              {Fore.WHITE}- Игра в рулетку
{Fore.RED}blackjack [сумма]             {Fore.WHITE}- Игра в блэкджек
{Fore.WHITE}         ---Криптовалюта---
{Fore.BLUE}trade buy [монета] [кол-во]  {Fore.WHITE}- Купить крипту
{Fore.BLUE}trade sell [монета] [кол-во] {Fore.WHITE}- Продать крипту
{Fore.BLUE}rates                        {Fore.WHITE}- Показать курсы обмена
{Fore.BLUE}wal                          {Fore.WHITE}- Показать баланс всего кошелька
{Fore.BLUE}chart [монета]               {Fore.WHITE}- Показать график курса
{Fore.WHITE}       ---Игровые события---
{Fore.WHITE}monthly                     {Fore.WHITE}- Текущее месячное событие
{Fore.WHITE}promo [код]                {Fore.WHITE}- Активировать промокод
{Fore.WHITE}          ---Об Extract---
{Fore.CYAN}extract                      {Fore.WHITE}- Информация о версии
{Fore.CYAN}wnew                         {Fore.WHITE}- Патчноут
{Fore.CYAN}forum                        {Fore.WHITE}- Открывает форум
{Fore.WHITE}            ---Прочее---
{Fore.MAGENTA}global                    {Fore.WHITE}- Общая статистика всех аккаунтов
{Fore.MAGENTA}exit                      {Fore.WHITE}- Выйти из игры
{Fore.MAGENTA}help                      {Fore.WHITE}- Справка по командам
        """
        print(dynamic_border(help_text.strip(), Fore.CYAN))
    
    def display_version(self):
        print_art()
        version_info = f"""
{Fore.YELLOW}{ADDINFO}
{Fore.YELLOW}{VERSION_ALL}
{Fore.RED}{INFO}
{Fore.RED}Авторы: Rexamm1t, Wefol1x
{Fore.RED}Telegram: @rexamm1t, @wefolix
{Fore.GREEN}Лицензия: MIT
{Fore.BLUE}Дата сборки: 27.01.2026
        """
        print(dynamic_border(version_info.strip(), Fore.BLUE))
    
    def check_autosave(self):
        if time.time() - self.last_save > AUTOSAVE_INTERVAL:
            self.save_users()
            self.last_save = time.time()

def main():
    print_art()
    casino = Casino()
    
    print(f"{Fore.GREEN}Загрузка системы...")
    for i in range(1, 101):
        bar_len = i // 5
        bar = "▓" * bar_len + "░" * (20 - bar_len)
        print(f"\r[{bar}] {i}%", end='', flush=True)
        time.sleep(0.01)
    print(f"\r{' '*50}\r", end='')
    
    try:
        while True:
            casino.check_autosave()
            current_time = datetime.now().strftime("%H:%M:%S")
            
            if casino.current_user:
                username = casino.current_user.get_styled_username()
                balance = float(casino.current_user.data.crypto_balance.get("EXTRACT", Decimal('0')))
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
                elif action.startswith("roulette"):
                    try:
                        bet = float(action.split()[1])
                        casino.roulette(bet)
                    except:
                        print(f"{Fore.RED}Используйте: roulette [сумма]")
                elif action.startswith("blackjack"):
                    try:
                        bet = float(action.split()[1])
                        casino.blackjack(bet)
                    except:
                        print(f"{Fore.RED}Используйте: blackjack [сумма]")
                elif action.startswith("trade"):
                    casino.trade(action[5:])
                elif action.startswith("chart "):
                    try:
                        coin = action.split()[1].upper()
                        casino.market.print_chart(coin)
                    except:
                        print(f"{Fore.RED}Используйте: chart [валюта]")
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
                            f"{Fore.CYAN}Уровень: {casino.current_user.data.level}",
                            f"{Fore.BLUE}Опыт: {casino.current_user.data.xp:.0f}/{casino.current_user.required_xp():.0f}",
                            casino.current_user.show_level_progress(),
                            f"{Fore.GREEN}Всего заработано: {float(casino.current_user.data.total_earned):.2f}{CURRENCY}"
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
                elif action == "achievements":
                    if casino.current_user:
                        casino.achievements.show_achievements(casino.current_user.username)
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
                logger.error(f"Input error: {e}")
                print(f"{Fore.RED}Ошибка ввода")
            except Exception as e:
                logger.error(f"Unknown error: {e}")
                print(f"{Fore.RED}Неизвестная ошибка")
    
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