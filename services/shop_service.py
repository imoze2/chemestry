from sqlalchemy.orm import Session
from database.models.user import UserInventory, ShopItem, UserShowcase, ItemType
import uuid

class ShopService:
    def __init__(self, db: Session):
        self.db = db

    def get_available_items(self):
        return self.db.query(ShopItem).filter(ShopItem.is_active == True).all()

    def purchase_item(self, user_id: uuid.UUID, shop_item_id: int) -> bool:
        from services.currency_service import CurrencyService
        item = self.db.query(ShopItem).filter(ShopItem.id == shop_item_id).first()
        if not item:
            return False
        curr_svc = CurrencyService(self.db)
        can_afford = curr_svc.spend(user_id, coins=item.price_coins or 0, crystals=item.price_crystals or 0)
        if can_afford:
            self.add_item_to_inventory(user_id, item.item_type_id)
            return True
        return False

    def add_item_to_inventory(self, user_id: uuid.UUID, item_type_id: int, quantity=1):
        existing = self.db.query(UserInventory).filter(
            UserInventory.user_id == user_id,
            UserInventory.item_type_id == item_type_id
        ).first()
        if existing:
            existing.quantity += quantity
        else:
            inv = UserInventory(user_id=user_id, item_type_id=item_type_id, quantity=quantity)
            self.db.add(inv)
        self.db.commit()

    def get_inventory(self, user_id: uuid.UUID):
        return self.db.query(UserInventory).filter(UserInventory.user_id == user_id).all()

    def equip_item(self, user_id: uuid.UUID, inventory_id: int, slot: int = None):
        """Экипирует предмет (аватар, тему и т.п.)"""
        item = self.db.query(UserInventory).filter(UserInventory.id == inventory_id).first()
        if item and item.user_id == user_id:
            # Снять текущую экипировку этой категории
            type_category = item.item_type.category
            # ...
            item.is_equipped = True
            item.equipped_slot = slot
            self.db.commit()

    def place_in_showcase(self, user_id: uuid.UUID, inventory_id: int, slot_number: int, artifact_id: int = None):
        showcase = UserShowcase(
            user_id=user_id,
            showcase_item_id=inventory_id,
            slot_number=slot_number,
            artifact_item_id=artifact_id
        )
        self.db.add(showcase)
        self.db.commit()