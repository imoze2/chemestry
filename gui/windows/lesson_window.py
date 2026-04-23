# gui/windows/lesson_window.py
import json
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QTabWidget, QScrollArea, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from sqlalchemy import func
from database.db import SessionLocal
from services.lesson_service import LessonService
from services.progress_service import ProgressService
from database.models.content import LessonVersion


class LessonWindow(QWidget):
    def __init__(self, user, track, lesson, db_session):
        super().__init__()
        self.user = user
        self.track = track
        self.lesson = lesson
        self.db = db_session
        self.lesson_service = LessonService(self.db)
        self.progress_service = ProgressService(self.db)

        # Получаем данные урока
        self.content = self.lesson_service.get_lesson_with_content(lesson.id, user.id)
        self.active_version = self.content['active_version']

        self.setWindowTitle(f"Урок: {self.active_version.title}")
        self.setFixedSize(800, 600)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Заголовок с информацией
        header = QHBoxLayout()
        title_label = QLabel(self.active_version.title)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        xp_label = QLabel(f"Награда: {self.active_version.xp_reward} XP")
        xp_label.setStyleSheet("color: #aaa;")
        header.addWidget(title_label)
        header.addStretch()
        header.addWidget(xp_label)
        main_layout.addLayout(header)

        # Вкладки
        self.tabs = QTabWidget()
        self.theory_tab = self.create_theory_tab()
        self.tabs.addTab(self.theory_tab, "Теория")
        # Практика пока заглушка
        practice_tab = QLabel("Задания будут доступны после изучения теории")
        practice_tab.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tabs.addTab(practice_tab, "Практика")
        main_layout.addWidget(self.tabs)

        # Нижняя панель с кнопками
        bottom_layout = QHBoxLayout()
        self.back_btn = QPushButton("Назад к урокам")
        self.back_btn.clicked.connect(self.back_to_lessons)
        self.complete_theory_btn = QPushButton("Завершить теорию")
        self.complete_theory_btn.clicked.connect(self.complete_theory)
        bottom_layout.addWidget(self.back_btn)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.complete_theory_btn)
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

    def create_theory_tab(self):
        """Создаёт вкладку с теорией на основе JSONB."""
        widget = QWidget()
        layout = QVBoxLayout()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        content_layout = QVBoxLayout()

        # Проходим по всем элементам теории
        for lesson_theory, theory in self.content['theory']:
            data = theory.data
            if isinstance(data, str):
                data = json.loads(data)
            blocks = data.get('blocks', [])
            for block in blocks:
                if block['type'] == 'text':
                    label = QLabel(block['content'])
                    label.setWordWrap(True)
                    label.setStyleSheet("font-size: 14px; margin: 5px;")
                    content_layout.addWidget(label)
                elif block['type'] == 'image':
                    # Изображение (путь к файлу)
                    pixmap = QPixmap(block['src'])
                    if not pixmap.isNull():
                        img_label = QLabel()
                        img_label.setPixmap(pixmap.scaledToWidth(600, Qt.TransformationMode.SmoothTransformation))
                        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        content_layout.addWidget(img_label)
                        if 'caption' in block:
                            caption = QLabel(block['caption'])
                            caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
                            caption.setStyleSheet("color: #aaa; font-style: italic;")
                            content_layout.addWidget(caption)
                    else:
                        error_label = QLabel(f"Изображение не найдено: {block['src']}")
                        error_label.setStyleSheet("color: red;")
                        content_layout.addWidget(error_label)
                # Здесь можно добавить другие типы блоков (анимации и т.д.)

        content_layout.addStretch()
        content_widget.setLayout(content_layout)
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        widget.setLayout(layout)
        return widget

    def complete_theory(self):
        # Отмечаем теорию как просмотренную
        track_progress = self.progress_service.get_or_create_track_progress(self.user.id, self.track.id)
        lesson_progress = self.progress_service.get_or_create_lesson_progress(
            track_progress.id, self.lesson.id
        )
        lesson_progress.theory_viewed = True
        lesson_progress.theory_viewed_at = func.now()
        self.db.commit()
        QMessageBox.information(self, "Теория", "Теория отмечена как изученная. Теперь можно перейти к заданиям.")
        # Активируем вкладку "Практика" (пока заглушка)
        self.tabs.setCurrentIndex(1)

    def back_to_lessons(self):
        from gui.windows.lesson_list_window import LessonListWindow
        self.lesson_list = LessonListWindow(self.user, self.track, self.db)
        self.lesson_list.show()
        self.close()