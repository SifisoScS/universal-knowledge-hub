from flask import Blueprint, render_template
from flask_login import current_user
from app.models import Score, CommunityPost, Event
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    leaderboard_scores = Score.query.order_by(Score.score.desc()).limit(5).all()
    events = Event.query.filter(Event.event_date >= datetime.utcnow()).order_by(Event.event_date.asc()).limit(5).all()
    return render_template('index.html', leaderboard_scores=leaderboard_scores, events=events)

@main_bp.route('/community')
def community():
    posts = CommunityPost.query.filter_by(is_active=True).order_by(CommunityPost.created_at.desc()).limit(10).all()
    return render_template('community.html', posts=posts)

@main_bp.route('/events')
def events():
    events = Event.query.order_by(Event.event_date.asc()).limit(10).all()
    return render_template('events.html', events=events)