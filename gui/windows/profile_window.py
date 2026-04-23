from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QFrame,
    QMessageBox
)

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap


class ProfileWindow(QWidget):

    def __init__(self, user, db_session):
        super().__init__()

        self.user = user
        self.session = db_session

        self.setWindowTitle("Интерактивная химия | Профиль")
        self.setFixedSize(600, 500)

        self.init_ui()

    def init_ui(self):

        main_layout = QVBoxLayout()

        # ---- верхняя панель ----

        top_layout = QHBoxLayout()

        settings_button = QPushButton("Настройки")
        settings_button.clicked.connect(self.open_settings)

        friends_button = QPushButton("Друзья")
        friends_button.clicked.connect(self.open_friends)

        menu_button = QPushButton("Меню")
        menu_button.clicked.connect(self.back_to_menu)

        top_layout.addWidget(settings_button)
        top_layout.addStretch()
        top_layout.addWidget(friends_button)
        top_layout.addStretch()
        top_layout.addWidget(menu_button)

        # ---- аватар ----

        avatar = QLabel()
        pixmap = QPixmap("C:\\0.0.Diploma2\\profile.png")

        avatar.setPixmap(pixmap.scaled(
            100,
            100,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))

        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ---- имя пользователя ----

        username_label = QLabel(self.user.username)
        username_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        username_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        # ---- витрина ----

        showcase_title = QLabel("Витрина")
        showcase_title.setStyleSheet("font-size: 16px;")

        showcase_scroll = self.create_scroll_section("здесь будет\nвитрина")

        # ---- достижения ----

        achievements_title = QLabel("Достижения")
        achievements_title.setStyleSheet("font-size: 16px;")

        achievements_scroll = self.create_scroll_section("здесь будет\nдостижение")

        # ---- сборка ----

        main_layout.addLayout(top_layout)

        main_layout.addSpacing(10)

        main_layout.addWidget(avatar)
        main_layout.addWidget(username_label)

        main_layout.addSpacing(20)

        main_layout.addWidget(showcase_title)
        main_layout.addWidget(showcase_scroll)

        main_layout.addSpacing(10)

        main_layout.addWidget(achievements_title)
        main_layout.addWidget(achievements_scroll)

        self.setLayout(main_layout)

    # ---- создание горизонтального скролла ----

    def create_scroll_section(self, filler):

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(120)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        layout = QHBoxLayout()

        # временные элементы витрины
        for _ in range(10):

            cell = QFrame()
            cell.setFixedSize(100, 100)
            cell.setStyleSheet("""
                background-color: #303030;
                border: 1px solid #999;
            """)

            label = QLabel(filler)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            cell_layout = QVBoxLayout()
            cell_layout.addWidget(label)

            cell.setLayout(cell_layout)

            layout.addWidget(cell)

        layout.addStretch()

        container.setLayout(layout)

        scroll.setWidget(container)

        return scroll

    # ---- кнопки ----

    def back_to_menu(self):
        from gui.windows.main_window import MainMenuWindow

        self.menu = MainMenuWindow(self.user, self.session)
        self.menu.show()

        self.close()

    def open_friends(self):
        from gui.windows.friends_window import FriendsWindow

        self.friends = FriendsWindow(self.user, self.session)
        self.friends.show()

        self.close()

    def open_settings(self):
        QMessageBox.information(self, None, "Открыть настройки")
