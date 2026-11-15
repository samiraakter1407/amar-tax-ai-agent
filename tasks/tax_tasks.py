
from crewai import Task

from agents.tax_agents import (
    classifier_agent,
    calculator_agent,
    document_agent,
    reviewer_agent
)

from models.tax_models import TaxpayerClassification


# ==========================================
# TASK 1: TAXPAYER CLASSIFICATION
# ==========================================

classifier_task = Task(

    description=(
        "Analyze the following taxpayer profile:\n\n"
        "{user_profile}\n\n"

        "Your responsibilities:\n"
        "1. Determine filing eligibility under the simplified "
        "assignment rules.\n"
        "2. Identify the taxpayer category: General, Female, "
        "Senior 65+, Disabled, or Freedom Fighter.\n"
        "3. Retrieve the correct tax-free threshold from "
        "the local tax database.\n"
        "4. Determine the applicable minimum tax based "
        "on the taxpayer's location.\n"
        "5. Check whether the taxpayer is under 18. "
        "A person under 18 cannot file independently.\n"
        "6. Flag negative or invalid income.\n"
        "7. If income is below or equal to the tax-free threshold, "
        "explain that filing is not mandatory under "
        "the simplified assignment rules.\n"
        "8. Do not assume that having a TIN independently "
        "makes filing mandatory unless the assignment rules "
        "explicitly establish that requirement.\n\n"

        "Use the local tax database as your source for "
        "tax thresholds and minimum tax values. "
        "Do not invent tax rules.\n\n"

        "Return a structured classification report containing "
        "the taxpayer category, filing eligibility, "
        "tax-free threshold, minimum tax, and warnings."
    ),

    expected_output=(
        "A structured taxpayer classification report containing "
        "taxpayer category, filing eligibility, tax-free "
        "threshold in BDT, minimum tax in BDT, and warnings."
    ),

    agent=classifier_agent,

    output_pydantic=TaxpayerClassification
)


# ==========================================
# TASK 2: SLAB TAX CALCULATION
# ==========================================

calculator_task = Task(

    description=(
        "Calculate the taxpayer's income tax using "
        "the original taxpayer profile:\n\n"
        "{user_profile}\n\n"

        "Carefully review the Classifier's output "
        "provided in the context.\n\n"

        "Your responsibilities:\n"
        "1. Use the tax-free threshold identified by "
        "the Classifier.\n"
        "2. Retrieve progressive tax slabs from the "
        "local tax database.\n"
        "3. Calculate gross tax using progressive slabs.\n"
        "4. Calculate allowable investment. It must not "
        "exceed 20% of total income.\n"
        "5. Calculate investment rebate using the "
        "15% rebate rate.\n"
        "6. Compare tax after rebate against the "
        "applicable minimum tax.\n"
        "7. Calculate final net payable tax.\n\n"

        "IMPORTANT VALIDATION RULES:\n"
        "- Always use the Calculate Slab Tax tool "
        "for numerical calculations.\n"
        "- Treat the calculation tool's numerical output "
        "as the source of truth.\n"
        "- Read and report every warning returned by "
        "the Calculate Slab Tax tool.\n"
        "- If declared investment exceeds total income, "
        "explicitly flag it as a validation issue.\n"
        "- Continue the calculation using the allowable "
        "investment cap returned by the tool.\n"
        "- Never ignore, remove, or contradict a warning "
        "from the calculation tool.\n"
        "- Clearly distinguish actual investment from "
        "allowable investment.\n"
        "- Do not claim that an excessive declared investment "
        "is valid merely because the calculation tool "
        "can calculate a capped rebate.\n\n"

        "If income is negative or invalid, flag it and do "
        "not proceed with a normal tax calculation.\n"
        "If income is below or equal to the tax-free threshold, "
        "follow the simplified assignment rules.\n\n"

        "Use only the local tax database. Never invent "
        "tax rates or calculation rules."
    ),

    expected_output=(
        "A detailed tax calculation report containing "
        "taxable income, gross tax, actual investment, "
        "allowable investment, investment rebate, "
        "minimum tax, net payable tax, and all warnings. "
        "All monetary values must be in BDT."
    ),

    agent=calculator_agent,

    context=[classifier_task]
)


