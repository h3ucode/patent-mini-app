import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from ..database import database

import json


class Claim(SQLAlchemyObjectType):
    class Meta:
        model = database.Claim
        interfaces = (graphene.relay.Node,)
        id = graphene.ID(source="claim_id")


class ClaimConnection(graphene.relay.Connection):
    class Meta:
        node = Claim
        interfaces = (graphene.relay.Node,)

    total_count = graphene.Int()

    def resolve_total_count(root, info):
        return len(root.edges) if root.edges else 0


class ClaimEdge(graphene.ObjectType):
    """Edge type for Claims"""

    node = graphene.Field(Claim)
    cursor = graphene.String()


class Patent(SQLAlchemyObjectType):
    class Meta:
        model = database.Patent
        interfaces = (graphene.relay.Node,)
        id = graphene.ID(source="patent_id")

    claims = graphene.Field(ClaimConnection)

    def resolve_claims(self, info):
        claims_list = self.claims.all() if self.claims else []

        # Create connection manually
        edges = [
            ClaimEdge(node=claim, cursor=str(i)) for i, claim in enumerate(claims_list)
        ]

        # Create connection
        connection = ClaimConnection(
            edges=edges,
            page_info=graphene.relay.PageInfo(
                has_next_page=False,
                has_previous_page=False,
                start_cursor=edges[0].cursor if edges else None,
                end_cursor=edges[-1].cursor if edges else None,
            ),
        )

        return connection


class Product(SQLAlchemyObjectType):
    class Meta:
        model = database.Product
        interfaces = (graphene.relay.Node,)
        id = graphene.ID(source="product_id")


class Company(SQLAlchemyObjectType):
    class Meta:
        model = database.Company
        interfaces = (graphene.relay.Node,)
        id = graphene.ID(source="company_id")

    products = graphene.List(Product)

    def resolve_products(self, info):
        return self.products


# Analysis Types
class ValidationResult(graphene.ObjectType):
    success = graphene.Boolean()
    message = graphene.String()
    patent_title = graphene.String()
    product_description = graphene.String()


class AnalysisResult(graphene.ObjectType):
    success = graphene.Boolean()
    patent_id = graphene.Int()
    product_id = graphene.Int()
    infringement_likelihood = graphene.String()
    relevant_claims = graphene.List(graphene.String)
    explanation = graphene.String()
    specific_features = graphene.List(graphene.String)
    created_at = graphene.String()


class ProductAnalysisResult(graphene.ObjectType):
    """Result of analyzing a patent and a product"""

    product_analysis_id = graphene.String()
    patent_id = graphene.Int()
    product_id = graphene.Int()
    product_name = graphene.String()
    infringement_likelihood = graphene.String()
    relevant_claims = graphene.List(graphene.String)
    explanation = graphene.String()
    specific_features = graphene.List(graphene.String)
    created_at = graphene.String()


class CompanyAnalysisResult(graphene.ObjectType):
    """Result of analyzing a company against a patent"""

    company_analysis_id = graphene.String()
    patent_id = graphene.Int()
    company_id = graphene.Int()
    company_name = graphene.String()
    overall_risk = graphene.String()
    overall_risk_assessment = graphene.String()
    product_analyses = graphene.List(ProductAnalysisResult)


class ProductPatentAnalysis(SQLAlchemyObjectType):
    class Meta:
        model = database.ProductPatentAnalysis
        interfaces = (graphene.relay.Node,)
        id = graphene.ID(source="product_analysis_id")

    # Add resolvers for JSON fields
    relevant_claims_list = graphene.List(graphene.String)
    specific_features_list = graphene.List(graphene.String)

    def resolve_relevant_claims_list(self, info):
        return json.loads(self.relevant_claims) if self.relevant_claims else []

    def resolve_specific_features_list(self, info):
        return json.loads(self.specific_features) if self.specific_features else []


class ProductAnalysisConnection(graphene.relay.Connection):
    class Meta:
        node = ProductPatentAnalysis


class CompanyPatentAnalysis(SQLAlchemyObjectType):
    class Meta:
        model = database.CompanyPatentAnalysis
        interfaces = (graphene.relay.Node,)
        id = graphene.ID(source="company_analysis_id")

    # Use SQLAlchemyConnectionField for edge-node traversal
    product_analyses = SQLAlchemyConnectionField(ProductAnalysisConnection)

    def resolve_product_analyses(self, info, **kwargs):
        # Add session to info.context
        if not hasattr(info.context, "get"):
            setattr(info.context, "get", lambda: info.context.db)
        return self.product_analyses
