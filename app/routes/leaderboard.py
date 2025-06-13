from flask import Blueprint, render_template, request
from app.models import Score, User, Quiz

leaderboard_bp = Blueprint('leaderboard', '__name__')

@leaderboard_bp.route('/leaderboard')
def leaderboard():
    category = request.args.get('category', 'All')
    timeframe = request.args.get('timeframe', 'all')
    
    query = Score.query.join(User).join(Quiz)
    
    if category != 'All':
        query = query.filter_by(category=category)
    
    if timeframe == 'week':
        from datetime import datetime, timedelta
        query = query.filter(Score.timestamp >= datetime.now() - timedelta(days=7))
    
    scores = query.order_by(Score.score.desc()).limit(10).all()
    return render_template('leaderboard.html', scores=scores, category=category, timeframe=timeframe)