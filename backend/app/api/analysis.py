import json
from typing import List, Dict, Set
import re
import uuid
from openai import AsyncOpenAI
import os
from datetime import datetime
from sqlalchemy.orm import Session
from api.database.database import (
    Company,
    Product,
    Patent,
    Claim,
    ProductPatentAnalysis,
    CompanyPatentAnalysis,
)
from api.database.database import get_db_session
import logging
from api.ai_analysis.ai_analysis import (
    ai_generate_company_overall_risk_assessment,
    analyze_claims_batch,
    ai_detail_product_infringement_analysis,
)
from api.ai_analysis.utils import build_claim_tree

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Initialize OpenAI client if API key is available
client = None
if os.getenv("OPENAI_API_KEY"):
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def analyze_company_against_patent(
    company: Company, patent: Patent, top_n=2
) -> Dict:
    """
    Analyze company's top_n products with the most base claims against a patent

    Input:
    company: Company
    patent: Patent
    top_n: int, default is 2

    Returns a CompanyPatentAnalysis record
    """
    db = next(get_db_session())
    try:
        claims = patent.claims.all()
        claim_tree = build_claim_tree(claims)
        base_claim_analyses = await base_claim_analyze_company_products(
            company, claim_tree["base_claims"]
        )

        # print(f"base_claim_analyses: {base_claim_analyses}")

        company_analysis = CompanyPatentAnalysis(
            company_analysis_id=str(uuid.uuid4()),
            patent_id=patent.patent_id,
            company_id=company.company_id,
            overall_risk="Low",
            overall_risk_assessment="Initial assessment",
            created_at=datetime.now().isoformat(),
        )

        db.add(company_analysis)
        db.flush()

        product_patent_analyses = []
        risk_counts = {"High": 0, "Moderate": 0, "Low": 0}
        product_analyses_explanations = []

        sorted_base_claim_analyses = sorted(
            base_claim_analyses.items(),
            key=lambda x: len(x[1]["relevant_base_claims"]),
            reverse=True,
        )

        for product_name, analysis in sorted_base_claim_analyses[:top_n]:
            product = db.query(Product).filter(Product.name == product_name).first()
            if not product:
                continue

            dependent_claims = []
            for claim_num in analysis["relevant_base_claims"]:
                dependent_claims.extend(
                    claim_tree["dependent_claims"].get(claim_num, [])
                )
            product_patent_analysis = await analyze_patent_with_single_product(
                patent=patent,
                product=product,
                claims=dependent_claims,
                company_analysis_id=company_analysis.company_analysis_id,
            )

            product_analysis = ProductPatentAnalysis(
                product_analysis_id=str(uuid.uuid4()),
                patent_id=patent.patent_id,
                product_id=product.product_id,
                company_analysis_id=company_analysis.company_analysis_id,
                infringement_likelihood=product_patent_analysis.get(
                    "infringement_likelihood", "Unknown"
                ),
                relevant_claims=json.dumps(
                    product_patent_analysis.get("relevant_claims", [])
                ),
                explanation=product_patent_analysis.get(
                    "explanation", "Initial analysis"
                ),
                specific_features=json.dumps(
                    product_patent_analysis.get("specific_features", [])
                ),
                created_at=datetime.now().isoformat(),
            )

            db.add(product_analysis)
            product_patent_analyses.append(product_analysis)
            risk_counts[product_analysis.infringement_likelihood] += 1
            product_analyses_explanations.append(product_analysis.explanation)

        # Set overall risk based on highest count, if all count is 0, set to Low
        company_analysis.overall_risk = (
            max(risk_counts, key=risk_counts.get)
            if any(risk_counts.values())
            else "Low"
        )

        # use ai to generate overall risk assessment base on risk counts and prodcut explanations.
        company_analysis.overall_risk_assessment = (
            await ai_generate_company_overall_risk_assessment(
                company_analysis.overall_risk, product_analyses_explanations
            )
        )

        db.commit()
        db.refresh(company_analysis)

        return company_analysis

    except Exception as e:
        logger.error(f"Error in analyze_company_against_patent: {str(e)}")
        db.rollback()
        raise e
    finally:
        db.close()


