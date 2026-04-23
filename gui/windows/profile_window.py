from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from services.currency_service import CurrencyService
from services.shop_service import ShopService
from services.achievement_service import AchievementService  # нужно добавить метод get_user_achievements

class ProfileWindow(QWidget):
    def __init__(self, user, db_session):
        super().__init__()
        self.user = user
        self.db = db_session
        self.setWindowTitle("Профиль")
        self.setFixedSize(600, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        # Верхняя панель
        top = QHBoxLayout()
        back_btn = QPushButton("Меню")
        back_btn.clicked.connect(self.back_to_menu)
        friends_btn = QPushButton("Друзья")
        friends_btn.clicked.connect(self.open_friends)
        store_btn = QPushButton("Магазин")
        store_btn.clicked.connect(self.open_store)
        top.addWidget(back_btn)
        top.addStretch()
        top.addWidget(friends_btn)
        top.addWidget(store_btn)
        layout.addLayout(top)

        # Аватар
        avatar = QLabel()
        pix = QPixmap("C:\\0.0.Diploma2\\profile.png")
        avatar.setPixmap(pix.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio))
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(avatar)

        username = QLabel(self.user.username)
        username.setAlignment(Qt.AlignmentFlag.AlignCenter)
        username.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(username)

        # Валюта
        curr_svc = CurrencyService(self.db)
        wallet = curr_svc.get_or_create_wallet(self.user.id)
        currency_label = QLabel(f"Монеты: {wallet.coins}  Кристаллы: {wallet.crystals}")
        currency_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(currency_label)

        # Витрина (горизонтальный скролл)
        layout.addWidget(QLabel("Витрина"))
        self.showcase_scroll = self.create_showcase()
        layout.addWidget(self.showcase_scroll)

        # Достижения
        layout.addWidget(QLabel("Достижения"))
        self.achievements_scroll = self.create_achievements()
        layout.addWidget(self.achievements_scroll)

        self.setLayout(layout)

    def create_showcase(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(120)
        container = QWidget()
        h_layout = QHBoxLayout()
        shop_svc = ShopService(self.db)
        inventory = shop_svc.get_inventory(self.user.id)
        for inv in inventory:
            if inv.is_equipped == False and inv.item_type.category == 'showcase':  # только витрины
                frame = QFrame()
                frame.setFixedSize(80, 80)
                frame.setStyleSheet("background-color: #303030; border: 1px solid gray;")
                lbl = QLabel(inv.item_type.name)
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                f_layout = QVBoxLayout(frame)
                f_layout.addWidget(lbl)
                h_layout.addWidget(frame)
        container.setLayout(h_layout)
        scroll.setWidget(container)
        return scroll

    def create_achievements(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(100)
        container = QWidget()
        h_layout = QHBoxLayout()
        from database.models.gamification import UserAchievement
        achievements = self.db.query(UserAchievement).filter(
            UserAchievement.user_id == self.user.id,
            UserAchievement.shown_to_user == True
        ).all()
        for ua in achievements:
            frame = QFrame()
            frame.setFixedSize(70, 70)
            frame.setStyleSheet("background-color: #202020; border: 1px solid gold;")
            lbl = QLabel(ua.achievement.name)
            lbl.setWordWrap(True)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            f_layout = QVBoxLayout(frame)
            f_layout.addWidget(lbl)
            h_layout.addWidget(frame)
        container.setLayout(h_layout)
        scroll.setWidget(container)
        return scroll

    def open_store(self):
        from gui.windows.store_window import StoreWindow
        self.store = StoreWindow(self.user, self.db)
        self.store.show()
        self.close()

    def back_to_menu(self):
        from gui.windows.main_window import MainMenuWindow
        self.menu = MainMenuWindow(self.user, self.db)
        self.menu.show()
        self.close()

    def open_friends(self):
        from gui.windows.friends_window import FriendsWindow
        self.friends_win = FriendsWindow(self.user, self.db)
        self.friends_win.show()
        self.close()