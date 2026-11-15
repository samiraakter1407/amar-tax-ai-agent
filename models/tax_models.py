
from pydantic import BaseModel, Field
from typing import List


# ==========================================
# PYDANTIC MODEL: TAXPAYER CLASSIFICATION
# ==========================================

class TaxpayerClassification(BaseModel):

    taxpayer_category: str = Field(
        description=(
            "Taxpayer category: General, Female, "
            "Senior 65+, Disabled, or Freedom Fighter"
        )
    )

    filing_mandatory: bool = Field(
        description=(
            "Whether filing a tax return is mandatory "
            "under the simplified assignment rules"
        )
    )

    tax_free_threshold: float = Field(
        description="Applicable tax-free income threshold in BDT"
    )

    minimum_tax: float = Field(
        description="Applicable minimum tax in BDT"
    )

    warnings: List[str] = Field(
        default_factory=list,
        description=(
            "Warnings or validation issues identified "
            "during taxpayer classification"
        )
    )
