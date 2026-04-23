from sqlalchemy.orm import Session
from database.models.gamification import Achievement, UserAchievement
from database.models.user import User
import uuid

class AchievementService:
    def __init__(self, db: Session):
        self.db = db

    def check_and_award(self, user_id: uuid.UUID, event_type: str, event_data: dict = None):
        """После важного действия (завершение урока, серия правильных ответов и т.д.)"""
        achievements = self.db.query(Achievement).filter(
            Achievement.condition_type == event_type
        ).all()

        for ach in achievements:
            if self._condition_met(ach, user_id, event_data):
                existing = self.db.query(UserAchievement).filter(
                    UserAchievement.user_id == user_id,
                    UserAchievement.achievement_id == ach.id
                ).first()
                if not existing:
                    ua = UserAchievement(user_id=user_id, achievement_id=ach.id)
                    self.db.add(ua)
                    # Награда
                    from services.currency_service import CurrencyService
                    curr = CurrencyService(self.db)
                    if ach.xp_reward:
                        # Здесь нужно сервис прогресса для добавления XP, но передадим обработку вызывающему коду
                        pass
                    if ach.coins_reward:
                        curr.add_coins(user_id, ach.coins_reward)
                    if ach.crystals_reward:
                        curr.add_crystals(user_id, ach.crystals_reward)
                    if ach.item_reward_id:
                        from services.shop_service import ShopService
                        shop = ShopService(self.db)
                        shop.add_item_to_inventory(user_id, ach.item_reward_id)
                    self.db.commit()

    def _condition_met(self, achievement: Achievement, user_id: uuid.UUID, event_data: dict) -> bool:
        data = achievement.condition_data
        if achievement.condition_type == 'complete_track':
            # data: {"track_id": int}
            return event_data.get('track_id') == data['track_id']
        elif achievement.condition_type == 'streak':
            # data: {"days": int}
            user = self.db.query(User).filter(User.id == user_id).first()
            return user.current_streak >= data['days']
        elif achievement.condition_type == 'count_tasks':
            # data: {"count": int}
            from database.models.progress import TaskAttempt
            count = self.db.query(TaskAttempt).filter(
                TaskAttempt.user_id == user_id,
                TaskAttempt.is_correct == True
            ).count()
            return count >= data['count']
        # Другие типы можно расширить аналогично
        return False