async def base_claim_analyze_company_products(
    company: Company, base_claims: List[Claim]
) -> Dict:
    """
    Analyze company's products against base claims

    Input:
    company: Company
    base_claims: List[Claim]

    Returns a dict of product name and its analysis
    """
    # Format all claims once
    claims_text = "\n\n".join(
        [f"Claim {claim.num}:\n{claim.text}" for claim in base_claims]
    )

    products_text = "\n\n".join(
        [
            f"Product: {product.name}\n" f"Description: {product.description}"
            for product in company.products
        ]
    )

    print(
        f"Analyzing {len(list(company.products))} products for company: {company.name}"
    )

    # Single batch analysis for all products
    base_claim_analyses = await analyze_claims_batch(claims_text, products_text)

    return {
        product_name: {
            "relevant_base_claims": analysis.get("relevant_claims", []),
            # "explanation_summary": generate_product_summary(
            #     product_name,
            #     analysis.get("relevant_claims", []),
            #     analysis.get("explanations", {}),
            # ),
        }
        for product_name, analysis in base_claim_analyses.items()
        if analysis.get("relevant_claims")  # Only include products with matches
    }


async def analyze_patent_with_single_product(
    patent: Patent,
    product: Product,
    claims: List[Claim],
    company_analysis_id: str = None,  # Add this parameter
) -> Dict:
    """
    Analyze a patent against a single product with detailed infringement analysis

    Will create a ProductPatentAnalysis record if company_analysis_id is not provided (Future use for single product analysis feature)

    Input:
    patent: Patent
    product: Product
    claims: List[Claim]
    company_analysis_id: str, default is None

    Returns a dict of product analysis
    """
    db = next(get_db_session())
    try:
        claims_text = "\n\n".join(
            [f"Claim {claim.num}:\n{claim.text}" for claim in claims]
        )
        product_text = f"Product: {product.name}\nDescription: {product.description}"
        single_product_analysis = await ai_detail_product_infringement_analysis(
            claims_text, product_text
        )
        # print(f"single_product_analysis: {single_product_analysis}")
        if not company_analysis_id:
            new_analysis = ProductPatentAnalysis(
                product_analysis_id=str(uuid.uuid4()),
                patent_id=patent.patent_id,
                product_id=product.product_id,
                company_analysis_id=company_analysis_id,  # Link to company analysis if provided
                infringement_likelihood=single_product_analysis[
                    "infringement_likelihood"
                ],
                relevant_claims=json.dumps(single_product_analysis["relevant_claims"]),
                explanation=single_product_analysis["explanation"],
                specific_features=json.dumps(
                    single_product_analysis["specific_features"]
                ),
                created_at=datetime.now().isoformat(),
            )

            db.add(new_analysis)
            db.commit()
            db.refresh(new_analysis)
        return single_product_analysis

    except Exception as e:
        logger.error(f"Error in analyze_patent_with_single_product: {str(e)}")
        db.rollback()
        raise e
    finally:
        db.close()


# Example usage:
# company_analysis = await analyze_company_products(company, base_claims)
# Result format:
# {
#     "company_name": "Walmart Inc.",
#     "product_analyses": {
#         "Walmart Shopping App": {
#             "relevant_claims": ["00001", "00002"],
#             "summary": "Walmart Shopping App potentially infringes on 2 claims. Key findings: Claim 1: Implements mobile advertisement selection; Claim 2: Uses tracking payload"
#         },
#         "Walmart+": {
#             "relevant_claims": ["00001"],
#             "summary": "Walmart+ potentially infringes on 1 claim. Key findings: Claim 1: Implements shopping list generation from ads"
#         }
#     }
# }
