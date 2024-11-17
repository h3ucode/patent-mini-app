import json
from typing import List, Dict, Set
import re
import uuid
from openai import AsyncOpenAI
import os
from datetime import datetime
from sqlalchemy.orm import Session

from api.database.database import get_db_session
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
client = None
if os.getenv("OPENAI_API_KEY"):
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def ai_generate_company_overall_risk_assessment(
    overall_risk: str, product_analyses_explanations: List[str]
) -> str:
    """Generate overall risk assessment using AI"""
    if not client:
        return "AI analysis not available"

    prompt = f"""
    Generate a brief, one-paragraph risk assessment summary for a company's potential patent infringement.
    
    Overall Risk Level: {overall_risk}
    
    Product Analysis Details:
    {' '.join(product_analyses_explanations)}
    
    Create a concise summary that:
    1. States the overall risk level and why
    2. Briefly mentions which products contribute most to the risk
    3. Keeps the entire summary to 2-3 sentences maximum
    
    Example format:
    "High risk of infringement due to implementation of core patent claims in multiple products, particularly 
    the Shopping App which implements most key elements of the patent claims. Walmart+ presents additional 
    moderate risk through its partial implementation of the patented technology."
    
    Provide only the summary paragraph, nothing else.
    """

    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a patent analysis expert. Be concise and focus on key risks.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=150,  # Limit response length
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error generating risk assessment: {e}")
        return f"Error generating risk assessment: {str(e)}"


async def analyze_claims_batch(claims_text: str, products_text: str) -> Dict:
    """Analyze multiple claims against multiple products in a single GPT call"""
    if not client:
        return {"product_analyses": {}}

    prompt = f"""
    Analyze if any of these products potentially infringe on the patent claims.
    
    Patent Claims:
    {claims_text}
    
    Products to Analyze:
    {products_text}
    
    For each product that might infringe any claims, analyze:
    1. Which specific claims are potentially infringed
    2. Brief explanation of how the product matches each claim
    
    You must respond in this exact JSON format, nothing else:
    {{
        "product_analyses": {{
            "product_name": {{
                "relevant_claims": ["claim numbers"],
                "explanations": {{
                    "claim_number": "brief explanation for this claim"
                }}
            }}
        }}
    }}
    
    Focus on technical implementations and only include strong matches.
    Be concise but specific in explanations.
    """

    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo-16k",  # Using 16K model for larger context
            messages=[
                {
                    "role": "system",
                    "content": "You are a patent analysis expert. Be precise and focus on technical implementations. Always respond in valid JSON format.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )

        # Extract JSON from the response text
        response_text = response.choices[0].message.content.strip()
        try:
            # Try to parse the response as JSON
            result = json.loads(response_text)
            return result.get("product_analyses", {})
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Raw response: {response_text}")
            return {"product_analyses": {}}

    except Exception as e:
        print(f"GPT batch analysis failed: {str(e)}")
        return {"product_analyses": {}}


async def ai_detail_product_infringement_analysis(
    claims_text: str, product_text: str
) -> Dict:
    """Analyze claims against a product with detailed infringement analysis"""
    if not client:
        return {
            "infringement_likelihood": "Error",
            "relevant_claims": [],
            "explanation": "AI analysis not available",
            "specific_features": [],
            "claim_details": {},
        }

    prompt = f"""
    You are an expert patent infringement analyst. Analyze if this product potentially infringes on the listed patent claims.

    Given the following list of patent claims,  I want you to check product's description and check against the claims.
    If you believe the product infringes on any of the claims, listed the claim numbers in the "relevant_claims" field.
    
    Patent Claims:
    {claims_text}
    
    Product to Analyze:
    {product_text}
    
    Analyze and strictly follow these criteria for infringement likelihood:
    1. HIGH Risk (Must meet either condition):
       - Product relates to 6 or more listed claims
       - Product implements core technical features
    2. MODERATE Risk:
       - Product matches 2-5 listed claims
       - Or implements core features from 1-2 independent claims
    3. LOW Risk:
       - Product matches only 1 listed claim or has only partial/indirect matches
       - Or implements no core technical features
    
    You must respond in this exact JSON format:
    {{
        "infringement_likelihood": "High/Moderate/Low",
        "relevant_claims": ["claim numbers that are potentially infringed"],
        "explanation": "brief explanation of how the product potentially infringes the patent",
        "specific_features": ["key technical feature 1", "key technical feature 2", ...],
    }}
    

    Only list the claim number in the "relevant_claims" field if you are 100% sure the product infringes on the claim.
    Focus on technical implementations and only include strong matches.
    Be specific about technical features and implementations.
    """

    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {
                    "role": "system",
                    "content": "You are a patent analysis expert. Be precise and focus on technical implementations. Always respond in valid JSON format.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )

        # Extract JSON from the response text
        response_text = response.choices[0].message.content.strip()
        try:
            # Parse response and ensure it matches ProductPatentAnalysis fields
            result = json.loads(response_text)

            return {
                "infringement_likelihood": result.get(
                    "infringement_likelihood", "Unknown"
                ),
                "relevant_claims": result.get("relevant_claims", []),
                "explanation": result.get("explanation", "Analysis failed"),
                "specific_features": result.get("specific_features", []),
            }
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Raw response: {response_text}")
            return {
                "infringement_likelihood": "Error",
                "relevant_claims": [],
                "explanation": "Error parsing analysis results",
                "specific_features": [],
            }

    except Exception as e:
        print(f"GPT analysis failed: {str(e)}")
        return {
            "infringement_likelihood": "Error",
            "relevant_claims": [],
            "explanation": f"Analysis failed: {str(e)}",
            "specific_features": [],
        }
