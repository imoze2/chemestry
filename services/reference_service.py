from sqlalchemy.orm import Session
from database.models.reference import ReferenceArticle, ReferenceSearchIndex
from sqlalchemy import func
from typing import List

class ReferenceService:
    def __init__(self, db: Session):
        self.db = db

    def search(self, query: str, filters: dict = None) -> List[ReferenceArticle]:
        """Полнотекстовый поиск по статьям"""
        tsquery = func.plainto_tsquery('russian', query)
        articles = self.db.query(ReferenceArticle).join(
            ReferenceSearchIndex,
            ReferenceArticle.id == ReferenceSearchIndex.article_id
        ).filter(
            ReferenceSearchIndex.search_vector.op('@@')(tsquery)
        ).order_by(
            func.ts_rank(ReferenceSearchIndex.search_vector, tsquery).desc()
        ).all()
        return articles

    def get_articles_by_category(self, category: str) -> List[ReferenceArticle]:
        return self.db.query(ReferenceArticle).filter(
            ReferenceArticle.category == category
        ).all()

    def get_article(self, article_id: int) -> ReferenceArticle:
        return self.db.query(ReferenceArticle).filter(ReferenceArticle.id == article_id).first()