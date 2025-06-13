from flask import Blueprint, request, jsonify

sifiso_bp = Blueprint('sifiso', __name__, url_prefix='/api')

@sifiso_bp.route('/sifiso', methods=['POST'])
def sifiso():
    data = request.get_json()
    message = data.get('message', '').lower()
    
    if 'quiz' in message or 'knowledge' in message:
        reply = 'Ready to test your knowledge? Head to the Knowledge Challenges tab!'
    elif 'community' in message:
        reply = 'Join our vibrant community hub to share ideas and collaborate!'
    elif 'event' in message:
        reply = 'Check out upcoming events to connect with others!'
    else:
        reply = "I'm Sifiso, your assistant. Ask about knowledge challenges, community, events, or more!"
    
    return jsonify({'reply': reply})