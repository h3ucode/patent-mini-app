import graphene
from .types import Patent, Company, CompanyPatentAnalysis
from ..database import database
import logging

logger = logging.getLogger(__name__)


class Query(graphene.ObjectType):
    patent = graphene.Field(Patent, publication_number=graphene.String(required=True))
    search_patents = graphene.List(
        Patent,
        query=graphene.String(),
        assignee=graphene.String(),
        limit=graphene.Int(default_value=10),
    )

    def resolve_patent(self, info, publication_number):
        try:
            logger.info(f"Resolving patent: {publication_number}")
            db = info.context.db
            return (
                db.query(database.Patent)
                .filter(database.Patent.publication_number == publication_number)
                .first()
            )
        except Exception as e:
            logger.error(f"Error resolving patent: {e}")
            raise

    def resolve_search_patents(self, info, query=None, assignee=None, limit=10):
        try:
            logger.info(f"Searching patents: query={query}, assignee={assignee}")
            db = info.context.db
            query_obj = db.query(database.Patent)

            if query:
                query_obj = query_obj.filter(
                    database.Patent.title.ilike(f"%{query}%")
                    | database.Patent.abstract.ilike(f"%{query}%")
                )

            if assignee:
                query_obj = query_obj.filter(
                    database.Patent.assignee.ilike(f"%{assignee}%")
                )

            return query_obj.limit(limit).all()
        except Exception as e:
            logger.error(f"Error searching patents: {e}")
            raise

    companies = graphene.List(Company)

    def resolve_companies(self, info):
        try:
            logger.info("Fetching companies")
            db = info.context.db
            return db.query(database.Company).all()
        except Exception as e:
            logger.error(f"Error fetching companies: {e}")
            raise

    company = graphene.Field(Company, name=graphene.String(required=True))
    company_analysis = graphene.Field(
        CompanyPatentAnalysis, company_analysis_id=graphene.String(required=True)
    )

    def resolve_company_analysis(self, info, company_analysis_id):
        try:
            logger.info(f"Fetching company analysis: {company_analysis_id}")
            db = info.context.db
            return (
                db.query(database.CompanyPatentAnalysis)
                .filter(
                    database.CompanyPatentAnalysis.company_analysis_id
                    == company_analysis_id
                )
                .first()
            )
        except Exception as e:
            logger.error(f"Error fetching company analysis: {e}")
            raise

    saved_analyses = graphene.List(CompanyPatentAnalysis)

    def resolve_saved_analyses(self, info):
        try:
            db = info.context.db
            return (
                db.query(database.CompanyPatentAnalysis)
                .filter(database.CompanyPatentAnalysis.is_saved == True)
                .order_by(database.CompanyPatentAnalysis.created_at.desc())
                .all()
            )
        except Exception as e:
            logger.error(f"Error fetching saved analyses: {e}")
            raise
