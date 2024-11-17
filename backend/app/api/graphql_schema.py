from graphene import Schema
from .graphql.query import Query
from .graphql.mutation import Mutation
from .graphql.context import get_context

schema = Schema(query=Query, mutation=Mutation)
