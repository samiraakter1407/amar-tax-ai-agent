
import json
from pathlib import Path
from crewai.tools import tool


# ==========================================
# DATABASE PATH CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "tax_rules.json"


# ==========================================
# TOOL 1: LOOKUP TAX DATABASE
# ==========================================

@tool("Lookup Tax Database")
def lookup_tax_db(section: str) -> str:
    """
    Retrieve a specific section from the local Bangladesh tax database.

    Available sections:
    tax_year, filing_deadline, thresholds,
    slabs_after_threshold, minimum_tax,
    investment_rebate, required_docs.
    """

    try:
        with open(DB_PATH, "r", encoding="utf-8") as file:
            tax_data = json.load(file)

        if section not in tax_data:
            return (
                f"Error: Section '{section}' not found. "
                f"Available sections: {list(tax_data.keys())}"
            )

        result = tax_data[section]
        return json.dumps(result, indent=4)

    except FileNotFoundError:
        return "Error: Local tax database file not found."

    except json.JSONDecodeError:
        return "Error: Tax database contains invalid JSON."

    except Exception as e:
        return f"Unexpected error: {str(e)}"


# ==========================================
# TOOL 2: CALCULATE SLAB TAX
# ==========================================

@tool("Calculate Slab Tax")
def calculate_slab_tax(
    total_income: float,
    tax_free_threshold: float,
    investment: float,
    minimum_tax: float
) -> str:
    """
    Calculate gross income tax, investment rebate,
    and net payable tax using the local tax database.

    Uses progressive tax slabs defined in tax_rules.json.
    """

    try:

        # ----------------------------------
        # 1. VALIDATE INPUTS
        # ----------------------------------

        if total_income < 0:
            return "Error: Income cannot be negative."

        if investment < 0:
            return "Error: Investment cannot be negative."

        if tax_free_threshold < 0 or minimum_tax < 0:
            return (
                "Error: Threshold and minimum tax "
                "cannot be negative."
            )

        # Flag investment exceeding total income.
        # Calculation continues using the allowable investment cap.

        investment_warning = None

        if investment > total_income:
            investment_warning = (
                "Declared investment exceeds total income. "
                "The investment is capped at 20% of total income "
                "for rebate calculation. Verify the declared amount."
            )

        # ----------------------------------
        # 2. LOAD LOCAL TAX DATABASE
        # ----------------------------------

        with open(DB_PATH, "r", encoding="utf-8") as file:
            tax_data = json.load(file)

        slabs = tax_data["slabs_after_threshold"]

        rebate_rate = tax_data[
            "investment_rebate"
        ]["rate"]

        max_investment_percent = tax_data[
            "investment_rebate"
        ]["max_investment_percent_of_income"]

        # ----------------------------------
        # 3. CALCULATE TAXABLE INCOME
        # ----------------------------------

        taxable_income = max(
            0,
            total_income - tax_free_threshold
        )

        # ----------------------------------
        # 4. CALCULATE PROGRESSIVE SLAB TAX
        # ----------------------------------

        remaining_income = taxable_income
        gross_tax = 0

        for slab in slabs:

            limit = slab["limit"]
            rate = slab["rate"]

            if remaining_income <= 0:
                break

            if limit is None:
                gross_tax += remaining_income * rate
                break

            taxable_amount = min(
                remaining_income,
                limit
            )

            gross_tax += taxable_amount * rate
            remaining_income -= taxable_amount

        # ----------------------------------
        # 5. CALCULATE ALLOWABLE INVESTMENT
        # ----------------------------------

        allowable_investment = min(
            investment,
            total_income * max_investment_percent
        )

        # ----------------------------------
        # 6. CALCULATE INVESTMENT REBATE
        # ----------------------------------

        investment_rebate = (
            allowable_investment * rebate_rate
        )

        # ----------------------------------
        # 7. CALCULATE NET PAYABLE TAX
        # ----------------------------------

        if total_income <= tax_free_threshold:

            net_payable_tax = 0

        else:

            net_payable_tax = max(
                gross_tax - investment_rebate,
                minimum_tax
            )

        # ----------------------------------
        # 8. PREPARE RESULT
        # ----------------------------------

        result = {

            "total_income": total_income,

            "tax_free_threshold": tax_free_threshold,

            "taxable_income": taxable_income,

            "gross_tax": round(gross_tax, 2),

            "actual_investment": investment,

            "allowable_investment": round(
                allowable_investment, 2
            ),

            "investment_rebate": round(
                investment_rebate, 2
            ),

            "minimum_tax": minimum_tax,

            "net_payable_tax": round(
                net_payable_tax, 2
            ),

            "warnings": (
                [investment_warning]
                if investment_warning
                else []
            )
        }

        return json.dumps(
            result,
            indent=4
        )

    except FileNotFoundError:
        return "Error: Local tax database file not found."

    except json.JSONDecodeError:
        return "Error: Invalid JSON in tax database."

    except Exception as e:
        return f"Tax calculation error: {str(e)}"
