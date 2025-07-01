"""
Script to insert sample data into Users and Todos tables using SQLAlchemy ORM.
Inserts 5 users and 5 todos (one for each user).
"""

from sqlalchemy.orm import Session
from database import SessionLocal
from models import Users, Todos


def insert_sample_data():
    db: Session = SessionLocal()
    try:
        users = []
        # Insert 5 users
        for i in range(1, 6):
            user = Users(
                email=f"user{i}@example.com",
                username=f"user{i}",
                first_name=f"First{i}",
                last_name=f"Last{i}",
                hashed_password=f"hashedpassword{i}",
                is_active=True,
                role="admin" if i == 1 else "user",
                phone_number=f"123456789{i}",
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            users.append(user)

        # Insert 5 todos, one for each user
        for i, user in enumerate(users, start=1):
            todo = Todos(
                title=f"Task {i}",
                description=f"This is todo task {i}.",
                priority=i,
                complete=False,
                owner_id=user.id,
            )
            db.add(todo)
            db.commit()
            db.refresh(todo)
            print(f"Inserted user: {user.username}, todo: {todo.title}")
    finally:
        db.close()


if __name__ == "__main__":
    insert_sample_data()
