from sqlalchemy import (
    Column, BigInteger, Integer, String, Text,
    Date, DateTime, ForeignKey, JSON, TIMESTAMP
)
from sqlalchemy.sql import func

from app.database import Base


class Region(Base):
    __tablename__ = "region"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    level = Column(String(20), nullable=False)
    state = Column(String(2))
    parent_id = Column(BigInteger, ForeignKey("region.id"))


class Category(Base):
    __tablename__ = "category"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)


class Opportunity(Base):
    __tablename__ = "opportunity"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    eligibility = Column(Text, nullable=False)

    required_documents = Column(JSON, nullable=False)
    application_steps = Column(JSON, nullable=False)

    region_id = Column(
        BigInteger,
        ForeignKey("region.id"),
        nullable=False
    )

    category_id = Column(
        BigInteger,
        ForeignKey("category.id"),
        nullable=False
    )

    last_reviewed = Column(Date, nullable=False)

    status = Column(
        String(20),
        nullable=False,
        default="unconfirmed"
    )

    created_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.current_timestamp()
    )


class Source(Base):
    __tablename__ = "source"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    opportunity_id = Column(
        BigInteger,
        ForeignKey("opportunity.id", ondelete="CASCADE"),
        nullable=False
    )

    name = Column(String(255), nullable=False)
    url = Column(String(2048), nullable=False)
    consulted_at = Column(Date, nullable=False)


class Document(Base):
    __tablename__ = "document"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    opportunity_id = Column(
        BigInteger,
        ForeignKey("opportunity.id", ondelete="CASCADE"),
        nullable=False
    )

    source_id = Column(
        BigInteger,
        ForeignKey("source.id", ondelete="SET NULL")
    )

    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding_model = Column(String(255))
