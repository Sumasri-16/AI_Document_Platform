def to_number(value):
    """
    Convert extracted financial value to float.
    """

    if value is None:
        return None

    try:
        value = str(value).strip()

        if not value:
            return None

        value = value.replace(",", "")

        # Accounting negative value: (12345)
        if value.startswith("(") and value.endswith(")"):
            value = "-" + value[1:-1]

        return float(value)

    except (ValueError, TypeError):
        return None


def find_value(data, *keys):
    """
    Return the first available value.
    """

    for key in keys:

        if key in data and data[key] is not None:
            return data[key]

    return None


# ============================================================
# INVOICE
# ============================================================

def validate_invoice(data):

    total = to_number(
        find_value(
            data,
            "total_amount",
            "total"
        )
    )

    if total is None:

        return {
            "status": "valid_with_warnings",
            "errors": [],
            "warnings": [
                "Invoice total could not be extracted."
            ],
            "checks": [
                {
                    "formula": "Invoice total exists",
                    "operands": {},
                    "calculated_value": None,
                    "reported_value": None,
                    "variance": None,
                    "status": "NOT_APPLICABLE"
                }
            ]
        }

    return {
        "status": "valid",
        "errors": [],
        "warnings": [],
        "checks": [
            {
                "formula": "Invoice total exists",
                "operands": {
                    "total": total
                },
                "calculated_value": total,
                "reported_value": total,
                "variance": 0,
                "status": "PASS"
            }
        ]
    }


# ============================================================
# BALANCE SHEET
# ============================================================

def validate_balance_sheet(data):

    total_assets = to_number(
        find_value(
            data,
            "total_assets",
            "assets_total"
        )
    )

    total_liabilities = to_number(
        find_value(
            data,
            "total_liabilities",
            "liabilities_total"
        )
    )

    if (
        total_assets is not None
        and total_liabilities is not None
    ):

        variance = (
            total_assets - total_liabilities
        )

        status = (
            "PASS"
            if abs(variance) < 0.01
            else "FAIL"
        )

        return {
            "status":
                "valid"
                if status == "PASS"
                else "valid_with_warnings",

            "errors": [],

            "warnings":
                []
                if status == "PASS"
                else [
                    "Balance Sheet totals do not match."
                ],

            "checks": [
                {
                    "formula":
                        "Total Assets = Total Liabilities",

                    "operands": {
                        "total_assets":
                            total_assets,

                        "total_liabilities":
                            total_liabilities
                    },

                    "calculated_value":
                        total_liabilities,

                    "reported_value":
                        total_assets,

                    "variance":
                        variance,

                    "status":
                        status
                }
            ]
        }

    return {
        "status": "valid_with_warnings",
        "errors": [],
        "warnings": [
            "Insufficient extracted values for Balance Sheet validation."
        ],
        "checks": [
            {
                "formula":
                    "Total Assets = Total Liabilities",

                "operands": {},

                "calculated_value": None,

                "reported_value":
                    total_assets,

                "variance": None,

                "status":
                    "NOT_APPLICABLE"
            }
        ]
    }


# ============================================================
# PROFIT & LOSS
# ============================================================

