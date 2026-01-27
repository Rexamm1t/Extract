import random
import json
import time
import os
import textwrap
import socket
import threading
import hashlib
import uuid
import sys
import math
import string
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict, deque, Counter, OrderedDict
from pathlib import Path
from itertools import cycle, chain
from hashlib import sha256, md5
import colorama
from colorama import Fore, Back, Style, init
init(autoreset=True)

try:
    from rich import print as rprint
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.console import Console
    from rich.layout import Layout
    from rich.text import Text
    from rich.markdown import Markdown
    from rich.syntax import Syntax
    from rich.prompt import Prompt, Confirm
    from rich.tree import Tree
    from rich.live import Live
    from rich.columns import Columns
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None

ADDINFO = "ПЛАТФОРМА EXTRACT 2025"
INFO = "Команда Extract (Rexamm1t, Wefol1x)"
VERSION = "EXTRACT 11.0.0"
VERSION_ALL = "EXTRACT 11.0.0 (4.0.2)"
SAVE_PATH = "data/users.json"
KEYS_PATH = "data/keys.json"
RECEIPTS_PATH = "logs/receipts.json"
CS_LOG_PATH = "logs/cs_l.json"
FORUM_PATH = "forum/meta.json"
ACHIEVEMENTS_PATH = "data/achievements.json"

CRYPTO_SYMBOLS = {
    "EXTRACT": "E", "BETASTD": "B", "EXRSD": "R", "DOGCOIN": "D",
    "BTC": "B", "ETH": "E", "LTC": "L", "BNB": "N", "ADA": "A",
    "SOL": "S", "XRP": "X", "DOT": "O", "DOGE": "G", "SHIB": "H",
    "AVAX": "V", "TRX": "T", "MATIC": "M", "ATOM": "T", "NOT": "N",
    "TON": "O", "XYZ": "Y", "ABC": "A", "DEF": "D", "GHI": "G",
    "JKL": "J", "MNO": "O", "PQR": "P"
}

CURRENCY = "E"
INITIAL_BALANCE = 10000.0
LEVEL_BASE_XP = 1000
AUTOSAVE_INTERVAL = 300
MAX_PLAYERS = 2
DEFAULT_PORT = 5555
MAX_MESSAGE_SIZE = 8192
CONNECTION_TIMEOUT = 30

class GameType(Enum):
    SLOTS = "slots"
    BATTLE = "battle"
    DICE = "dice"
    HIGHLOW = "highlow"
    ROULETTE = "roulette"
    BLACKJACK = "blackjack"

class MessageType(Enum):
    HANDSHAKE = "handshake"
    PING = "ping"
    PONG = "pong"
    CHAT = "chat"
    GAME_INVITE = "game_invite"
    GAME_ACCEPT = "game_accept"
    GAME_DECLINE = "game_decline"
    GAME_START = "game_start"
    GAME_MOVE = "game_move"
    GAME_RESULT = "game_result"
    TRANSFER = "transfer"
    DISCONNECT = "disconnect"
    ERROR = "error"
    SYNC_REQUEST = "sync_request"
    SYNC_RESPONSE = "sync_response"

@dataclass
class GameState:
    game_id: str
    game_type: GameType
    bet: float
    player1: str
    player2: str
    current_player: str
    state: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    moves: List[Dict[str, Any]] = field(default_factory=list)
    winner: Optional[str] = None
    completed: bool = False

class NetworkMessage:
    def __init__(self, msg_type: MessageType, data: Dict[str, Any], sender: str = None):
        self.type = msg_type
        self.data = data
        self.sender = sender
        self.timestamp = time.time()
        self.message_id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "data": self.data,
            "sender": self.sender,
            "timestamp": self.timestamp,
            "id": self.message_id
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NetworkMessage':
        msg_type = MessageType(data["type"])
        return cls(msg_type, data["data"], data.get("sender"))

    def serialize(self) -> bytes:
        try:
            return json.dumps(self.to_dict()).encode('utf-8')
        except:
            return json.dumps(self.to_dict()).encode('utf-8')

    @classmethod
    def deserialize(cls, data: bytes) -> Optional['NetworkMessage']:
        try:
            msg_dict = json.loads(data.decode('utf-8', errors='ignore'))
            return cls.from_dict(msg_dict)
        except Exception as e:
            return None

MONTHLY_EVENTS = {
    1: {"name": "Новогодний буст", "effects": {"slots_multiplier": 1.8, "free_daily_spins": 3, "level_up_bonus": 2000}},
    2: {"name": "Битва сердец", "effects": {"double_win_chance": True, "referral_bonus": 1.5, "loss_protection": 0.25}},
    3: {"name": "Весенний рост", "effects": {"xp_boost": 2.0, "trade_xp_bonus": 3, "daily_interest": 0.01}},
    4: {"name": "Апрельская лотерея", "effects": {"jackpot_chance": 0.15, "insurance": 0.2, "daily_bonus": 1500}},
    5: {"name": "Майская буря", "effects": {"battle_xp": 1.8, "daily_gift": 1500, "free_spins": 2}},
    6: {"name": "Летний круиз", "effects": {"trade_fee": 0.7, "slots_bonus": 3000, "xp_multiplier": 1.4}},
    7: {"name": "Горячая полоса", "effects": {"xp_multiplier": 1.4, "free_spins": 3, "daily_interest": 0.015}},
    8: {"name": "Августовский ветер", "effects": {"win_multiplier": 1.25, "insurance": 0.25, "trade_bonus": 1.1}},
    9: {"name": "Осенний урожай", "effects": {"trade_bonus": 1.3, "daily_gift": 2000, "xp_boost": 1.5}},
    10: {"name": "Хэллоуин", "effects": {"jackpot_chance": 0.2, "battle_xp": 2.0, "mystery_gift": True}},
    11: {"name": "Ноябрьская буря", "effects": {"xp_multiplier": 1.6, "slots_bonus": 4000, "loss_protection": 0.3}},
    12: {"name": "Зимнее чудо", "effects": {"win_multiplier": 1.5, "year_end_special": True, "unlimited_withdrawals": True}}
}

ACHIEVEMENTS = {
    "first_win": {"name": "Первая победа", "description": "Выиграйте первую игру", "xp_reward": 100},
    "level_10": {"name": "Уровень 10", "description": "Достигните 10 уровня", "xp_reward": 500},
    "millionaire": {"name": "Миллионер", "description": "Накопите 1,000,000 E", "xp_reward": 1000},
    "slots_master": {"name": "Мастер слотов", "description": "Выиграйте 100 раз в слотах", "xp_reward": 300},
    "trader": {"name": "Трейдер", "description": "Выполните 50 сделок", "xp_reward": 200},
    "live_player": {"name": "Сетевой игрок", "description": "Сыграйте 10 раз в сетевом режиме", "xp_reward": 150},
    "network_warrior": {"name": "Сетевой воин", "description": "Выиграйте 5 сетевых игр подряд", "xp_reward": 500}
}

def dynamic_border(text: str, border_color=Fore.MAGENTA, width: Optional[int] = None) -> str:
    if RICH_AVAILABLE:
        console.print(Panel(text, border_style=border_color[5:].lower(), width=width))
        return ""
    lines = text.split('\n')
    max_width = width if width else max(len(line) for line in lines) + 4
    border = '═' * (max_width - 2)
    bordered = [
        f"{border_color}╔{border}╗",
        *[f"{border_color}║ {line.ljust(max_width - 4)} ║" for line in lines],
        f"{border_color}╚{border}╝{Style.RESET_ALL}"
    ]
    return '\n'.join(bordered)

def rainbow_text(text: str) -> str:
    colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
    return ''.join([colors[i % len(colors)] + char for i, char in enumerate(text)]) + Style.RESET_ALL

def gradient_text(text: str, colors: List[str]) -> str:
    return ''.join([colors[i % len(colors)] + char for i, char in enumerate(text)]) + Style.RESET_ALL

def format_currency(amount: float) -> str:
    return f"{amount:,.2f}"

def print_header():
    if RICH_AVAILABLE:
        console.print(Panel.fit(f"[bold cyan]{VERSION}[/bold cyan]\n[italic yellow]{INFO}[/italic yellow]", 
                                title="🎰 EXTRACT", border_style="cyan"))
        return
    
    art = """
    ╔═══════════════════════════════════════╗
    ║          ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄          ║
    ║         ██████████████████████████         ║
    ║         ██                         ██      ║
    ║         ██        EXTRACT          ██      ║
    ║         ██                         ██      ║
    ║         ████████████████████████████       ║
    ║                                         ║
    ╚═══════════════════════════════════════╝
    """
    print(gradient_text(art, [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]))
    print(gradient_text("EXTRACT", [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]))

def print_currency_ascii_chart(crypto_market, currency: str):
    if currency not in crypto_market.rates:
        dynamic_border(f"Валюта {currency} не найдена", Fore.RED)
        return
    
    rate = crypto_market.rates[currency]
    symbol = CRYPTO_SYMBOLS.get(currency, currency)
    
    if RICH_AVAILABLE:
        table = Table(title=f"📊 Курс {currency}", show_header=True, header_style="bold magenta")
        table.add_column("Параметр", style="cyan")
        table.add_column("Значение", style="green")
        table.add_row("Валюта", f"{currency} ({symbol})")
        table.add_row("Текущий курс", f"{rate:,.2f} {CURRENCY}")
        
        try:
            with open(CS_LOG_PATH, "r") as f:
                old_rates = json.load(f)
            old_rate = old_rates.get(currency, rate)
            change = ((rate - old_rate) / old_rate) * 100 if old_rate != 0 else 0
            trend = "📈" if change > 0 else "📉" if change < 0 else "➡️"
            change_str = f"{trend} {change:+.2f}%"
            table.add_row("Изменение", change_str)
        except:
            table.add_row("Изменение", "N/A")
        
        console.print(table)
        return
    
    max_width = 50
    scale_factor = 100000
    if currency == "BTC":
        scale_factor = 1000
    elif currency == "ETH":
        scale_factor = 10000
    elif currency in ["BNB", "SOL", "ADA"]:
        scale_factor = 50000
    
    bar_width = min(int(rate / scale_factor * max_width), max_width)
    bar = '█' * bar_width + '░' * (max_width - bar_width)
    
    try:
        with open(CS_LOG_PATH, "r") as f:
            old_rates = json.load(f)
        old_rate = old_rates.get(currency, rate)
        change = ((rate - old_rate) / old_rate) * 100 if old_rate != 0 else 0
        trend = "ВВЕРХ" if change > 0 else "ВНИЗ" if change < 0 else "БЕЗ ИЗМЕНЕНИЙ"
        change_color = Fore.GREEN if change >= 0 else Fore.RED
    except:
        change = 0
        trend = "БЕЗ ИЗМЕНЕНИЙ"
        change_color = Fore.YELLOW
    
    content = [
        f"{Fore.CYAN}Валюта: {Fore.YELLOW}{currency} ({symbol})",
        f"{Fore.CYAN}Текущий курс: {Fore.GREEN}{rate:,.2f} {CURRENCY}",
        f"{Fore.CYAN}Изменение: {change_color}{trend} {change:+.2f}%",
        "",
        f"{Fore.BLUE}Визуализация курса:",
        f"{Fore.GREEN}{bar}",
        f"{Fore.CYAN}0{' ' * (max_width - 2)}{rate:,.2f} {CURRENCY}"
    ]
    dynamic_border('\n'.join(content), Fore.CYAN)

