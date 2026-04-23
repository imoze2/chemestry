from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea, QGridLayout, QMessageBox
from services.shop_service import ShopService

class StoreWindow(QWidget):
    def __init__(self, user, db_session):
        super().__init__()
        self.user = user
        self.db = db_session
        self.shop_svc = ShopService(self.db)
        self.setWindowTitle("Магазин")
        self.setFixedSize(600, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("Магазин предметов")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        scroll = QScrollArea()
        container = QWidget()
        grid = QGridLayout()
        items = self.shop_svc.get_available_items()
        row = 0
        col = 0
        for shop_item in items:
            item_type = shop_item.item_type
            frame = QWidget()
            frame_layout = QVBoxLayout()
            frame_layout.addWidget(QLabel(f"<b>{item_type.name}</b>"))
            frame_layout.addWidget(QLabel(item_type.description))
            price = f"💰{shop_item.price_coins}" if shop_item.price_coins else f"💎{shop_item.price_crystals}"
            btn = QPushButton(f"Купить ({price})")
            btn.clicked.connect(lambda _, sid=shop_item.id: self.buy(sid))
            frame_layout.addWidget(btn)
            frame.setLayout(frame_layout)
            grid.addWidget(frame, row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1
        container.setLayout(grid)
        scroll.setWidget(container)
        layout.addWidget(scroll)

        back_btn = QPushButton("Назад в профиль")
        back_btn.clicked.connect(self.back_to_profile)
        layout.addWidget(back_btn)
        self.setLayout(layout)

    def buy(self, shop_item_id):
        success = self.shop_svc.purchase_item(self.user.id, shop_item_id)
        if success:
            QMessageBox.information(self, "Успех", "Предмет куплен!")
        else:
            QMessageBox.warning(self, "Ошибка", "Недостаточно средств.")

    def back_to_profile(self):
        from gui.windows.profile_window import ProfileWindow
        self.profile = ProfileWindow(self.user, self.db)
        self.profile.show()
        self.close()