from app import create_app, db
from app.models import User, QuizCategory, Quiz, Question, QuestionOption, Badge

app = create_app()
with app.app_context():
    # Create admin user
    admin = User(username='admin', email='admin@imbizo.com', password='hashed_password', is_admin=True)
    db.session.add(admin)

    # Create category
    category = QuizCategory(name='General Knowledge', description='Test your trivia!', icon='fa-brain')
    db.session.add(category)
    db.session.commit()

    # Create quiz
    quiz = Quiz(title='Trivia Challenge', category_id=category.id, created_by=admin.id)
    db.session.add(quiz)
    db.session.commit()

    # Create question
    question = Question(quiz_id=quiz.id, text='What is the capital of France?', difficulty=1, created_by=admin.id)
    db.session.add(question)
    db.session.commit()

    # Create options
    options = [
        QuestionOption(question_id=question.id, text='Paris', is_correct=True, order_index=1),
        QuestionOption(question_id=question.id, text='London', is_correct=False, order_index=2),
        QuestionOption(question_id=question.id, text='Berlin', is_correct=False, order_index=3),
        QuestionOption(question_id=question.id, text='Madrid', is_correct=False, order_index=4)
    ]
    db.session.add_all(options)

    # Create badge
    badge = Badge(name='Trivia Master', description='Score 100% on a quiz', points=100, category_id=category.id)
    db.session.add(badge)
    db.session.commit()