class NetworkManager:
    def __init__(self, casino):
        self.casino = casino
        self.server: Optional[socket.socket] = None
        self.client: Optional[socket.socket] = None
        self.connection: Optional[socket.socket] = None
        self.connections: List[Tuple[socket.socket, Tuple[str, int]]] = []
        self.peer_username: Optional[str] = None
        self.peer_address: Optional[Tuple[str, int]] = None
        self.ping: int = 0
        self.last_ping_time: float = 0
        self.is_host: bool = False
        self.is_connected: bool = False
        self.running: bool = False
        self.game_sessions: Dict[str, GameState] = {}
        self.message_queue: deque = deque()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.lock = threading.Lock()
        self.local_ip: str = self.get_local_ip()
        self.port: int = DEFAULT_PORT
        self.last_sync_time: float = 0
        self.sync_interval: float = 5.0

    def get_local_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def start_server(self, port: int = DEFAULT_PORT) -> bool:
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind(('0.0.0.0', port))
            self.server.listen(MAX_PLAYERS - 1)
            self.server.settimeout(1)
            self.port = port
            
            border_content = (
                f"{Fore.GREEN}Сервер запущен\n"
                f"IP: {self.local_ip}:{port}\n"
                f"Ожидание подключения..."
            )
            dynamic_border(border_content, Fore.GREEN)
            
            self.is_host = True
            self.running = True
            threading.Thread(target=self.accept_connections, daemon=True).start()
            return True
        except Exception as e:
            dynamic_border(f"Ошибка запуска сервера: {str(e)}", Fore.RED)
            return False

    def accept_connections(self):
        while self.running and self.server:
            try:
                conn, addr = self.server.accept()
                if len(self.connections) >= MAX_PLAYERS - 1:
                    conn.close()
                    continue
                conn.settimeout(CONNECTION_TIMEOUT)
                self.connections.append((conn, addr))
                
                border_content = (
                    f"{Fore.GREEN}Подключение от {addr[0]}:{addr[1]}\n"
                    f"Всего подключений: {len(self.connections)}"
                )
                dynamic_border(border_content, Fore.GREEN)
                
                threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()
                
                if len(self.connections) == 1:
                    self.connection = conn
                    self.peer_address = addr
                    threading.Thread(target=self.ping_loop, daemon=True).start()
                    threading.Thread(target=self.process_messages, daemon=True).start()
                    
                    if self.casino.current_user:
                        self.send_message(NetworkMessage(
                            MessageType.HANDSHAKE,
                            {"username": self.casino.current_user.username}
                        ))
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    pass
                break

    def connect_to_server(self, ip: str, port: int = DEFAULT_PORT) -> bool:
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.settimeout(10)
            self.client.connect((ip, port))
            self.client.settimeout(CONNECTION_TIMEOUT)
            self.connection = self.client
            self.peer_address = (ip, port)
            self.is_connected = True
            self.running = True
            self.port = port
            
            border_content = (
                f"{Fore.GREEN}Подключено к {ip}:{port}\n"
                f"Локальный IP: {self.local_ip}"
            )
            dynamic_border(border_content, Fore.GREEN)
            
            threading.Thread(target=self.handle_client, args=(self.client, (ip, port)), daemon=True).start()
            threading.Thread(target=self.ping_loop, daemon=True).start()
            threading.Thread(target=self.process_messages, daemon=True).start()
            
            if self.casino.current_user:
                self.send_message(NetworkMessage(
                    MessageType.HANDSHAKE,
                    {"username": self.casino.current_user.username}
                ))
            return True
        except Exception as e:
            dynamic_border(f"Ошибка подключения: {str(e)}", Fore.RED)
            return False

    def handle_client(self, conn: socket.socket, addr: Tuple[str, int]):
        buffer = b''
        while self.running and conn:
            try:
                data = conn.recv(MAX_MESSAGE_SIZE)
                if not data:
                    self.disconnect()
                    break
                buffer += data
                while len(buffer) >= 4:
                    try:
                        message = NetworkMessage.deserialize(buffer[:MAX_MESSAGE_SIZE])
                        if message:
                            with self.lock:
                                self.message_queue.append((message, conn))
                            buffer = buffer[MAX_MESSAGE_SIZE:]
                        else:
                            break
                    except Exception as e:
                        break
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    pass
                break

    def process_messages(self):
        while self.running:
            try:
                if self.message_queue:
                    with self.lock:
                        message, conn = self.message_queue.popleft()
                    self.handle_message(message)
                time.sleep(0.01)
            except Exception as e:
                if self.running:
                    pass

    def send_message(self, message: NetworkMessage) -> bool:
        if not self.connection or not self.running:
            return False
        try:
            data = message.serialize()
            self.connection.sendall(data)
            return True
        except Exception as e:
            return False

    def broadcast_message(self, message: NetworkMessage):
        for conn, addr in self.connections:
            try:
                data = message.serialize()
                conn.sendall(data)
            except Exception as e:
                pass

    def handle_message(self, message: NetworkMessage):
        try:
            if message.type == MessageType.HANDSHAKE:
                self.peer_username = message.data.get("username", "Неизвестно")
                border_content = (
                    f"{Fore.CYAN}Игрок подключен: {self.peer_username}\n"
                    f"Подключение установлено"
                )
                dynamic_border(border_content, Fore.CYAN)
                self.send_message(NetworkMessage(
                    MessageType.SYNC_REQUEST,
                    {"timestamp": time.time()}
                ))
            elif message.type == MessageType.PING:
                if message.data.get("request"):
                    self.send_message(NetworkMessage(MessageType.PONG, {"response": True}))
                else:
                    self.ping = int((time.time() - self.last_ping_time) * 1000)
            elif message.type == MessageType.PONG:
                self.ping = int((time.time() - self.last_ping_time) * 1000)
            elif message.type == MessageType.CHAT:
                sender = message.data.get("sender", "Неизвестно")
                text = message.data.get("text", "")
                if RICH_AVAILABLE:
                    console.print(f"[yellow][ЧАТ от {sender}]:[/yellow] {text}")
                else:
                    print(f"\n{Fore.YELLOW}[ЧАТ от {sender}]: {text}")
            elif message.type == MessageType.GAME_INVITE:
                self.handle_game_invite(message)
            elif message.type == MessageType.GAME_ACCEPT:
                game_id = message.data.get("game_id")
                if game_id in self.game_sessions:
                    self.start_network_game(game_id)
            elif message.type == MessageType.GAME_DECLINE:
                game_id = message.data.get("game_id")
                dynamic_border("Игрок отклонил приглашение", Fore.YELLOW)
                if game_id in self.game_sessions:
                    del self.game_sessions[game_id]
            elif message.type == MessageType.GAME_START:
                self.handle_game_start(message)
            elif message.type == MessageType.GAME_MOVE:
                self.handle_game_move(message)
            elif message.type == MessageType.GAME_RESULT:
                self.handle_game_result(message)
            elif message.type == MessageType.TRANSFER:
                self.handle_transfer(message)
            elif message.type == MessageType.ERROR:
                error = message.data.get("error", "Неизвестная ошибка")
                dynamic_border(f"Сетевая ошибка: {error}", Fore.RED)
            elif message.type == MessageType.DISCONNECT:
                dynamic_border("Игрок отключился", Fore.YELLOW)
                self.disconnect()
            elif message.type == MessageType.SYNC_REQUEST:
                self.handle_sync_request(message)
            elif message.type == MessageType.SYNC_RESPONSE:
                self.handle_sync_response(message)
        except Exception as e:
            pass

    def handle_game_invite(self, message: NetworkMessage):
        game_type = GameType(message.data.get("game"))
        bet = message.data.get("bet", 0)
        game_id = message.data.get("game_id")
        sender = message.data.get("sender", "Неизвестно")
        
        border_content = (
            f"{Fore.MAGENTA}Получено игровое приглашение!\n"
            f"От: {sender}\n"
            f"Игра: {game_type.value}\n"
            f"Ставка: {bet} {CURRENCY}\n"
            f"ID игры: {game_id}\n"
            f"Введите 'live accept {game_id}' для принятия"
        )
        dynamic_border(border_content, Fore.MAGENTA)

    def handle_game_start(self, message: NetworkMessage):
        game_id = message.data.get("game_id")
        game_type = GameType(message.data.get("game_type"))
        bet = message.data.get("bet", 0)
        
        if not self.casino.current_user:
            self.send_message(NetworkMessage(MessageType.ERROR, {"error": "Пользователь не выбран"}))
            return
        
        if self.casino.current_user.crypto_balance.get("EXTRACT", 0) < bet:
            self.send_message(NetworkMessage(MessageType.ERROR, {"error": "Недостаточно средств"}))
            return
        
        self.casino.current_user.crypto_balance["EXTRACT"] -= bet
        self.casino.current_user.live_games_played += 1
        
        game_state = GameState(
            game_id=game_id,
            game_type=game_type,
            bet=bet,
            player1=self.peer_username or "Неизвестно",
            player2=self.casino.current_user.username,
            current_player=self.peer_username or "Неизвестно"
        )
        self.game_sessions[game_id] = game_state
        
        border_content = (
            f"{Fore.GREEN}Игра началась!\n"
            f"Игра: {game_type.value}\n"
            f"Ставка: {bet} {CURRENCY}\n"
            f"Оппонент: {self.peer_username}"
        )
        dynamic_border(border_content, Fore.GREEN)

    def handle_game_move(self, message: NetworkMessage):
        game_id = message.data.get("game_id")
        move_data = message.data.get("data", {})
        
        if game_id not in self.game_sessions:
            return
        
        game_state = self.game_sessions[game_id]
        game_state.moves.append(move_data)
        
        if game_state.game_type == GameType.DICE:
            self.process_dice_move(game_state, move_data)
        elif game_state.game_type == GameType.BATTLE:
            self.process_battle_move(game_state, move_data)
        elif game_state.game_type == GameType.HIGHLOW:
            self.process_highlow_move(game_state, move_data)
        elif game_state.game_type == GameType.ROULETTE:
            self.process_roulette_move(game_state, move_data)
        elif game_state.game_type == GameType.BLACKJACK:
            self.process_blackjack_move(game_state, move_data)
        elif game_state.game_type == GameType.SLOTS:
            self.process_slots_move(game_state, move_data)

    def handle_game_result(self, message: NetworkMessage):
        result = message.data.get("result")
        win_amount = message.data.get("win_amount", 0)
        game_id = message.data.get("game_id")
        
        if result == "win":
            border_content = (
                f"{Fore.GREEN}Поздравляем! Вы выиграли!\n"
                f"Приз: +{win_amount} {CURRENCY}"
            )
            dynamic_border(border_content, Fore.GREEN)
            if self.casino.current_user:
                self.casino.current_user.crypto_balance["EXTRACT"] += win_amount
                self.casino.current_user.add_xp(win_amount * 0.2)
                if self.casino.current_user.live_games_played >= 10:
                    self.casino.achievements.unlock_achievement(
                        self.casino.current_user.username, 
                        "live_player", 
                        self.casino.current_user
                    )
        elif result == "lose":
            dynamic_border("Вы проиграли", Fore.RED)
        elif result == "draw":
            dynamic_border("Ничья - Ставка возвращена", Fore.YELLOW)
            if self.casino.current_user and game_id in self.game_sessions:
                self.casino.current_user.crypto_balance["EXTRACT"] += self.game_sessions[game_id].bet
        
        if game_id in self.game_sessions:
            del self.game_sessions[game_id]

    def handle_transfer(self, message: NetworkMessage):
        currency = message.data.get("currency", "EXTRACT")
        amount = message.data.get("amount", 0)
        sender = message.data.get("sender", "Неизвестно")
        
        if self.casino.current_user:
            current = self.casino.current_user.crypto_balance.get(currency, 0)
            self.casino.current_user.crypto_balance[currency] = current + amount
            
            border_content = (
                f"{Fore.GREEN}Перевод получен!\n"
                f"От: {sender}\n"
                f"Сумма: {amount} {CRYPTO_SYMBOLS.get(currency, currency)}\n"
                f"Новый баланс: {self.casino.current_user.crypto_balance[currency]}"
            )
            dynamic_border(border_content, Fore.GREEN)

    def handle_sync_request(self, message: NetworkMessage):
        if self.casino.current_user:
            sync_data = {
                "username": self.casino.current_user.username,
                "balance": self.casino.current_user.crypto_balance.get("EXTRACT", 0),
                "level": self.casino.current_user.level,
                "timestamp": time.time()
            }
            self.send_message(NetworkMessage(MessageType.SYNC_RESPONSE, sync_data))

    def handle_sync_response(self, message: NetworkMessage):
        username = message.data.get("username", "Неизвестно")
        balance = message.data.get("balance", 0)
        level = message.data.get("level", 1)
        
        border_content = (
            f"{Fore.CYAN}Информация синхронизирована\n"
            f"Имя: {username}\n"
            f"Баланс: {balance} {CURRENCY}\n"
            f"Уровень: {level}"
        )
        dynamic_border(border_content, Fore.CYAN)

    def ping_loop(self):
        while self.running and self.connection:
            try:
                self.last_ping_time = time.time()
                self.send_message(NetworkMessage(MessageType.PING, {"request": True}))
                time.sleep(2)
            except:
                break

    def create_game_session(self, game_type: GameType, bet: float) -> str:
        game_id = str(uuid.uuid4())
        if not self.casino.current_user:
            player1 = "Хост"
        else:
            player1 = self.casino.current_user.username
        
        game_state = GameState(
            game_id=game_id,
            game_type=game_type,
            bet=bet,
            player1=player1,
            player2=self.peer_username or "Ожидание",
            current_player=player1
        )
        self.game_sessions[game_id] = game_state
        return game_id

    def invite_to_game(self, game_type: GameType, bet: float):
        if not self.connection or not self.peer_username:
            dynamic_border("Нет подключения к игроку", Fore.RED)
            return
        
        if not self.casino.current_user:
            dynamic_border("Пользователь не выбран", Fore.RED)
            return
        
        if self.casino.current_user.crypto_balance.get("EXTRACT", 0) < bet:
            dynamic_border("Недостаточно средств", Fore.RED)
            return
        
        game_id = self.create_game_session(game_type, bet)
        self.send_message(NetworkMessage(
            MessageType.GAME_INVITE,
            {
                "game": game_type.value,
                "bet": bet,
                "game_id": game_id,
                "sender": self.casino.current_user.username
            }
        ))
        
        border_content = (
            f"{Fore.CYAN}Приглашение отправлено\n"
            f"Игра: {game_type.value}\n"
            f"Ставка: {bet} {CURRENCY}\n"
            f"ID игры: {game_id}"
        )
        dynamic_border(border_content, Fore.CYAN)

    def accept_game_invite(self, game_id: str):
        if game_id not in self.game_sessions:
            dynamic_border("Игра не найдена", Fore.RED)
            return
        
        if not self.casino.current_user:
            dynamic_border("Пользователь не выбран", Fore.RED)
            return
        
        game_state = self.game_sessions[game_id]
        if self.casino.current_user.crypto_balance.get("EXTRACT", 0) < game_state.bet:
            dynamic_border("Недостаточно средств", Fore.RED)
            return
        
        self.casino.current_user.crypto_balance["EXTRACT"] -= game_state.bet
        self.casino.current_user.live_games_played += 1
        
        self.send_message(NetworkMessage(
            MessageType.GAME_ACCEPT,
            {"game_id": game_id}
        ))
        self.start_network_game(game_id)

    def start_network_game(self, game_id: str):
        if game_id not in self.game_sessions:
            dynamic_border("Сессия игры не найдена", Fore.RED)
            return
        
        game_state = self.game_sessions[game_id]
        if not self.casino.current_user:
            dynamic_border("Пользователь не выбран", Fore.RED)
            return
        
        self.send_message(NetworkMessage(
            MessageType.GAME_START,
            {
                "game_id": game_id,
                "game_type": game_state.game_type.value,
                "bet": game_state.bet
            }
        ))
        
        border_content = (
            f"{Fore.GREEN}Игра началась!\n"
            f"Игра: {game_state.game_type.value}\n"
            f"Ставка: {game_state.bet} {CURRENCY}\n"
            f"Оппонент: {game_state.player1 if game_state.player2 == self.casino.current_user.username else game_state.player2}"
        )
        dynamic_border(border_content, Fore.GREEN)
        self.play_network_game(game_state)

    def play_network_game(self, game_state: GameState):
        game_handlers = {
            GameType.DICE: self.play_network_dice,
            GameType.BATTLE: self.play_network_battle,
            GameType.HIGHLOW: self.play_network_highlow,
            GameType.ROULETTE: self.play_network_roulette,
            GameType.BLACKJACK: self.play_network_blackjack,
            GameType.SLOTS: self.play_network_slots
        }
        
        handler = game_handlers.get(game_state.game_type)
        if handler:
            handler(game_state)
        else:
            dynamic_border("Неизвестный тип игры", Fore.RED)

    def play_network_dice(self, game_state: GameState):
        dynamic_border("Сетевые кости", Fore.YELLOW)
        player_roll = sum(random.randint(1, 6) for _ in range(3))
        print(f"{Fore.CYAN}Ваш бросок: {player_roll}")
        
        self.send_message(NetworkMessage(
            MessageType.GAME_MOVE,
            {
                "game_id": game_state.game_id,
                "data": {"roll": player_roll, "player": self.casino.current_user.username}
            }
        ))
        
        print(f"{Fore.YELLOW}Ожидание броска оппонента...")
        timeout = time.time() + 30
        while time.time() < timeout:
            if len(game_state.moves) >= 2:
                break
            time.sleep(0.1)
        
        if len(game_state.moves) >= 2:
            self.process_dice_result(game_state)

    def process_dice_move(self, game_state: GameState, move_data: Dict):
        roll = move_data.get("roll", 0)
        player = move_data.get("player", "Неизвестно")
        print(f"{Fore.MAGENTA}Бросок {player}: {roll}")
        if len(game_state.moves) >= 2:
            self.process_dice_result(game_state)

    def process_dice_result(self, game_state: GameState):
        if len(game_state.moves) < 2:
            return
        
        player1_roll = game_state.moves[0].get("roll", 0)
        player2_roll = game_state.moves[1].get("roll", 0)
        
        print(f"\n{Fore.CYAN}Финальный результат:")
        print(f"Игрок 1: {player1_roll}")
        print(f"Игрок 2: {player2_roll}")
        
        if player1_roll > player2_roll:
            winner = game_state.player1
            win_amount = game_state.bet * 1.5
        elif player2_roll > player1_roll:
            winner = game_state.player2
            win_amount = game_state.bet * 1.5
        else:
            winner = None
            win_amount = game_state.bet
        
        if winner:
            result = "win" if winner == self.casino.current_user.username else "lose"
            border_content = (
                f"{Fore.GREEN if result == 'win' else Fore.RED}"
                f"{'Вы выиграли!' if result == 'win' else 'Вы проиграли'}\n"
                f"Победитель: {winner}\n"
                f"Приз: {win_amount} {CURRENCY}"
            )
            dynamic_border(border_content, Fore.GREEN if result == 'win' else Fore.RED)
            self.send_message(NetworkMessage(
                MessageType.GAME_RESULT,
                {
                    "game_id": game_state.game_id,
                    "result": result,
                    "win_amount": win_amount if result == "win" else 0
                }
            ))
        else:
            dynamic_border("Ничья! Ставка возвращена", Fore.YELLOW)
            self.send_message(NetworkMessage(
                MessageType.GAME_RESULT,
                {
                    "game_id": game_state.game_id,
                    "result": "draw"
                }
            ))

    def play_network_battle(self, game_state: GameState):
        dynamic_border("Сетевая битва", Fore.RED)
        base_attack = random.randint(50, 150)
        level_bonus = self.casino.current_user.level * 2 if self.casino.current_user else 0
        player_attack = base_attack + level_bonus
        
        print(f"{Fore.CYAN}Ваша сила атаки: {player_attack}")
        self.send_message(NetworkMessage(
            MessageType.GAME_MOVE,
            {
                "game_id": game_state.game_id,
                "data": {"attack": player_attack, "player": self.casino.current_user.username}
            }
        ))
        
        print(f"{Fore.YELLOW}Ожидание атаки оппонента...")
        timeout = time.time() + 30
        while time.time() < timeout:
            if len(game_state.moves) >= 2:
                break
            time.sleep(0.1)
        
        if len(game_state.moves) >= 2:
            self.process_battle_result(game_state)

    def process_battle_move(self, game_state: GameState, move_data: Dict):
        attack = move_data.get("attack", 0)
        player = move_data.get("player", "Неизвестно")
        print(f"{Fore.MAGENTA}Атака {player}: {attack}")
        if len(game_state.moves) >= 2:
            self.process_battle_result(game_state)

    def process_battle_result(self, game_state: GameState):
        if len(game_state.moves) < 2:
            return
        
        player1_attack = game_state.moves[0].get("attack", 0)
        player2_attack = game_state.moves[1].get("attack", 0)
        
        print(f"\n{Fore.CYAN}Результат битвы:")
        print(f"Атака игрока 1: {player1_attack}")
        print(f"Атака игрока 2: {player2_attack}")
        
        if player1_attack > player2_attack:
            winner = game_state.player1
            win_amount = game_state.bet * 3
        elif player2_attack > player1_attack:
            winner = game_state.player2
            win_amount = game_state.bet * 3
        else:
            winner = None
            win_amount = game_state.bet
        
        if winner:
            result = "win" if winner == self.casino.current_user.username else "lose"
            border_content = (
                f"{Fore.GREEN if result == 'win' else Fore.RED}"
                f"{'Победа!' if result == 'win' else 'Поражение'}\n"
                f"Победитель: {winner}\n"
                f"Приз: {win_amount} {CURRENCY}"
            )
            dynamic_border(border_content, Fore.GREEN if result == 'win' else Fore.RED)
            self.send_message(NetworkMessage(
                MessageType.GAME_RESULT,
                {
                    "game_id": game_state.game_id,
                    "result": result,
                    "win_amount": win_amount if result == "win" else 0
                }
            ))
        else:
            dynamic_border("Ничья! Ставка возвращена", Fore.YELLOW)
            self.send_message(NetworkMessage(
                MessageType.GAME_RESULT,
                {
                    "game_id": game_state.game_id,
                    "result": "draw"
                }
            ))

    def play_network_highlow(self, game_state: GameState):
        dynamic_border("Сеть Выше-Ниже", Fore.MAGENTA)
        current_number = random.randint(1, 200)
        print(f"{Fore.CYAN}Текущее число: {current_number}")
        
        while True:
            choice = input(f"{Fore.YELLOW}Следующее будет выше (в) или ниже (н)? ").lower()
            if choice in ['в', 'н']:
                break
            print(f"{Fore.RED}Неверный выбор. Введите 'в' или 'н'")
        
        next_number = random.randint(1, 200)
        self.send_message(NetworkMessage(
            MessageType.GAME_MOVE,
            {
                "game_id": game_state.game_id,
                "data": {
                    "current": current_number,
                    "choice": choice,
                    "next": next_number,
                    "player": self.casino.current_user.username
                }
            }
        ))
        
        print(f"{Fore.CYAN}Ваше следующее число: {next_number}")
        print(f"{Fore.YELLOW}Ожидание оппонента...")
        timeout = time.time() + 30
        while time.time() < timeout:
            if len(game_state.moves) >= 2:
                break
            time.sleep(0.1)
        
        if len(game_state.moves) >= 2:
            self.process_highlow_result(game_state)

    def process_highlow_move(self, game_state: GameState, move_data: Dict):
        current = move_data.get("current", 0)
        choice = move_data.get("choice", "")
        next_num = move_data.get("next", 0)
        player = move_data.get("player", "Неизвестно")
        
        print(f"\n{Fore.MAGENTA}Ход {player}:")
        print(f"Текущее: {current}, Выбор: {choice}, Следующее: {next_num}")
        if len(game_state.moves) >= 2:
            self.process_highlow_result(game_state)

    def process_highlow_result(self, game_state: GameState):
        if len(game_state.moves) < 2:
            return
        
        scores = []
        for move in game_state.moves:
            current = move.get("current", 0)
            choice = move.get("choice", "")
            next_num = move.get("next", 0)
            player = move.get("player", "Неизвестно")
            won = (choice == 'в' and next_num > current) or (choice == 'н' and next_num < current)
            scores.append({"player": player, "won": won, "next": next_num})
        
        print(f"\n{Fore.CYAN}Результаты игры:")
        for score in scores:
            status = "Выиграл" if score["won"] else "Проиграл"
            print(f"{score['player']}: {status} (Число: {score['next']})")
        
        player1_won = scores[0]["won"]
        player2_won = scores[1]["won"]
        
        if player1_won and not player2_won:
            winner = game_state.player1
            win_amount = game_state.bet * 2
        elif player2_won and not player1_won:
            winner = game_state.player2
            win_amount = game_state.bet * 2
        else:
            winner = None
            win_amount = game_state.bet
        
        if winner:
            result = "win" if winner == self.casino.current_user.username else "lose"
            border_content = (
                f"{Fore.GREEN if result == 'win' else Fore.RED}"
                f"{'Вы выиграли!' if result == 'win' else 'Вы проиграли'}\n"
                f"Победитель: {winner}\n"
                f"Приз: {win_amount} {CURRENCY}"
            )
            dynamic_border(border_content, Fore.GREEN if result == 'win' else Fore.RED)
            self.send_message(NetworkMessage(
                MessageType.GAME_RESULT,
                {
                    "game_id": game_state.game_id,
                    "result": result,
                    "win_amount": win_amount if result == "win" else 0
                }
            ))
        else:
            dynamic_border("Ничья! Ставка возвращена", Fore.YELLOW)
            self.send_message(NetworkMessage(
                MessageType.GAME_RESULT,
                {
                    "game_id": game_state.game_id,
                    "result": "draw"
                }
            ))

    def play_network_roulette(self, game_state: GameState):
        dynamic_border("Сетевая рулетка", Fore.RED)
        print(f"{Fore.YELLOW}Выберите ставку:")
        print(f"{Fore.RED}1. Красное (x2)")
        print(f"{Fore.WHITE}2. Черное (x2)")
        print(f"{Fore.GREEN}3. Зеленое (x14)")
        
        while True:
            try:
                choice = int(input("Ваш выбор (1-3): "))
                if choice in [1, 2, 3]:
                    break
                print(f"{Fore.RED}Неверный выбор. Введите 1, 2 или 3")
            except ValueError:
                print(f"{Fore.RED}Неверный ввод. Введите число")
        
        result = random.randint(0, 36)
        if result == 0:
            color = 3
        elif result % 2 == 0:
            color = 1
        else:
            color = 2
        
        self.send_message(NetworkMessage(
            MessageType.GAME_MOVE,
            {
                "game_id": game_state.game_id,
                "data": {
                    "choice": choice,
                    "result": result,
                    "color": color,
                    "player": self.casino.current_user.username
                }
            }
        ))
        
        print(f"{Fore.CYAN}Ваш результат: {result}")
        if color == 1:
            print(f"{Fore.RED}Красное!")
        elif color == 2:
            print(f"{Fore.WHITE}Черное!")
        else:
            print(f"{Fore.GREEN}Зеленое!")
        
        print(f"{Fore.YELLOW}Ожидание оппонента...")
        timeout = time.time() + 30
        while time.time() < timeout:
            if len(game_state.moves) >= 2:
                break
            time.sleep(0.1)
        
        if len(game_state.moves) >= 2:
            self.process_roulette_result(game_state)

    def process_roulette_move(self, game_state: GameState, move_data: Dict):
        choice = move_data.get("choice", 0)
        result = move_data.get("result", 0)
        color = move_data.get("color", 0)
        player = move_data.get("player", "Неизвестно")
        
        print(f"\n{Fore.MAGENTA}Спин {player}:")
        print(f"Выбор: {choice}, Результат: {result}")
        if color == 1:
            print(f"{Fore.RED}Красное!")
        elif color == 2:
            print(f"{Fore.WHITE}Черное!")
        else:
            print(f"{Fore.GREEN}Зеленое!")
        
        if len(game_state.moves) >= 2:
            self.process_roulette_result(game_state)

    def process_roulette_result(self, game_state: GameState):
        if len(game_state.moves) < 2:
            return
        
        results = []
        for move in game_state.moves:
            choice = move.get("choice", 0)
            color = move.get("color", 0)
            player = move.get("player", "Неизвестно")
            won = choice == color
            multiplier = 14 if color == 3 else 2
            win_amount = game_state.bet * multiplier if won else 0
            results.append({
                "player": player,
                "won": won,
                "win_amount": win_amount
            })
        
        print(f"\n{Fore.CYAN}Результаты игры:")
        for res in results:
            status = "Выиграл" if res["won"] else "Проиграл"
            amount = f"+{res['win_amount']}" if res["won"] else "0"
            print(f"{res['player']}: {status} ({amount} {CURRENCY})")
        
        player1_won = results[0]["won"]
        player2_won = results[1]["won"]
        
        if player1_won and not player2_won:
            winner = game_state.player1
            win_amount = results[0]["win_amount"]
        elif player2_won and not player1_won:
            winner = game_state.player2
            win_amount = results[1]["win_amount"]
        else:
            winner = None
            win_amount = game_state.bet
        
        if winner:
            result = "win" if winner == self.casino.current_user.username else "lose"
            border_content = (
                f"{Fore.GREEN if result == 'win' else Fore.RED}"
                f"{'Вы выиграли!' if result == 'win' else 'Вы проиграли'}\n"
                f"Победитель: {winner}\n"
                f"Приз: {win_amount} {CURRENCY}"
            )
            dynamic_border(border_content, Fore.GREEN if result == 'win' else Fore.RED)
            self.send_message(NetworkMessage(
                MessageType.GAME_RESULT,
                {
                    "game_id": game_state.game_id,
                    "result": result,
                    "win_amount": win_amount if result == "win" else 0
                }
            ))
        else:
            dynamic_border("Ничья! Ставка возвращена", Fore.YELLOW)
            self.send_message(NetworkMessage(
                MessageType.GAME_RESULT,
                {
                    "game_id": game_state.game_id,
                    "result": "draw"
                }
            ))

    def play_network_blackjack(self, game_state: GameState):
        dynamic_border("Сетевой блэкджек", Fore.BLUE)
        deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4
        random.shuffle(deck)
        
        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]
        
        print(f"{Fore.CYAN}Ваши карты: {player_hand} (Сумма: {sum(player_hand)})")
        print(f"{Fore.RED}Карта дилера: {dealer_hand[0]}")
        
        while sum(player_hand) < 21:
            action = input(f"{Fore.YELLOW}Еще карту или хватит? (е/х): ").lower()
            if action == 'е':
                player_hand.append(deck.pop())
                if sum(player_hand) > 21 and 11 in player_hand:
                    player_hand[player_hand.index(11)] = 1
                print(f"{Fore.CYAN}Ваши карты: {player_hand} (Сумма: {sum(player_hand)})")
                if sum(player_hand) > 21:
                    print(f"{Fore.RED}Перебор!")
                    break
            else:
                break
        
        player_sum = sum(player_hand)
        while sum(dealer_hand) < 17:
            dealer_hand.append(deck.pop())
            if sum(dealer_hand) > 21 and 11 in dealer_hand:
                dealer_hand[dealer_hand.index(11)] = 1
        
        dealer_sum = sum(dealer_hand)
        print(f"{Fore.RED}Карты дилера: {dealer_hand} (Сумма: {dealer_sum})")
        
        self.send_message(NetworkMessage(
            MessageType.GAME_MOVE,
            {
                "game_id": game_state.game_id,
                "data": {
                    "player_hand": player_hand,
                    "player_sum": player_sum,
                    "dealer_hand": dealer_hand,
                    "dealer_sum": dealer_sum,
                    "player": self.casino.current_user.username
                }
            }
        ))
        
        print(f"{Fore.YELLOW}Ожидание оппонента...")
        timeout = time.time() + 30
        while time.time() < timeout:
            if len(game_state.moves) >= 2:
                break
            time.sleep(0.1)
        
        if len(game_state.moves) >= 2:
            self.process_blackjack_result(game_state)

    def process_blackjack_move(self, game_state: GameState, move_data: Dict):
        player_hand = move_data.get("player_hand", [])
        player_sum = move_data.get("player_sum", 0)
        dealer_hand = move_data.get("dealer_hand", [])
        dealer_sum = move_data.get("dealer_sum", 0)
        player = move_data.get("player", "Неизвестно")
        
        print(f"\n{Fore.MAGENTA}Игра {player}:")
        print(f"Карты игрока: {player_hand} (Сумма: {player_sum})")
        print(f"Карты дилера: {dealer_hand} (Сумма: {dealer_sum})")
        if len(game_state.moves) >= 2:
            self.process_blackjack_result(game_state)

    def process_blackjack_result(self, game_state: GameState):
        if len(game_state.moves) < 2:
            return
        
        results = []
        for move in game_state.moves:
            player_sum = move.get("player_sum", 0)
            dealer_sum = move.get("dealer_sum", 0)
            player = move.get("player", "Неизвестно")
            
            if player_sum > 21:
                won = False
            elif dealer_sum > 21:
                won = True
            elif player_sum > dealer_sum:
                won = True
            elif player_sum < dealer_sum:
                won = False
            else:
                won = None
            
            win_amount = game_state.bet * 2 if won else 0
            results.append({
                "player": player,
                "won": won,
                "player_sum": player_sum,
                "dealer_sum": dealer_sum,
                "win_amount": win_amount
            })
        
        print(f"\n{Fore.CYAN}Результаты игры:")
        for res in results:
            if res["won"] is None:
                status = "Ничья"
            else:
                status = "Выиграл" if res["won"] else "Проиграл"
            print(f"{res['player']}: {status} (Игрок: {res['player_sum']}, Дилер: {res['dealer_sum']})")
        
        player1_result = results[0]["won"]
        player2_result = results[1]["won"]
        
        if player1_result and not player2_result:
            winner = game_state.player1
            win_amount = results[0]["win_amount"]
        elif player2_result and not player1_result:
            winner = game_state.player2
            win_amount = results[1]["win_amount"]
        else:
            winner = None
            win_amount = game_state.bet
        
        if winner:
            result = "win" if winner == self.casino.current_user.username else "lose"
            border_content = (
                f"{Fore.GREEN if result == 'win' else Fore.RED}"
                f"{'Вы выиграли!' if result == 'win' else 'Вы проиграли'}\n"
                f"Победитель: {winner}\n"
                f"Приз: {win_amount} {CURRENCY}"
            )
            dynamic_border(border_content, Fore.GREEN if result == 'win' else Fore.RED)
            self.send_message(NetworkMessage(
                MessageType.GAME_RESULT,
                {
                    "game_id": game_state.game_id,
                    "result": result,
                    "win_amount": win_amount if result == "win" else 0
                }
            ))
        else:
            dynamic_border("Ничья! Ставка возвращена", Fore.YELLOW)
            self.send_message(NetworkMessage(
                MessageType.GAME_RESULT,
                {
                    "game_id": game_state.game_id,
                    "result": "draw"
                }
            ))

    def play_network_slots(self, game_state: GameState):
        dynamic_border("Сетевые слоты", Fore.CYAN)
        symbols = [("ВИШНЯ", 0.3), ("АПЕЛЬСИН", 0.25), ("ЛИМОН", 0.2), 
                  ("КОЛОКОЛ", 0.15), ("ЗВЕЗДА", 0.07), ("АЛМАЗ", 0.03)]
        
        if RICH_AVAILABLE:
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                task = progress.add_task("Крутим...", total=10)
                for i in range(10):
                    temp = random.choices([s[0] for s in symbols], weights=[s[1] for s in symbols], k=3)
                    progress.update(task, advance=1)
                    time.sleep(0.1)
        else:
            print("Крутим...")
            for _ in range(5):
                temp = random.choices([s[0] for s in symbols], weights=[s[1] for s in symbols], k=3)
                print("\r" + " | ".join(temp[:1]), end='', flush=True)
                time.sleep(0.1)
            print()
        
        results = random.choices([s[0] for s in symbols], weights=[s[1] for s in symbols], k=3)
        print("Результат: " + " | ".join(results))
        
        win = 0
        if results.count("АЛМАЗ") == 3:
            win = game_state.bet * 50
        elif results[0] == results[1] == results[2]:
            multiplier = 10
            if results[0] == "КОЛОКОЛ":
                multiplier = 15
            elif results[0] == "ЗВЕЗДА":
                multiplier = 20
            win = game_state.bet * multiplier
        elif results[0] == results[1]:
            win = game_state.bet * 3
            if results[0] == "АЛМАЗ":
                win = game_state.bet * 10
        
        self.send_message(NetworkMessage(
            MessageType.GAME_MOVE,
            {
                "game_id": game_state.game_id,
                "data": {
                    "results": results,
                    "win": win,
                    "player": self.casino.current_user.username
                }
            }
        ))
        
        print(f"{Fore.YELLOW}Ожидание оппонента...")
        timeout = time.time() + 30
        while time.time() < timeout:
            if len(game_state.moves) >= 2:
                break
            time.sleep(0.1)
        
        if len(game_state.moves) >= 2:
            self.process_slots_result(game_state)

    def process_slots_move(self, game_state: GameState, move_data: Dict):
        results = move_data.get("results", [])
        win = move_data.get("win", 0)
        player = move_data.get("player", "Неизвестно")
        
        print(f"\n{Fore.MAGENTA}Спин {player}:")
        print("Результат: " + " | ".join(results))
        if win > 0:
            print(f"{Fore.GREEN}Выигрыш: {win} {CURRENCY}")
        else:
            print(f"{Fore.RED}Нет выигрыша")
        
        if len(game_state.moves) >= 2:
            self.process_slots_result(game_state)

    def process_slots_result(self, game_state: GameState):
        if len(game_state.moves) < 2:
            return
        
        results = []
        for move in game_state.moves:
            win = move.get("win", 0)
            player = move.get("player", "Неизвестно")
            results.append({
                "player": player,
                "win": win
            })
        
        print(f"\n{Fore.CYAN}Результаты игры:")
        for res in results:
            status = "Выиграл" if res["win"] > 0 else "Проиграл"
            amount = f"+{res['win']}" if res["win"] > 0 else "0"
            print(f"{res['player']}: {status} ({amount} {CURRENCY})")
        
        player1_win = results[0]["win"]
        player2_win = results[1]["win"]
        
        if player1_win > player2_win:
            winner = game_state.player1
            win_amount = player1_win
        elif player2_win > player1_win:
            winner = game_state.player2
            win_amount = player2_win
        else:
            winner = None
            win_amount = game_state.bet
        
        if winner:
            result = "win" if winner == self.casino.current_user.username else "lose"
            border_content = (
                f"{Fore.GREEN if result == 'win' else Fore.RED}"
                f"{'Вы выиграли!' if result == 'win' else 'Вы проиграли'}\n"
                f"Победитель: {winner}\n"
                f"Приз: {win_amount} {CURRENCY}"
            )
            dynamic_border(border_content, Fore.GREEN if result == 'win' else Fore.RED)
            self.send_message(NetworkMessage(
                MessageType.GAME_RESULT,
                {
                    "game_id": game_state.game_id,
                    "result": result,
                    "win_amount": win_amount if result == "win" else 0
                }
            ))
        else:
            dynamic_border("Ничья! Ставка возвращена", Fore.YELLOW)
            self.send_message(NetworkMessage(
                MessageType.GAME_RESULT,
                {
                    "game_id": game_state.game_id,
                    "result": "draw"
                }
            ))

    def send_chat_message(self, text: str) -> bool:
        if not self.connection or not self.running:
            return False
        return self.send_message(NetworkMessage(
            MessageType.CHAT,
            {
                "text": text,
                "sender": self.casino.current_user.username if self.casino.current_user else "Вы"
            }
        ))

    def send_transfer(self, currency: str, amount: float) -> bool:
        if not self.connection or not self.casino.current_user:
            return False
        
        if self.casino.current_user.crypto_balance.get(currency, 0) < amount:
            dynamic_border("Недостаточно средств", Fore.RED)
            return False
        
        self.casino.current_user.crypto_balance[currency] -= amount
        return self.send_message(NetworkMessage(
            MessageType.TRANSFER,
            {
                "currency": currency,
                "amount": amount,
                "sender": self.casino.current_user.username
            }
        ))

    def disconnect(self):
        self.running = False
        self.is_host = False
        self.is_connected = False
        
        if self.connection:
            try:
                self.send_message(NetworkMessage(MessageType.DISCONNECT, {}))
                self.connection.close()
            except:
                pass
            self.connection = None
        
        for conn, addr in self.connections:
            try:
                conn.close()
            except:
                pass
        self.connections.clear()
        
        if self.server:
            try:
                self.server.close()
            except:
                pass
            self.server = None
        
        if self.client:
            try:
                self.client.close()
            except:
                pass
            self.client = None
        
        self.peer_username = None
        self.peer_address = None
        self.ping = 0
        self.game_sessions.clear()
        dynamic_border("Отключено от сети", Fore.YELLOW)

