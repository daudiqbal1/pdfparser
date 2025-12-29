import pdfplumber
import re
from typing import Dict, List

from .utils import parse_amount, is_transaction_line
from .models import ParseResult


class PDFParser:
    def __init__(self, language: str = "en"):
        self.language = language

    def parse(self, pdf_path: str) -> ParseResult:
        with pdfplumber.open(pdf_path) as pdf:
            pages = [p.extract_text() for p in pdf.pages]

        metadata = self._parse_metadata(pages[0])
        transactions = self._parse_transactions(pages)

        return ParseResult(
            metadata=metadata,
            transactions=transactions
        )

    # ---------- METADATA ----------
    def _parse_metadata(self, text: str) -> dict:
        lines = [l.strip() for l in text.splitlines() if l.strip()]

        # Stop before table
        metadata_lines = []
        for line in lines:
            if line.lower() == "transaction date":
                break
            metadata_lines.append(line)

        field_map = {
            ("no. rekening", "account no"): "account_no",
            ("unit kerja", "business unit"): "business_unit",
            ("nama produk", "product name"): "product_name",
            ("valuta", "currency"): "currency",
            ("tanggal laporan", "statement date"): "statement_date",
            ("periode transaksi", "transaction period"): "transaction_period",
        }

        result = {v: "" for v in field_map.values()}
        current_field = None

        i = 0
        while i < len(metadata_lines) - 1:
            line = metadata_lines[i].lower()
            next_line = metadata_lines[i + 1].lower()

            # 1️⃣ Detect bilingual label pair
            for (id_label, en_label), key in field_map.items():
                if line == id_label and next_line == en_label:
                    current_field = key
                    break

            # 2️⃣ Assign value to the last seen field
            if current_field and metadata_lines[i].startswith(":"):
                result[current_field] = metadata_lines[i].lstrip(":").strip()
                current_field = None

            i += 1

        return result



    # ---------- TRANSACTIONS ----------
    def _parse_transactions(self, pages: List[str]) -> List[Dict]:
        transactions = []
        buffer = ""

        for page in pages:
            for line in page.splitlines():
                line = line.strip()
                if not line:
                    continue

                if is_transaction_line(line):
                    if buffer:
                        tx = self._parse_transaction_block(buffer)
                        if tx:
                            transactions.append(tx)
                    buffer = line
                else:
                    buffer += " " + line

        if buffer:
            tx = self._parse_transaction_block(buffer)
            if tx:
                transactions.append(tx)

        return transactions

    def _parse_transaction_block(self, block: str) -> dict | None:
        parts = block.split()

        # --- HARD GUARDS ---
        if len(parts) < 8:
            return None

        # Must start with date + time
        if not re.match(r"\d{2}/\d{2}/\d{2}", parts[0]):
            return None

        # Last 3 fields must be amounts
        try:
            debit = parse_amount(parts[-3])
            credit = parse_amount(parts[-2])
            balance = parse_amount(parts[-1])
        except ValueError:
            return None  # <-- THIS fixes your crash

        transaction_date = f"{parts[0]} {parts[1]}"
        user_id = parts[-4]
        description = " ".join(parts[2:-4])

        return {
            "transaction_date": transaction_date,
            "description": description,
            "user_id": user_id,
            "debit": debit,
            "credit": credit,
            "balance": balance,
        }