# ==========================================
# TASK 3: DOCUMENT ORGANIZER
# ==========================================

document_task = Task(

    description=(
        "Prepare a customized tax document checklist "
        "for the following taxpayer profile:\n\n"
        "{user_profile}\n\n"

        "Review the outputs of the Classifier and "
        "Slab Calculator provided in the context.\n\n"

        "Your responsibilities:\n"
        "1. Retrieve required documents from the "
        "required_docs section of the local tax database.\n"
        "2. Always include all common documents.\n"
        "3. Identify the taxpayer's profession and income "
        "sources, then include relevant profession-specific "
        "documents.\n"
        "4. For salaried taxpayers, include salaried documents.\n"
        "5. For business owners, include business documents.\n"
        "6. For freelancers, include freelancer documents.\n"
        "7. For landlords, include landlord documents.\n"
        "8. For investors, include investor documents.\n"
        "9. If the taxpayer has no TIN, add "
        "'TIN Registration' as the FIRST checklist item.\n"
        "10. If the profession is unknown or unavailable "
        "in the database, use the general common-document "
        "checklist.\n\n"

        "Do not invent document requirements.\n"
        "Only include documents explicitly listed in the "
        "local tax database.\n"
        "Do not add extra documents based on assumptions "
        "about age, profession, or taxpayer category.\n"
        "Use the local tax database as your source."
    ),

    expected_output=(
        "A customized tax document checklist containing "
        "common documents, profession-specific documents, "
        "and a TIN Registration item at the top when "
        "the taxpayer has no TIN. Include a short explanation."
    ),

    agent=document_agent,

    context=[
        classifier_task,
        calculator_task
    ]
)


# ==========================================
# TASK 4: COMPLIANCE REVIEWER
# ==========================================

