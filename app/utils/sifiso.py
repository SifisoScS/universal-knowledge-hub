from app.models import UserQuestion, CommunityPost
from app import db
from datetime import datetime

class SifisoAI:
    def __init__(self, user_id):
        self.user_id = user_id

    def respond(self, question, tags):
        # Query CommunityPost for related wisdom
        related_posts = CommunityPost.query.filter(CommunityPost.tags.ilike(f'%{tags}%')).limit(3).all()
        community_context = "\n".join([f"- {post.title}: {post.content[:100]}..." for post in related_posts]) if related_posts else "No community insights yet. Start a thread!"

        # Structured response for knowledge.html
        return {
            "question": question,
            "greeting": f"Ayo greets you! Your question '{question}' sparks wisdom.",
            "answer": f"Exploring '{question}' with tags '{tags}', here's a thought: Knowledge shared grows like a baobab tree.",
            "community_context": community_context,
            "proverb": "Umuntu ngumuntu ngabantu: A person is a person through others.",
            "follow_up": "What else do you wonder about this topic?",
            "closer": "Together, we learn and rise!",
            "community_link": f"/community?topic={tags.split(',')[0]}" if tags else "/community",
            "tags": tags
        }

    def save_question(self, question, tags):
        user_question = UserQuestion(
            user_id=self.user_id,
            question=question,
            tags=tags,
            created_at=datetime.utcnow()
        )
        db.session.add(user_question)
        db.session.commit()