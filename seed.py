from app import create_app, db
from app.models import User, CommunityPost, UserQuestion
from werkzeug.security import generate_password_hash
from datetime import datetime

def seed_data():
    db.drop_all()
    db.create_all()

    user1 = User(
        username='user1',
        email='user1@example.com',
        created_at=datetime.utcnow()
    )
    user1.set_password('password123')
    db.session.add(user1)
    db.session.commit()

    post1 = CommunityPost(
        user_id=user1.id,
        title='How can we heal with herbs?',
        content='Exploring traditional and modern uses of healing plants.',
        tags='Nature,Culture,Khoisan',
        created_at=datetime.utcnow()
    )
    db.session.add(post1)

    question1 = UserQuestion(
        user_id=user1.id,
        question='What are healing herbs?',
        tags='Nature,Culture,Khoisan',
        created_at=datetime.utcnow()
    )
    db.session.add(question1)
    db.session.commit()

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed_data()
        print("Database seeded successfully!")