import random
import json
import time
import os
import textwrap
import hashlib
import secrets
import logging
import sys
from typing import Dict, List, Optional, Any, Tuple
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
RESERVES_PATH = "data/reserves.json"

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

class CreditRisk(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class StakingPlan(Enum):
    FLEXIBLE = "flexible"
    FIXED_7D = "fixed_7d"
    FIXED_30D = "fixed_30d"
    VIP = "vip"

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
class CreditContract:
    id: str
    username: str
    currency: str
    amount: Decimal
    interest_rate: Decimal
    daily_interest: Decimal
    taken_date: str
    due_date: str
    days_passed: int = 0
    total_paid: Decimal = Decimal('0')
    penalty_days: int = 0
    status: str = "active"
    lender: CreditRisk = CreditRisk.MEDIUM
    
    def to_dict(self) -> dict:
        data = asdict(self)
        data['interest_rate'] = format(float(self.interest_rate), 'f')
        data['daily_interest'] = format(float(self.daily_interest), 'f')
        data['amount'] = float(self.amount)
        data['total_paid'] = float(self.total_paid)
        data['lender'] = self.lender.value
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CreditContract':
        data['interest_rate'] = Decimal(str(data['interest_rate']))
        data['daily_interest'] = Decimal(str(data['daily_interest']))
        data['amount'] = Decimal(str(data['amount']))
        data['total_paid'] = Decimal(str(data.get('total_paid', 0)))
        data['lender'] = CreditRisk(data['lender'])
        return cls(**data)

@dataclass
class StakingContract:
    id: str
    username: str
    currency: str
    amount: Decimal
    plan: StakingPlan
    interest_rate: Decimal
    start_date: str
    end_date: Optional[str] = None
    days_staked: int = 0
    total_earned: Decimal = Decimal('0')
    last_claim_date: Optional[str] = None
    status: str = "active"
    
    def to_dict(self) -> dict:
        data = asdict(self)
        data['interest_rate'] = format(float(self.interest_rate), 'f')
        data['amount'] = float(self.amount)
        data['total_earned'] = float(self.total_earned)
        data['plan'] = self.plan.value
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'StakingContract':
        data['interest_rate'] = Decimal(str(data['interest_rate']))
        data['amount'] = Decimal(str(data['amount']))
        data['total_earned'] = Decimal(str(data.get('total_earned', 0)))
        data['plan'] = StakingPlan(data['plan'])
        return cls(**data)

@dataclass
class UserReserve:
    currency: str
    balance: Decimal
    created_at: str
    last_fee_date: str
    
    def to_dict(self) -> dict:
        return {
            "currency": self.currency,
            "balance": float(self.balance),
            "created_at": self.created_at,
            "last_fee_date": self.last_fee_date
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'UserReserve':
        return cls(
            currency=data["currency"],
            balance=Decimal(str(data["balance"])),
            created_at=data["created_at"],
            last_fee_date=data["last_fee_date"]
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
    reserves: Dict[str, UserReserve] = field(default_factory=dict)

class CreditSystem:
    def __init__(self, market):
        self.market = market
        self.contracts: Dict[str, CreditContract] = {}
        self.vaults: Dict[str, Decimal] = {}
        self.load_data()
    
    def load_data(self):
        try:
            os.makedirs(os.path.dirname("data/credits.json"), exist_ok=True)
            if os.path.exists("data/credits.json"):
                with open("data/credits.json", 'r') as f:
                    data = json.load(f)
                    for contract_data in data.get('contracts', []):
                        contract = CreditContract.from_dict(contract_data)
                        self.contracts[contract.id] = contract
            
            if os.path.exists("data/bank_vaults.json"):
                with open("data/bank_vaults.json", 'r') as f:
                    vaults_data = json.load(f)
                    self.vaults = {k: Decimal(str(v)) for k, v in vaults_data.items()}
            else:
                self.vaults = {coin: Decimal('100000') for coin in self.market.rates.keys()}
                self.save_vaults()
        except Exception as e:
            logger.error(f"Ошибка загрузки кредитов: {e}")
    
    def save_data(self):
        try:
            data = {
                'contracts': [contract.to_dict() for contract in self.contracts.values()],
                'updated_at': datetime.now().isoformat()
            }
            with open("data/credits.json", 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Ошибка сохранения кредитов: {e}")
    
    def save_vaults(self):
        try:
            vaults_float = {k: float(v) for k, v in self.vaults.items()}
            with open("data/bank_vaults.json", 'w') as f:
                json.dump(vaults_float, f, indent=4)
        except Exception as e:
            logger.error(f"Ошибка сохранения резервов: {e}")
    
    def get_credit_offers(self, currency: str, user_level: int) -> List[Dict]:
        offers = []
        for risk in CreditRisk:
            base_rate = {
                CreditRisk.LOW: Decimal('0.15'),
                CreditRisk.MEDIUM: Decimal('0.22'),
                CreditRisk.HIGH: Decimal('0.30')
            }[risk]
            
            level_bonus = Decimal(str(user_level)) * Decimal('0.001')
            final_rate = base_rate - level_bonus
            final_rate = max(Decimal('0.15'), min(Decimal('0.30'), final_rate))
            
            max_amount = self.vaults.get(currency, Decimal('0')) * Decimal('0.1')
            
            offers.append({
                'lender': risk.value,
                'name': self._get_lender_name(risk),
                'interest_rate': float(final_rate),
                'daily_interest_percent': float(final_rate * Decimal('100')),
                'max_amount': float(max_amount),
                'description': self._get_lender_description(risk),
                'color': self._get_lender_color(risk)
            })
        
        return offers
    
    def _get_lender_name(self, risk: CreditRisk) -> str:
        names = {
            CreditRisk.LOW: "🏛️ EXTRACT Банк",
            CreditRisk.MEDIUM: "💼 Быстрые Кредиты",
            CreditRisk.HIGH: "⚡ Мгновенные Займы"
        }
        return names.get(risk, "Неизвестный кредитор")
    
    def _get_lender_description(self, risk: CreditRisk) -> str:
        desc = {
            CreditRisk.LOW: "Надежный банк с низкими процентами",
            CreditRisk.MEDIUM: "Средний риск, быстрая выдача",
            CreditRisk.HIGH: "Высокий риск, мгновенное одобрение"
        }
        return desc.get(risk, "")
    
    def _get_lender_color(self, risk: CreditRisk) -> str:
        colors = {
            CreditRisk.LOW: Fore.GREEN,
            CreditRisk.MEDIUM: Fore.YELLOW,
            CreditRisk.HIGH: Fore.RED
        }
        return colors.get(risk, Fore.WHITE)
    
    def take_credit(self, username: str, currency: str, amount: Decimal, lender_type: CreditRisk) -> Optional[CreditContract]:
        if self.vaults.get(currency, Decimal('0')) < amount:
            return None
        
        offers = self.get_credit_offers(currency, 1)
        offer = next((o for o in offers if o['lender'] == lender_type.value), None)
        if not offer:
            return None
        
        interest_rate = Decimal(str(offer['interest_rate']))
        daily_interest = amount * interest_rate / Decimal('365')
        
        contract = CreditContract(
            id=secrets.token_hex(8),
            username=username,
            currency=currency,
            amount=amount,
            interest_rate=interest_rate,
            daily_interest=daily_interest,
            taken_date=datetime.now().isoformat(),
            due_date=(datetime.now() + timedelta(days=1)).isoformat(),
            lender=lender_type
        )
        
        self.vaults[currency] -= amount
        self.contracts[contract.id] = contract
        
        self.save_data()
        self.save_vaults()
        
        return contract
    
    def calculate_daily_interest(self, contract_id: str) -> Decimal:
        if contract_id not in self.contracts:
            return Decimal('0')
        
        contract = self.contracts[contract_id]
        today = datetime.now()
        due_date = datetime.fromisoformat(contract.due_date)
        
        if today <= due_date:
            return Decimal('0')
        
        days_overdue = (today - due_date).days
        if days_overdue > contract.penalty_days:
            new_days = days_overdue - contract.penalty_days
            additional_interest = contract.daily_interest * Decimal(str(new_days))
            contract.penalty_days = days_overdue
            self.save_data()
            return additional_interest
        
        return Decimal('0')
    
    def pay_credit(self, contract_id: str, user_balance: Dict[str, Decimal]) -> Tuple[bool, str]:
        if contract_id not in self.contracts:
            return False, "Кредит не найден"
        
        contract = self.contracts[contract_id]
        
        interest_due = self.calculate_daily_interest(contract_id)
        total_due = contract.amount + interest_due
        
        if user_balance.get(contract.currency, Decimal('0')) < total_due:
            return False, f"Недостаточно средств. Нужно: {float(total_due):.4f} {contract.currency}"
        
        user_balance[contract.currency] -= total_due
        
        self.vaults[contract.currency] = self.vaults.get(contract.currency, Decimal('0')) + contract.amount
        
        contract.status = "repaid"
        contract.total_paid = total_due
        
        self.save_data()
        self.save_vaults()
        
        return True, f"Кредит погашен. Возвращено: {float(total_due):.4f} {contract.currency}"
    
    def get_user_credits(self, username: str) -> List[CreditContract]:
        return [c for c in self.contracts.values() if c.username == username and c.status == "active"]
    
    def update_credit_statuses(self):
        today = datetime.now()
        updated = False
        
        for contract in self.contracts.values():
            if contract.status != "active":
                continue
            
            due_date = datetime.fromisoformat(contract.due_date)
            if today > due_date + timedelta(days=7):
                contract.status = "defaulted"
                updated = True
        
        if updated:
            self.save_data()
    
    def get_credit_stats(self) -> Dict:
        active = [c for c in self.contracts.values() if c.status == "active"]
        defaulted = [c for c in self.contracts.values() if c.status == "defaulted"]
        
        total_issued = sum(c.amount for c in self.contracts.values())
        total_repaid = sum(c.total_paid for c in self.contracts.values())
        
        return {
            "active_contracts": len(active),
            "defaulted_contracts": len(defaulted),
            "total_issued": float(total_issued),
            "total_repaid": float(total_repaid),
            "bank_reserves": {k: float(v) for k, v in self.vaults.items()}
        }

class StakingSystem:
    def __init__(self, market):
        self.market = market
        self.contracts: Dict[str, StakingContract] = {}
        self.staking_pools: Dict[str, Dict] = {}
        self.load_data()
    
    def load_data(self):
        try:
            os.makedirs(os.path.dirname("data/staking.json"), exist_ok=True)
            if os.path.exists("data/staking.json"):
                with open("data/staking.json", 'r') as f:
                    data = json.load(f)
                    for contract_data in data.get('contracts', []):
                        contract = StakingContract.from_dict(contract_data)
                        self.contracts[contract.id] = contract
            
            self._init_staking_pools()
        except Exception as e:
            logger.error(f"Ошибка загрузки стейкинга: {e}")
            self._init_staking_pools()
    
    def _init_staking_pools(self):
        base_rates = {
            "EXTRACT": Decimal('0.0005'),
            "BTC": Decimal('0.0003'),
            "ETH": Decimal('0.0004'),
            "BETASTD": Decimal('0.0010'),
            "DOGCOIN": Decimal('0.0008'),
        }
        
        for coin in self.market.rates.keys():
            self.staking_pools[coin] = {
                'total_staked': Decimal('0'),
                'base_rate': base_rates.get(coin, Decimal('0.0002')),
                'users': 0
            }
    
    def save_data(self):
        try:
            data = {
                'contracts': [contract.to_dict() for contract in self.contracts.values()],
                'updated_at': datetime.now().isoformat(),
                'pools': {k: {'total_staked': float(v['total_staked']), 'users': v['users']} 
                         for k, v in self.staking_pools.items()}
            }
            with open("data/staking.json", 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Ошибка сохранения стейкинга: {e}")
    
    def get_staking_plans(self, currency: str, has_eup_plus: bool = False) -> List[Dict]:
        base_rate = self.staking_pools[currency]['base_rate']
        
        plans = []
        
        plans.append({
            'id': StakingPlan.FLEXIBLE.value,
            'name': 'Гибкий вклад',
            'lock_period': 0,
            'interest_rate': float(base_rate * Decimal('0.5')),
            'description': 'Можно забрать в любой момент',
            'min_amount': 1,
            'color': 'blue'
        })
        
        plans.append({
            'id': StakingPlan.FIXED_7D.value,
            'name': '7-дневный вклад',
            'lock_period': 7,
            'interest_rate': float(base_rate * Decimal('2.0')),
            'description': 'Заблокировано на 7 дней',
            'min_amount': 10,
            'color': 'green'
        })
        
        plans.append({
            'id': StakingPlan.FIXED_30D.value,
            'name': '30-дневный вклад',
            'lock_period': 30,
            'interest_rate': float(base_rate * Decimal('3.5')),
            'description': 'Заблокировано на 30 дней',
            'min_amount': 100,
            'color': 'yellow'
        })
        
        if has_eup_plus:
            plans.append({
                'id': StakingPlan.VIP.value,
                'name': 'VIP вклад 🏆',
                'lock_period': 90,
                'interest_rate': float(base_rate * Decimal('5.0')),
                'description': 'Только для EUP+. Максимальная доходность',
                'min_amount': 1000,
                'color': 'magenta'
            })
        
        return plans
    
    def open_staking(self, username: str, currency: str, amount: Decimal, 
                    plan: StakingPlan, has_eup_plus: bool = False) -> Optional[StakingContract]:
        
        if plan == StakingPlan.VIP and not has_eup_plus:
            return None
        
        plans = self.get_staking_plans(currency, has_eup_plus)
        selected_plan = next((p for p in plans if p['id'] == plan.value), None)
        if not selected_plan:
            return None
        
        if amount < Decimal(str(selected_plan['min_amount'])):
            return None
        
        start_date = datetime.now()
        end_date = None
        if plan != StakingPlan.FLEXIBLE:
            end_date = start_date + timedelta(days=selected_plan['lock_period'])
        
        contract = StakingContract(
            id=secrets.token_hex(8),
            username=username,
            currency=currency,
            amount=amount,
            plan=plan,
            interest_rate=Decimal(str(selected_plan['interest_rate'])),
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat() if end_date else None,
            last_claim_date=start_date.isoformat()
        )
        
        self.staking_pools[currency]['total_staked'] += amount
        self.staking_pools[currency]['users'] += 1
        
        self.contracts[contract.id] = contract
        self.save_data()
        
        return contract
    
    def calculate_earnings(self, contract_id: str) -> Decimal:
        if contract_id not in self.contracts:
            return Decimal('0')
        
        contract = self.contracts[contract_id]
        
        if contract.end_date:
            end_date = datetime.fromisoformat(contract.end_date)
            if datetime.now() < end_date and contract.plan != StakingPlan.FLEXIBLE:
                return Decimal('-1')
        
        last_claim = datetime.fromisoformat(contract.last_claim_date)
        days_passed = (datetime.now() - last_claim).days
        
        if days_passed <= 0:
            return Decimal('0')
        
        daily_earnings = contract.amount * contract.interest_rate
        total_earnings = daily_earnings * Decimal(str(days_passed))
        
        return total_earnings
    
    def claim_earnings(self, contract_id: str, user_balance: Dict[str, Decimal]) -> Tuple[bool, str, Decimal]:
        earnings = self.calculate_earnings(contract_id)
        
        if earnings == Decimal('-1'):
            return False, "Вклад заблокирован до окончания срока", Decimal('0')
        
        if earnings <= Decimal('0'):
            return False, "Нет накопленных процентов", Decimal('0')
        
        contract = self.contracts[contract_id]
        contract.total_earned += earnings
        contract.last_claim_date = datetime.now().isoformat()
        
        user_balance[contract.currency] = user_balance.get(contract.currency, Decimal('0')) + earnings
        
        self.save_data()
        
        return True, f"Получено: {float(earnings):.4f} {contract.currency}", earnings
    
    def close_staking(self, contract_id: str, user_balance: Dict[str, Decimal]) -> Tuple[bool, str]:
        if contract_id not in self.contracts:
            return False, "Вклад не найден"
        
        contract = self.contracts[contract_id]
        
        if contract.end_date:
            end_date = datetime.fromisoformat(contract.end_date)
            if datetime.now() < end_date and contract.plan != StakingPlan.FLEXIBLE:
                penalty = contract.amount * Decimal('0.1')
                return_amount = contract.amount - penalty
                message = f"Досрочное закрытие. Штраф 10%. Возвращено: {float(return_amount):.4f}"
            else:
                return_amount = contract.amount
                message = f"Вклад закрыт. Возвращено: {float(return_amount):.4f}"
        else:
            return_amount = contract.amount
            message = f"Вклад закрыт. Возвращено: {float(return_amount):.4f}"
        
        user_balance[contract.currency] = user_balance.get(contract.currency, Decimal('0')) + return_amount
        
        self.staking_pools[contract.currency]['total_staked'] -= contract.amount
        self.staking_pools[contract.currency]['users'] = max(0, self.staking_pools[contract.currency]['users'] - 1)
        
        contract.status = "completed"
        
        self.save_data()
        
        return True, message
    
    def get_user_stakes(self, username: str) -> List[StakingContract]:
        return [s for s in self.contracts.values() if s.username == username and s.status == "active"]
    
    def get_staking_stats(self) -> Dict:
        active_stakes = [s for s in self.contracts.values() if s.status == "active"]
        
        total_staked = {}
        for stake in active_stakes:
            total_staked[stake.currency] = total_staked.get(stake.currency, Decimal('0')) + stake.amount
        
        return {
            "total_contracts": len(active_stakes),
            "total_staked": {k: float(v) for k, v in total_staked.items()},
            "pools": {k: {'total_staked': float(v['total_staked']), 'users': v['users']} 
                     for k, v in self.staking_pools.items() if v['total_staked'] > 0}
        }
    
    def update_staking_earnings(self):
        today = datetime.now()
        updated = False
        
        for contract in self.contracts.values():
            if contract.status != "active":
                continue
            
            if contract.plan == StakingPlan.VIP:
                last_update = datetime.fromisoformat(contract.last_claim_date)
                if (today - last_update).days >= 1:
                    daily_earnings = contract.amount * contract.interest_rate
                    contract.total_earned += daily_earnings
                    contract.last_claim_date = today.isoformat()
                    updated = True
        
        if updated:
            self.save_data()

class ReserveSystem:
    def __init__(self):
        self.reserves: Dict[str, Dict[str, UserReserve]] = {}
        self.load_reserves()
    
    def load_reserves(self):
        try:
            os.makedirs(os.path.dirname(RESERVES_PATH), exist_ok=True)
            if os.path.exists(RESERVES_PATH):
                with open(RESERVES_PATH, 'r') as f:
                    data = json.load(f)
                    for username, user_reserves in data.items():
                        self.reserves[username] = {}
                        for currency, reserve_data in user_reserves.items():
                            self.reserves[username][currency] = UserReserve.from_dict(reserve_data)
            else:
                self.reserves = {}
        except Exception as e:
            logger.error(f"Ошибка загрузки резервов: {e}")
            self.reserves = {}
    
    def save_reserves(self):
        try:
            data = {}
            for username, user_reserves in self.reserves.items():
                data[username] = {}
                for currency, reserve in user_reserves.items():
                    data[username][currency] = reserve.to_dict()
            
            with open(RESERVES_PATH, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Ошибка сохранения резервов: {e}")
    
    def create_reserve(self, username: str, currency: str, amount: Decimal, has_eup_plus: bool) -> bool:
        if username not in self.reserves:
            self.reserves[username] = {}
        
        if currency in self.reserves[username]:
            return False
        
        reserve = UserReserve(
            currency=currency,
            balance=amount,
            created_at=datetime.now().isoformat(),
            last_fee_date=datetime.now().isoformat()
        )
        
        self.reserves[username][currency] = reserve
        self.save_reserves()
        return True
    
    def put_to_reserve(self, username: str, currency: str, amount: Decimal, has_eup_plus: bool) -> Tuple[bool, str]:
        if username not in self.reserves or currency not in self.reserves[username]:
            return False, f"Сначала создайте резерв для {currency}"
        
        reserve = self.reserves[username][currency]
        
        today = datetime.now()
        last_fee_date = datetime.fromisoformat(reserve.last_fee_date)
        
        if (today - last_fee_date).days >= 7:
            fee_percent = Decimal('0.001') if has_eup_plus else Decimal('0.02')
            fee = reserve.balance * fee_percent
            reserve.balance -= fee
            reserve.last_fee_date = today.isoformat()
        
        reserve.balance += amount
        self.save_reserves()
        
        return True, f"Положили в резерв: {float(amount):.2f} {currency}. Текущий баланс: {float(reserve.balance):.2f}"
    
    def take_from_reserve(self, username: str, currency: str, amount: Decimal, has_eup_plus: bool) -> Tuple[bool, str]:
        if username not in self.reserves or currency not in self.reserves[username]:
            return False, f"Резерв для {currency} не найден"
        
        reserve = self.reserves[username][currency]
        
        today = datetime.now()
        last_fee_date = datetime.fromisoformat(reserve.last_fee_date)
        
        if (today - last_fee_date).days >= 7:
            fee_percent = Decimal('0.001') if has_eup_plus else Decimal('0.02')
            fee = reserve.balance * fee_percent
            reserve.balance -= fee
            reserve.last_fee_date = today.isoformat()
        
        if reserve.balance < amount:
            return False, f"Недостаточно средств в резерве. Доступно: {float(reserve.balance):.2f}"
        
        reserve.balance -= amount
        self.save_reserves()
        
        return True, f"Взяли из резерва: {float(amount):.2f} {currency}. Остаток: {float(reserve.balance):.2f}"
    
    def get_user_reserves(self, username: str, has_eup_plus: bool) -> List[Dict]:
        if username not in self.reserves:
            return []
        
        today = datetime.now()
        user_reserves = []
        
        for currency, reserve in self.reserves[username].items():
            last_fee_date = datetime.fromisoformat(reserve.last_fee_date)
            days_until_fee = 7 - (today - last_fee_date).days
            days_until_fee = max(0, days_until_fee)
            
            fee_percent = 0.1 if has_eup_plus else 2.0
            next_fee_date = last_fee_date + timedelta(days=7)
            
            user_reserves.append({
                'currency': currency,
                'balance': float(reserve.balance),
                'created_at': reserve.created_at[:10],
                'next_fee_date': next_fee_date.strftime('%d.%m.%Y'),
                'days_until_fee': days_until_fee,
                'fee_percent': fee_percent
            })
        
        return user_reserves
    
    def get_reserve_balance(self, username: str, currency: str) -> Decimal:
        if username in self.reserves and currency in self.reserves[username]:
            return self.reserves[username][currency].balance
        return Decimal('0')
    
    def update_all_fees(self):
        today = datetime.now()
        updated = False
        
        for username, user_reserves in self.reserves.items():
            for currency, reserve in user_reserves.items():
                last_fee_date = datetime.fromisoformat(reserve.last_fee_date)
                if (today - last_fee_date).days >= 7:
                    user = None
                    for user_obj in casino.users.values():
                        if user_obj.username == username:
                            user = user_obj
                            break
                    
                    if user:
                        has_eup_plus = (user.data.subscription.type == SubscriptionType.EUP_PLUS and 
                                       user.has_active_subscription())
                        fee_percent = Decimal('0.001') if has_eup_plus else Decimal('0.02')
                        fee = reserve.balance * fee_percent
                        reserve.balance -= fee
                        reserve.last_fee_date = today.isoformat()
                        updated = True
        
        if updated:
            self.save_reserves()

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
                price_scale.append(max_val - i * step)
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
░█▀▀░█░█░▀█▀░█▀▄░█▀█░█▀▀░▀█▀
░█▀▀░▄▀▄░░█░░█▀▄░█▀█░█░░░░█░
░▀▀▀░▀░▀░░▀░░▀░▀░▀░▀░▀▀▀░░▀░
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
        data_dict["reserves"] = {currency: reserve.to_dict() for currency, reserve in self.data.reserves.items()}
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
        
        if "reserves" in data:
            user.data.reserves = {}
            for currency, reserve_data in data["reserves"].items():
                user.data.reserves[currency] = UserReserve.from_dict(reserve_data)
        
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
    
    def show_stats(self, credit_stats=None, stake_stats=None, reserve_stats=None):
        THEME = {
            'eup': Fore.CYAN,
            'eup_plus': Fore.YELLOW,
            'base': Fore.GREEN,
            'stats': Fore.MAGENTA,
            'transactions': Fore.WHITE
        }
        
        width = 50
        
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
            f"{THEME['base']}╭{'─'*(width-2)}╮",
            f"│{'ПРОФИЛЬ ПОДПИСКИ'.center(width-2)}│",
            f"├{'─'*(width-2)}┤",
            f"    {sub_header.ljust(width-8)}{THEME['base']}"
        ]
        profile.extend(sub_details)
        profile.extend([
            f"{THEME['base']}╭{'─'*(width-2)}╮",
            f"│{'ОСНОВНАЯ СТАТИСТИКА'.center(width-2)}│",
            f"├{'─'*(width-2)}┤",
            f"  {Fore.YELLOW}Баланс: {float(self.data.crypto_balance['EXTRACT']):,.2f} {CURRENCY}",
            f"  {THEME['stats']}WLR: {self.win_loss_ratio()}%",
            f"  {THEME['stats']}Игр: {self.data.games_played}  🏆 {self.data.wins}  💀 {self.data.losses}",
            f"{THEME['base']} ─{'─'*(width-4)} ",
            f"  {THEME['stats']}Уровень: {self.data.level}",
            f"  {THEME['stats']}{self.show_level_progress()}"
        ])
        
        hours = int(self.data.play_time // 3600)
        minutes = int((self.data.play_time % 3600) // 60)
        seconds = int(self.data.play_time % 60)
        profile.append(f"  {Fore.CYAN}Время в игре: {hours:02d}:{minutes:02d}:{seconds:02d}")
        
        top_coins = sorted(
            [(k, v) for k, v in self.data.crypto_balance.items() if v > Decimal('0') and k != "EXTRACT"],
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        if top_coins:
            profile.extend([
                f"{THEME['base']}╭{'─'*(width-2)}╮",
                f"│{'ТОП АКТИВЫ'.center(width-2)}│",
                f"├{'─'*(width-2)}┤",
            ])
            for coin, amount in top_coins:
                profile.append(f"  {THEME['stats']}{CRYPTO_SYMBOLS[coin]} {coin}: {float(amount):>12.2f}")
        
        if credit_stats is not None:
            if credit_stats:
                total_credit = sum(c.amount for c in credit_stats)
                profile.append(f"  {Fore.RED}Кредиты: {len(credit_stats)} на сумму {float(total_credit):.2f}")
            else:
                profile.append(f"  {Fore.GREEN}Активных кредитов нет")
        
        if stake_stats is not None:
            if stake_stats:
                total_stake = sum(s.amount for s in stake_stats)
                total_earned = sum(s.total_earned for s in stake_stats)
                profile.append(f"  {Fore.GREEN}Вклады: {len(stake_stats)} на сумму {float(total_stake):.2f}")
                profile.append(f"  {Fore.YELLOW}Заработано вкладами: {float(total_earned):.2f}")
            else:
                profile.append(f"  {Fore.GREEN}Активных вкладов нет")
        
        if reserve_stats is not None:
            if reserve_stats:
                total_reserve = sum(r['balance'] for r in reserve_stats)
                profile.append(f"  {Fore.BLUE}Резервы: {len(reserve_stats)} на сумму {float(total_reserve):.2f}")
            else:
                profile.append(f"  {Fore.GREEN}Резервов нет")
        
        if self.data.transactions:
            profile.extend([
                f"{THEME['base']}╭{'─'*(width-2)}╮",
                f"│{'ПОСЛЕДНИЕ ТРАНЗАКЦИИ'.center(width-2)}│",
                f"├{'─'*(width-2)}┤",
            ])
            for t in self.data.transactions[:6]:
                if t.action in ['buy', 'sell']:
                    action_icon = "+" if t.action == 'buy' else "-"
                    action_color = Fore.GREEN if t.action == 'buy' else Fore.RED
                    line = f"  {action_icon} {t.timestamp[5:16]} {action_color}{t.action.upper()} {float(t.amount):.2f} {t.coin} {THEME['transactions']}за {float(t.total)}{CURRENCY}"
                    if len(line) > width - 4:
                        line = line[:width-7] + "..."
                    profile.append(line)
                elif t.action == 'transfer_in':
                    line = f"  + {t.timestamp[5:16]} {Fore.GREEN}Получено {float(t.amount):.2f} {t.coin} от {t.from_user}"
                    if len(line) > width - 4:
                        line = line[:width-7] + "..."
                    profile.append(line)
                elif t.action == 'transfer_out':
                    line = f"  - {t.timestamp[5:16]} {Fore.RED}Переведено {float(t.amount):.2f} {t.coin} комиссия: {float(t.commission):.2f}"
                    if len(line) > width - 4:
                        line = line[:width-7] + "..."
                    profile.append(line)
        
        profile.append(f"{THEME['base']} ─{'─'*(width-4)} ")
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
            bonus = Decimal('2000000')
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
        self.credit_system = CreditSystem(self.market)
        self.staking_system = StakingSystem(self.market)
        self.reserve_system = ReserveSystem()
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
        print(f"2. Черное (x2)")
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
    
    def chart_now(self, coin: str):
        if not self.current_user:
            print(f"{Fore.RED}Сначала выберите пользователя! add/login [ник]")
            return
        
        coin = coin.upper()
        if coin not in self.market.rates:
            print(f"{Fore.RED}Неизвестная валюта: {coin}")
            return
        
        def clear_screen():
            os.system('cls' if os.name == 'nt' else 'clear')
            print_art()
            print(f"{Fore.CYAN}{'═'*60}")
            print(f"{Fore.YELLOW}CHART-NOW: {coin} - Интерактивная торговля")
            print(f"{Fore.CYAN}{'═'*60}")
        
        selected_button = 0
        buttons = ["[КУПИТЬ]", "[ПРОДАТЬ]"]
        
        while True:
            clear_screen()
            
            rate = self.market.get_rate(coin)
            current_balance = self.current_user.data.crypto_balance.get(coin, Decimal('0'))
            extract_balance = self.current_user.data.crypto_balance.get("EXTRACT", Decimal('0'))
            
            print(f"{Fore.GREEN}Текущий курс: 1 {coin} = {float(rate):.2f} {CURRENCY}")
            print(f"{Fore.YELLOW}Ваш баланс: {float(current_balance):.4f} {coin} | {float(extract_balance):.2f} {CURRENCY}")
            
            self.market.print_chart(coin)
            
            print(f"\n{Fore.CYAN}{'═'*60}")
            print(f"{Fore.WHITE}Управление: a / d - переключение | Enter - выбор | Q - выход")
            print(f"{Fore.CYAN}{'═'*60}")
            
            button_line = ""
            for i, btn in enumerate(buttons):
                if i == selected_button:
                    button_line += f"{Style.BRIGHT}{Fore.GREEN}{btn}{Style.RESET_ALL} "
                else:
                    button_line += f"{Fore.WHITE}{btn} "
            print(f"\n{button_line}\n")
            
            try:
                import msvcrt
                key = msvcrt.getch().decode('utf-8', errors='ignore').lower()
            except:
                try:
                    import tty, termios
                    fd = sys.stdin.fileno()
                    old_settings = termios.tcgetattr(fd)
                    try:
                        tty.setraw(sys.stdin.fileno())
                        key = sys.stdin.read(1).lower()
                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                except:
                    key = input(f"{Fore.YELLOW}Введите команду (←/→/enter/q): ").strip().lower()
            
            if key in ['q', 'й']:
                print(f"{Fore.YELLOW}Выход из режима торговли...")
                time.sleep(0.5)
                clear_screen()
                return
            elif key in ['\r', '\n']:
                if selected_button == 0:
                    print(f"\n{Fore.CYAN}КУПИТЬ {coin}")
                    try:
                        amount = Decimal(input(f"{Fore.YELLOW}Введите количество {coin}: "))
                        if amount <= Decimal('0'):
                            print(f"{Fore.RED}Количество должно быть положительным!")
                            time.sleep(1)
                            continue
                        
                        cost = amount * rate * Decimal('1.01')
                        if extract_balance < cost:
                            print(f"{Fore.RED}Недостаточно средств!")
                            time.sleep(1)
                            continue
                        
                        self.current_user.data.crypto_balance["EXTRACT"] -= cost
                        self.current_user.data.crypto_balance[coin] = current_balance + amount
                        self.current_user.add_transaction('buy', coin, amount, cost)
                        self.market.update_rates()
                        self.save_users()
                        
                        print(f"{Fore.GREEN}Куплено {float(amount):.4f} {coin} за {float(cost):.2f} {CURRENCY}")
                        time.sleep(1)
                        continue
                    except:
                        print(f"{Fore.RED}Ошибка ввода!")
                        time.sleep(1)
                        continue
                else:
                    print(f"\n{Fore.CYAN}ПРОДАТЬ {coin}")
                    try:
                        amount = Decimal(input(f"{Fore.YELLOW}Введите количество {coin}: "))
                        if amount <= Decimal('0'):
                            print(f"{Fore.RED}Количество должно быть положительным!")
                            time.sleep(1)
                            continue
                        
                        if current_balance < amount:
                            print(f"{Fore.RED}Недостаточно {coin}!")
                            time.sleep(1)
                            continue
                        
                        value = amount * rate * Decimal('0.99')
                        self.current_user.data.crypto_balance[coin] = current_balance - amount
                        self.current_user.data.crypto_balance["EXTRACT"] += value
                        self.current_user.add_transaction('sell', coin, amount, value)
                        self.market.update_rates()
                        self.save_users()
                        
                        print(f"{Fore.GREEN}Продано {float(amount):.4f} {coin} за {float(value):.2f} {CURRENCY}")
                        time.sleep(1)
                        continue
                    except:
                        print(f"{Fore.RED}Ошибка ввода!")
                        time.sleep(1)
                        continue
            elif key in ['a', 'ф', ',', '<']:
                selected_button = (selected_button - 1) % len(buttons)
            elif key in ['d', 'в', '.', '>']:
                selected_button = (selected_button + 1) % len(buttons)
    
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
{Fore.BLUE}chart -now [монета]          {Fore.WHITE}- Интерактивная торговля с графиком
{Fore.WHITE}       ---Игровые события---
{Fore.WHITE}monthly                     {Fore.WHITE}- Текущее месячное событие
{Fore.WHITE}promo [код]                {Fore.WHITE}- Активировать промокод
{Fore.WHITE}        ---Кредиты и Вклады---
{Fore.GREEN}credit offers              {Fore.WHITE}- Показать кредитные предложения
{Fore.GREEN}credit take [тип] [валюта] [сумма]{Fore.WHITE}- Взять кредит (тип: low/medium/high)
{Fore.GREEN}credit my                  {Fore.WHITE}- Мои активные кредиты
{Fore.GREEN}credit pay [id]            {Fore.WHITE}- Погасить кредит
{Fore.GREEN}stake offers               {Fore.WHITE}- Показать предложения по стейкингу
{Fore.GREEN}stake open [план] [валюта] [сумма]{Fore.WHITE}- Открыть вклад (план: flexible/fixed_7d/fixed_30d/vip)
{Fore.GREEN}stake my                   {Fore.WHITE}- Мои активные вклады
{Fore.GREEN}stake claim [id]           {Fore.WHITE}- Забрать проценты со вклада
{Fore.GREEN}stake close [id]           {Fore.WHITE}- Закрыть вклад
{Fore.GREEN}bank stats                 {Fore.WHITE}- Статистика банка
{Fore.GREEN}reserv create [валюта] [сумма]{Fore.WHITE}- Создать резерв
{Fore.GREEN}reserv put [валюта] [сумма]{Fore.WHITE}- Положить в резерв
{Fore.GREEN}reserv take [валюта] [сумма]{Fore.WHITE}- Взять из резерва
{Fore.GREEN}reserv show                {Fore.WHITE}- Показать мои резервы
{Fore.GREEN}reserv info                {Fore.WHITE}- Информация о резервах
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
            self.credit_system.update_credit_statuses()
            self.staking_system.update_staking_earnings()
            self.reserve_system.update_all_fees()
            self.save_users()
            self.last_save = time.time()
    
    def show_profile(self):
        if not self.current_user:
            print(f"{Fore.RED}Пользователь не выбран! Загрузитесь в аккаунт.")
            return
        
        has_eup_plus = (self.current_user.data.subscription.type == SubscriptionType.EUP_PLUS and 
                       self.current_user.has_active_subscription())
        
        credit_stats = self.credit_system.get_user_credits(self.current_user.username)
        stake_stats = self.staking_system.get_user_stakes(self.current_user.username)
        reserve_stats = self.reserve_system.get_user_reserves(self.current_user.username, has_eup_plus)
        
        self.current_user.show_stats(
            credit_stats=credit_stats,
            stake_stats=stake_stats,
            reserve_stats=reserve_stats
        )
    
    def show_credit_offers(self):
        if not self.current_user:
            return
        
        print(dynamic_border(f"{Fore.CYAN}КРЕДИТНЫЕ ПРЕДЛОЖЕНИЯ", Fore.CYAN))
        
        available_currencies = ["EXTRACT", "BTC", "ETH", "BETASTD", "DOGCOIN"]
        
        for currency in available_currencies:
            offers = self.credit_system.get_credit_offers(currency, self.current_user.data.level)
            
            print(f"\n{Fore.YELLOW}{'═'*60}")
            print(f"{Fore.GREEN}Валюта: {currency} {CRYPTO_SYMBOLS[currency]}")
            print(f"{Fore.YELLOW}{'─'*60}")
            
            for offer in offers:
                color = offer['color']
                print(f"\n{color}{offer['name']}")
                print(f"{Fore.WHITE}  Процент в день: {offer['daily_interest_percent']:.1f}%")
                print(f"  Максимальная сумма: {offer['max_amount']:.2f}")
                print(f"  {offer['description']}")
                print(f"  {Fore.CYAN}Команда: credit take {offer['lender']} {currency} [сумма]")
    
    def take_credit(self, lender_str: str, currency: str, amount: Decimal):
        if not self.current_user:
            return
        
        try:
            lender = CreditRisk(lender_str.lower())
        except ValueError:
            print(f"{Fore.RED}Неверный тип кредитора. Используйте: low, medium, high")
            return
        
        if currency not in self.market.rates:
            print(f"{Fore.RED}Неизвестная валюта: {currency}")
            return
        
        offers = self.credit_system.get_credit_offers(currency, self.current_user.data.level)
        offer = next((o for o in offers if o['lender'] == lender.value), None)
        
        if not offer:
            print(f"{Fore.Red}Предложение не найдено")
            return
        
        if amount > Decimal(str(offer['max_amount'])):
            print(f"{Fore.RED}Слишком большая сумма. Максимум: {offer['max_amount']:.2f}")
            return
        
        daily_interest = amount * Decimal(str(offer['interest_rate'])) / Decimal('365')
        print(dynamic_border(
            f"{Fore.YELLOW}ПОДТВЕРЖДЕНИЕ КРЕДИТА\n\n"
            f"{Fore.CYAN}Кредитор: {offer['name']}\n"
            f"Валюта: {currency} {CRYPTO_SYMBOLS[currency]}\n"
            f"Сумма: {float(amount):.2f}\n"
            f"Процент в день: {offer['daily_interest_percent']:.1f}%\n"
            f"Ежедневный платеж: {float(daily_interest):.4f}\n"
            f"Срок: 1 день\n\n"
            f"{Fore.RED}⚠️  Если не вернете в срок, будут начисляться проценты!\n\n"
            f"{Fore.GREEN}Подтвердить? (yes/no):",
            Fore.YELLOW
        ))
        
        if input(">>> ").lower() != "yes":
            print(f"{Fore.YELLOW}Отменено.")
            return
        
        contract = self.credit_system.take_credit(
            self.current_user.username,
            currency,
            amount,
            lender
        )
        
        if contract:
            current_balance = self.current_user.data.crypto_balance.get(currency, Decimal('0'))
            self.current_user.data.crypto_balance[currency] = current_balance + amount
            
            print(dynamic_border(
                f"{Fore.GREEN}✅ КРЕДИТ ОФОРМЛЕН!\n\n"
                f"ID кредита: {contract.id}\n"
                f"Получено: {float(amount):.2f} {currency}\n"
                f"Вернуть до: {contract.due_date[:10]}\n"
                f"Сумма к возврату: {float(contract.amount):.2f}\n"
                f"Ежедневные проценты: {float(contract.daily_interest):.4f}",
                Fore.GREEN
            ))
            
            self.current_user.add_transaction(
                'credit_taken',
                currency,
                amount,
                amount
            )
            
            self.save_users()
        else:
            print(f"{Fore.RED}Не удалось оформить кредит")
    
    def show_my_credits(self):
        if not self.current_user:
            return
        
        credits = self.credit_system.get_user_credits(self.current_user.username)
        
        if not credits:
            print(dynamic_border(f"{Fore.YELLOW}У вас нет активных кредитов", Fore.YELLOW))
            return
        
        print(f"{Fore.CYAN}╔{'═'*100}╗")
        print(f"{Fore.CYAN}║{'ВАШИ АКТИВНЫЕ КРЕДИТЫ':^100}║")
        print(f"{Fore.CYAN}╠{'═'*100}╣")
        
        for i, credit in enumerate(credits, 1):
            interest_due = self.credit_system.calculate_daily_interest(credit.id)
            total_due = credit.amount + interest_due
            
            due_date = datetime.fromisoformat(credit.due_date)
            is_overdue = datetime.now() > due_date
            
            if is_overdue:
                row_color = Fore.RED
                status = f"ПРОСРОЧЕН {credit.penalty_days} дн."
            else:
                row_color = Fore.YELLOW
                status = "АКТИВЕН"
            
            print(f"{row_color}║ {i:2}. ID: {credit.id[:8]} | "
                  f"Валюта: {credit.currency:6} | "
                  f"Сумма: {float(credit.amount):>10.2f} | "
                  f"Ставка: {float(credit.interest_rate*Decimal('100')):>5.1f}% | "
                  f"Долг: {float(total_due):>10.4f} | "
                  f"Вернуть до: {due_date.strftime('%d.%m.%Y')} | "
                  f"{status:<15} ║")
        
        print(f"{Fore.CYAN}╚{'═'*100}╝")
        print(f"{Fore.GREEN}Для погашения: credit pay [id_кредита]")
    
    def pay_credit(self, credit_id: str):
        if not self.current_user:
            return
        
        success, message = self.credit_system.pay_credit(
            credit_id,
            self.current_user.data.crypto_balance
        )
        
        if success:
            print(dynamic_border(f"{Fore.GREEN}✅ {message}", Fore.GREEN))
            
            credit = self.credit_system.contracts.get(credit_id)
            if credit:
                self.current_user.add_transaction(
                    'credit_paid',
                    credit.currency,
                    credit.amount,
                    credit.amount
                )
            
            self.save_users()
        else:
            print(dynamic_border(f"{Fore.RED}❌ {message}", Fore.RED))
    
    def show_staking_offers(self):
        if not self.current_user:
            return
        
        print(dynamic_border(f"{Fore.CYAN}ПРЕДЛОЖЕНИЯ ПО СТЕЙКИНГУ", Fore.CYAN))
        
        available_currencies = ["EXTRACT", "BTC", "ETH", "BETASTD", "DOGCOIN", "SOL", "ADA"]
        
        for currency in available_currencies:
            if currency not in self.market.rates:
                continue
            
            has_eup_plus = (self.current_user.data.subscription.type == 
                           SubscriptionType.EUP_PLUS and 
                           self.current_user.has_active_subscription())
            
            plans = self.staking_system.get_staking_plans(currency, has_eup_plus)
            
            print(f"\n{Fore.YELLOW}{'═'*60}")
            print(f"{Fore.GREEN}Валюта: {currency} {CRYPTO_SYMBOLS[currency]}")
            print(f"{Fore.YELLOW}{'─'*60}")
            
            for plan in plans:
                color_map = {
                    'blue': Fore.BLUE,
                    'green': Fore.GREEN,
                    'yellow': Fore.YELLOW,
                    'magenta': Fore.MAGENTA
                }
                color = color_map.get(plan['color'], Fore.WHITE)
                
                print(f"\n{color}{plan['name']}")
                print(f"{Fore.WHITE}  Годовая доходность: {plan['interest_rate']*365*100:.1f}%")
                print(f"  Минимальная сумма: {plan['min_amount']}")
                print(f"  {plan['description']}")
                
                if plan['lock_period'] > 0:
                    print(f"  Срок блокировки: {plan['lock_period']} дней")
                
                print(f"  {Fore.CYAN}Команда: stake open {plan['id']} {currency} [сумма]")
    
    def open_staking(self, plan_str: str, currency: str, amount: Decimal):
        if not self.current_user:
            return
        
        try:
            plan = StakingPlan(plan_str.lower())
        except ValueError:
            print(f"{Fore.RED}Неверный план. Используйте: flexible, fixed_7d, fixed_30d, vip")
            return
        
        if currency not in self.market.rates:
            print(f"{Fore.RED}Неизвестная валюта: {currency}")
            return
        
        current_balance = self.current_user.data.crypto_balance.get(currency, Decimal('0'))
        if current_balance < amount:
            print(f"{Fore.RED}Недостаточно средств. Доступно: {float(current_balance):.4f}")
            return
        
        has_eup_plus = (self.current_user.data.subscription.type == 
                       SubscriptionType.EUP_PLUS and 
                       self.current_user.has_active_subscription())
        
        if plan == StakingPlan.VIP and not has_eup_plus:
            print(f"{Fore.RED}VIP план доступен только для подписчиков EUP+!")
            return
        
        plans = self.staking_system.get_staking_plans(currency, has_eup_plus)
        selected_plan = next((p for p in plans if p['id'] == plan.value), None)
        
        if not selected_plan:
            print(f"{Fore.Red}План не найден")
            return
        
        if amount < Decimal(str(selected_plan['min_amount'])):
            print(f"{Fore.RED}Минимальная сумма: {selected_plan['min_amount']}")
            return
        
        annual_yield = Decimal(str(selected_plan['interest_rate'])) * Decimal('365') * Decimal('100')
        
        print(dynamic_border(
            f"{Fore.YELLOW}ПОДТВЕРЖДЕНИЕ ВКЛАДА\n\n"
            f"{Fore.CYAN}План: {selected_plan['name']}\n"
            f"Валюта: {currency} {CRYPTO_SYMBOLS[currency]}\n"
            f"Сумма: {float(amount):.2f}\n"
            f"Годовая доходность: {float(annual_yield):.1f}%\n"
            f"Ежедневный процент: {selected_plan['interest_rate']*100:.4f}%\n"
            f"{selected_plan['description']}\n",
            Fore.YELLOW
        ))
        
        if selected_plan['lock_period'] > 0:
            print(f"{Fore.RED}⚠️  Средства будут заблокированы на {selected_plan['lock_period']} дней!\n")
        
        print(f"{Fore.GREEN}Подтвердить? (yes/no):")
        
        if input(">>> ").lower() != "yes":
            print(f"{Fore.YELLOW}Отменено.")
            return
        
        contract = self.staking_system.open_staking(
            self.current_user.username,
            currency,
            amount,
            plan,
            has_eup_plus
        )
        
        if contract:
            self.current_user.data.crypto_balance[currency] = current_balance - amount
            
            print(dynamic_border(
                f"{Fore.GREEN}✅ ВКЛАД ОТКРЫТ!\n\n"
                f"ID вклада: {contract.id}\n"
                f"Застейкано: {float(amount):.2f} {currency}\n"
                f"План: {selected_plan['name']}\n"
                f"Начало: {contract.start_date[:10]}\n"
                f"Доходность: {float(annual_yield):.1f}% годовых\n"
                f"Забирайте проценты: stake claim {contract.id}\n"
                f"Закрыть вклад: stake close {contract.id}",
                Fore.GREEN
            ))
            
            self.current_user.add_transaction(
                'stake_opened',
                currency,
                -amount,
                amount
            )
            
            self.save_users()
        else:
            print(f"{Fore.RED}Не удалось открыть вклад")
    
    def show_my_stakes(self):
        if not self.current_user:
            return
        
        stakes = self.staking_system.get_user_stakes(self.current_user.username)
        
        if not stakes:
            print(dynamic_border(f"{Fore.YELLOW}У вас нет активных вкладов", Fore.YELLOW))
            return
        
        print(f"{Fore.CYAN}╔{'═'*120}╗")
        print(f"{Fore.CYAN}║{'ВАШИ АКТИВНЫЕ ВКЛАДЫ':^120}║")
        print(f"{Fore.CYAN}╠{'═'*120}╣")
        
        for i, stake in enumerate(stakes, 1):
            earnings = self.staking_system.calculate_earnings(stake.id)
            
            if stake.plan == StakingPlan.FLEXIBLE:
                row_color = Fore.BLUE
            elif stake.plan == StakingPlan.FIXED_7D:
                row_color = Fore.GREEN
            elif stake.plan == StakingPlan.FIXED_30D:
                row_color = Fore.YELLOW
            else:
                row_color = Fore.MAGENTA
            
            earnings_text = f"{float(earnings):.4f}" if earnings != Decimal('-1') else "ЗАБЛОКИРОВАНО"
            earnings_color = Fore.GREEN if earnings > Decimal('0') else Fore.RED
            
            end_date_text = stake.end_date[:10] if stake.end_date else "БЕССРОЧНЫЙ"
            
            print(f"{row_color}║ {i:2}. ID: {stake.id[:8]} | "
                  f"Валюта: {stake.currency:6} | "
                  f"Сумма: {float(stake.amount):>10.2f} | "
                  f"План: {stake.plan.value:10} | "
                  f"Доходность: {float(stake.interest_rate*Decimal('365*100')):>5.1f}% | "
                  f"Накоплено: {earnings_color}{earnings_text:>12}{row_color} | "
                  f"Окончание: {end_date_text:12} | "
                  f"Всего заработано: {float(stake.total_earned):>8.4f} ║")
        
        print(f"{Fore.CYAN}╚{'═'*120}╝")
        print(f"{Fore.GREEN}Забрать проценты: stake claim [id_вклада]")
        print(f"{Fore.YELLOW}Закрыть вклад: stake close [id_вклада]")
    
    def claim_staking_earnings(self, stake_id: str):
        if not self.current_user:
            return
        
        success, message, earnings = self.staking_system.claim_earnings(
            stake_id,
            self.current_user.data.crypto_balance
        )
        
        if success:
            print(dynamic_border(f"{Fore.GREEN}✅ {message}", Fore.GREEN))
            
            stake = self.staking_system.contracts.get(stake_id)
            if stake:
                self.current_user.add_transaction(
                    'stake_earnings',
                    stake.currency,
                    earnings,
                    earnings
                )
            
            self.save_users()
        else:
            print(dynamic_border(f"{Fore.RED}❌ {message}", Fore.RED))
    
    def close_staking(self, stake_id: str):
        if not self.current_user:
            return
        
        success, message = self.staking_system.close_staking(
            stake_id,
            self.current_user.data.crypto_balance
        )
        
        if success:
            print(dynamic_border(f"{Fore.GREEN}✅ {message}", Fore.GREEN))
            
            stake = self.staking_system.contracts.get(stake_id)
            if stake:
                self.current_user.add_transaction(
                    'stake_closed',
                    stake.currency,
                    stake.amount,
                    stake.amount
                )
            
            self.save_users()
        else:
            print(dynamic_border(f"{Fore.RED}❌ {message}", Fore.RED))
    
    def show_bank_stats(self):
        credit_stats = self.credit_system.get_credit_stats()
        staking_stats = self.staking_system.get_staking_stats()
        
        content = [
            f"{Fore.CYAN}{'═'*60}",
            f"{Fore.YELLOW}📊 СТАТИСТИКА БАНКА EXTRACT",
            f"{Fore.CYAN}{'─'*60}",
            f"{Fore.GREEN}КРЕДИТЫ:",
            f"  Активных кредитов: {credit_stats['active_contracts']}",
            f"  Просроченных: {credit_stats['defaulted_contracts']}",
            f"  Всего выдано: {credit_stats['total_issued']:.2f} Ⓔ экв.",
            f"  Возвращено: {credit_stats['total_repaid']:.2f} Ⓔ экв.",
            f"{Fore.CYAN}{'─'*60}",
            f"{Fore.BLUE}СТЕЙКИНГ:",
            f"  Активных вкладов: {staking_stats['total_contracts']}",
        ]
        
        if staking_stats['total_staked']:
            content.append(f"  Всего застейкано:")
            for currency, amount in staking_stats['total_staked'].items():
                content.append(f"    {currency}: {amount:.2f}")
        
        content.append(f"{Fore.CYAN}{'─'*60}")
        content.append(f"{Fore.MAGENTA}БАНКОВСКИЕ РЕЗЕРВЫ:")
        
        for currency, amount in credit_stats['bank_reserves'].items():
            if amount > 0:
                content.append(f"  {currency}: {amount:.2f}")
        
        content.append(f"{Fore.CYAN}{'═'*60}")
        
        print(dynamic_border('\n'.join(content), Fore.CYAN))
    
    def create_reserve(self, currency: str, amount: Decimal):
        if not self.current_user:
            return
        
        if currency not in self.market.rates:
            print(f"{Fore.RED}Неизвестная валюта: {currency}")
            return
        
        current_balance = self.current_user.data.crypto_balance.get(currency, Decimal('0'))
        if current_balance < amount:
            print(f"{Fore.RED}Недостаточно средств. Доступно: {float(current_balance):.4f}")
            return
        
        has_eup_plus = (self.current_user.data.subscription.type == 
                       SubscriptionType.EUP_PLUS and 
                       self.current_user.has_active_subscription())
        
        success = self.reserve_system.create_reserve(
            self.current_user.username,
            currency,
            amount,
            has_eup_plus
        )
        
        if success:
            self.current_user.data.crypto_balance[currency] = current_balance - amount
            
            print(dynamic_border(
                f"{Fore.GREEN}✅ РЕЗЕРВ СОЗДАН!\n\n"
                f"Валюта: {currency} {CRYPTO_SYMBOLS[currency]}\n"
                f"Начальный баланс: {float(amount):.2f}\n"
                f"Комиссия: {'0.1% в неделю' if has_eup_plus else '2% в неделю'}\n"
                f"Дата создания: {datetime.now().strftime('%d.%m.%Y')}",
                Fore.GREEN
            ))
            
            self.current_user.add_transaction(
                'reserve_created',
                currency,
                -amount,
                amount
            )
            
            self.save_users()
        else:
            print(f"{Fore.RED}Резерв для этой валюты уже существует!")
    
    def put_to_reserve(self, currency: str, amount: Decimal):
        if not self.current_user:
            return
        
        if currency not in self.market.rates:
            print(f"{Fore.RED}Неизвестная валюта: {currency}")
            return
        
        current_balance = self.current_user.data.crypto_balance.get(currency, Decimal('0'))
        if current_balance < amount:
            print(f"{Fore.RED}Недостаточно средств. Доступно: {float(current_balance):.4f}")
            return
        
        has_eup_plus = (self.current_user.data.subscription.type == 
                       SubscriptionType.EUP_PLUS and 
                       self.current_user.has_active_subscription())
        
        success, message = self.reserve_system.put_to_reserve(
            self.current_user.username,
            currency,
            amount,
            has_eup_plus
        )
        
        if success:
            self.current_user.data.crypto_balance[currency] = current_balance - amount
            
            print(dynamic_border(f"{Fore.GREEN}✅ {message}", Fore.GREEN))
            
            self.current_user.add_transaction(
                'reserve_deposit',
                currency,
                -amount,
                amount
            )
            
            self.save_users()
        else:
            print(dynamic_border(f"{Fore.RED}❌ {message}", Fore.RED))
    
    def take_from_reserve(self, currency: str, amount: Decimal):
        if not self.current_user:
            return
        
        if currency not in self.market.rates:
            print(f"{Fore.RED}Неизвестная валюта: {currency}")
            return
        
        has_eup_plus = (self.current_user.data.subscription.type == 
                       SubscriptionType.EUP_PLUS and 
                       self.current_user.has_active_subscription())
        
        success, message = self.reserve_system.take_from_reserve(
            self.current_user.username,
            currency,
            amount,
            has_eup_plus
        )
        
        if success:
            current_balance = self.current_user.data.crypto_balance.get(currency, Decimal('0'))
            self.current_user.data.crypto_balance[currency] = current_balance + amount
            
            print(dynamic_border(f"{Fore.GREEN}✅ {message}", Fore.GREEN))
            
            self.current_user.add_transaction(
                'reserve_withdrawal',
                currency,
                amount,
                amount
            )
            
            self.save_users()
        else:
            print(dynamic_border(f"{Fore.RED}❌ {message}", Fore.RED))
    
    def show_my_reserves(self):
        if not self.current_user:
            return
        
        has_eup_plus = (self.current_user.data.subscription.type == 
                       SubscriptionType.EUP_PLUS and 
                       self.current_user.has_active_subscription())
        
        reserves = self.reserve_system.get_user_reserves(self.current_user.username, has_eup_plus)
        
        if not reserves:
            print(dynamic_border(f"{Fore.YELLOW}У вас нет резервов", Fore.YELLOW))
            return
        
        print(f"{Fore.CYAN}╔{'═'*100}╗")
        print(f"{Fore.CYAN}║{'ВАШИ РЕЗЕРВЫ':^100}║")
        print(f"{Fore.CYAN}╠{'═'*100}╣")
        
        for i, reserve in enumerate(reserves, 1):
            fee_color = Fore.GREEN if reserve['fee_percent'] == 0.1 else Fore.YELLOW
            days_color = Fore.GREEN if reserve['days_until_fee'] > 3 else Fore.RED
            
            print(f"{Fore.CYAN}║ {i:2}. Валюта: {reserve['currency']:6} {CRYPTO_SYMBOLS[reserve['currency']]} | "
                  f"Баланс: {reserve['balance']:>12.2f} | "
                  f"Создан: {reserve['created_at']:>10} | "
                  f"Следующая комиссия: {reserve['next_fee_date']} | "
                  f"{days_color}Дней до комиссии: {reserve['days_until_fee']:>2} | "
                  f"{fee_color}Комиссия: {reserve['fee_percent']}% ║")
        
        print(f"{Fore.CYAN}╚{'═'*100}╝")
        print(f"{Fore.GREEN}Положить в резерв: reserv put [валюта] [сумма]")
        print(f"{Fore.YELLOW}Взять из резерва: reserv take [валюта] [сумма]")
    
    def show_reserve_info(self):
        info = f"""
    {Fore.CYAN}╔{'═'*50}╗
    ║{'ИНФОРМАЦИЯ О РЕЗЕРВАХ':^50}║
    ╠{'═'*50}╣
    ║ {Fore.GREEN}Резерв - это сберегательный счет для хранения средств║
    ║ {Fore.YELLOW}Особенности:                                      ║
    ║ ▪ Неограниченная сумма                           ║
    ║ ▪ Еженедельная комиссия                         ║
    ║ ▪ Защита от спонтанных трат                     ║
    ╠{'─'*50}╣
    ║ {Fore.RED}Комиссии:                                          ║
    ║ ▪ Обычные пользователи: 2% в неделю             ║
    ║ ▪ EUP+ подписчики: 0.1% в неделю                ║
    ╠{'─'*50}╣
    ║ {Fore.BLUE}Команды:                                          ║
    ║ ▪ reserv create [валюта] [сумма]                ║
    ║ ▪ reserv put [валюта] [сумма]                   ║
    ║ ▪ reserv take [валюта] [сумма]                  ║
    ║ ▪ reserv show                                   ║
    ╚{'═'*50}╝
    """
        print(info)

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
                        if action.startswith("chart -now "):
                            coin = action.split()[2].upper()
                            casino.chart_now(coin)
                        else:
                            coin = action.split()[1].upper()
                            casino.market.print_chart(coin)
                    except:
                        print(f"{Fore.RED}Используйте: chart [валюта] или chart -now [валюта]")
                elif action == "global":
                    casino.global_stats()
                elif action == "eup info":
                    casino.show_eup_info()
                elif action == "rates":
                    casino.show_rates()
                elif action == "show":
                    casino.show_profile()
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
                elif action == "credit offers":
                    if casino.current_user:
                        casino.show_credit_offers()
                    else:
                        print(f"{Fore.RED}Сначала войдите в аккаунт!")
                elif action.startswith("credit take "):
                    if casino.current_user:
                        try:
                            parts = action.split()
                            if len(parts) != 5:
                                raise ValueError
                            lender = parts[2]
                            currency = parts[3].upper()
                            amount = Decimal(parts[4])
                            casino.take_credit(lender, currency, amount)
                        except:
                            print(f"{Fore.RED}Используйте: credit take [low/medium/high] [валюта] [сумма]")
                    else:
                        print(f"{Fore.RED}Сначала войдите в аккаунт!")
                elif action == "credit my":
                    if casino.current_user:
                        casino.show_my_credits()
                    else:
                        print(f"{Fore.RED}Сначала войдите в аккаунт!")
                elif action.startswith("credit pay "):
                    if casino.current_user:
                        try:
                            credit_id = action.split()[2]
                            casino.pay_credit(credit_id)
                        except:
                            print(f"{Fore.RED}Используйте: credit pay [id_кредита]")
                    else:
                        print(f"{Fore.RED}Сначала войдите в аккаунт!")
                elif action == "stake offers":
                    if casino.current_user:
                        casino.show_staking_offers()
                    else:
                        print(f"{Fore.RED}Сначала войдите в аккаунт!")
                elif action.startswith("stake open "):
                    if casino.current_user:
                        try:
                            parts = action.split()
                            if len(parts) != 5:
                                raise ValueError
                            plan = parts[2]
                            currency = parts[3].upper()
                            amount = Decimal(parts[4])
                            casino.open_staking(plan, currency, amount)
                        except:
                            print(f"{Fore.RED}Используйте: stake open [план] [валюта] [сумма]")
                    else:
                        print(f"{Fore.RED}Сначала войдите в аккаунт!")
                elif action == "stake my":
                    if casino.current_user:
                        casino.show_my_stakes()
                    else:
                        print(f"{Fore.RED}Сначала войдите в аккаунт!")
                elif action.startswith("stake claim "):
                    if casino.current_user:
                        try:
                            stake_id = action.split()[2]
                            casino.claim_staking_earnings(stake_id)
                        except:
                            print(f"{Fore.RED}Используйте: stake claim [id_вклада]")
                    else:
                        print(f"{Fore.RED}Сначала войдите в аккаунт!")
                elif action.startswith("stake close "):
                    if casino.current_user:
                        try:
                            stake_id = action.split()[2]
                            casino.close_staking(stake_id)
                        except:
                            print(f"{Fore.RED}Используйте: stake close [id_вклада]")
                    else:
                        print(f"{Fore.RED}Сначала войдите в аккаунт!")
                elif action == "bank stats":
                    casino.show_bank_stats()
                elif action.startswith("reserv create "):
                    if casino.current_user:
                        try:
                            parts = action.split()
                            if len(parts) != 4:
                                raise ValueError
                            currency = parts[2].upper()
                            amount = Decimal(parts[3])
                            casino.create_reserve(currency, amount)
                        except:
                            print(f"{Fore.RED}Используйте: reserv create [валюта] [сумма]")
                    else:
                        print(f"{Fore.RED}Сначала войдите в аккаунт!")
                elif action.startswith("reserv put "):
                    if casino.current_user:
                        try:
                            parts = action.split()
                            if len(parts) != 4:
                                raise ValueError
                            currency = parts[2].upper()
                            amount = Decimal(parts[3])
                            casino.put_to_reserve(currency, amount)
                        except:
                            print(f"{Fore.RED}Используйте: reserv put [валюта] [сумма]")
                    else:
                        print(f"{Fore.RED}Сначала войдите в аккаунт!")
                elif action.startswith("reserv take "):
                    if casino.current_user:
                        try:
                            parts = action.split()
                            if len(parts) != 4:
                                raise ValueError
                            currency = parts[2].upper()
                            amount = Decimal(parts[3])
                            casino.take_from_reserve(currency, amount)
                        except:
                            print(f"{Fore.RED}Используйте: reserv take [валюта] [сумма]")
                    else:
                        print(f"{Fore.RED}Сначала войдите в аккаунт!")
                elif action == "reserv show":
                    if casino.current_user:
                        casino.show_my_reserves()
                    else:
                        print(f"{Fore.RED}Сначала войдите в аккаунт!")
                elif action == "reserv info":
                    casino.show_reserve_info()
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