class CryptoMarket:
    def __init__(self):
        self.rates = self.generate_rates()
        self.history = deque(maxlen=100)
        self.last_update = time.time()
        self.update_interval = 60

    def generate_rates(self) -> Dict[str, float]:
        return {
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
        current_time = time.time()
        if current_time - self.last_update < self.update_interval:
            return
        
        self.history.append(self.rates.copy())
        for coin in self.rates:
            if coin != "EXTRACT":
                change = random.uniform(-0.07, 0.07)
                self.rates[coin] = max(0.01, self.rates[coin] * (1 + change))
        
        self.last_update = current_time
        self.save_rates()

    def get_rate(self, coin: str) -> float:
        return self.rates.get(coin, 0.0)

    def save_rates(self):
        try:
            os.makedirs(os.path.dirname(CS_LOG_PATH), exist_ok=True)
            with open(CS_LOG_PATH, "w") as f:
                json.dump(self.rates, f, indent=4)
        except Exception as e:
            pass

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
                    "author": "Команда Extract",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "pinned": True
                }]
                with open(FORUM_PATH, 'w', encoding='utf-8') as f:
                    json.dump(default_messages, f, indent=4)
            with open(FORUM_PATH, 'r', encoding='utf-8') as f:
                self.messages = json.load(f)
        except Exception as e:
            self.messages = []

    def show_forum(self, limit: int = 5):
        if RICH_AVAILABLE:
            console.print(Panel.fit("[bold cyan]ФОРУМ EXTRACT[/bold cyan]", border_style="cyan"))
            pinned = [m for m in self.messages if m.get("pinned", False)]
            regular = [m for m in self.messages if not m.get("pinned", False)]
            messages = (pinned + regular)[:limit]
            
            for msg in messages:
                pin = "📌 " if msg.get("pinned", False) else ""
                console.print(Panel(
                    f"[bold yellow]{pin}{msg['title']}[/bold yellow]\n"
                    f"[italic white]Автор: {msg.get('author', 'Команда Extract')} | Дата: {msg.get('date', 'N/A')}[/italic white]\n\n"
                    f"{msg['content']}",
                    border_style="green" if msg.get("pinned") else "blue"
                ))
            return
        
        pinned = [m for m in self.messages if m.get("pinned", False)]
        regular = [m for m in self.messages if not m.get("pinned", False)]
        messages = (pinned + regular)[:limit]
        
        if not messages:
            dynamic_border("На форуме пока нет сообщений", Fore.YELLOW)
            return
        
        content = [
            f"{Fore.RED}╔{'═'*50}╗",
            f"║{'ФОРУМ EXTRACT'.center(50)}║",
            f"╠{'═'*50}╣"
        ]
        
        for msg in messages:
            pin = "ЗАКРЕПЛЕНО " if msg.get("pinned", False) else ""
            content.append(f"║ {pin}{Fore.YELLOW}{msg['title'].ljust(48)}║")
            content.append(f"║ {Fore.WHITE}Автор: {msg.get('author', 'Команда Extract')} | Дата: {msg.get('date', 'N/A')} ║")
            content.append(f"╠{'-'*50}╣")
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
            if os.path.exists(ACHIEVEMENTS_PATH):
                with open(ACHIEVEMENTS_PATH, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}

    def save_achievements(self):
        try:
            os.makedirs(os.path.dirname(ACHIEVEMENTS_PATH), exist_ok=True)
            with open(ACHIEVEMENTS_PATH, 'w') as f:
                json.dump(self.user_achievements, f, indent=4)
        except Exception as e:
            pass

    def unlock_achievement(self, username: str, achievement_key: str, user):
        if username not in self.user_achievements:
            self.user_achievements[username] = []
        
        if achievement_key not in self.user_achievements[username]:
            self.user_achievements[username].append(achievement_key)
            user.add_xp(self.achievements[achievement_key]["xp_reward"])
            
            border_content = (
                f"{Fore.GREEN}Новое достижение!\n"
                f"{self.achievements[achievement_key]['name']}\n"
                f"{self.achievements[achievement_key]['description']}\n"
                f"+{self.achievements[achievement_key]['xp_reward']} опыта"
            )
            dynamic_border(border_content, Fore.YELLOW)
            self.save_achievements()

    def show_achievements(self, username: str):
        user_achs = self.user_achievements.get(username, [])
        
        if RICH_AVAILABLE:
            table = Table(title="🏆 Ваши достижения", show_header=True, header_style="bold cyan")
            table.add_column("Достижение", style="yellow")
            table.add_column("Описание", style="green")
            table.add_column("Опыт", justify="right", style="magenta")
            
            for ach_key in user_achs:
                if ach_key in self.achievements:
                    ach = self.achievements[ach_key]
                    table.add_row(ach['name'], ach['description'], f"+{ach['xp_reward']}")
            
            unlocked_count = len(user_achs)
            total_count = len(self.achievements)
            console.print(table)
            console.print(f"[cyan]Прогресс: {unlocked_count}/{total_count} ({unlocked_count/total_count*100:.1f}%)[/cyan]")
            return
        
        content = [f"{Fore.CYAN}Ваши достижения:"]
        for ach_key in user_achs:
            if ach_key in self.achievements:
                ach = self.achievements[ach_key]
                content.append(f"{Fore.GREEN}✓ {ach['name']} - {ach['description']}")
        
        unlocked_count = len(user_achs)
        total_count = len(self.achievements)
        content.append(f"{Fore.YELLOW}Прогресс: {unlocked_count}/{total_count}")
        dynamic_border('\n'.join(content), Fore.BLUE)

