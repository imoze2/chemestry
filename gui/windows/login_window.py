# gui/windows/login_window.py

from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QMessageBox
)

from PyQt6.QtCore import Qt

from gui.windows.register_window import RegisterWindow
from gui.windows.main_window import MainMenuWindow
from services.auth_service import AuthService

class LoginWindow(QWidget):

    def __init__(self, db_session):
        super().__init__()

        self.db_session = db_session

        self.setWindowTitle("Интерактивная химия | Вход")
        self.setFixedSize(400, 300)

        self.init_ui()

    def init_ui(self):

        layout = QVBoxLayout()
        layout.setSpacing(15)

        title = QLabel("Вход")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Имя пользователя")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        login_button = QPushButton("Войти")
        login_button.clicked.connect(self.login)

        register_button = QPushButton("Регистрация")
        register_button.setFlat(True)
        register_button.clicked.connect(self.open_register)

        layout.addWidget(title)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(login_button)
        layout.addWidget(register_button)

        layout.addStretch()

        self.setLayout(layout)

    def open_register(self):
        self.register_window = RegisterWindow(self.db_session)
        self.register_window.show()
        self.close()

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        success, result = AuthService.login(username, password)

        if success:
            self.close()
            self.main_window = MainMenuWindow(result, self.db_session)
            self.main_window.show()

        else:
            QMessageBox.warning(self, "Ошибка!", result)
            self.username_input.clear()
            self.password_input.clear()