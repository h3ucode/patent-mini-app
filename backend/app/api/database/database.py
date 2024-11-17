from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    JSON,
    ForeignKey,
    Text,
    Boolean,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
import json
from pathlib import Path
from uuid import uuid4
from sqlalchemy.orm import Session


SQLALCHEMY_DATABASE_URL = "sqlite:///./data/patent_db.sqlite"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False, "timeout": 30}
)

# Create scoped session factory
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

Base = declarative_base()


class Claim(Base):
    __tablename__ = "claims"

    claim_id = Column(Integer, primary_key=True)
    num = Column(String, index=True)
    text = Column(Text)
    patent_id = Column(Integer, ForeignKey("patents.patent_id"))
    patent = relationship("Patent", back_populates="claims")


class Patent(Base):
    __tablename__ = "patents"

    patent_id = Column(Integer, primary_key=True)
    publication_number = Column(String, index=True)
    title = Column(String)
    ai_summary = Column(Text, nullable=True)
    raw_source_url = Column(String, nullable=True)
    assignee = Column(String, nullable=True)
    inventors = Column(String, nullable=True)
    priority_date = Column(String, nullable=True)
    application_date = Column(String, nullable=True)
    grant_date = Column(String, nullable=True)
    abstract = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    jurisdictions = Column(String, nullable=True)
    classifications = Column(String, nullable=True)
    citations = Column(String, nullable=True)
    image_urls = Column(String, nullable=True)
    landscapes = Column(String, nullable=True)
    created_at = Column(String, nullable=True)
    updated_at = Column(String, nullable=True)
    publish_date = Column(String, nullable=True)
    citations_non_patent = Column(String, nullable=True)
    provenance = Column(String, nullable=True)
    attachment_urls = Column(String, nullable=True)
    application_events = Column(String, nullable=True)
    claims = relationship(
        "Claim",
        back_populates="patent",
        cascade="all, delete-orphan",
        lazy="dynamic",  # This is important for relay-style pagination
    )

    def __init__(self, **kwargs):
        claims_data = None
        if "claims" in kwargs:
            if isinstance(kwargs["claims"], str):
                claims_data = json.loads(kwargs["claims"])
            else:
                claims_data = kwargs["claims"]
            kwargs.pop("claims")

        valid_fields = self.__table__.columns.keys()
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_fields}

        for field in ["inventors", "classifications", "citations", "image_urls"]:
            if isinstance(filtered_kwargs.get(field), (dict, list)):
                filtered_kwargs[field] = json.dumps(filtered_kwargs[field])

        super().__init__(**filtered_kwargs)

        # Create claims after patent is initialized
        if claims_data:
            for claim in claims_data:
                self.claims.append(Claim(num=claim["num"], text=claim["text"]))


class Company(Base):
    __tablename__ = "companies"
    company_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    products = relationship("Product", back_populates="company")


class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String, nullable=True)
    company_id = Column(Integer, ForeignKey("companies.company_id"))
    company = relationship("Company", back_populates="products")


