from groq import Groq
from django.conf import settings
from .rag_service import rag_service
import json
import re
import logging

logger = logging.getLogger(__name__)


class GroqAIService:
    """
    Enhanced AI Service with RAG integration
    
    Uses ChromaDB to retrieve relevant reviews, then uses Groq for generation
    """
    
    def __init__(self):
        if not settings.GROQ_API_KEY:
            logger.warning("GROQ_API_KEY not configured - AI features will be limited")
            self.client = None
        else:
            self.client = Groq(api_key=settings.GROQ_API_KEY)
        
        self.model = settings.GROQ_MODEL
    
    def _safe_api_call(self, messages, temperature=0.3, max_tokens=500):
        """Safe API call with error handling"""
        if not self.client:
            raise ValueError("Groq API client not initialized")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            raise
    
    def _extract_json(self, text):
        """Extract JSON from potentially markdown-wrapped response"""
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return json.loads(text)
    
    def generate_place_summary(self, place_id, place_name):
        """
        Generate RAG-enhanced summary for a place
        
        Uses vector search to find diverse reviews, then AI to summarize
        """
        try:
            # Get diverse review context using RAG
            review_context = rag_service.get_place_review_context(
                place_id=place_id,
                top_k=15  # Use 15 most representative reviews
            )
            
            if not review_context:
                return {
                    'summary': f'No reviews available for {place_name} yet. Be the first to share your experience!',
                    'sentiment_score': 0,
                    'sentiment_label': 'neutral',
                    'positive_percentage': 0,
                    'negative_percentage': 0,
                    'neutral_percentage': 0,
                    'top_keywords': [],
                    'highlights': [],
                    'concerns': []
                }
            
            prompt = f"""Analyze these reviews for "{place_name}" and provide comprehensive insights:

{review_context}

Provide your response in this exact JSON format:
{{
    "summary": "2-3 sentences highlighting the overall consensus",
    "sentiment_score": 0.0,
    "sentiment_label": "positive/negative/neutral",
    "positive_percentage": 0.0,
    "negative_percentage": 0.0,
    "neutral_percentage": 0.0,
    "top_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
    "highlights": ["Best aspect 1", "Best aspect 2", "Best aspect 3"],
    "concerns": ["Common concern 1", "Common concern 2"]
}}

Rules:
- sentiment_score: -1 (very negative) to 1 (very positive)
- Percentages must sum to 100
- Keywords: single words or 2-word phrases
- Highlights: 3 most praised aspects
- Concerns: Up to 2 common complaints (empty list if none)"""
            
            result_text = self._safe_api_call([
                {
                    "role": "system",
                    "content": "You analyze customer reviews with RAG context. Provide structured, accurate insights based ONLY on the provided reviews. Respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ], temperature=0.2, max_tokens=600)
            
            result = self._extract_json(result_text)
            
            # Validate and normalize
            result['sentiment_score'] = max(-1, min(1, float(result.get('sentiment_score', 0))))
            result['positive_percentage'] = max(0, min(100, float(result.get('positive_percentage', 0))))
            result['negative_percentage'] = max(0, min(100, float(result.get('negative_percentage', 0))))
            result['neutral_percentage'] = max(0, min(100, float(result.get('neutral_percentage', 0))))
            
            # Ensure highlights and concerns exist
            result['highlights'] = result.get('highlights', [])[:3]
            result['concerns'] = result.get('concerns', [])[:2]
            
            return result
            
        except Exception as e:
            logger.error(f"AI Summary Error: {str(e)}")
            return {
                'summary': 'Unable to generate summary at this time.',
                'sentiment_score': 0,
                'sentiment_label': 'neutral',
                'positive_percentage': 0,
                'negative_percentage': 0,
                'neutral_percentage': 0,
                'top_keywords': [],
                'highlights': [],
                'concerns': []
            }
    
    def analyze_review_sentiment(self, review_text, rating):
        """
        Analyze individual review with RAG context
        
        Finds similar reviews to understand context better
        """
        try:
            # Find similar reviews for context
            similar_reviews = rag_service.search_similar_reviews(
                query=review_text,
                top_k=3
            )
            
            context = ""
            if similar_reviews:
                context = "\nSimilar reviews for context:\n" + "\n".join([
                    f"- {r['text'][:100]}..." for r in similar_reviews[:2]
                ])
            
            prompt = f"""Analyze this review (Rating: {rating}/5):

"{review_text}"
{context}

Provide analysis in JSON format:
{{
    "sentiment": "positive/negative/neutral",
    "sentiment_score": 0.0,
    "quality_score": 0.0,
    "is_spam": false,
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "helpful_reason": "Why this review is helpful (or not)"
}}

- sentiment_score: -1 to 1
- quality_score: 0 to 1 (helpfulness based on detail, specificity)
- is_spam: true if generic, fake, or unhelpful
- keywords: 3 main topics
- helpful_reason: One sentence explanation"""
            
            result_text = self._safe_api_call([
                {
                    "role": "system",
                    "content": "You analyze review quality and sentiment with RAG context. Respond with JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ], temperature=0.2, max_tokens=250)
            
            return self._extract_json(result_text)
            
        except Exception as e:
            logger.error(f"Review Analysis Error: {str(e)}")
            return {
                'sentiment': 'neutral',
                'sentiment_score': 0,
                'quality_score': 0.5,
                'is_spam': False,
                'keywords': [],
                'helpful_reason': 'Standard review'
            }
    
    def generate_search_suggestions(self, query, user_id=None):
        """
        RAG-enhanced search suggestions
        
        Uses vector search to find related places/reviews
        """
        try:
            # Search for reviews matching query
            similar_reviews = rag_service.search_similar_reviews(
                query=query,
                top_k=5
            )
            
            context = ""
            if similar_reviews:
                places = set([r['metadata'].get('place_id') for r in similar_reviews])
                context = f"\nFound {len(places)} relevant places in database"
            
            prompt = f"""User is searching for: "{query}"
{context}

Suggest 5 relevant, specific search queries. Consider:
- Similar places
- Related categories
- Location-based searches
- Rating-based filters

Return as JSON:
{{
    "suggestions": ["specific query 1", "specific query 2", ...]
}}"""
            
            result_text = self._safe_api_call([
                {"role": "system", "content": "Suggest relevant place searches with RAG context. JSON only."},
                {"role": "user", "content": prompt}
            ], temperature=0.6, max_tokens=150)
            
            return self._extract_json(result_text).get('suggestions', [])
            
        except Exception as e:
            logger.error(f"Suggestions Error: {str(e)}")
            return []
    
    def generate_recommendations(self, user_review_history, preferences=None):
        """
        RAG-enhanced personalized recommendations
        
        Uses user's review history to find similar patterns
        """
        try:
            if not user_review_history:
                return []
            
            # Create user preference profile from their reviews
            user_profile = " ".join([
                f"{r['place_name']} (rated {r['rating']}/5)"
                for r in user_review_history[:10]
            ])
            
            # Find places similar to user's liked places
            similar_places = []
            for review in user_review_history:
                if review['rating'] >= 4:  # Only consider liked places
                    similar = rag_service.search_similar_reviews(
                        query=review['text'],
                        top_k=3
                    )
                    similar_places.extend(similar)
            
            context = f"User has reviewed: {user_profile}"
            if similar_places:
                context += f"\nFound {len(similar_places)} similar highly-rated places"
            
            prompt = f"""{context}

Recommend 5 specific types of places this user would enjoy. Be specific!

Return as JSON:
{{
    "recommendations": [
        {{"type": "Specific place type", "reason": "Why based on their history"}},
        ...
    ]
}}"""
            
            result_text = self._safe_api_call([
                {"role": "system", "content": "Recommend places with RAG user context. JSON only."},
                {"role": "user", "content": prompt}
            ], temperature=0.7, max_tokens=400)
            
            return self._extract_json(result_text).get('recommendations', [])
            
        except Exception as e:
            logger.error(f"Recommendations Error: {str(e)}")
            return []
    
    def answer_question_about_place(self, place_id, place_name, question):
        """
        RAG-powered Q&A about a place
        
        Retrieves relevant reviews and answers specific questions
        """
        try:
            # Search for reviews relevant to the question
            relevant_reviews = rag_service.search_similar_reviews(
                query=question,
                place_id=place_id,
                top_k=8
            )
            
            if not relevant_reviews:
                return {
                    "answer": f"I don't have enough review information to answer that about {place_name}.",
                    "confidence": "low",
                    "sources": []
                }
            
            review_context = "\n\n".join([
                f"Review (Rating: {r['metadata']['rating']}/5): {r['text']}"
                for r in relevant_reviews
            ])
            
            prompt = f"""Question about "{place_name}": {question}

Relevant reviews:
{review_context}

Answer the question based ONLY on the reviews provided. Return JSON:
{{
    "answer": "Direct answer to the question",
    "confidence": "high/medium/low",
    "sources": ["Quote from review 1", "Quote from review 2"]
}}

If reviews don't contain relevant information, say so."""
            
            result_text = self._safe_api_call([
                {
                    "role": "system",
                    "content": "Answer questions about places using only the provided review context. Be factual and cite sources. JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ], temperature=0.1, max_tokens=300)
            
            return self._extract_json(result_text)
            
        except Exception as e:
            logger.error(f"Q&A Error: {str(e)}")
            return {
                "answer": "I'm unable to answer that question right now.",
                "confidence": "low",
                "sources": []
            }


# Initialize service
ai_service = GroqAIService()