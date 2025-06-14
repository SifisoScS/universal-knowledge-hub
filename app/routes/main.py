from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Score, CommunityPost, Event, UserQuestion, SavedWisdom
from app import db
from app.utils.sifiso import SifisoAI
from datetime import datetime

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
    
    if request.method == 'POST':
        question = request.form.get('question')
        tags_list = request.form.getlist('tags[]') or request.form.getlist('tags')
        tags = ','.join(tags_list)
        print(f"Received question: {question}, tags: {tags}")  # Debug
        if question:
            response = sifiso.respond(question, tags)
            sifiso.save_question(question, tags)
            flash('You’ve just unlocked a Thought Thread!', 'success')
            return render_template('knowledge.html', response=response, categories=categories)
        flash('Please ask a question.', 'error')
    
    return render_template('knowledge.html', categories=categories)

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