class ProductPatentAnalysis(Base):
    __tablename__ = "product_patent_analyses"

    product_analysis_id = Column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    patent_id = Column(Integer, ForeignKey("patents.patent_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))
    company_analysis_id = Column(
        String(36),
        ForeignKey("company_patent_analyses.company_analysis_id"),
        nullable=True,
    )
    infringement_likelihood = Column(String)  # High, Medium, Low
    relevant_claims = Column(String)  # JSON string of claim numbers
    explanation = Column(String)
    specific_features = Column(String)  # JSON string of features
    created_at = Column(String)

    patent = relationship("Patent", backref="product_patent_analyses")
    product = relationship("Product", backref="product_patent_analyses")
    company_analysis = relationship(
        "CompanyPatentAnalysis",
        back_populates="product_analyses",
        foreign_keys=[company_analysis_id],
    )


class CompanyPatentAnalysis(Base):
    __tablename__ = "company_patent_analyses"

    company_analysis_id = Column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    patent_id = Column(Integer, ForeignKey("patents.patent_id"))
    company_id = Column(Integer, ForeignKey("companies.company_id"))
    overall_risk = Column(String)
    overall_risk_assessment = Column(String)
    created_at = Column(String)
    is_saved = Column(Boolean, default=False)
    is_saved_at = Column(String, nullable=True)

    patent = relationship("Patent", backref="company_patent_analyses")
    company = relationship("Company", backref="company_patent_analyses")
    product_analyses = relationship(
        "ProductPatentAnalysis",
        back_populates="company_analysis",
        foreign_keys=[ProductPatentAnalysis.company_analysis_id],
        lazy="joined",
    )


def create_fresh_db():
    """Creates a fresh database with initial data"""
    print("Creating fresh database...")

    # Drop and create all tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Schema created successfully")

    # Initialize with company and patent data
    initialize_company_and_patent()
    print("Fresh database created with initial data")


def update_schema():
    """Updates schema without affecting existing data"""
    print("Updating database schema...")
    try:
        # First ensure all tables exist
        Base.metadata.create_all(bind=engine)
        print("Base tables verified")

        # Get all models from Base
        for table in Base.metadata.sorted_tables:
            table_name = table.name
            print(f"\nChecking table: {table_name}")

            # Get expected columns from model
            model_columns = {col.name: col for col in table.columns}

            # Get existing columns from database
            with engine.connect() as conn:
                result = conn.execute(f"PRAGMA table_info('{table_name}')")
                existing_columns = {row[1]: row for row in result.fetchall()}

                # Check for missing columns
                for col_name, col in model_columns.items():
                    if col_name not in existing_columns:
                        print(f"Adding column {col_name} to {table_name}")

                        # Get column type for SQLite
                        col_type = str(col.type)
                        if isinstance(col.type, Boolean):
                            col_type = "BOOLEAN"

                        # Get default value if any
                        default_value = ""
                        if col.default is not None:
                            if isinstance(col.default.arg, bool):
                                default_value = (
                                    f" DEFAULT {1 if col.default.arg else 0}"
                                )
                            else:
                                default_value = f" DEFAULT {col.default.arg}"

                        # Construct and execute ALTER TABLE statement
                        alter_stmt = f"""
                            ALTER TABLE {table_name} 
                            ADD COLUMN {col_name} {col_type}{default_value}
                        """
                        try:
                            conn.execute(alter_stmt)
                            conn.commit()
                            print(f"Successfully added column {col_name}")
                        except Exception as e:
                            print(f"Error adding column {col_name}: {e}")
                            continue

        print("\nSchema update complete")

    except Exception as e:
        print(f"Error in schema update: {e}")
        raise


def init_db(fresh=False):
    """Main initialization function"""
    if fresh:
        create_fresh_db()
    else:
        update_schema()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        SessionLocal.remove()


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        SessionLocal.remove()


def initialize_company_and_patent():
    db = SessionLocal()
    try:
        # Check if database is empty
        if not db.query(Patent).first():
            print("Database is empty, loading initial data...")

            # Load patents
            patents_file = Path("/app/data/patents.json")
            if patents_file.exists():
                with open(patents_file, "r") as f:
                    patents = json.load(f)
                    print(f"Found {len(patents)} patents to insert")
                    for patent in patents:
                        try:
                            db_patent = Patent(**patent)
                            db.add(db_patent)
                        except Exception as e:
                            print(f"Error inserting patent: {e}")
                            print(f"Patent data: {patent}")
                            raise e
                db.commit()
                print("Patents data loaded successfully")
            else:
                print("Patents file not found")

            # Load companies and products
            if not db.query(Company).first():
                products_file = Path("/app/data/company_products.json")
                if products_file.exists():
                    with open(products_file, "r") as f:
                        companies_list = json.load(f).get("companies")
                        print(f"Found {len(companies_list)} companies to insert")
                        for company_data in companies_list:
                            company_name = company_data.get("name")
                            product_list = company_data.get("products")

                            company = Company(name=company_name)
                            db.add(company)
                            db.flush()

                            for product_data in product_list:
                                product = Product(
                                    name=product_data["name"],
                                    description=product_data.get("description"),
                                    company_id=company.company_id,
                                )
                                db.add(product)
                    db.commit()
                    print("Companies and products loaded successfully")
                else:
                    print("Company products file not found")
        else:
            print("Database already contains data, skipping initialization")
    finally:
        db.close()
