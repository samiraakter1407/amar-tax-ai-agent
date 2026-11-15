# Amar Tax — Bangladesh AI Tax Advisor

A multi-agent AI tax advisory system built with **CrewAI**, **Python**, and **Google Gemini**. The system analyzes taxpayer profiles, calculates estimated tax using a simulated Bangladesh tax database, organizes required documents, and reviews the final report for inconsistencies.

> **Disclaimer:** This project uses simplified, simulated tax rules for an academic assignment. It is not an official Bangladesh NBR tax calculator and should not be used for actual tax filing.

## Features

- **Taxpayer Classification Agent:** Determines taxpayer category, tax-free threshold, filing obligation, and minimum tax.
- **Slab Calculator Agent:** Calculates progressive income tax, allowable investment, investment rebate, and net payable tax.
- **Document Organizer Agent:** Generates a profession-specific document checklist.
- **Compliance Reviewer Agent:** Cross-checks the other agents' outputs and assigns a Passed or Flagged status.
- **Structured Output:** Uses Pydantic for taxpayer classification.
- **Custom Tools:** Uses local tax database lookup and tax calculation tools.
- **Bangla Summary:** Produces a short Bangla summary alongside the English report.

## Technology Stack

- Python 3.13
- CrewAI
- Google Gemini
- Pydantic
- python-dotenv
- JSON

## Project Structure

```text
amar-tax-ai-agent/
│
├── agents/
│   ├── __init__.py
│   └── tax_agents.py
│
├── data/
│   └── tax_rules.json
│
├── models/
│   ├── __init__.py
│   └── tax_models.py
│
├── outputs/
│
├── tasks/
│   ├── __init__.py
│   └── tax_tasks.py
│
├── tools/
│   ├── __init__.py
│   └── tax_tools.py
│
├── venv/
│
├── .env
├── .gitignore
├── main.py
├── requirements.txt
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd amar-tax-ai-agent
```

Replace `YOUR_REPOSITORY_URL` with the actual repository URL.

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Gemini API key

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Replace the placeholder with your own API key. Never commit your `.env` file or expose your API key publicly.

### 5. Run the application

```bash
python main.py
```

## Multi-Agent Workflow

The application follows a sequential multi-agent workflow:

1. **Classifier:** Analyzes the taxpayer profile and retrieves the applicable tax rules.
2. **Calculator:** Uses the classification results to calculate tax progressively.
3. **Document Organizer:** Creates a document checklist based on profession and income sources.
4. **Compliance Reviewer:** Reviews the previous outputs and produces the final tax readiness report.

The agents exchange information through CrewAI task context.

## Simplified Tax Calculation Assumptions

The project uses the local `data/tax_rules.json` file as its source of truth.

- Taxable income is calculated after deducting the applicable tax-free threshold.
- Progressive tax slabs are applied to taxable income.
- Allowable investment is capped at 20% of total income.
- Investment rebate is 15% of allowable investment.
- Net tax is the greater of tax after rebate and minimum tax when income exceeds the threshold.
- Net payable tax is zero when income is equal to or below the applicable threshold.

These are simulated assignment rules, not a statement of current official tax law.

## Error Handling

The system is designed to identify the following cases:

- Taxpayers under 18 cannot file independently.
- Negative or invalid income is flagged.
- Investment exceeding total income is flagged.
- Filing is not mandatory when income is at or below the applicable threshold under the simplified rules.
- Taxpayers without a TIN receive a TIN Registration checklist item.
- Unknown professions use the general document checklist.

## Test Scenarios

The assignment includes the following test scenarios:

| Test | Scenario | Expected behavior |
|---|---|---|
| 1 | Example scenario: 34-year-old female, total income ৳1,500,000, investment ৳200,000 | Net tax ৳110,000; Passed |
| 2 | 16-year-old with income ৳500,000 | Minor filing restriction flagged |
| 3 | 45-year-old male, income ৳300,000, Rangpur | Filing not mandatory under simplified rules |
| 4 | Income ৳800,000, investment ৳1,000,000 | Excessive investment flagged |

## Local Database and Fallback

The simulated tax rules are stored in `data/tax_rules.json`. The custom tools read this local database for thresholds, progressive slabs, minimum tax, investment rebate, and document requirements.

The local database is intended to provide a consistent source of tax rules for the assignment, rather than relying on live tax information.

## Limitations

- Tax rules are simulated for educational purposes.
- The system does not submit tax returns.
- Tax calculations depend on the local JSON database and simplified assumptions.
- AI-generated explanations may require human review.
- Gemini API availability and rate limits may affect execution.

## Security

- Keep API credentials in `.env`.
- Do not commit `.env` or virtual environment files.
- Review `.gitignore` before pushing the project to GitHub.

## Author

Developed as an academic project for Applied AI with Multi-Agent Systems (CrewAI).
