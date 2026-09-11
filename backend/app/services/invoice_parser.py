import re


def clean_number(value):
    """Clean a financial number while preserving negative values."""
    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    value = value.replace(",", "")
    value = value.replace("₹", "")
    value = value.replace("$", "")

    # Handle accounting format: (12345) -> -12345
    if value.startswith("(") and value.endswith(")"):
        value = "-" + value[1:-1]

    return value


def get_line_numbers(line):
    """
    Extract financial numbers from a line.
    Ignores small numbers such as Schedule 6 and Schedule 7.
    """
    matches = re.findall(
        r"(?<!\d)-?\(?\d[\d,]*(?:\.\d+)?\)?",
        line
    )

    numbers = []

    for value in matches:
        cleaned = clean_number(value)

        if cleaned is None:
            continue

        try:
            number = float(cleaned)

            # Ignore schedule numbers such as 6, 7, 13, 14, etc.
            if abs(number) >= 1000:
                numbers.append(cleaned)

        except ValueError:
            continue

    return numbers


def find_amount_after_label(line):
    """Return the first meaningful financial amount after a label."""
    numbers = get_line_numbers(line)

    if numbers:
        return numbers[0]

    return None


# ============================================================
# INVOICE
# ============================================================

def extract_invoice_data(text):
    data = {
        "invoice_number": None,
        "date": None,
        "time": None,
        "total_amount": None,
        "items": []
    }

    lines = text.splitlines()

    for line in lines:
        clean_line = line.strip()
        lower_line = clean_line.lower()

        # Invoice number
        if data["invoice_number"] is None:
            match = re.search(
                r"(?:invoice\s*(?:no|number|#)|inv\s*(?:no|number|#))"
                r"\s*[:\-]?\s*([A-Za-z0-9\/\-_]+)",
                clean_line,
                re.IGNORECASE
            )

            if match:
                data["invoice_number"] = match.group(1)

        # Date
        if data["date"] is None:
            match = re.search(
                r"\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b",
                clean_line
            )

            if match:
                data["date"] = match.group(0)

        # Total
        if data["total_amount"] is None:
            total_keywords = [
                "grand total",
                "invoice total",
                "total amount",
                "amount due",
                "net amount",
                "total"
            ]

            if any(keyword in lower_line for keyword in total_keywords):
                numbers = get_line_numbers(clean_line)

                if numbers:
                    data["total_amount"] = numbers[-1]

    return data


# ============================================================
# BALANCE SHEET
# ============================================================

def extract_balance_sheet_data(text):
    financial_data = {}

    lines = text.splitlines()

    for line in lines:
        clean_line = line.strip()
        lower_line = clean_line.lower()

        numbers = get_line_numbers(clean_line)

        if not numbers:
            continue

        if "total assets" in lower_line:
            financial_data["total_assets"] = numbers[0]

        elif "total liabilities" in lower_line:
            financial_data["total_liabilities"] = numbers[0]

        elif "shareholders" in lower_line and "funds" in lower_line:
            financial_data["shareholders_funds"] = numbers[0]

        elif "equity" in lower_line and "total" in lower_line:
            financial_data["total_equity"] = numbers[0]

        elif "capital" in lower_line and "total" in lower_line:
            financial_data["share_capital"] = numbers[0]

        elif "reserves" in lower_line and "surplus" in lower_line:
            financial_data["reserves_and_surplus"] = numbers[0]

        elif "cash and cash equivalents" in lower_line:
            financial_data["cash_and_cash_equivalents"] = numbers[0]

    return financial_data


# ============================================================
# PROFIT & LOSS
# ============================================================

def extract_profit_and_loss_data(text):
    financial_data = {}

    lines = text.splitlines()

    for line in lines:
        clean_line = line.strip()
        lower_line = clean_line.lower()

        numbers = get_line_numbers(clean_line)

        if not numbers:
            continue

        if "total income" in lower_line:
            financial_data["total_income"] = numbers[0]

        elif "total revenue" in lower_line:
            financial_data["total_revenue"] = numbers[0]

        elif lower_line.startswith("revenue"):
            financial_data["revenue"] = numbers[0]

        elif "interest earned" in lower_line:
            financial_data["interest_earned"] = numbers[0]

        elif "other income" in lower_line:
            financial_data["other_income"] = numbers[0]

        elif "interest expended" in lower_line:
            financial_data["interest_expended"] = numbers[0]

        elif "operating expenses" in lower_line:
            financial_data["operating_expenses"] = numbers[0]

        elif "total expenditure" in lower_line:
            financial_data["total_expenditure"] = numbers[0]

        elif "total expenses" in lower_line:
            financial_data["total_expenses"] = numbers[0]

        elif "provisions and contingencies" in lower_line:
            financial_data["provisions_and_contingencies"] = numbers[0]

        elif "net profit for the year" in lower_line:
            financial_data["net_profit_for_year"] = numbers[0]
            financial_data["net_profit"] = numbers[0]
            financial_data["profit"] = numbers[0]

        elif "net income" in lower_line:
            financial_data["net_income"] = numbers[0]
            financial_data["net_profit"] = numbers[0]

        elif lower_line.startswith("profit"):
            financial_data["profit"] = numbers[0]

    return financial_data