class User:
    def __init__(self, username: str):
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
        self.subscription = {"type": "none", "expires_at": None, "autorenew": False}
        self.last_login = None
        self.free_spins = 0
        self.consecutive_wins = 0
        self.achievements = []
        self.live_games_played = 0
        self.consecutive_live_wins = 0

    def to_dict(self) -> Dict[str, Any]:
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
            "consecutive_wins": self.consecutive_wins,
            "achievements": self.achievements,
            "live_games_played": self.live_games_played,
            "consecutive_live_wins": self.consecutive_live_wins
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
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
        user.achievements = data.get("achievements", [])
        user.live_games_played = data.get("live_games_played", 0)
        user.consecutive_live_wins = data.get("consecutive_live_wins", 0)
        return user

    def start_session(self):
        self.session_start = time.time()

    def end_session(self):
        if self.session_start:
            self.play_time += time.time() - self.session_start
            self.session_start = None

    def update_stats(self, won: bool):
        self.games_played += 1
        if won:
            self.wins += 1
            self.consecutive_wins += 1
        else:
            self.losses += 1
            self.consecutive_wins = 0

    def add_transaction(self, action: str, coin: str, amount: float, price: float):
        self.transactions.insert(0, {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
            "coin": coin,
            "amount": round(amount, 4),
            "total": round(price, 2)
        })
        self.transactions = self.transactions[:10]

    def win_loss_ratio(self) -> float:
        if self.games_played == 0:
            return 0.0
        return round(self.wins / self.games_played * 100, 1)

    def add_xp(self, amount: float):
        xp_gain = amount
        if self.subscription["type"] == "eup":
            xp_gain *= 1.2
        elif self.subscription["type"] == "eup_plus":
            xp_gain *= 1.5
        
        self.xp += xp_gain
        while self.xp >= self.required_xp():
            self.xp -= self.required_xp()
            self.level_up()

    def required_xp(self) -> int:
        base = LEVEL_BASE_XP * 5
        return int(base * (self.level ** 2.2 + self.level * 8))

    def level_up(self):
        self.level += 1
        reward = self.level * 1000
        self.crypto_balance["EXTRACT"] += reward
        
        border_content = (
            f"{Fore.GREEN}Повышение уровня! {self.level-1} => {self.level}\n"
            f"+{reward}{CURRENCY} - бонус за уровень!\n"
            f"Следующий уровень: {self.required_xp():.0f} опыта"
        )
        dynamic_border(border_content, Fore.YELLOW)

    def show_level_progress(self) -> str:
        req = self.required_xp()
        progress = min(1.0, self.xp / req)
        gradient = [Fore.RED, Fore.YELLOW, Fore.GREEN]
        color = gradient[min(2, int(progress * 3))]
        bar = "▓" * int(progress * 20) + "░" * (20 - int(progress * 20))
        return f"{Fore.CYAN}{bar} {progress*100:.1f}%"

    def crywall(self):
        if RICH_AVAILABLE:
            table = Table(title="💰 Кошелек", show_header=True, header_style="bold cyan")
            table.add_column("Валюта", style="yellow")
            table.add_column("Символ", style="green")
            table.add_column("Баланс", justify="right", style="magenta")
            
            for coin, amount in self.crypto_balance.items():
                if amount > 0:
                    symbol = CRYPTO_SYMBOLS[coin]
                    table.add_row(coin, symbol, f"{amount:,.4f}")
            
            console.print(table)
            return
        
        content = [f"{Fore.CYAN}╔{'═'*25}╦{'═'*15}╗"]
        for coin, amount in self.crypto_balance.items():
            if amount <= 0:
                continue
            symbol = CRYPTO_SYMBOLS[coin]
            line = f"║ {symbol} {coin.ljust(10)} ║ {amount:>10.4f} ║"
            color = Fore.GREEN if coin == "EXTRACT" else Fore.YELLOW
            content.append(color + line)
        content.append(f"{Fore.CYAN}╚{'═'*25}╩{'═'*15}╝")
        print('\n'.join(content))

    def show_stats(self):
        if RICH_AVAILABLE:
            stats_table = Table(title=f"📊 Статистика {self.username}", show_header=False)
            stats_table.add_column("Параметр", style="cyan")
            stats_table.add_column("Значение", style="yellow")
            
            stats_table.add_row("Баланс", f"{self.crypto_balance['EXTRACT']:,.2f} {CURRENCY}")
            stats_table.add_row("Уровень", str(self.level))
            stats_table.add_row("Опыт", f"{self.xp:.0f}/{self.required_xp():.0f}")
            stats_table.add_row("Процент побед", f"{self.win_loss_ratio()}%")
            stats_table.add_row("Игр сыграно", str(self.games_played))
            stats_table.add_row("Побед/Поражений", f"{self.wins}/{self.losses}")
            stats_table.add_row("Сетевых игр", str(self.live_games_played))
            stats_table.add_row("Побед подряд", str(self.consecutive_wins))
            
            console.print(stats_table)
            return
        
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
            sub_icon = "♦" if self.subscription["type"] == "eup" else "★"
            sub_color = THEME[self.subscription["type"]]
            sub_header = f"{sub_icon} {sub_color}{self.subscription['type'].upper()}"
            sub_details = [
                f"  {sub_color}Истекает: {expiry_date.strftime('%d.%m.%Y')}",
                f"  {sub_color}Дней осталось: {days_left}",
                f"  {sub_color}Бонусы: +{25 if self.subscription['type'] == 'eup_plus' else 10}% к выигрышам, "
                f"{20 if self.subscription['type'] == 'eup_plus' else 10}% страховка"
            ]
        else:
            sub_header = f"○ {Fore.RED}БЕЗ ПОДПИСКИ"
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
            f"  {THEME['stats']}Процент побед: {self.win_loss_ratio()}%           ",
            f"  {THEME['stats']}Игр: {self.games_played}  ТРОФЕЙ {self.wins}  ЧЕРЕП {self.losses}\n",
            f"{THEME['base']} ─────────────────────────────────\n",
            f"  {THEME['stats']}Уровень: {self.level:<2}\n",
            f"  {THEME['stats']}{self.show_level_progress()}\n",
            f"  {Fore.CYAN}Сетевых игр: {self.live_games_played}",
            f"  {Fore.MAGENTA}Побед подряд: {self.consecutive_live_wins}\n"
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

    def has_active_subscription(self) -> bool:
        if self.subscription["type"] == "none":
            return False
        if self.subscription["expires_at"] is None:
            return False
        expiry_date = datetime.strptime(self.subscription["expires_at"], "%Y-%m-%d")
        return datetime.now() <= expiry_date

    def get_styled_username(self) -> str:
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
            dynamic_border(f"{Fore.CYAN}Ежедневный бонус EUP: +1,000,000{CURRENCY}", Fore.CYAN)
        elif self.subscription["type"] == "eup_plus":
            bonus = 10000000
            self.crypto_balance["EXTRACT"] += bonus
            dynamic_border(f"{Fore.YELLOW}Ежедневный бонус EUP+: +2,000,000{CURRENCY}", Fore.YELLOW)
            if random.random() < 0.05:
                btc_bonus = 10.0
                self.crypto_balance["BTC"] = self.crypto_balance.get("BTC", 0) + btc_bonus
                dynamic_border(f"{Fore.GREEN}СУПЕР БОНУС! +10 BTC", Fore.GREEN)

    def check_subscription(self):
        if not self.has_active_subscription():
            self.subscription = {"type": "none", "expires_at": None, "autorenew": False}

    def buy_eup(self, days: int):
        if not 1 <= days <= 365:
            dynamic_border("Ошибка: можно купить от 1 до 365 дней!", Fore.RED)
            return
        
        cost = 10 * days
        border_content = (
            f"{Fore.BLUE}EUP базовая -------------------- Базовая\n"
            f"{Fore.CYAN}Подтвердите покупку EUP на {days} дней\n"
            f"Стоимость: {cost} BTC\n"
            f"Ваш баланс BTC: {self.crypto_balance.get('BTC', 0):.8f} BTC\n"
            f"{Fore.YELLOW}Введите 'да' для оплаты:"
        )
        dynamic_border(border_content, Fore.CYAN)
        confirm = input(">>> ").lower()
        
        if confirm == "да":
            if self.crypto_balance.get("BTC", 0) >= cost:
                self.crypto_balance["BTC"] -= cost
                expiry_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
                self.subscription = {"type": "eup", "expires_at": expiry_date, "autorenew": True}
                border_content = (
                    f"{Fore.GREEN}Оплачено! EUP активна до {expiry_date}\n"
                    f"{Fore.BLUE}Спасибо за покупку!\n"
                    f"Новый баланс BTC: {self.crypto_balance['BTC']:.8f} BTC"
                )
                dynamic_border(border_content, Fore.GREEN)
            else:
                dynamic_border("Недостаточно BTC!", Fore.RED)
        else:
            dynamic_border("Отменено.", Fore.YELLOW)

    def buy_eup_plus(self, days: int):
        if not 1 <= days <= 365:
            dynamic_border("Ошибка: можно купить от 1 до 365 дней!", Fore.RED)
            return
        
        cost = 15 * days
        border_content = (
            f"{Fore.YELLOW}EUP плюс -------------------- Плюс\n"
            f"{Fore.YELLOW}Покупка EUP+ на {days} дней\n"
            f"Стоимость: {cost} BTC\n"
            f"Ваш баланс: {self.crypto_balance.get('BTC', 0):.8f} BTC\n"
            f"{Fore.CYAN}Введите 'да' для подтверждения:"
        )
        dynamic_border(border_content, Fore.YELLOW)
        
        if input(">>> ").lower() != "да":
            dynamic_border("Отменено.", Fore.YELLOW)
            return
        
        if self.crypto_balance.get("BTC", 0) < cost:
            dynamic_border(f"Недостаточно BTC. Требуется: {cost} BTC", Fore.RED)
            return
        
        self.crypto_balance["BTC"] -= cost
        expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        self.subscription = {"type": "eup_plus", "expires_at": expiry, "autorenew": False}
        bonus = 2000000
        self.crypto_balance["EXTRACT"] += bonus
        
        border_content = (
            f"{Fore.GREEN}EUP+ активирована до {expiry}!\n"
            f"+{bonus}{CURRENCY} бонус за покупку. Спасибо за покупку!\n"
            f"Новый баланс BTC: {self.crypto_balance['BTC']:.8f} BTC"
        )
        dynamic_border(border_content, Fore.GREEN)

    def eup_status(self):
        if not self.has_active_subscription():
            dynamic_border("У вас нет активных подписок.", Fore.RED)
            return
        
        remaining = (datetime.strptime(self.subscription["expires_at"], "%Y-%m-%d") - datetime.now()).days
        border_content = (
            f"{Fore.CYAN}Статус подписки\n"
            f"Истекает: {self.subscription['expires_at']}\n"
            f"Дней осталось: {remaining}\n"
            f"Автопродление: {'вкл' if self.subscription.get('autorenew', False) else 'выкл'}\n"
        )
        dynamic_border(border_content, Fore.CYAN)

    def eup_autonone(self):
        if not self.has_active_subscription():
            dynamic_border("У вас нет активной подписки!", Fore.RED)
            return
        
        self.subscription["autorenew"] = False
        dynamic_border(
            f"Автопродление отключено. Текущая подписка истекает {self.subscription['expires_at']}.",
            Fore.GREEN
        )

