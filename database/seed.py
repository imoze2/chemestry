# database/seed.py
import json
from database.db import SessionLocal
from database.models.content import Track, Lesson, LessonVersion, Theory, LessonTheory, Task, LessonTask
from database.models.user import User
from sqlalchemy.sql import func
import uuid

def seed_data():
    db = SessionLocal()

    # Проверим, есть ли уже треки
    if db.query(Track).count() > 0:
        print("Данные уже есть в БД, пропускаем заполнение.")
        return

    # 1. Создаём треки
    track8 = Track(name="Химия 8 класс", description="Базовый курс химии для 8 класса", is_published=True)
    track9 = Track(name="Химия 9 класс", description="Продвинутый курс для 9 класса", is_published=True)
    db.add_all([track8, track9])
    db.commit()

    # 2. Уроки для 8 класса
    lesson8_1 = Lesson(track_id=track8.id, order_index=1)
    lesson8_2 = Lesson(track_id=track8.id, order_index=2)
    db.add_all([lesson8_1, lesson8_2])
    db.commit()

    # 3. Версии уроков
    ver8_1 = LessonVersion(
        version_of=lesson8_1.id,
        title="Введение. Вещества и их свойства",
        estimated_time=30,
        xp_reward=50,
        version_number=1,
        is_active=True
    )
    ver8_2 = LessonVersion(
        version_of=lesson8_2.id,
        title="Атомы и молекулы",
        estimated_time=45,
        xp_reward=75,
        version_number=1,
        is_active=True
    )
    db.add_all([ver8_1, ver8_2])
    db.commit()

    # 4. Теория
    theory1 = Theory(
        data=json.dumps({
            "blocks": [
                {"type": "text", "content": "Химия — наука о веществах, их свойствах и превращениях."},
                {"type": "text", "content": "Вещества состоят из молекул, а молекулы — из атомов."},
                {"type": "image", "src": "assets/atoms.png", "caption": "Модель атома"}
            ]
        }),
        topic_tags=["введение", "вещества"],
        estimated_time=15
    )
    theory2 = Theory(
        data=json.dumps({
            "blocks": [
                {"type": "text", "content": "Атом — мельчайшая частица химического элемента."},
                {"type": "text", "content": "Молекула — наименьшая частица вещества, обладающая его химическими свойствами."}
            ]
        }),
        topic_tags=["атомы", "молекулы"],
        estimated_time=20
    )
    db.add_all([theory1, theory2])
    db.commit()

    # 5. Связь теории с уроками
    lt1 = LessonTheory(lesson_id=lesson8_1.id, theory_id=theory1.id, order_index=1, is_required=True)
    lt2 = LessonTheory(lesson_id=lesson8_2.id, theory_id=theory2.id, order_index=1, is_required=True)
    db.add_all([lt1, lt2])
    db.commit()

    # 6. Создадим простые задания (заглушки)
    task1 = Task(
        type="choice",
        source_type="static",
        question_text="Какая частица является наименьшей частицей вещества?",
        data=json.dumps({
            "options": ["Атом", "Молекула", "Электрон", "Ядро"],
            "correct": 1  # индекс правильного ответа
        }),
        correct_answers=json.dumps({"answer": 1}),
        scoring_type="binary",
        max_score=1,
        topic_tags=["атомы", "молекулы"]
    )
    task2 = Task(
        type="true_false",
        source_type="static",
        question_text="Вода состоит из молекул.",
        data=json.dumps({}),
        correct_answers=json.dumps({"answer": True}),
        scoring_type="binary",
        max_score=1,
        topic_tags=["вещества"]
    )
    db.add_all([task1, task2])
    db.commit()

    # 7. Привязка заданий к урокам
    lt1 = LessonTask(lesson_id=lesson8_1.id, task_id=task2.id, order_index=1, is_required=True)
    lt2 = LessonTask(lesson_id=lesson8_2.id, task_id=task1.id, order_index=1, is_required=True)
    db.add_all([lt1, lt2])
    db.commit()

    # 8. Для 9 класса тоже что-то добавим
    lesson9_1 = Lesson(track_id=track9.id, order_index=1)
    db.add(lesson9_1)
    db.commit()

    ver9_1 = LessonVersion(
        version_of=lesson9_1.id,
        title="Периодический закон",
        estimated_time=40,
        xp_reward=80,
        version_number=1,
        is_active=True
    )
    db.add(ver9_1)
    db.commit()

    theory3 = Theory(
        data=json.dumps({
            "blocks": [
                {"type": "text", "content": "Периодический закон Д.И. Менделеева..."}
            ]
        }),
        topic_tags=["периодический_закон"],
        estimated_time=25
    )
    db.add(theory3)
    db.commit()
    LessonTheory(lesson_id=lesson9_1.id, theory_id=theory3.id, order_index=1, is_required=True)
    db.commit()

    print("Тестовые данные успешно добавлены.")

if __name__ == "__main__":
    seed_data()