def validate_profit_and_loss(data):
    """
    Validate:

    Total Income - Total Expenditure = Net Profit
    """

    revenue = to_number(
        find_value(
            data,
            "total_income",
            "revenue",
            "total_revenue",
            "sales"
        )
    )

    expenses = to_number(
        find_value(
            data,
            "total_expenditure",
            "expenses",
            "total_expenses"
        )
    )

    profit = to_number(
        find_value(
            data,
            "net_profit",
            "net_profit_for_year",
            "profit",
            "net_income"
        )
    )

    # --------------------------------------------------------
    # All required values available
    # --------------------------------------------------------

    if (
        revenue is not None
        and expenses is not None
        and profit is not None
    ):

        calculated_profit = (
            revenue - expenses
        )

        variance = (
            calculated_profit - profit
        )

        status = (
            "PASS"
            if abs(variance) < 0.01
            else "FAIL"
        )

        return {

            "status":
                "valid"
                if status == "PASS"
                else "valid_with_warnings",

            "errors": [],

            "warnings":
                []
                if status == "PASS"
                else [
                    "Calculated profit does not match reported net profit."
                ],

            "checks": [

                {
                    "formula":
                        "Total Income - Total Expenditure = Net Profit",

                    "operands": {

                        "total_income":
                            revenue,

                        "total_expenditure":
                            expenses,

                        "net_profit":
                            profit
                    },

                    "calculated_value":
                        calculated_profit,

                    "reported_value":
                        profit,

                    "variance":
                        variance,

                    "status":
                        status
                }
            ]
        }

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    return {

        "status":
            "valid_with_warnings",

        "errors": [],

        "warnings": [
            "Insufficient extracted values for P&L validation."
        ],

        "checks": [

            {
                "formula":
                    "Total Income - Total Expenditure = Net Profit",

                "operands": {},

                "calculated_value":
                    None,

                "reported_value":
                    profit,

                "variance":
                    None,

                "status":
                    "NOT_APPLICABLE"
            }
        ]
    }


# ============================================================
# CASH FLOW
# ============================================================

def validate_cash_flow(data):

    opening_cash = to_number(
        find_value(
            data,
            "opening_cash",
            "beginning_cash",
            "cash_at_beginning"
        )
    )

    net_change = to_number(
        find_value(
            data,
            "net_cash_change",
            "net_change_in_cash",
            "net_increase_in_cash",
            "net_decrease_in_cash"
        )
    )

    closing_cash = to_number(
        find_value(
            data,
            "closing_cash",
            "ending_cash",
            "cash_at_end"
        )
    )

    if (
        opening_cash is not None
        and net_change is not None
        and closing_cash is not None
    ):

        calculated_closing = (
            opening_cash + net_change
        )

        variance = (
            calculated_closing - closing_cash
        )

        status = (
            "PASS"
            if abs(variance) < 0.01
            else "FAIL"
        )

        return {

            "status":
                "valid"
                if status == "PASS"
                else "valid_with_warnings",

            "errors": [],

            "warnings":
                []
                if status == "PASS"
                else [
                    "Calculated closing cash does not match reported closing cash."
                ],

            "checks": [

                {
                    "formula":
                        "Opening Cash + Net Cash Change = Closing Cash",

                    "operands": {

                        "opening_cash":
                            opening_cash,

                        "net_cash_change":
                            net_change,

                        "closing_cash":
                            closing_cash
                    },

                    "calculated_value":
                        calculated_closing,

                    "reported_value":
                        closing_cash,

                    "variance":
                        variance,

                    "status":
                        status
                }
            ]
        }

    return {

        "status":
            "valid_with_warnings",

        "errors": [],

        "warnings": [
            "Insufficient extracted values for Cash Flow validation."
        ],

        "checks": [

            {
                "formula":
                    "Opening Cash + Net Cash Change = Closing Cash",

                "operands": {},

                "calculated_value":
                    None,

                "reported_value":
                    closing_cash,

                "variance":
                    None,

                "status":
                    "NOT_APPLICABLE"
            }
        ]
    }


# ============================================================
# MAIN VALIDATION ROUTER
# ============================================================

def validate_invoice_data(extracted_data):

    document_type = extracted_data.get(
        "document_type",
        ""
    ).lower()

    financial_data = extracted_data.get(
        "financial_data",
        {}
    )

    if document_type == "balance_sheet":

        return validate_balance_sheet(
            financial_data
        )

    elif document_type == "profit_and_loss":

        return validate_profit_and_loss(
            financial_data
        )

    elif document_type == "cash_flow_statement":

        return validate_cash_flow(
            financial_data
        )

    else:

        return validate_invoice(
            extracted_data
        )