# ============================================================
# CASH FLOW
# ============================================================

def extract_cash_flow_data(text):
    financial_data = {}

    lines = text.splitlines()

    for line in lines:
        clean_line = line.strip()
        lower_line = clean_line.lower()

        # -----------------------------------------
        # Operating activities
        # -----------------------------------------

        if "net cash flow" in lower_line and "operating activities" in lower_line:
            numbers = get_line_numbers(clean_line)

            if numbers:
                financial_data["cash_from_operating_activities"] = numbers[0]

        # -----------------------------------------
        # Investing activities
        # -----------------------------------------

        elif "net cash used in investing activities" in lower_line:
            numbers = get_line_numbers(clean_line)

            if numbers:
                financial_data["cash_from_investing_activities"] = numbers[0]

        # -----------------------------------------
        # Financing activities
        # -----------------------------------------

        elif "net cash generated from financing activities" in lower_line:
            numbers = get_line_numbers(clean_line)

            if numbers:
                financial_data["cash_from_financing_activities"] = numbers[0]

        # -----------------------------------------
        # Net change in cash
        # -----------------------------------------

        elif "net increase" in lower_line and "cash and cash equivalents" in lower_line:
            numbers = get_line_numbers(clean_line)

            if numbers:
                financial_data["net_cash_change"] = numbers[0]

        elif "net decrease" in lower_line and "cash and cash equivalents" in lower_line:
            numbers = get_line_numbers(clean_line)

            if numbers:
                financial_data["net_cash_change"] = numbers[0]

        # -----------------------------------------
        # Opening cash
        # IMPORTANT:
        # Ignore Schedule 6 and 7.
        # Pick the first actual large financial number.
        # -----------------------------------------

        elif "cash and cash equivalents as at april 1st" in lower_line:
            numbers = get_line_numbers(clean_line)

            if numbers:
                financial_data["opening_cash"] = numbers[0]

        # -----------------------------------------
        # Closing cash
        # IMPORTANT:
        # Ignore Schedule 6 and 7.
        # Pick the first actual large financial number.
        # -----------------------------------------

        elif "cash and cash equivalents as at march 31st" in lower_line:
            numbers = get_line_numbers(clean_line)

            if numbers:
                financial_data["closing_cash"] = numbers[0]

        # -----------------------------------------
        # Generic cash balance
        # -----------------------------------------

        elif (
            "cash and cash equivalents" in lower_line
            and "march 31" in lower_line
        ):
            numbers = get_line_numbers(clean_line)

            if numbers and "closing_cash" not in financial_data:
                financial_data["closing_cash"] = numbers[0]

    # Use closing cash as total amount if available
    if financial_data.get("closing_cash") is not None:
        financial_data["cash_and_cash_equivalents"] = (
            financial_data["closing_cash"]
        )

    return financial_data


# ============================================================
# MAIN EXTRACTION FUNCTION
# ============================================================

def extract_invoice_fields(text):
    """
    Main extraction function.

    The document type is supplied later by main.py.
    We therefore extract useful financial information
    from the OCR text without changing the upload system.
    """

    invoice_data = extract_invoice_data(text)

    balance_sheet_data = extract_balance_sheet_data(text)
    profit_loss_data = extract_profit_and_loss_data(text)
    cash_flow_data = extract_cash_flow_data(text)

    # Detect useful date information
    date_value = None

    date_patterns = [
        r"(?:for the year ended|year ended)\s+"
        r"([A-Za-z]+\s+\d{1,2},\s+\d{4})",
        r"(?:for the year ended|year ended)\s+"
        r"([A-Za-z]+\s+\d{1,2}\s+\d{4})"
    ]

    for pattern in date_patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            date_value = match.group(1)
            break

    # Combine all financial information.
    # Document type is added by main.py.
    financial_data = {}

    financial_data.update(balance_sheet_data)
    financial_data.update(profit_loss_data)
    financial_data.update(cash_flow_data)

    result = {
        "invoice_number": invoice_data.get("invoice_number"),
        "date": date_value or invoice_data.get("date"),
        "time": invoice_data.get("time"),
        "total_amount": invoice_data.get("total_amount"),
        "items": invoice_data.get("items", []),
        "financial_data": financial_data
    }

    # For cash-flow documents, use closing cash as total amount
    if (
        result["total_amount"] is None
        and financial_data.get("closing_cash") is not None
    ):
        result["total_amount"] = financial_data["closing_cash"]

    return result