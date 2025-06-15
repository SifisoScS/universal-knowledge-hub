from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.models import Score, CommunityPost, Event, UserQuestion, SavedWisdom, UserResponse
from app import db
from app.utils.sifiso import SifisoAI
from datetime import datetime
import json

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    leaderboard_scores = Score.query.order_by(Score.score.desc()).limit(5).all()
    events = Event.query.filter(Event.event_date >= datetime.utcnow()).order_by(Event.event_date.asc()).limit(5).all()
    return render_template('index.html', leaderboard_scores=leaderboard_scores, events=events)

@main_bp.route('/start_quizzing', methods=['GET', 'POST'])
@login_required
def start_quizzing():
    sifiso = SifisoAI(user_id=current_user.id)
    categories = ['Science', 'Nature', 'Life', 'Society', 'Culture', 'Art', 'Technology', 'Random', 'Khoisan', 'Zulu']
    history = []

    # Fetch chat history for authenticated user
    if current_user.is_authenticated:
        questions = UserQuestion.query.filter_by(user_id=current_user.id).order_by(UserQuestion.created_at.asc()).all()
        for q in questions:
            responses = UserResponse.query.filter_by(question_id=q.id).all()
            history.extend([{
                'question': q.question,
                'response': json.loads(r.response),
                'tags': q.tags or '',
                'created_at': q.created_at
            } for r in responses])

    if request.method == 'POST':
        question = request.form.get('question')
        print(f"Received question: {question}")  # Debug

        if not question:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Please ask a question.'}), 400
            flash('Please ask a question.', 'error')
            return render_template('knowledge.html', categories=categories, history=history)

        # Generate and save response
        response = sifiso.respond(question, '')  # No tags
        sifiso.save_question(question, '')  # No tags

        # Save to database
        user_question = UserQuestion(
            user_id=current_user.id,
            question=question,
            tags='',
            created_at=datetime.utcnow()
        )
        db.session.add(user_question)
        db.session.flush()  # Get ID
        user_response = UserResponse(
            question_id=user_question.id,
            response=json.dumps(response),
            created_at=datetime.utcnow()
        )
        db.session.add(user_response)
        db.session.commit()

        # Return JSON for AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'question': question,
                'response': response,
                'tags': '',
                'created_at': datetime.utcnow().strftime('%H:%M, %b %d, %Y')
            })

        # Fallback for non-AJAX (rare)
        history.append({
            'question': question,
            'response': response,
            'tags': '',
            'created_at': datetime.utcnow()
        })
        flash('You’ve just unlocked a Thought Thread!', 'success')
        return render_template('knowledge.html', categories=categories, history=history)

    return render_template('knowledge.html', categories=categories, history=history)

@main_bp.route('/save_wisdom', methods=['POST'])
@login_required
def save_wisdom():
    question = request.form.get('question')
    response = request.form.get('response')
    tags = request.form.get('tags')
    if question and response:
        wisdom = SavedWisdom(
            user_id=current_user.id,
            question=question,
            response=response,
            tags=tags,
            created_at=datetime.utcnow()
        )
        db.session.add(wisdom)
        db.session.commit()
        flash('Wisdom saved to your profile!', 'success')
    else:
        flash('Failed to save wisdom.', 'error')
    return redirect(url_for('main.start_quizzing'))

@main_bp.route('/community', methods=['GET', 'POST'])
@login_required
def community():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        tags = ','.join(request.form.getlist('tags'))
        if title and content:
            post = CommunityPost(
                user_id=current_user.id,
                title=title,
                content=content,
                tags=tags,
                created_at=datetime.utcnow(),
                is_active=True
            )
            db.session.add(post)
            db.session.commit()
            flash('Post created!', 'success')
            return redirect(url_for('main.community'))
        flash('Title and content are required.', 'error')

    topic = request.args.get('topic')
    query = CommunityPost.query.filter_by(is_active=True)
    if topic:
        query = query.filter(CommunityPost.tags.ilike(f'%{topic}%'))
    posts = query.order_by(CommunityPost.created_at.desc()).limit(10).all()
    return render_template('community.html', posts=posts)

@main_bp.route('/community_posts/<int:post_id>')
def post_detail(post_id):
    post = CommunityPost.query.get_or_404(post_id)
    return render_template('community_posts.html', post=post)

@main_bp.route('/events')
def events():
    events = Event.query.order_by(Event.event_date.asc()).limit(10).all()
    return render_template('events.html', events=events)