class Casino:
    def __init__(self):
        self.users = {}
        self.current_user = None
        self.market = CryptoMarket()
        self.last_command = ""
        self.last_save = time.time()
        self.promo_codes = self._load_promocodes()
        self.forum = Forum()
        self.achievements = Achievements()
        self.network = NetworkManager(self)
        self.load_users()

    def save_users(self):
        try:
            os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
            with open(SAVE_PATH, "w") as f:
                data = {un: user.to_dict() for un, user in self.users.items()}
                json.dump(data, f, indent=4)
        except Exception as e:
            pass

    def load_users(self):
        try:
            if os.path.exists(SAVE_PATH):
                with open(SAVE_PATH, "r") as f:
                    data = json.load(f)
                    self.users = {un: User.from_dict(user_data) for un, user_data in data.items()}
        except (FileNotFoundError, json.JSONDecodeError):
            self.users = {}
        except Exception as e:
            pass

    def _load_promocodes(self) -> Dict[str, Dict]:
        try:
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
            return {}

    def _save_promocodes(self):
        try:
            os.makedirs(os.path.dirname(KEYS_PATH), exist_ok=True)
            with open(KEYS_PATH, "w") as f:
                json.dump(self.promo_codes, f, indent=4, ensure_ascii=False)
        except Exception as e:
            pass

    def activate_promo(self, code: str):
        if not self.current_user:
            dynamic_border("Требуется авторизация!", Fore.RED)
            return
        
        code = code.lower()
        promo = self.promo_codes.get(code)
        
        if not promo:
            dynamic_border("Неверный промокод!", Fore.RED)
            return
        
        if promo["used"]:
            dynamic_border("Промокод уже использован!", Fore.RED)
            return
        
        if promo["type"] == "xp":
            self.current_user.add_xp(promo["amount"])
            msg = f"+{promo['amount']} опыта"
        elif promo["type"] == "currency":
            self._update_balance(promo["amount"])
            msg = f"+{promo['amount']}{CURRENCY}"
        elif promo["type"] == "eup":
            expiry_date = (datetime.now() + timedelta(days=promo['amount'])).strftime("%Y-%m-%d")
            self.current_user.subscription = {"type": "eup", "expires_at": expiry_date, "autorenew": False}
            msg = f"Подписка EUP на {promo['amount']} дней"
        elif promo["type"] == "eup_plus":
            expiry_date = (datetime.now() + timedelta(days=promo['amount'])).strftime("%Y-%m-%d")
            self.current_user.subscription = {"type": "eup_plus", "expires_at": expiry_date, "autorenew": False}
            msg = f"Подписка EUP+ на {promo['amount']} дней"
        elif promo["type"] == "crypto":
            coin = promo["coin"]
            amount = promo["amount"]
            self.current_user.crypto_balance[coin] += amount
            msg = f"+{amount} {coin} {CRYPTO_SYMBOLS[coin]}"
        else:
            dynamic_border("Неизвестный тип промокода!", Fore.RED)
            return
        
        self.promo_codes[code]["used"] = True
        self._save_promocodes()
        
        border_content = (
            f"{Fore.GREEN}Активация успешна!\n"
            f"{Fore.CYAN}Награда: {msg}"
        )
        dynamic_border(border_content, Fore.GREEN)

    def get_current_event(self) -> Optional[Dict]:
        current_month = datetime.now().month
        event = MONTHLY_EVENTS.get(current_month, {}).copy()
        if event:
            event["active"] = True
            return event
        return None

    def apply_event_bonus(self, bonus_type: str, base_value: float) -> float:
        event = self.get_current_event()
        if not event or "effects" not in event:
            return base_value
        bonus = event["effects"].get(bonus_type, 1.0)
        if isinstance(bonus, (int, float)):
            return base_value * bonus
        return base_value

    def show_monthly_event(self):
        event = self.get_current_event()
        if not event:
            dynamic_border("В этом месяце нет активных событий", Fore.YELLOW)
            return
        
        month_name = datetime.now().strftime("%B")
        days_left = (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1) - datetime.now()
        
        if RICH_AVAILABLE:
            console.print(Panel(
                f"[bold magenta]{month_name} - {event['name']}[/bold magenta]\n"
                f"[cyan]Дней осталось: {days_left.days}[/cyan]\n\n"
                f"[green]Активные бонусы:[/green]",
                title="📅 Мероприятие месяца",
                border_style="magenta"
            ))
            
            for effect, value in event["effects"].items():
                if isinstance(value, bool):
                    console.print(f"  • {effect}: {'✅ Активен' if value else '❌ Не активен'}")
                elif isinstance(value, float):
                    console.print(f"  • {effect}: [yellow]x{value}[/yellow]")
                else:
                    console.print(f"  • {effect}: [green]+{value}[/green]")
            return
        
        content = [
            f"{Fore.MAGENTA}Календарь: {month_name} - {event['name']}",
            f"{Fore.CYAN}Дней осталось: {days_left.days}",
            f"{Fore.GREEN}Активные бонусы:",
        ]
        
        bonus_icons = {"multiplier": "📊", "bonus": "🎁", "special": "⭐", "protection": "🛡️"}
        for effect, value in event["effects"].items():
            icon = bonus_icons.get(effect.split('_')[-1], "•")
            if isinstance(value, bool):
                content.append(f"{icon} {effect}: {'Активен' if value else 'Не активен'}")
            elif isinstance(value, float):
                content.append(f"{icon} {effect}: x{value}")
            else:
                content.append(f"{icon} {effect}: +{value}")
        
        dynamic_border('\n'.join(content), Fore.MAGENTA)

    def _check_balance(self, amount: float, currency: str = "EXTRACT") -> bool:
        if not self.current_user:
            return False
        return self.current_user.crypto_balance.get(currency, 0) >= amount

    def _update_balance(self, amount: float, currency: str = "EXTRACT"):
        if self.current_user:
            self.current_user.crypto_balance[currency] += amount

    def _validate_bet(self, bet: float) -> bool:
        if not self.current_user:
            dynamic_border("Сначала выберите пользователя!", Fore.RED)
            return False
        if bet <= 0:
            dynamic_border("Ставка должна быть положительной!", Fore.RED)
            return False
        if not self._check_balance(bet):
            dynamic_border("Недостаточно средств!", Fore.RED)
            return False
        return True

    def _process_result(self, win: float, bet: float):
        win = self.apply_event_bonus("win_multiplier", win)
        if win > 0:
            self._update_balance(win)
            self.current_user.update_stats(True)
            self.current_user.add_xp(win)
            if self.current_user.wins == 1:
                self.achievements.unlock_achievement(self.current_user.username, "first_win", self.current_user)
            if self.current_user.games_played >= 100:
                self.achievements.unlock_achievement(self.current_user.username, "slots_master", self.current_user)
        else:
            self.current_user.update_stats(False)
            self.current_user.add_xp(bet * 0.1)
        
        self.current_user.total_earned += win
        self.save_users()

    def _apply_subscription_bonus(self, win: float) -> float:
        if not self.current_user:
            return win
        if self.current_user.subscription["type"] == "eup":
            return win * 1.10
        elif self.current_user.subscription["type"] == "eup_plus":
            return win * 1.25
        return win

    def _apply_subscription_refund(self, bet: float) -> float:
        if not self.current_user or not self.current_user.has_active_subscription():
            return 0
        refund_rate = 0.20 if self.current_user.subscription["type"] == "eup_plus" else 0.10
        refund = bet * refund_rate
        self._update_balance(refund)
        return refund

    def create_user(self, username: str):
        if username in self.users:
            dynamic_border(f"Пользователь {username} уже существует!", Fore.RED)
            return
        
        self.users[username] = User(username)
        self.current_user = self.users[username]
        self.save_users()
        
        if RICH_AVAILABLE:
            console.print(f"[bold green]Пользователь {username} создан![/bold green]")
        else:
            print(gradient_text(f"Пользователь {username} создан!", [Fore.GREEN, Fore.LIGHTGREEN_EX]))

    def select_user(self, username: str):
        if username in self.users:
            if self.current_user:
                self.current_user.end_session()
            self.current_user = self.users[username]
            self.current_user.start_session()
            self.current_user.check_subscription()
            self.current_user.give_daily_bonus()
            
            dynamic_border(f"Выбран пользователь: {self.current_user.get_styled_username()}", Fore.GREEN)
            
            if self.network.connection and self.current_user:
                self.network.send_message(NetworkMessage(
                    MessageType.HANDSHAKE,
                    {"username": self.current_user.username}
                ))
        else:
            dynamic_border("Пользователь не найден!", Fore.RED)

    def delete_user(self, username: str):
        if username in self.users:
            if self.current_user and self.current_user.username == username:
                self.current_user.end_session()
                self.current_user = None
            del self.users[username]
            self.save_users()
            dynamic_border(f"Пользователь {username} удален!", Fore.GREEN)
        else:
            dynamic_border("Пользователь не найден!", Fore.RED)

    def show_all_profiles(self):
        if not self.users:
            dynamic_border("Нет созданных пользователей!", Fore.RED)
            return
        
        if RICH_AVAILABLE:
            table = Table(title="👥 Зарегистрированные пользователи", show_header=True)
            table.add_column("№", style="cyan")
            table.add_column("Имя пользователя", style="yellow")
            table.add_column("Уровень", style="green")
            table.add_column("Баланс", justify="right", style="magenta")
            
            for i, (un, user) in enumerate(self.users.items(), 1):
                table.add_row(str(i), user.get_styled_username(), str(user.level), f"{user.crypto_balance['EXTRACT']:,.2f}")
            
            console.print(table)
            return
        
        profiles = [f"{i+1}. {self.users[un].get_styled_username()}" for i, un in enumerate(self.users.keys())]
        content = [f"{Fore.CYAN}Зарегистрированные пользователи:"] + profiles
        dynamic_border('\n'.join(content), Fore.BLUE)

    def slots(self, bet: float):
        if not self._validate_bet(bet):
            return
        
        actual_bet = bet
        used_free_spin = False
        
        if self.current_user.free_spins > 0:
            dynamic_border(
                f"Используется бесплатный спин (осталось: {self.current_user.free_spins-1})",
                Fore.GREEN
            )
            self.current_user.free_spins -= 1
            actual_bet = bet
            used_free_spin = True
        else:
            self._update_balance(-bet)
        
        if RICH_AVAILABLE:
            console.print(Panel.fit("🎰 СЛОТЫ EXTRACT", border_style="cyan"))
        else:
            dynamic_border("СЛОТЫ EXTRACT", Fore.CYAN)
        
        symbols = [("ВИШНЯ", 0.3), ("АПЕЛЬСИН", 0.25), ("ЛИМОН", 0.2), 
                  ("КОЛОКОЛ", 0.15), ("ЗВЕЗДА", 0.07), ("АЛМАЗ", 0.03)]
        
        def spin_animation():
            if RICH_AVAILABLE:
                with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                    task = progress.add_task("Крутим барабаны...", total=10)
                    for i in range(10):
                        temp = random.choices([s[0] for s in symbols], weights=[s[1] for s in symbols], k=3)
                        progress.update(task, advance=1)
                        time.sleep(0.1)
            else:
                for _ in range(10):
                    temp = random.choices([s[0] for s in symbols], weights=[s[1] for s in symbols], k=3)
                    print("\r" + " | ".join(temp), end='', flush=True)
                    time.sleep(0.1)
        
        spin_animation()
        results = random.choices([s[0] for s in symbols], weights=[s[1] for s in symbols], k=3)
        
        if RICH_AVAILABLE:
            console.print(f"\n[bold]Результат:[/bold] {' | '.join(results)}")
        else:
            print("\r" + " | ".join(results) + "   ")
        
        win = 0
        free_spins_won = 0
        
        if results.count("АЛМАЗ") == 3:
            win = bet * 50
            free_spins_won = 5
            dynamic_border(f"ДЖЕКПОТ! 3 АЛМАЗА! +{win}{CURRENCY} + {free_spins_won} БЕСПЛАТНЫХ СПИНОВ", Fore.GREEN)
        elif results[0] == results[1] == results[2]:
            multiplier = 10
            if results[0] == "КОЛОКОЛ":
                multiplier = 15
            elif results[0] == "ЗВЕЗДА":
                multiplier = 20
            win = bet * multiplier
            free_spins_won = 2
            dynamic_border(f"СУПЕР! 3 {results[0]}! +{win}{CURRENCY} + {free_spins_won} БЕСПЛАТНЫХ СПИНА", Fore.GREEN)
        elif results[0] == results[1]:
            win = bet * 3
            if results[0] == "АЛМАЗ":
                win = bet * 10
                free_spins_won = 1
            dynamic_border(f"Линия выиграла! +{win}{CURRENCY}" + (f" + {free_spins_won} БЕСПЛАТНЫЙ СПИН" if free_spins_won else ""), Fore.YELLOW)
        elif used_free_spin:
            if random.random() < 0.3:
                free_spins_won = 1
                dynamic_border("В следующий раз повезет! +1 БЕСПЛАТНЫЙ СПИН", Fore.BLUE)
            else:
                dynamic_border("Проигрыш", Fore.RED)
        else:
            refund = self._apply_subscription_refund(bet)
            if refund > 0:
                dynamic_border(f"Проигрыш {Fore.YELLOW}(Возврат: +{refund}{CURRENCY})", Fore.RED)
            else:
                dynamic_border("Проигрыш", Fore.RED)
        
        if win > 0:
            win = self._apply_subscription_bonus(win)
            win = self.apply_event_bonus("slots_multiplier", win)
            self._update_balance(win)
            if free_spins_won > 0:
                self.current_user.free_spins += free_spins_won
                print(f"{Fore.CYAN}Теперь у вас {self.current_user.free_spins} бесплатных спинов!")
        
        self._process_result(win, actual_bet)

    def trade(self, command: str):
        if not self.current_user:
            dynamic_border("Сначала выберите пользователя! add/login [имя]", Fore.RED)
            return
        
        try:
            parts = command.split()
            if len(parts) < 3:
                raise ValueError
            
            action = parts[0].lower()
            coin = parts[1].upper()
            amount = float(parts[2])
            
            if amount <= 0:
                dynamic_border("Сумма должна быть положительной!", Fore.RED)
                return
            
            if coin not in self.market.rates:
                dynamic_border(f"Неизвестная валюта: {coin}", Fore.RED)
                return
            
            if action == "buy":
                cost = amount * self.market.get_rate(coin) * 1.01
                cost = self.apply_event_bonus("trade_fee", cost)
                
                if not self._check_balance(cost):
                    dynamic_border("Недостаточно средств!", Fore.RED)
                    return
                
                self._update_balance(-cost)
                self.current_user.crypto_balance[coin] += amount
                self.current_user.add_transaction('buy', coin, amount, cost)
                
                if len([t for t in self.current_user.transactions if t['action'] in ['buy', 'sell']]) >= 50:
                    self.achievements.unlock_achievement(self.current_user.username, "trader", self.current_user)
                
                dynamic_border(f"Куплено {amount:.4f} {coin}", Fore.CYAN, 40)
                
            elif action == "sell":
                if self.current_user.crypto_balance.get(coin, 0) < amount:
                    dynamic_border(f"Недостаточно {coin} для продажи!", Fore.RED)
                    return
                
                value = amount * self.market.get_rate(coin) * 0.99
                value = self.apply_event_bonus("trade_bonus", value)
                self.current_user.crypto_balance[coin] -= amount
                self._update_balance(value)
                self.current_user.add_transaction('sell', coin, amount, value)
                
                if len([t for t in self.current_user.transactions if t['action'] in ['buy', 'sell']]) >= 50:
                    self.achievements.unlock_achievement(self.current_user.username, "trader", self.current_user)
                
                dynamic_border(f"Продано {amount:.4f} {coin}", Fore.MAGENTA, 40)
            else:
                dynamic_border(f"Неизвестное действие: {action}", Fore.RED)
                return
            
            self.market.update_rates()
            self.save_users()
            
        except (IndexError, ValueError):
            dynamic_border("Ошибка: trade [buy/sell] [валюта] [сумма]", Fore.RED)

    def monster_battle(self, bet: float):
        if not self._validate_bet(bet):
            return
        
        if RICH_AVAILABLE:
            console.print(Panel.fit("⚔️ БИТВЫ EXTRACT", border_style="red"))
        else:
            dynamic_border("БИТВЫ EXTRACT", Fore.RED)
        
        self._update_balance(-bet)
        player_attack = random.randint(50, 150) + self.current_user.level * 2
        monster_attack = random.randint(50, 150)
        
        print(f"{Fore.CYAN}Ваша сила атаки: {player_attack}")
        print(f"{Fore.RED}Сила атаки монстра: {monster_attack}")
        
        if player_attack > monster_attack:
            win = bet * 3
            win = self._apply_subscription_bonus(win)
            win = self.apply_event_bonus("battle_xp", win)
            dynamic_border(f"ПОБЕДА! +{win}{CURRENCY}", Fore.GREEN)
        else:
            win = 0
            refund = self._apply_subscription_refund(bet)
            if refund > 0:
                dynamic_border(f"ПОРАЖЕНИЕ {Fore.YELLOW}(Возврат: +{refund}{CURRENCY})", Fore.RED)
            else:
                dynamic_border("ПОРАЖЕНИЕ", Fore.RED)
        
        self._process_result(win, bet)

    def dice(self, bet: float):
        if not self._validate_bet(bet):
            return
        
        if RICH_AVAILABLE:
            console.print(Panel.fit("🎲 КОСТИ EXTRACT", border_style="yellow"))
        else:
            dynamic_border("КОСТИ EXTRACT", Fore.YELLOW)
        
        self._update_balance(-bet)
        player_dice = sum(random.randint(1, 6) for _ in range(3))
        dealer_dice = sum(random.randint(1, 6) for _ in range(3))
        
        print(f"{Fore.CYAN}Ваши кости: {player_dice}")
        print(f"{Fore.RED}Кости дилера: {dealer_dice}")
        
        if player_dice > dealer_dice:
            win = bet * 2
            win = self._apply_subscription_bonus(win)
            dynamic_border(f"ВЫИГРЫШ! +{win}{CURRENCY}", Fore.GREEN)
        else:
            win = 0
            refund = self._apply_subscription_refund(bet)
            if refund > 0:
                dynamic_border(f"ПРОИГРЫШ {Fore.YELLOW}(Возврат: +{refund}{CURRENCY})", Fore.RED)
            else:
                dynamic_border("ПРОИГРЫШ", Fore.RED)
        
        self._process_result(win, bet)

    def high_low(self, bet: float):
        if not self._validate_bet(bet):
            return
        
        if RICH_AVAILABLE:
            console.print(Panel.fit("📈 ВЫШЕ-НИЖЕ EXTRACT", border_style="magenta"))
        else:
            dynamic_border("ВЫШЕ-НИЖЕ EXTRACT", Fore.MAGENTA)
        
        self._update_balance(-bet)
        current = random.randint(1, 200)
        print(f"Текущее число: {Fore.CYAN}{current}")
        
        choice = input(f"{Fore.YELLOW}Следующее будет выше (в) или ниже (н)? ").lower()
        next_num = random.randint(1, 200)
        print(f"Новое число: {Fore.CYAN}{next_num}")
        
        won = (choice == 'в' and next_num > current) or (choice == 'н' and next_num < current)
        
        if won:
            base_win = bet * 2
            win = self._apply_subscription_bonus(base_win)
            win = self.apply_event_bonus("win_multiplier", win)
            dynamic_border(f"ВЫИГРЫШ! +{win}{CURRENCY}", Fore.GREEN)
            self._process_result(win, bet)
        else:
            win = 0
            refund = self._apply_subscription_refund(bet)
            if refund > 0:
                dynamic_border(f"ПРОИГРЫШ {Fore.YELLOW}(Возврат: +{refund}{CURRENCY})", Fore.RED)
            else:
                dynamic_border("ПРОИГРЫШ", Fore.RED)
            self._process_result(0, bet)

    def roulette(self, bet: float):
        if not self._validate_bet(bet):
            return
        
        if RICH_AVAILABLE:
            console.print(Panel.fit("🎡 РУЛЕТКА EXTRACT", border_style="red"))
        else:
            dynamic_border("РУЛЕТКА EXTRACT", Fore.RED)
        
        self._update_balance(-bet)
        print(f"{Fore.YELLOW}Выберите цвет:")
        print(f"{Fore.RED}1. Красное (x2)")
        print(f"{Fore.WHITE}2. Черное (x2)")
        print(f"{Fore.GREEN}3. Зеленое (x14)")
        
        try:
            choice = int(input("Ваш выбор (1-3): "))
            if choice not in [1, 2, 3]:
                dynamic_border("Неверный выбор!", Fore.RED)
                self._update_balance(bet)
                return
        except ValueError:
            dynamic_border("Неверный ввод!", Fore.RED)
            self._update_balance(bet)
            return
        
        result = random.randint(0, 36)
        if result == 0:
            color = 3
        elif result % 2 == 0:
            color = 1
        else:
            color = 2
        
        print(f"Результат: {result}")
        if color == 1:
            print(f"{Fore.RED}Красное!")
        elif color == 2:
            print(f"{Fore.WHITE}Черное!")
        else:
            print(f"{Fore.GREEN}Зеленое!")
        
        if choice == color:
            win = bet * 14 if color == 3 else bet * 2
            win = self._apply_subscription_bonus(win)
            dynamic_border(f"ВЫИГРЫШ! +{win}{CURRENCY}", Fore.GREEN)
        else:
            win = 0
            refund = self._apply_subscription_refund(bet)
            if refund > 0:
                dynamic_border(f"ПРОИГРЫШ {Fore.YELLOW}(Возврат: +{refund}{CURRENCY})", Fore.RED)
            else:
                dynamic_border("ПРОИГРЫШ", Fore.RED)
        
        self._process_result(win, bet)

    def blackjack(self, bet: float):
        if not self._validate_bet(bet):
            return
        
        if RICH_AVAILABLE:
            console.print(Panel.fit("🃏 БЛЭКДЖЕК EXTRACT", border_style="blue"))
        else:
            dynamic_border("БЛЭКДЖЕК EXTRACT", Fore.BLUE)
        
        self._update_balance(-bet)
        deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4
        random.shuffle(deck)
        
        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]
        
        print(f"{Fore.CYAN}Ваши карты: {player_hand} (Сумма: {sum(player_hand)})")
        print(f"{Fore.RED}Карта дилера: {dealer_hand[0]}")
        
        while sum(player_hand) < 21:
            action = input(f"{Fore.YELLOW}Еще карту? (д/н): ").lower()
            if action == 'д':
                player_hand.append(deck.pop())
                if sum(player_hand) > 21 and 11 in player_hand:
                    player_hand[player_hand.index(11)] = 1
                print(f"{Fore.CYAN}Ваши карты: {player_hand} (Сумма: {sum(player_hand)})")
                if sum(player_hand) > 21:
                    dynamic_border("Перебор! Вы проиграли.", Fore.RED)
                    self._process_result(0, bet)
                    return
            else:
                break
        
        while sum(dealer_hand) < 17:
            dealer_hand.append(deck.pop())
            if sum(dealer_hand) > 21 and 11 in dealer_hand:
                dealer_hand[dealer_hand.index(11)] = 1
        
        print(f"{Fore.RED}Карты дилера: {dealer_hand} (Сумма: {sum(dealer_hand)})")
        
        player_sum = sum(player_hand)
        dealer_sum = sum(dealer_hand)
        
        if dealer_sum > 21 or player_sum > dealer_sum:
            win = bet * 2
            win = self._apply_subscription_bonus(win)
            dynamic_border(f"ВЫИГРЫШ! +{win}{CURRENCY}", Fore.GREEN)
        elif player_sum == dealer_sum:
            dynamic_border("Ничья! Ставка возвращена.", Fore.YELLOW)
            self._update_balance(bet)
            return
        else:
            win = 0
            refund = self._apply_subscription_refund(bet)
            if refund > 0:
                dynamic_border(f"ПРОИГРЫШ {Fore.YELLOW}(Возврат: +{refund}{CURRENCY})", Fore.RED)
            else:
                dynamic_border("ПРОИГРЫШ", Fore.RED)
        
        self._process_result(win, bet)

    def show_rates(self):
        try:
            with open(CS_LOG_PATH, "r") as f:
                old_rates = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            old_rates = self.market.rates.copy()
        
        if RICH_AVAILABLE:
            table = Table(title="📈 Текущие курсы", show_header=True, header_style="bold cyan")
            table.add_column("Валюта", style="yellow")
            table.add_column("Символ", style="green")
            table.add_column("Курс", justify="right", style="magenta")
            table.add_column("Изменение", justify="right")
            
            for coin, rate in self.market.rates.items():
                if coin == "EXTRACT":
                    continue
                old_rate = old_rates.get(coin, rate)
                change = ((rate - old_rate) / old_rate) * 100 if old_rate != 0 else 0
                change_str = f"{change:+.2f}%"
                change_style = "green" if change >= 0 else "red"
                table.add_row(coin, CRYPTO_SYMBOLS[coin], f"{rate:.2f} {CURRENCY}", 
                            f"[{change_style}]{change_str}[/{change_style}]")
            
            console.print(table)
            return
        
        content = [f"{Fore.CYAN}Текущие курсы:"]
        for coin, rate in self.market.rates.items():
            if coin == "EXTRACT":
                continue
            old_rate = old_rates.get(coin, rate)
            change = ((rate - old_rate) / old_rate) * 100 if old_rate != 0 else 0
            color = Fore.GREEN if change >= 0 else Fore.RED
            change_text = f"{color}({change:+.2f}%){Style.RESET_ALL}"
            content.append(f"{CRYPTO_SYMBOLS[coin]} 1 {coin} = {rate:.2f}{CURRENCY} {change_text}")
        
        dynamic_border('\n'.join(content), Fore.BLUE)

    def rename_account(self, current_name: str, new_name: str) -> bool:
        if current_name not in self.users:
            dynamic_border(f"Ошибка: пользователь '{current_name}' не найден!", Fore.RED)
            return False
        
        if new_name in self.users:
            dynamic_border(f"Ошибка: имя '{new_name}' уже занято!", Fore.RED)
            return False
        
        if not (new_name.isalnum() and 3 <= len(new_name) <= 16):
            dynamic_border("Ошибка: новое имя должно содержать 3-16 буквенно-цифровых символов!", Fore.RED)
            return False
        
        confirm = input(f"{Fore.RED}Переименовать '{current_name}' в '{new_name}'? (д/н): ").strip().lower()
        if confirm != 'д':
            dynamic_border("Отменено.", Fore.YELLOW)
            return False
        
        user_data = self.users.pop(current_name)
        user_data.username = new_name
        self.users[new_name] = user_data
        
        if self.current_user and self.current_user.username == current_name:
            self.current_user = user_data
        
        self.save_users()
        dynamic_border(f"Успех: '{current_name}' переименован в '{new_name}'!", Fore.GREEN)
        return True

    def transfer(self, sender: str, receiver: str, currency: str, amount: float) -> bool:
        if not isinstance(sender, str) or not isinstance(receiver, str) or not isinstance(currency, str):
            dynamic_border("Ошибка: неверный формат параметров", Fore.RED)
            return False
        
        currency = currency.upper()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if sender not in self.users:
            dynamic_border(f"Ошибка: отправитель '{sender}' не найден!", Fore.RED)
            return False
        
        if receiver not in self.users:
            dynamic_border(f"Ошибка: получатель '{receiver}' не найден!", Fore.RED)
            return False
        
        if currency not in CRYPTO_SYMBOLS:
            dynamic_border(f"Ошибка: валюта '{currency}' не поддерживается!", Fore.RED)
            return False
        
        try:
            amount = round(float(amount), 8)
            if amount <= 0:
                dynamic_border("Ошибка: сумма должна быть больше 0!", Fore.RED)
                return False
        except (ValueError, TypeError):
            dynamic_border("Ошибка: неверный формат суммы!", Fore.RED)
            return False
        
        sender_balance = round(self.users[sender].crypto_balance.get(currency, 0), 8)
        if sender_balance < amount:
            dynamic_border(
                f"Ошибка: недостаточно средств! Доступно: {sender_balance:.8f}{CRYPTO_SYMBOLS[currency]}",
                Fore.RED
            )
            return False
        
        commission_rate = 0.00 if self.users[sender].has_active_subscription() else 0.05
        commission = round(amount * commission_rate, 8)
        received_amount = round(amount - commission, 8)
        
        if RICH_AVAILABLE:
            console.print(Panel.fit(
                f"[bold yellow]ПОДТВЕРЖДЕНИЕ ПЕРЕВОДА[/bold yellow]\n\n"
                f"[white]От:[/white] [green]{sender}[/green]\n"
                f"[white]Кому:[/white] [green]{receiver}[/green]\n"
                f"[white]Валюта:[/white] [green]{currency} {CRYPTO_SYMBOLS[currency]}[/green]\n"
                f"[white]Сумма:[/white] [green]{amount:.8f}[/green]\n"
                f"[white]Комиссия:[/white] [red]{commission:.8f} ({commission_rate*100}%)[/red] {'[без комиссии]' if commission_rate == 0 else ''}\n"
                f"[white]Получит:[/white] [yellow]{received_amount:.8f}[/yellow]\n\n"
                f"[bold cyan]Подтвердить перевод? (да/нет):[/bold cyan]",
                border_style="yellow"
            ))
        else:
            confirm_text = f"""
{Fore.CYAN}{'='*50}
{Fore.YELLOW}ПОДТВЕРЖДЕНИЕ ПЕРЕВОДА
{Fore.CYAN}{'.'*50}
{Fore.WHITE}От: {Fore.GREEN}{sender:<44}
{Fore.WHITE}Кому: {Fore.GREEN}{receiver:<46}
{Fore.WHITE}Валюта: {Fore.GREEN}{currency} {CRYPTO_SYMBOLS[currency]:<36}
{Fore.CYAN}{'='*50}
{Fore.WHITE}Сумма: {Fore.GREEN}{amount:.8f}
{Fore.WHITE}Комиссия: {Fore.RED}{commission:.8f} ({commission_rate*100}%){" [Без комиссии]" if commission_rate == 0 else ""}
{Fore.WHITE}Получит: {Fore.YELLOW}{received_amount:.8f}
{Fore.CYAN}{'^'*50}
{Style.BRIGHT}Подтвердить перевод? (да/нет): {Style.RESET_ALL}"""
            print(confirm_text)
        
        confirm = input(">>> ").strip().lower()
        if confirm != 'да':
            dynamic_border("Перевод отменен", Fore.YELLOW)
            return False
        
        self.users[sender].crypto_balance[currency] = round(
            self.users[sender].crypto_balance.get(currency, 0) - amount, 8
        )
        self.users[receiver].crypto_balance[currency] = round(
            self.users[receiver].crypto_balance.get(currency, 0) + received_amount, 8
        )
        
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
        dynamic_border(f"Успех: {received_amount:.8f}{CRYPTO_SYMBOLS[currency]} -> {receiver}", Fore.GREEN)
        return True

    def show_receipts(self):
        try:
            if not os.path.exists(RECEIPTS_PATH):
                dynamic_border("История переводов пуста", Fore.YELLOW)
                return
            
            with open(RECEIPTS_PATH, 'r', encoding='utf-8') as f:
                receipts = json.load(f)
            
            if not receipts:
                dynamic_border("История переводов пуста", Fore.YELLOW)
                return
            
            if RICH_AVAILABLE:
                table = Table(title="📋 Последние переводы", show_header=True)
                table.add_column("Дата", style="cyan")
                table.add_column("От", style="yellow")
                table.add_column("Кому", style="green")
                table.add_column("Сумма", justify="right", style="magenta")
                table.add_column("Комиссия", justify="right", style="red")
                
                for receipt in receipts[:10]:
                    table.add_row(
                        receipt['timestamp'][:16],
                        receipt['sender'],
                        receipt['receiver'],
                        f"{receipt['amount']:.8f}{CRYPTO_SYMBOLS.get(receipt['currency'], '?')}",
                        f"{receipt['commission']:.8f}"
                    )
                
                console.print(table)
                return
            
            content = [f"{Fore.CYAN}Последние переводы:"]
            for i, receipt in enumerate(receipts[:5], 1):
                content.append(
                    f"{Fore.WHITE}{i}. {receipt['timestamp'][:16]} "
                    f"{Fore.YELLOW}{receipt['sender']} -> {receipt['receiver']} "
                    f"{Fore.GREEN}{receipt['amount']:.8f}{CRYPTO_SYMBOLS.get(receipt['currency'], '?')} "
                    f"{Fore.RED}(комиссия: {receipt['commission']:.8f})"
                )
            
            dynamic_border('\n'.join(content), Fore.BLUE)
        except Exception as e:
            dynamic_border(f"Ошибка загрузки истории переводов: {str(e)}", Fore.RED)

    def _save_receipt(self, receipt_data: Dict):
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
            pass

    def check_user(self, username: str):
        if username not in self.users:
            dynamic_border(f"Пользователь '{username}' не найден!", Fore.RED)
            return
        
        user = self.users[username]
        
        if RICH_AVAILABLE:
            info_table = Table(title=f"👤 Информация о пользователе", show_header=False)
            info_table.add_column("Параметр", style="cyan")
            info_table.add_column("Значение", style="yellow")
            
            info_table.add_row("Имя", user.get_styled_username())
            info_table.add_row("Баланс", f"{user.crypto_balance.get('EXTRACT', 0):.2f} {CURRENCY}")
            info_table.add_row("Уровень", str(user.level))
            info_table.add_row("Опыт", f"{user.xp:.0f}/{user.required_xp():.0f}")
            info_table.add_row("Процент побед", f"{user.win_loss_ratio()}%")
            info_table.add_row("Сетевых игр", str(user.live_games_played))
            
            top_coins = sorted(
                [(k, v) for k, v in user.crypto_balance.items() if v > 0 and k != "EXTRACT"],
                key=lambda x: x[1],
                reverse=True
            )[:3]
            
            if top_coins:
                info_table.add_row("", "")
                info_table.add_row("[bold green]Топ активы[/bold green]", "")
                for coin, amount in top_coins:
                    info_table.add_row(f"  {CRYPTO_SYMBOLS[coin]} {coin}", f"{amount:.4f}")
            
            console.print(info_table)
            return
        
        content = [
            f"{Fore.CYAN}Информация о пользователе: {user.get_styled_username()}",
            f"{Fore.GREEN}Баланс: {user.crypto_balance.get('EXTRACT', 0):.2f} {CURRENCY}",
            f"{Fore.BLUE}Уровень: {user.level}",
            f"{Fore.YELLOW}Опыт: {user.xp}/{user.required_xp()} ({user.show_level_progress()})",
            f"{Fore.MAGENTA}Сетевых игр: {user.live_games_played}"
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
        
        dynamic_border('\n'.join(content), Fore.CYAN)

    def global_stats(self):
        total_balance = sum(u.crypto_balance.get("EXTRACT", 0) for u in self.users.values())
        total_games = sum(u.games_played for u in self.users.values())
        total_network_games = sum(u.live_games_played for u in self.users.values())
        
        if RICH_AVAILABLE:
            stats_table = Table(title="🌐 Глобальная статистика", show_header=False)
            stats_table.add_column("Параметр", style="cyan")
            stats_table.add_column("Значение", style="yellow")
            
            stats_table.add_row("Пользователей", str(len(self.users)))
            stats_table.add_row("Общий баланс", f"{total_balance:,.2f} {CURRENCY}")
            stats_table.add_row("Всего игр", str(total_games))
            stats_table.add_row("Сетевых игр", str(total_network_games))
            
            if self.users:
                richest_user = max(self.users.values(), key=lambda u: u.crypto_balance.get("EXTRACT", 0))
                highest_level = max(self.users.values(), key=lambda u: u.level)
                
                stats_table.add_row("Самый богатый", f"{richest_user.username} ({richest_user.crypto_balance['EXTRACT']:,.2f})")
                stats_table.add_row("Самый высокий уровень", f"{highest_level.username} (уровень {highest_level.level})")
            
            console.print(stats_table)
            return
        
        border_content = (
            f"Пользователей: {len(self.users)}\n"
            f"Общий баланс: {format_currency(total_balance)} {CURRENCY}\n"
            f"Всего игр: {total_games}\n"
            f"Сетевых игр: {total_network_games}"
        )
        dynamic_border(border_content, Fore.CYAN)

    def show_eup_info(self):
        if RICH_AVAILABLE:
            info = Panel.fit(
                "[bold cyan]ИНФОРМАЦИЯ О ПОДПИСКАХ[/bold cyan]\n\n"
                "[bold blue]EUP (Extract User Privilege)[/bold blue]\n"
                "   Цена: 10 BTC/день\n"
                "   Бонусы:\n"
                "     +10% к выигрышам\n"
                "     +10% страховка при проигрыше\n"
                "     Ежедневный бонус 1,000,000E\n\n"
                "[bold yellow]EUP+ (Extract User Privilege+)[/bold yellow]\n"
                "   Цена: 15 BTC/день\n"
                "   Бонусы:\n"
                "     +25% к выигрышам\n"
                "     +20% страховка при проигрыше\n"
                "     Ежедневный бонус 2,000,000E\n"
                "     Шанс получить 10 BTC",
                title="💎 Подписки",
                border_style="cyan"
            )
            console.print(info)
            console.print("[cyan]Для покупки используйте:[/cyan]")
            console.print("[blue]eup buy [дни][/blue]      - купить EUP")
            console.print("[yellow]eup_plus buy [дни][/yellow] - купить EUP+")
            return
        
        info = f"""
{Fore.CYAN}╔{'═'*35}╗
║{'ИНФОРМАЦИЯ О ПОДПИСКАХ'.center(35)}║
╠{'═'*35}╣
║ {Fore.BLUE}EUP (Extract User Privilege){Fore.CYAN}      ║
║   Цена: 10 BTC/день               ║
║   Бонусы:                        ║
║     +10% к выигрышам              ║
║     +10% страховка при проигрыше  ║
║     Ежедневный бонус 1,000,000{CURRENCY}     ║
╠{'-'*35}╣
║ {Fore.YELLOW}EUP+ (Extract User Privilege+){Fore.CYAN}    ║
║   Цена: 15 BTC/день               ║
║   Бонусы:                        ║
║     +25% к выигрышам              ║
║     +20% страховка при проигрыше  ║
║     Ежедневный бонус 2,000,000{CURRENCY}     ║
║     Шанс получить 10 BTC          ║
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
{Fore.WHITE}1. Extract Live - сетевая игра
{Fore.RED}---
"""
        dynamic_border(path_text.strip(), Fore.CYAN)

    def display_help(self):
        if RICH_AVAILABLE:
            help_text = """
[bold cyan]Доступные команды:[/bold cyan]

[bold white]           ---Аккаунт---[/bold white]
[green]add    [имя][/green]                [white]- Создать нового пользователя[/white]
[green]login  [имя][/green]                [white]- Выбрать пользователя[/white]
[green]all[/green]                         [white]- Все профили[/white]
[green]rename [старое] [новое][/green]    [white]- Переименовать пользователя[/white]
[green]transfer [от] [кому] [валюта] [сумма][/green] - Сделать перевод
[green]receipts[/green]                    [white]- Показать последние переводы[/white]
[green]delete [имя][/green]                [white]- Удалить пользователя[/white]
[green]check [имя][/green]                 [white]- Информация о пользователе[/white]
[green]show[/green]                        [white]- Статистика профиля[/white]
[green]level[/green]                       [white]- Детальная информация об уровне[/white]
[green]achievements[/green]                [white]- Показать достижения[/white]
[green]exit -a[/green]                     [white]- Выйти из аккаунта[/white]

[bold white]      ---Покупка и статус EUP---[/bold white]
[yellow]eup buy [дни][/yellow]              [white]- Купить подписку EUP[/white]
[yellow]eup_plus buy [дни][/yellow]         [white]- Купить подписку EUP+[/white]
[yellow]eup status[/yellow]                 [white]- Статус подписки[/white]
[yellow]eup info[/yellow]                   [white]- Информация о подписках[/white]
[yellow]eup autonone[/yellow]               [white]- Отключить автопродление[/white]

[bold white]             ---Игры---[/bold white]
[red]slots [сумма][/red]                 [white]- Играть в слоты[/white]
[red]battle [сумма][/red]                [white]- Битва с монстром[/white]
[red]dice [сумма][/red]                  [white]- Игра в кости[/white]
[red]highlow [сумма][/red]               [white]- Игра Выше-Ниже[/white]
[red]roulette [сумма][/red]              [white]- Рулетка[/white]
[red]blackjack [сумма][/red]             [white]- Блэкджек[/white]

[bold white]         ---Криптовалюта---[/bold white]
[blue]trade buy [валюта] [сумма][/blue]  [white]- Купить криптовалюту[/white]
[blue]trade sell [валюта] [сумма][/blue] [white]- Продать криптовалюту[/white]
[blue]rates[/blue]                        [white]- Показать курсы обмена[/white]
[blue]wal[/blue]                          [white]- Показать баланс кошелька[/white]
[blue]chart [валюта][/blue]               [white]- Показать ASCII график для валюты[/white]

[bold white]       ---Extract Live (Сетевая игра)---[/bold white]
[cyan]live host [порт][/cyan]            [white]- Создать сервер (по умолчанию порт 5555)[/white]
[cyan]live connect [IP] [порт][/cyan]    [white]- Подключиться к серверу[/white]
[cyan]live disconnect[/cyan]             [white]- Отключиться от сети[/white]
[cyan]live chat [сообщение][/cyan]       [white]- Отправить сообщение игроку[/white]
[cyan]live invite [игра] [ставка][/cyan] [white]- Пригласить в игру (dice/highlow/battle/slots/roulette/blackjack)[/white]
[cyan]live accept [game_id][/cyan]       [white]- Принять приглашение в игру[/white]
[cyan]live decline[/cyan]                [white]- Отклонить приглашение[/white]
[cyan]live transfer [валюта] [сумма][/cyan][white]- Отправить перевод подключенному игроку[/white]
[cyan]live status[/cyan]                 [white]- Показать статус подключения[/white]

[bold white]       ---Игровые события---[/bold white]
[white]monthly[/white]                     [white]- Текущее месячное событие[/white]
[white]promo [код][/white]                [white]- Активировать промокод[/white]

[bold white]          ---О EXTRACT---[/bold white]
[cyan]extract[/cyan]                      [white]- Информация о версии[/white]
[cyan]wnew[/cyan]                         [white]- Заметки о обновлениях[/white]
[cyan]forum[/cyan]                        [white]- Открыть форум[/white]

[bold white]            ---Другое---[/bold white]
[magenta]global[/magenta]                    [white]- Глобальная статистика для всех аккаунтов[/white]
[magenta]exit[/magenta]                      [white]- Выйти из игры[/white]
[magenta]help[/magenta]                      [white]- Справка по командам[/white]
"""
            console.print(Panel.fit(help_text.strip(), title="📖 Помощь", border_style="cyan"))
            return
        
        help_text = f"""
{Fore.CYAN}Доступные команды:
{Fore.WHITE}           ---Аккаунт---
{Fore.GREEN}add    [имя]                {Fore.WHITE}- Создать нового пользователя
{Fore.GREEN}login  [имя]                {Fore.WHITE}- Выбрать пользователя
{Fore.GREEN}all                         {Fore.WHITE}- Все профили
{Fore.GREEN}rename [старое] [новое]    {Fore.WHITE}- Переименовать пользователя
{Fore.GREEN}transfer [от] [кому] [валюта] [сумма] - Сделать перевод
{Fore.GREEN}receipts                    {Fore.WHITE}- Показать последние переводы
{Fore.GREEN}delete [имя]                {Fore.WHITE}- Удалить пользователя
{Fore.GREEN}check [имя]                 {Fore.WHITE}- Информация о пользователе
{Fore.GREEN}show                        {Fore.WHITE}- Статистика профиля
{Fore.GREEN}level                       {Fore.WHITE}- Детальная информация об уровне
{Fore.GREEN}achievements                {Fore.WHITE}- Показать достижения
{Fore.GREEN}exit -a                     {Fore.WHITE}- Выйти из аккаунта
{Fore.WHITE}      ---Покупка и статус EUP---
{Fore.YELLOW}eup buy [дни]              {Fore.WHITE}- Купить подпику EUP
{Fore.YELLOW}eup_plus buy [дни]         {Fore.WHITE}- Купить подписку EUP+
{Fore.YELLOW}eup status                 {Fore.WHITE}- Статус подписки
{Fore.YELLOW}eup info                   {Fore.WHITE}- Информация о подписках
{Fore.YELLOW}eup autonone               {Fore.WHITE}- Отключить автопродление
{Fore.WHITE}             ---Игры---
{Fore.RED}slots [сумма]                 {Fore.WHITE}- Играть в слоты
{Fore.RED}battle [сумма]                {Fore.WHITE}- Битва с монстром
{Fore.RED}dice [сумма]                  {Fore.WHITE}- Игра в кости
{Fore.RED}highlow [сумма]               {Fore.WHITE}- Игра Выше-Ниже
{Fore.RED}roulette [сумма]              {Fore.WHITE}- Рулетка
{Fore.RED}blackjack [сумма]             {Fore.WHITE}- Блэкджек
{Fore.WHITE}         ---Криптовалюта---
{Fore.BLUE}trade buy [валюта] [сумма]  {Fore.WHITE}- Купить криптовалюту
{Fore.BLUE}trade sell [валюта] [сумма] {Fore.WHITE}- Продать криптовалюту
{Fore.BLUE}rates                        {Fore.WHITE}- Показать курсы обмена
{Fore.BLUE}wal                          {Fore.WHITE}- Показать баланс кошелька
{Fore.BLUE}chart [валюта]               {Fore.WHITE}- Показать ASCII график для валюты
{Fore.WHITE}       ---Extract Live (Сетевая игра)---
{Fore.CYAN}live host [порт]            {Fore.WHITE}- Создать сервер (по умолчанию порт 5555)
{Fore.CYAN}live connect [IP] [порт]    {Fore.WHITE}- Подключиться к серверу
{Fore.CYAN}live disconnect             {Fore.WHITE}- Отключиться от сети
{Fore.CYAN}live chat [сообщение]       {Fore.WHITE}- Отправить сообщение игроку
{Fore.CYAN}live invite [игра] [ставка] {Fore.WHITE}- Пригласить в игру (dice/highlow/battle/slots/roulette/blackjack)
{Fore.CYAN}live accept [game_id]       {Fore.WHITE}- Принять приглашение в игру
{Fore.CYAN}live decline                {Fore.WHITE}- Отклонить приглашение
{Fore.CYAN}live transfer [валюта] [сумма]{Fore.WHITE}- Отправить перевод подключенному игроку
{Fore.CYAN}live status                 {Fore.WHITE}- Показать статус подключения
{Fore.WHITE}       ---Игровые события---
{Fore.WHITE}monthly                     {Fore.WHITE}- Текущее месячное событие
{Fore.WHITE}promo [код]                {Fore.WHITE}- Активировать промокод
{Fore.WHITE}          ---О EXTRACT---
{Fore.CYAN}extract                      {Fore.WHITE}- Информация о версии
{Fore.CYAN}wnew                         {Fore.WHITE}- Заметки о обновлениях
{Fore.CYAN}forum                        {Fore.WHITE}- Открыть форум
{Fore.WHITE}            ---Другое---
{Fore.MAGENTA}global                    {Fore.WHITE}- Глобальная статистика для всех аккаунтов
{Fore.MAGENTA}exit                      {Fore.WHITE}- Выйти из игры
{Fore.MAGENTA}help                      {Fore.WHITE}- Справка по командам
"""
        dynamic_border(help_text.strip(), Fore.CYAN)

    def display_version(self):
        print_header()
        version_info = f"""
{Fore.YELLOW}{ADDINFO}
{Fore.YELLOW}{VERSION_ALL}
{Fore.RED}{INFO}
{Fore.RED}Авторы: Rexamm1t, Wefol1x
{Fore.RED}Telegram: @rexamm1t, @wefolix
{Fore.GREEN}Лицензия: MIT
{Fore.CYAN}Сетевая игра: Extract Live доступна!
"""
        dynamic_border(version_info.strip(), Fore.BLUE)

    def check_autosave(self):
        if time.time() - self.last_save > AUTOSAVE_INTERVAL:
            self.save_users()
            self.last_save = time.time()

def main():
    print_header()
    casino = Casino()
    
    try:
        while True:
            casino.check_autosave()
            casino.market.update_rates()
            current_time = datetime.now().strftime("%H:%M:%S")
            
            if casino.current_user:
                username = casino.current_user.get_styled_username()
                balance = casino.current_user.crypto_balance.get("EXTRACT", 0)
                
                if casino.network.running and casino.network.peer_username:
                    ping_color = Fore.GREEN if casino.network.ping < 100 else Fore.YELLOW if casino.network.ping < 300 else Fore.RED
                    mode = "СЕТЬ " + ("Хост" if casino.network.is_host else "Клиент")
                    prompt = (
                        f"{Fore.BLUE}╭─[{current_time}] {mode} - {username} ↔ {casino.network.peer_username} "
                        f"{ping_color}[{casino.network.ping}мс]{Fore.BLUE} - {Fore.GREEN}{format_currency(balance)} {CURRENCY}\n"
                        f"{Fore.BLUE}╰─{gradient_text('➤', [Fore.CYAN, Fore.BLUE])} {Style.RESET_ALL}"
                    )
                else:
                    prompt = (
                        f"{Fore.BLUE}╭─[{current_time}] - {username}{Fore.BLUE} - {Fore.GREEN}{format_currency(balance)} {CURRENCY}\n"
                        f"{Fore.BLUE}╰─{gradient_text('➤', [Fore.GREEN, Fore.YELLOW])} {Style.RESET_ALL}"
                    )
            else:
                prompt = f"{Fore.BLUE}╭─[{current_time}] - {VERSION_ALL} - Нужна помощь? - help\n╰─➤ {Style.RESET_ALL}"
            
            try:
                action = input(prompt).strip()
                casino.last_command = action.split()[0] if action else ""
                
                if action.startswith("live "):
                    parts = action.split()
                    if parts[1] == "host":
                        port = int(parts[2]) if len(parts) > 2 else DEFAULT_PORT
                        casino.network.start_server(port)
                    elif parts[1] == "connect":
                        ip = parts[2]
                        port = int(parts[3]) if len(parts) > 3 else DEFAULT_PORT
                        casino.network.connect_to_server(ip, port)
                    elif parts[1] == "disconnect":
                        casino.network.disconnect()
                    elif parts[1] == "chat":
                        if casino.network.running:
                            message = " ".join(parts[2:])
                            casino.network.send_chat_message(message)
                        else:
                            dynamic_border("Нет подключения к сети", Fore.RED)
                    elif parts[1] == "invite":
                        if casino.network.running and casino.network.peer_username:
                            if len(parts) < 4:
                                dynamic_border("Используйте: live invite [игра] [ставка]", Fore.RED)
                            else:
                                game = parts[2]
                                bet = float(parts[3])
                                try:
                                    game_type = GameType(game)
                                    casino.network.invite_to_game(game_type, bet)
                                except:
                                    dynamic_border(
                                        "Неизвестная игра. Доступно: dice, battle, highlow, roulette, blackjack, slots",
                                        Fore.RED
                                    )
                        else:
                            dynamic_border("Нет подключения к игроку", Fore.RED)
                    elif parts[1] == "accept":
                        if casino.network.running:
                            game_id = parts[2] if len(parts) > 2 else ""
                            if game_id:
                                casino.network.accept_game_invite(game_id)
                            else:
                                dynamic_border("Укажите game_id", Fore.RED)
                        else:
                            dynamic_border("Нет подключения к игроку", Fore.RED)
                    elif parts[1] == "decline":
                        if casino.network.running:
                            game_id = parts[2] if len(parts) > 2 else ""
                            casino.network.send_message(NetworkMessage(
                                MessageType.GAME_DECLINE,
                                {"game_id": game_id}
                            ))
                            dynamic_border("Приглашение отклонено", Fore.YELLOW)
                        else:
                            dynamic_border("Нет подключения к игроку", Fore.RED)
                    elif parts[1] == "transfer":
                        if casino.network.running and casino.network.peer_username:
                            if len(parts) < 4:
                                dynamic_border("Используйте: live transfer [валюта] [сумма]", Fore.RED)
                            else:
                                currency = parts[2].upper()
                                amount = float(parts[3])
                                if casino.network.send_transfer(currency, amount):
                                    dynamic_border("Перевод отправлен!", Fore.GREEN)
                                else:
                                    dynamic_border("Ошибка отправки перевода", Fore.RED)
                        else:
                            dynamic_border("Нет подключения к игроку", Fore.RED)
                    elif parts[1] == "status":
                        if casino.network.running:
                            status = "Хост" if casino.network.is_host else "Клиент"
                            peer = casino.network.peer_username or "Ожидание..."
                            ping_color = Fore.GREEN if casino.network.ping < 100 else Fore.YELLOW if casino.network.ping < 300 else Fore.RED
                            border_content = (
                                f"{Fore.CYAN}Статус подключения:\n"
                                f"Режим: {status}\n"
                                f"Игрок: {peer}\n"
                                f"Пинг: {ping_color}{casino.network.ping}мс"
                            )
                            dynamic_border(border_content, Fore.CYAN)
                        else:
                            dynamic_border("Нет подключения к сети", Fore.YELLOW)
                    else:
                        dynamic_border("Неизвестная команда live. Введите 'help' для справки", Fore.RED)
                
                elif action.startswith("add "):
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
                        dynamic_border("Используйте: check [имя]", Fore.RED)
                
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
                            dynamic_border("Перевод не выполнен", Fore.YELLOW)
                    except ValueError:
                        dynamic_border("Ошибка: используйте 'transfer <от> <кому> <валюта> <сумма>'", Fore.RED)
                
                elif action == "receipts":
                    casino.show_receipts()
                
                elif action.startswith("rename "):
                    parts = action.split()
                    if len(parts) != 3:
                        dynamic_border("Ошибка: используйте `rename <старое_имя> <новое_имя>`", Fore.RED)
                        continue
                    
                    current_name = parts[1]
                    new_name = parts[2]
                    
                    if current_name == new_name:
                        dynamic_border("Ошибка: новое имя не должно совпадать со старым!", Fore.YELLOW)
                        continue
                    
                    if not (current_name.isprintable() and new_name.isprintable()):
                        dynamic_border("Ошибка: имена содержат недопустимые символы!", Fore.RED)
                        continue
                    
                    casino.rename_account(current_name, new_name)
                
                elif action.startswith("delete "):
                    username = action.split(" ", 1)[1]
                    casino.delete_user(username)
                
                elif action == "exit -a":
                    if casino.current_user:
                        casino.current_user.end_session()
                        casino.current_user = None
                        dynamic_border("Вы вышли из системы", Fore.GREEN)
                
                elif action.startswith("slots"):
                    try:
                        bet = float(action.split()[1])
                        casino.slots(bet)
                    except:
                        dynamic_border("Используйте: slots [сумма]", Fore.RED)
                
                elif action.startswith("battle"):
                    try:
                        bet = float(action.split()[1])
                        casino.monster_battle(bet)
                    except:
                        dynamic_border("Используйте: battle [сумма]", Fore.RED)
                
                elif action.startswith("dice"):
                    try:
                        bet = float(action.split()[1])
                        casino.dice(bet)
                    except:
                        dynamic_border("Используйте: dice [сумма]", Fore.RED)
                
                elif action.startswith("highlow"):
                    try:
                        bet = float(action.split()[1])
                        casino.high_low(bet)
                    except:
                        dynamic_border("Используйте: highlow [сумма]", Fore.RED)
                
                elif action.startswith("roulette"):
                    try:
                        bet = float(action.split()[1])
                        casino.roulette(bet)
                    except:
                        dynamic_border("Используйте: roulette [сумма]", Fore.RED)
                
                elif action.startswith("blackjack"):
                    try:
                        bet = float(action.split()[1])
                        casino.blackjack(bet)
                    except:
                        dynamic_border("Используйте: blackjack [сумма]", Fore.RED)
                
                elif action.startswith("trade"):
                    casino.trade(action[5:])
                
                elif action == "global":
                    casino.global_stats()
                
                elif action == "eup info":
                    casino.show_eup_info()
                
                elif action == "rates":
                    casino.show_rates()
                
                elif action.startswith("chart "):
                    coin = action.split(" ", 1)[1].upper()
                    print_currency_ascii_chart(casino.market, coin)
                
                elif action == "show":
                    if casino.current_user:
                        casino.current_user.show_stats()
                    else:
                        dynamic_border("Пользователь не выбран! Войдите в аккаунт.", Fore.RED)
                
                elif action == "level":
                    if casino.current_user:
                        content = [
                            f"{Fore.CYAN}Уровень: {casino.current_user.level}",
                            f"{Fore.BLUE}Опыт: {casino.current_user.xp:.0f}/{casino.current_user.required_xp():.0f}",
                            casino.current_user.show_level_progress(),
                            f"{Fore.GREEN}Всего заработано: {format_currency(casino.current_user.total_earned)}{CURRENCY}",
                            f"{Fore.CYAN}Сетевых игр: {casino.current_user.live_games_played}"
                        ]
                        dynamic_border('\n'.join(content), Fore.YELLOW)
                    else:
                        dynamic_border("Пользователь не выбран!", Fore.RED)
                
                elif action == "monthly":
                    casino.show_monthly_event()
                
                elif action == "wal":
                    if casino.current_user:
                        casino.current_user.crywall()
                    else:
                        dynamic_border("Пользователь не выбран!", Fore.RED)
                
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
                            dynamic_border("Сначала войдите в систему!", Fore.RED)
                    except:
                        dynamic_border("Используйте: eup buy [дни]", Fore.RED)
                
                elif action.startswith("eup_plus buy"):
                    try:
                        days = int(action.split()[2])
                        if casino.current_user:
                            casino.current_user.buy_eup_plus(days)
                        else:
                            dynamic_border("Сначала войдите в систему!", Fore.RED)
                    except:
                        dynamic_border("Используйте: eup_plus buy [дни]", Fore.RED)
                
                elif action == "eup status":
                    if casino.current_user:
                        casino.current_user.eup_status()
                    else:
                        dynamic_border("Пользователь не выбран!", Fore.RED)
                
                elif action == "eup autonone":
                    if casino.current_user:
                        casino.current_user.eup_autonone()
                    else:
                        dynamic_border("Пользователь не выбран!", Fore.RED)
                
                elif action == "achievements":
                    if casino.current_user:
                        casino.achievements.show_achievements(casino.current_user.username)
                    else:
                        dynamic_border("Пользователь не выбран!", Fore.RED)
                
                elif action == "exit":
                    if casino.current_user:
                        casino.current_user.end_session()
                    casino.network.disconnect()
                    casino.save_users()
                    
                    if RICH_AVAILABLE:
                        console.print("[bold green]До скорой встречи! Ваш прогресс сохранен.[/bold green]")
                    else:
                        print(gradient_text("\nДо скорой встречи! Ваш прогресс сохранен.\n", [Fore.GREEN, Fore.BLUE]))
                    break
                
                else:
                    dynamic_border("Неизвестная команда. Введите 'help' для справки", Fore.RED)
            
            except (IndexError, ValueError) as e:
                dynamic_border(f"Ошибка ввода: {str(e)}", Fore.RED)
            except Exception as e:
                dynamic_border(f"Неизвестная ошибка: {str(e)}", Fore.RED)
    
    except KeyboardInterrupt:
        dynamic_border("\nЭкстренное сохранение...", Fore.RED)
        if casino.current_user:
            casino.current_user.end_session()
        casino.network.disconnect()
        casino.save_users()
        dynamic_border("Прогресс сохранен. До свидания!", Fore.GREEN)
        sys.exit(0)

if __name__ == "__main__":
    for path in [SAVE_PATH, KEYS_PATH, RECEIPTS_PATH, CS_LOG_PATH, FORUM_PATH, ACHIEVEMENTS_PATH]:
        os.makedirs(os.path.dirname(path), exist_ok=True)
    main()