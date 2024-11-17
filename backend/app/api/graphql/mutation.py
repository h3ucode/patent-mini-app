import graphene
from datetime import datetime
from .types import ValidationResult, ProductAnalysisResult, CompanyPatentAnalysis
from ..database import database

import logging
import traceback
from ..analysis import (
    analyze_company_against_patent,
    analyze_patent_with_single_product,
)
import json

logger = logging.getLogger(__name__)


class AnalyzeCompanyAgainstPatentInput(graphene.InputObjectType):
    patent_publication_number = graphene.String(required=True)
    company_name = graphene.String(required=True)


class AnalyzeProductAgainstPatentInput(graphene.InputObjectType):
    patent_id = graphene.String(required=True)
    product_name = graphene.String(required=True)


class ValidateInput(graphene.InputObjectType):
    patent_id = graphene.String(required=True)
    product_name = graphene.String(required=True)


class Mutation(graphene.ObjectType):
    analyze_product_patent = graphene.Field(
        ProductAnalysisResult, input=AnalyzeProductAgainstPatentInput(required=True)
    )

    async def resolve_analyze_product_patent(self, info, input):
        try:
            logger.info(f"Starting analysis for {input.patent_id}")
            db = info.context.db

            patent = (
                db.query(database.Patent)
                .filter(database.Patent.publication_number == input.patent_id)
                .first()
            )

            product = (
                db.query(database.Product)
                .filter(database.Product.name == input.product_name)
                .first()
            )

            if not patent or not product:
                raise Exception("Patent or product not found")

            product_patent_analysis = await analyze_patent_with_single_product(
                patent=patent,
                product=product,
                claims=[],
            )

            return ProductAnalysisResult(
                product_analysis_id=product_patent_analysis.product_analysis_id,
                patent_id=patent.patent_id,
                product_id=product.product_id,
                product_name=product.name,
                infringement_likelihood=product_patent_analysis.infringement_likelihood,
                relevant_claims=json.loads(product_patent_analysis.relevant_claims),
                explanation=product_patent_analysis.explanation,
                specific_features=json.loads(product_patent_analysis.specific_features),
                created_at=product_patent_analysis.created_at,
            )

        except Exception as e:
            logger.error(f"Error in analyze_patent: {e}")
            logger.error(traceback.format_exc())
            return ProductAnalysisResult(
                product_analysis_id=None,
                patent_id=None,
                product_id=None,
                product_name=None,
                infringement_likelihood="Error",
                relevant_claims=[],
                explanation=f"Error during analysis: {str(e)}",
                specific_features=[],
                created_at=datetime.now().isoformat(),
            )

    analyze_company_against_patent = graphene.Field(
        CompanyPatentAnalysis, input=AnalyzeCompanyAgainstPatentInput(required=True)
    )

    async def resolve_analyze_company_against_patent(
        self, info, input: AnalyzeCompanyAgainstPatentInput
    ):
        try:
            logger.info(f"Starting analysis for {input.patent_publication_number}")
            db = info.context.db

            patent = (
                db.query(database.Patent)
                .filter(
                    database.Patent.publication_number
                    == input.patent_publication_number
                )
                .first()
            )

            company = (
                db.query(database.Company)
                .filter(database.Company.name == input.company_name)
                .first()
            )

            if not patent or not company:
                raise Exception("Patent or company not found")

            company_patent_analysis = await analyze_company_against_patent(
                company, patent, top_n=2
            )

            return company_patent_analysis

        except Exception as e:
            logger.error(f"Error in analyze_patent: {e}")
            logger.error(traceback.format_exc())
            raise

    validate_inputs = graphene.Field(
        ValidationResult, input=ValidateInput(required=True)
    )

    def resolve_validate_inputs(self, info, input):
        try:
            logger.info(f"Starting validation for {input.patent_id}")
            db = info.context.db
            if not db:
                logger.error("No database session in context")
                raise Exception("Database session not available")

            patent = (
                db.query(database.Patent)
                .filter(database.Patent.publication_number == input.patent_id)
                .first()
            )

            product = (
                db.query(database.Product)
                .filter(database.Product.name == input.product_name)
                .first()
            )

            if not patent:
                logger.warning(f"Patent not found: {input.patent_id}")
                return ValidationResult(
                    success=False,
                    message=f"Patent not found: {input.patent_id}",
                    patent_title=None,
                    product_description=None,
                )

            if not product:
                logger.warning(f"Product not found: {input.product_name}")
                return ValidationResult(
                    success=False,
                    message=f"Product not found: {input.product_name}",
                    patent_title=None,
                    product_description=None,
                )

            logger.info(f"Found patent and product: {patent.title}, {product.name}")
            return ValidationResult(
                success=True,
                message="Validation successful",
                patent_title=patent.title,
                product_description=product.description,
            )

        except Exception as e:
            logger.error(f"Error in validate_inputs: {e}")
            logger.error(traceback.format_exc())
            return ValidationResult(
                success=False,
                message=f"Error during validation: {str(e)}",
                patent_title=None,
                product_description=None,
            )

    toggle_save_analysis = graphene.Field(
        CompanyPatentAnalysis,
        company_analysis_id=graphene.String(required=True),
        is_saved=graphene.Boolean(required=True),
    )

    def resolve_toggle_save_analysis(self, info, company_analysis_id, is_saved):
        try:
            db = info.context.db
            analysis = (
                db.query(database.CompanyPatentAnalysis)
                .filter(
                    database.CompanyPatentAnalysis.company_analysis_id
                    == company_analysis_id
                )
                .first()
            )

            if not analysis:
                raise Exception("Analysis not found")

            analysis.is_saved = is_saved
            if is_saved:
                analysis.is_saved_at = datetime.now().isoformat()
            else:
                analysis.is_saved_at = None

            db.commit()
            return analysis

        except Exception as e:
            logger.error(f"Error toggling save status: {e}")
            logger.error(traceback.format_exc())
            raise
