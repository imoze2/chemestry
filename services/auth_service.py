import bcrypt
from database.db import SessionLocal
from database.models.user import User


class AuthService:

    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        return hashed.decode()

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed_password.encode())

    @staticmethod
    def register(username: str, email: str, password: str):

        db = SessionLocal()

        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            return False, "Такой пользователь уже зарегистрирован"

        hashed_password = AuthService.hash_password(password)

        user = User(
            username=username,
            email=email,
            password_hash=hashed_password
        )

        db.add(user)
        db.commit()

        return True, "Успешная регистрация"

    @staticmethod
    def login(username: str, password: str):

        db = SessionLocal()

        user = db.query(User).filter(User.username == username).first()

        if not user:
            return False, "Пользователя с таким именем не существует"

        if not AuthService.verify_password(password, user.password_hash):
            return False, "Неверный пароль"

        return True, user