reviewer_task = Task(

    description="""

    Perform a strict final compliance review of the taxpayer's report.

    ORIGINAL TAXPAYER PROFILE:
    {user_profile}

    Review the outputs of the Classifier, Calculator,
    and Document Organizer.

    ==========================================
    1. TAXPAYER CLASSIFICATION
    ==========================================

    - Verify taxpayer category and tax-free threshold
      using the local database.
    - Verify the applicable minimum tax using location.
    - Check age, gender, disability status,
      freedom fighter status, and TIN status.
    - Do not invent classification rules.

    ==========================================
    2. FILING OBLIGATION
    ==========================================

    Determine filing obligation separately from
    independent filing ability.

    - If total income exceeds the applicable threshold,
      filing obligation is Mandatory.
    - If total income is equal to or below the threshold,
      filing obligation is Not mandatory under these rules.
    - Having a TIN alone does not create a filing obligation.
    - If age is below 18, independent filing ability is
      Not permitted.

    For a minor whose income exceeds the threshold, report:

    Filing obligation: Mandatory.
    Independent filing: Not permitted (under 18).

    Never describe this situation as "filing not mandatory"
    merely because the taxpayer is a minor.

    ==========================================
    3. TAX CALCULATION VALIDATION
    ==========================================

    Independently verify the Calculator Agent's results
    using the actual taxpayer profile and the local
    tax database.

    Retrieve the progressive tax slabs from the database.

    Remember:
    - Taxable income = Total income - Tax-free threshold,
      with a minimum taxable income of zero.
    - Apply each progressive slab only to the portion
      of taxable income falling within that slab.
    - Do not apply one tax rate to the entire taxable income.
    - Calculate investment rebate using the database rate.
    - Allowable investment cannot exceed the database's
      maximum investment percentage of total income.
    - Final payable tax is the greater of tax after rebate
      and minimum tax when income exceeds the threshold.
    - If income is equal to or below the threshold,
      net payable tax is zero under the assignment rules.

    Verify all of the following:

    - Total income
    - Tax-free threshold
    - Taxable income
    - Gross tax
    - Actual investment
    - Allowable investment
    - Investment rebate
    - Tax after rebate
    - Minimum tax
    - Final net payable tax

    IMPORTANT:
    - Use the actual slab limits and rates from the database.
    - Show the slab-by-slab calculation for the current taxpayer.
    - Check that each slab is calculated progressively.
    - Do not rely only on the Calculator Agent's final number.
    - Do not use a previous test case as the calculation
      basis for the current taxpayer.
    - Use the Calculate Slab Tax tool's numerical output
      as the primary calculation result.
    - If the written explanation contradicts the tool output,
      identify the inconsistency.
    - Do not invent alternative tax rates or figures.

    ==========================================
    4. INVESTMENT VALIDATION
    ==========================================

    - Compare actual declared investment with total income.
    - Check the allowable investment cap.
    - Verify the investment rebate.
    - If declared investment exceeds total income,
      mark the report as Flagged.
    - Include the warning returned by the calculation tool.
    - Do not treat the capped investment calculation
      as proof that the declared investment is valid.

    ==========================================
    5. DOCUMENT VALIDATION
    ==========================================

    - Verify all common documents are included.
    - Verify documents for each relevant income source.
    - If TIN is unavailable, TIN Registration must be
      the first checklist item.
    - Verify documents against the required_docs section
      of the local tax database.
    - Do not invent or add documents that are not listed
      in the local database.
    - If a profession is unknown, verify that the
      general common-document checklist is used.

    ==========================================
    6. VALIDATION AND COMPLIANCE
    ==========================================

    Check for:

    - Negative income
    - Invalid or missing values
    - Excessive investment
    - Incorrect tax calculations
    - Incorrect slab explanations
    - Classification inconsistencies
    - Filing obligation errors
    - Missing or invented documents
    - Ignored calculation warnings

    Mark compliance as:

    Passed:
    All outputs, calculations, explanations, and documents
    are consistent with the local database and assignment rules.

    Flagged:
    Any calculation, explanation, eligibility, investment,
    or document inconsistency exists.

    Do not mark Passed if filing obligation and
    independent filing ability are confused.

    Do not mark Passed if the Calculator Agent ignores
    an investment warning.

    ==========================================
    FINAL REPORT FORMAT
    ==========================================

    SECTION 1: FINAL TAX REPORT

    | Category | Details | Amount (BDT) |
    |---|---|---|

    Include:

    - Taxpayer Category
    - Filing Obligation
    - Independent Filing Ability
    - Tax-Free Threshold
    - Total Income
    - Taxable Income
    - Gross Tax
    - Actual Investment
    - Allowable Investment
    - Investment Rebate
    - Minimum Tax
    - Final Net Payable Tax

    Use N/A for non-monetary amounts.

    SECTION 2: REQUIRED DOCUMENTS

    Provide the complete customized checklist as bullet points.

    SECTION 3: COMPLIANCE REVIEW

    State Passed or Flagged.

    Explain all findings, inconsistencies, and warnings.
    Include the progressive slab calculation when relevant.

    SECTION 4: বাংলা সারসংক্ষেপ

    Write exactly four separate lines:

    1. Filing obligation and independent filing ability.
    2. Total tax payable.
    3. Required documents.
    4. Compliance result.

    Use only the local database and simplified assignment rules.
    Never invent tax rates, thresholds, or requirements.

    Do not include internal reasoning or conversational
    commentary in the final report.

    """,

    expected_output="""

    A final report containing:

    1. An English Markdown tax table.
    2. A customized document checklist.
    3. A strict Passed or Flagged compliance review.
    4. Exactly four separate Bangla summary lines.

    Filing obligation and independent filing ability must
    always be reported separately.

    All numerical results must be consistent across
    the English report and Bangla summary.

    """,

    agent=reviewer_agent,

    context=[
        classifier_task,
        calculator_task,
        document_task
    ]
)
