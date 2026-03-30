"""Script para crear el usuario admin inicial."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import hash_password
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.user_model import UserModel


def create_admin(email: str, password: str, username: str = "admin") -> None:
    db = SessionLocal()
    try:
        existing = db.query(UserModel).filter(UserModel.email == email).first()
        if existing:
            print(f"Ya existe un usuario con el email: {email}")
            return

        user = UserModel(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Usuario admin creado: id={user.id}, email={user.email}, username={user.username}")
    finally:
        db.close()


if __name__ == "__main__":
    EMAIL = "daniel@danielwar.tech"
    PASSWORD = "Sekiro0112398*-0"
    USERNAME = "daniel"

    create_admin(EMAIL, PASSWORD, USERNAME)
