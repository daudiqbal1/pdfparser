from dataclasses import dataclass
from typing import List, Dict


@dataclass
class StatementMetadata:
    account_no: str
    business_unit: str
    product_name: str
    currency: str
    statement_date: str
    transaction_period: str


@dataclass
class Transaction:
    transaction_date: str
    description: str
    user_id: str
    debit: float
    credit: float
    balance: float


@dataclass
class ParseResult:
    metadata: Dict
    transactions: List[Dict]
