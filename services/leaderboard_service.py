from datetime import date, timedelta
from sqlalchemy.orm import Session
from database.models.gamification import LeaderboardCategory, LeaderboardEntry
from database.models.user import User
import uuid

class LeaderboardService:
    def __init__(self, db: Session):
        self.db = db

    def update_entry(self, user_id: uuid.UUID, metric_type: str, score: float):
        """Обновляет запись лидерборда для заданной метрики"""
        category = self.db.query(LeaderboardCategory).filter(
            LeaderboardCategory.metric_type == metric_type,
            LeaderboardCategory.is_active == True
        ).first()
        if not category:
            return

        # Определяем период
        period_start = date.today()
        if category.reset_period == 'weekly':
            period_start = period_start - timedelta(days=period_start.weekday())
        elif category.reset_period == 'monthly':
            period_start = period_start.replace(day=1)
        elif category.reset_period == 'daily':
            period_start = period_start  # уже сегодня

        entry = self.db.query(LeaderboardEntry).filter(
            LeaderboardEntry.category_id == category.id,
            LeaderboardEntry.user_id == user_id,
            LeaderboardEntry.period_start == period_start
        ).first()

        if entry:
            if category.metric_type in ('xp_total', 'xp_weekly', 'xp_daily', 'xp_monthly'):
                entry.score += score  # для XP суммируем
            else:
                entry.score = score  # для точности/стриков заменяем
        else:
            entry = LeaderboardEntry(
                category_id=category.id,
                user_id=user_id,
                period_start=period_start,
                score=score,
                rank=0
            )
            self.db.add(entry)
        self.db.commit()

        # Пересчёт рангов (упрощённо, можно сделать по триггеру или отдельно)
        entries = self.db.query(LeaderboardEntry).filter(
            LeaderboardEntry.category_id == category.id,
            LeaderboardEntry.period_start == period_start
        ).order_by(LeaderboardEntry.score.desc()).all()
        for i, e in enumerate(entries, start=1):
            e.rank = i
        self.db.commit()