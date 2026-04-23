# database/models/reference.py
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Text, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import JSONB, ARRAY, TSVECTOR
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.db import Base


class ReferenceArticle(Base):
    __tablename__ = "reference_articles"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(JSONB, nullable=False)
    summary = Column(Text)

    category = Column(String(50))
    topic_tags = Column(ARRAY(Text))

    search_keywords = Column(ARRAY(Text))
    chemical_formulas = Column(ARRAY(Text))

    required_lesson_id = Column(Integer, ForeignKey("lessons.id"))

    difficulty_level = Column(Integer)  # 1-3

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # связи с другими статьями
    related_from = relationship(
        "ReferenceArticleRelation",
        foreign_keys="ReferenceArticleRelation.article_id",
        back_populates="article",
        cascade="all, delete-orphan"
    )
    related_to = relationship(
        "ReferenceArticleRelation",
        foreign_keys="ReferenceArticleRelation.related_article_id",
        back_populates="related_article",
        cascade="all, delete-orphan"
    )
    search_index = relationship("ReferenceSearchIndex", back_populates="article", uselist=False, cascade="all, delete-orphan")


class ReferenceArticleRelation(Base):
    __tablename__ = "reference_article_relations"
    __table_args__ = (
        UniqueConstraint("article_id", "related_article_id", name="unique_article_relation"),
    )

    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey("reference_articles.id", ondelete="CASCADE"), nullable=False)
    related_article_id = Column(Integer, ForeignKey("reference_articles.id", ondelete="CASCADE"), nullable=False)

    article = relationship("ReferenceArticle", foreign_keys=[article_id], back_populates="related_from")
    related_article = relationship("ReferenceArticle", foreign_keys=[related_article_id], back_populates="related_to")


class ReferenceSearchIndex(Base):
    __tablename__ = "reference_search_index"

    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey("reference_articles.id", ondelete="CASCADE"), nullable=False)
    search_vector = Column(TSVECTOR)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    article = relationship("ReferenceArticle", back_populates="search_index")

    # Индекс создадим отдельно через сырой SQL при инициализации БД