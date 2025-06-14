from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models import db, Quiz, Question, Score

knowledge_bp = Blueprint('knowledge', __name__)

@knowledge_bp.route('/knowledge')
@login_required
def knowledge():
    quizzes = Quiz.query.all()
    return render_template('knowledge.html', quizzes=quizzes)

@knowledge_bp.route('/knowledge/<int:quiz_id>')
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions
    return render_template('knowledge_questions.html', quiz=quiz, questions=questions)

@knowledge_bp.route('/knowledge/submit', methods=['POST'])
@login_required
def submit():
    quiz_id = int(request.form.get('quiz_id'))
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions
    score = 0
    correct_answers = 0
    
    for question in questions:
        user_answer = request.form.get(f'question_{question.id}')
        if user_answer and int(user_answer) == question.correct_option:
            score += 1
            correct_answers += 1
    
    score_record = Score(
        user_id=current_user.id,
        quiz_id=quiz_id,
        score=score,
        correct_answers=correct_answers,
        total_questions=len(questions),
        time_taken=request.form.get('time_taken', 0, type=int)
    )
    db.session.add(score_record)
    db.session.commit()
    
    return jsonify({'score': score, 'total': len(questions)})