from app.models import UserQuestion, CommunityPost
from app import db
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SifisoAI:
    def __init__(self, user_id):
        self.user_id = user_id
        self.serper_api_key = os.getenv('SERPER_API_KEY')

    def _normalize_title(self, title):
        """Simplify title to catch near-duplicates (e.g., removing site suffixes)."""
        return title.lower().split(" - ")[0].strip()

    def _fetch_serper_results(self, query):
        """Fetch web results from Serper API."""
        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": self.serper_api_key,
            "Content-Type": "application/json"
        }
        payload = {"q": query, "num": 5, "gl": "za"}
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            results = response.json().get("organic", [])

            seen_titles = set()
            filtered_results = []

            for r in results:
                raw_title = r['title']
                title = self._normalize_title(raw_title)
                if title not in seen_titles and "wikipedia" not in raw_title.lower():
                    seen_titles.add(title)
                    snippet = r['snippet'][:300].strip()
                    link = r.get('link', '#')
                    filtered_results.append(f"• **{raw_title}** ([Source]({link}))\n  _{snippet}_")
            
            print(f"Serper success: {len(filtered_results)} results for '{query}'")
            return filtered_results[:3] or ["• _No high-quality web insights available._"]

        except requests.RequestException as e:
            print(f"Serper API error: {e}, Status Code: {response.status_code if 'response' in locals() else 'N/A'}, Response: {response.text if 'response' in locals() else 'N/A'}")
            return ["• _No web insights available due to API error._"]

    def respond(self, question, tags):
        # Community insights
        related_posts = CommunityPost.query.filter(CommunityPost.tags.ilike(f'%{tags}%')).limit(3).all()
        if related_posts:
            community_context = "\n".join(
                [f"• **{post.title}**\n  _{post.content[:100]}..._" for post in related_posts]
            )
        else:
            community_context = "• _No community insights yet. Start a thread!_"

        # Web insights
        web_results = self._fetch_serper_results(question)
        web_context = "\n".join(web_results)

        # Fallback for Khoisan healing methods
        if "khoisan healing" in question.lower() and "No web insights" in web_context:
            web_context = (
                "• **Herbal Remedies**\n  _Khoisan use plants like buchu and aloe ferox for skin ailments and digestion._\n"
                "• **Trance Dance**\n  _Healing rituals involve trance dances to connect with ancestors for spiritual healing._\n"
                "• **Massage and Cuts**\n  _Medicinal cuts and massage channel 'potency' to treat illness._"
            )

        # Structured response
        return {
            "question": question,
            "greeting": f"🧠 Ayo greets you! Your question '**{question}**' sparks wisdom.",
            "answer": f"### 🌐 Web Insights\n{web_context}",
            "community_context": f"### 🗣️ Community Wisdom\n{community_context}",
            "proverb": "🪶 *Umuntu ngumuntu ngabantu:* A person is a person through others.",
            "follow_up": "✨ What else do you wonder about this topic?",
            "closer": "🚀 Together, we learn and rise!",
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