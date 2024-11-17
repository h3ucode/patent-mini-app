from typing import Optional
from sqlalchemy.orm import Session
from .. import database
from dataclasses import dataclass


@dataclass
class Context:
    """Context class that can be safely serialized"""

    db: Session = None

    def get(self, *args, **kwargs):
        """Required by SQLAlchemyConnectionField - returns the database session
        regardless of arguments passed"""
        return self.db


def get_context() -> Context:
    """Get context without dependency injection"""
    return Context()
