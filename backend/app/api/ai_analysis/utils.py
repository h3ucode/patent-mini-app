import re
from typing import Dict, List


def build_claim_tree(claims) -> Dict:
    """Build a tree structure of claim dependencies"""
    claim_tree = {"base_claims": [], "dependent_claims": {}}

    for claim in claims:
        dependency_match = re.search(r"claim (\d+)", claim.text.lower())
        if dependency_match:
            parent_num = str(int(dependency_match.group(1))).zfill(5)
            if parent_num not in claim_tree["dependent_claims"]:
                claim_tree["dependent_claims"][parent_num] = [claim]
            else:
                claim_tree["dependent_claims"][parent_num].append(claim)
        else:
            claim_tree["base_claims"].append(claim)

    print(
        f"Base Claims: {len(claim_tree['base_claims'])}, Dependent Claims: {claim_tree['base_claims']}"
    )
    return claim_tree


def generate_product_summary(
    product_name: str, relevant_claims: List[str], explanations: Dict[str, str]
) -> str:
    """Generate a concise summary for a product's claim matches"""
    if not relevant_claims:
        return f"No relevant claims found for {product_name}"

    claim_summaries = []
    for claim_num in relevant_claims:
        explanation = explanations.get(claim_num, "").split(".")[
            0
        ]  # Get first sentence
        claim_summaries.append(f"Claim {claim_num}: {explanation}")

    return (
        f"{product_name} potentially infringes on {len(relevant_claims)} claims. "
        f"Key findings: {'; '.join(claim_summaries)}"
    )
