# database/seed.py
import json
from database.db import SessionLocal
from database.models.content import Track, Lesson, LessonVersion, Theory, LessonTheory, Task, LessonTask, TaskGenerator, TaskVariant
from database.models.user import User
from sqlalchemy.sql import func
import uuid
import random

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
    lesson8_1 = Lesson(track_id=track8.id, order_index=0)
    lesson8_2 = Lesson(track_id=track8.id, order_index=1)
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

    # ---------- Создаём несколько генераторов для разных типов ----------
    # Генератор для choice
    gen_choice = TaskGenerator(
        type='choice',
        template_data={
            "questions": [
                {"text": "Какая частица является наименьшей частицей вещества?", 
                 "options": ["Атом", "Молекула", "Электрон", "Ядро"], "correct_index": 1},
                {"text": "Что такое валентность?", 
                 "options": ["Число связей", "Масса атома", "Заряд ядра", "Число протонов"], "correct_index": 0},
            ]
        },
        difficulty=2,
        topic_tags=["вещество", "атомы"]
    )
    db.add(gen_choice)

    # Генератор для balance_equation
    gen_balance = TaskGenerator(
        type='balance_equation',
        template_data={
            "equations": [
                {"reactants": ["H2", "O2"], "products": ["H2O"], "coefficients": [2, 1, 2]},
                {"reactants": ["Na", "Cl2"], "products": ["NaCl"], "coefficients": [2, 1, 2]},
            ]
        },
        difficulty=3,
        topic_tags=["уравнения"]
    )
    db.add(gen_balance)

    # Генератор для calculation
    gen_calc = TaskGenerator(
        type='calculation',
        template_data={
            "formulas": [
                {
                    "params": {"mass": [10, 100], "molar_mass": [18, 100]},
                    "question_template": "Вычислите количество вещества (моль), если масса вещества {mass} г, молярная масса {molar_mass} г/моль.",
                    "expression": "mass / molar_mass",
                    "tolerance": 0.01
                }
            ]
        },
        difficulty=4,
        topic_tags=["расчеты"]
    )
    db.add(gen_calc)

    db.commit()

    # ---------- Создаём задания, привязанные к генераторам или со статическими вариантами ----------
    tasks_data = [
        # type, generator, static_variants (если не генератор)
        {'type': 'choice', 'generator': gen_choice, 'max_score': 1, 'topic_tags': ['атомы']},
        {'type': 'true_false', 'static_variants': [
            {"variant_data": {"question_text": "Вода состоит из молекул H2O."}, "correct_answer": {"answer": True}},
            {"variant_data": {"question_text": "Кислород — это металл."}, "correct_answer": {"answer": False}},
        ], 'max_score': 1},
        {'type': 'match', 'static_variants': [
            {"variant_data": {"left_items": ["H2O", "CO2", "NaCl"], 
                              "right_items": ["вода", "углекислый газ", "поваренная соль"]},
             "correct_answer": {"matches": {"0": 0, "1": 1, "2": 2}}},
        ]},
        {'type': 'fill_blank', 'static_variants': [
            {"variant_data": {"text": "Химическая формула воды — ______."}, "correct_answer": {"answer": "H2O"}},
        ]},
        {'type': 'balance_equation', 'generator': gen_balance},
        {'type': 'predict_product', 'static_variants': [
            {"variant_data": {"reactants": ["NaOH", "HCl"]}, "correct_answer": {"products": ["NaCl", "H2O"]}},
        ]},
        {'type': 'classify', 'static_variants': [
            {"variant_data": {"item_name": "NaCl", "options": ["оксид", "кислота", "соль", "основание"]},
             "correct_answer": {"class": "соль"}},
        ]},
        {'type': 'calculation', 'generator': gen_calc, 'max_score': 1, 'scoring_type': 'binary'},
        {'type': 'chain_transform', 'static_variants': [
            {"variant_data": {"starting_material": "CuO", "steps": [
                {"reagent": "H2SO4", "product": "CuSO4"},
                {"reagent": "Fe", "product": "Cu"}
            ]},
            "correct_answer": {"products": [["CuSO4"], ["Cu"]]}},
        ]},
        {'type': 'virtual_lab', 'static_variants': [
            {"variant_data": {"name": "Реакция нейтрализации", "reagents": ["NaOH", "HCl"], 
                              "procedure": "Смешайте растворы.", "observations": ["Выделение газа", "Изменение цвета", "Ничего"]},
             "correct_answer": {"observation": "Ничего"}},
        ]},
        {'type': 'puzzle', 'static_variants': [
            {"variant_data": {"clues": ["Самый лёгкий газ."]}, "correct_answer": {"answer": "водород"}},
        ]},
        {'type': 'timed', 'static_variants': [
            {"variant_data": {"text": "Сколько протонов в атоме углерода?", "time_limit": 10},
             "correct_answer": {"answer": "6"}},
        ]},
    ]

    for td in tasks_data:
        task = Task(
            type=td['type'],
            source_type='generated' if 'generator' in td else 'static',
            generator_id=td.get('generator', None).id if 'generator' in td else None,
            question_text=f"Задание типа {td['type']}",
            data={},
            correct_answers={},
            scoring_type='binary' if not td['type'] == 'match' else 'partial',
            max_score=td.get('max_score', 1),
            topic_tags=td.get('topic_tags', []),
        )
        db.add(task)
        db.flush()  # чтобы получить task.id

        if 'static_variants' in td:
            for var in td['static_variants']:
                variant = TaskVariant(
                    base_task_id=task.id,
                    variant_data=var['variant_data'],
                    correct_answer=var['correct_answer'],
                )
                db.add(variant)

    db.commit()

    # Привязываем задания к урокам (например, к первому уроку 8 класса)
    lesson = db.query(Lesson).filter(Lesson.order_index == 0).first()
    tasks = db.query(Task).all()
    for i, t in enumerate(tasks):
        lt = LessonTask(lesson_id=lesson.id, task_id=t.id, order_index=i, is_required=True)
        db.add(lt)
    db.commit()

    # 8. Для 9 класса тоже что-то добавим
    lesson9_1 = Lesson(track_id=track9.id, order_index=0)
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