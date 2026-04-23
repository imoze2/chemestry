from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QListWidget, QLabel, QScrollArea, QFrame, QSplitter
)
from PyQt6.QtCore import Qt
from database.models.reference import ReferenceArticle
from services.reference_service import ReferenceService
import json

class ReferenceWindow(QWidget):
    def __init__(self, user, db_session):
        super().__init__()
        self.user = user
        self.db = db_session
        self.ref_svc = ReferenceService(self.db)
        self.setWindowTitle("Справочник")
        self.setFixedSize(800, 600)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Поиск
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по статьям...")
        search_btn = QPushButton("Найти")
        search_btn.clicked.connect(self.perform_search)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        main_layout.addLayout(search_layout)

        # Сплиттер: список статей и просмотр
        splitter = QSplitter()
        self.article_list = QListWidget()
        self.article_list.itemClicked.connect(self.display_article)
        self.content_area = QScrollArea()
        self.content_label = QLabel()
        self.content_label.setWordWrap(True)
        self.content_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.content_area.setWidget(self.content_label)
        self.content_area.setWidgetResizable(True)

        splitter.addWidget(self.article_list)
        splitter.addWidget(self.content_area)
        splitter.setSizes([250, 550])

        main_layout.addWidget(splitter)

        # Категории (упрощённо)
        cat_layout = QHBoxLayout()
        for cat in ["Основы", "Неорганика", "Органика", "Реакции"]:
            btn = QPushButton(cat)
            btn.clicked.connect(lambda _, c=cat: self.load_category(c))
            cat_layout.addWidget(btn)
        main_layout.addLayout(cat_layout)

        # Назад
        back_btn = QPushButton("Назад в меню")
        back_btn.clicked.connect(self.back_to_menu)
        main_layout.addWidget(back_btn)

        self.setLayout(main_layout)

    def perform_search(self):
        query = self.search_input.text()
        articles = self.ref_svc.search(query)
        self.article_list.clear()
        for art in articles:
            self.article_list.addItem(art.title)

    def load_category(self, category):
        articles = self.ref_svc.get_articles_by_category(category)
        self.article_list.clear()
        for art in articles:
            self.article_list.addItem(art.title)

    def display_article(self, item):
        title = item.text()
        article = self.ref_svc.db.query(ReferenceArticle).filter(
            ReferenceArticle.title == title
        ).first()
        if article:
            content = article.content
            if isinstance(content, str):
                content = json.loads(content)
            html = "<h2>" + article.title + "</h2>"
            if content.get('blocks'):
                for block in content['blocks']:
                    if block['type'] == 'text':
                        html += "<p>" + block['content'] + "</p>"
                    elif block['type'] == 'image':
                        html += f'<img src="{block["src"]}" width="400">'
                    # молекулы и т.д. можно отображать аналогично теории
            self.content_label.setText(html)

    def back_to_menu(self):
        from gui.windows.main_window import MainMenuWindow
        self.menu = MainMenuWindow(self.user, self.db)
        self.menu.show()
        self.close()