
from crewai import Crew, Process

from agents.tax_agents import (
    classifier_agent,
    calculator_agent,
    document_agent,
    reviewer_agent
)

from tasks.tax_tasks import (
    classifier_task,
    calculator_task,
    document_task,
    reviewer_task
)


# ==========================================
# CREATE THE AMAR TAX CREW
# ==========================================

amar_tax_crew = Crew(

    agents=[
        classifier_agent,
        calculator_agent,
        document_agent,
        reviewer_agent
    ],

    tasks=[
        classifier_task,
        calculator_task,
        document_task,
        reviewer_task
    ],

    process=Process.sequential,

    verbose=True
)


# ==========================================
# GENERATE TAX REPORT
# ==========================================

def generate_tax_report(user_profile):

    print("\n" + "=" * 60)
    print("                 AMAR TAX AI ADVISOR")
    print("=" * 60)

    result = amar_tax_crew.kickoff(
        inputs={
            "user_profile": user_profile
        }
    )

    return result


# ==========================================
# MAIN PROGRAM
# ==========================================

if __name__ == "__main__":

    # Sample taxpayer profile
    sample_profile = """
    Age: 35
    Gender: Male
    Profession: Salaried
    Annual Salary: 800000 BDT
    Freelance Income: 0 BDT
    Total Income: 800000 BDT
    Investment: 1000000 BDT
    Location: Dhaka
    TIN: Yes
    Disability Status: No
    Freedom Fighter Status: No
    """

    try:

        # Generate the tax report
        report = generate_tax_report(sample_profile)

        # Display the final report
        print("\n" + "=" * 60)
        print("                  FINAL TAX REPORT")
        print("=" * 60)

        print(report)

        print("\n" + "=" * 60)
        print("             TAX REPORT GENERATION COMPLETE")
        print("=" * 60)

    except Exception as error:

        print("\nAn error occurred while generating the tax report.")

        print(f"Error details: {error}")
