from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count

from apps.places.models import Place, Review
from .models import PlaceAISummary, ReviewAIAnalysis, UserSearchHistory
from .serializers import (
    PlaceAISummarySerializer,
    ReviewAIAnalysisSerializer,
    SearchSuggestionSerializer,
    RecommendationSerializer,
    PlaceQuestionSerializer,
    QuestionAnswerSerializer,
    RegenerateSummarySerializer
)
from .services import ai_service
from .rag_service import rag_service
import logging

logger = logging.getLogger(__name__)


class PlaceAISummaryView(generics.RetrieveAPIView):
    """
    GET /api/ai/places/{place_id}/summary/
    
    Get AI-generated summary for a place
    Auto-generates if doesn't exist or is outdated
    """
    
    serializer_class = PlaceAISummarySerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        place_id = self.kwargs.get('place_id')
        place = get_object_or_404(Place, id=place_id)
        
        # Check if summary exists and is current
        try:
            summary = place.ai_summary
            if summary.needs_update():
                # Regenerate if outdated
                summary = self._regenerate_summary(place)
        except PlaceAISummary.DoesNotExist:
            # Generate new summary
            summary = self._regenerate_summary(place)
        
        return summary
    
    def _regenerate_summary(self, place):
        """Generate or regenerate AI summary"""
        try:
            # Generate summary using RAG
            ai_result = ai_service.generate_place_summary(
                place_id=place.id,
                place_name=place.name
            )
            
            # Update or create summary
            summary, created = PlaceAISummary.objects.update_or_create(
                place=place,
                defaults={
                    'summary': ai_result['summary'],
                    'sentiment_score': ai_result['sentiment_score'],
                    'sentiment_label': ai_result['sentiment_label'],
                    'positive_percentage': ai_result['positive_percentage'],
                    'negative_percentage': ai_result['negative_percentage'],
                    'neutral_percentage': ai_result['neutral_percentage'],
                    'top_keywords': ai_result['top_keywords'],
                    'highlights': ai_result.get('highlights', []),
                    'concerns': ai_result.get('concerns', []),
                    'review_count_at_generation': place.reviews.count()
                }
            )
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary for place {place.id}: {str(e)}")
            # Return basic summary on error
            summary, _ = PlaceAISummary.objects.get_or_create(
                place=place,
                defaults={
                    'summary': 'Summary generation in progress.',
                    'sentiment_score': 0,
                    'sentiment_label': 'neutral',
                    'positive_percentage': 0,
                    'negative_percentage': 0,
                    'neutral_percentage': 0,
                    'top_keywords': [],
                    'highlights': [],
                    'concerns': [],
                    'review_count_at_generation': 0
                }
            )
            return summary


class RegenerateSummaryView(APIView):
    """
    POST /api/ai/places/{place_id}/regenerate-summary/
    
    Force regeneration of place summary
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, place_id):
        serializer = RegenerateSummarySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        place = get_object_or_404(Place, id=place_id)
        
        try:
            # Generate summary
            ai_result = ai_service.generate_place_summary(
                place_id=place.id,
                place_name=place.name
            )
            
            # Update or create
            summary, created = PlaceAISummary.objects.update_or_create(
                place=place,
                defaults={
                    'summary': ai_result['summary'],
                    'sentiment_score': ai_result['sentiment_score'],
                    'sentiment_label': ai_result['sentiment_label'],
                    'positive_percentage': ai_result['positive_percentage'],
                    'negative_percentage': ai_result['negative_percentage'],
                    'neutral_percentage': ai_result['neutral_percentage'],
                    'top_keywords': ai_result['top_keywords'],
                    'highlights': ai_result.get('highlights', []),
                    'concerns': ai_result.get('concerns', []),
                    'review_count_at_generation': place.reviews.count()
                }
            )
            
            return Response({
                'message': 'Summary regenerated successfully',
                'summary': PlaceAISummarySerializer(summary).data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error regenerating summary: {str(e)}")
            return Response({
                'error': 'Failed to regenerate summary',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SearchSuggestionsView(APIView):
    """
    GET /api/ai/search-suggestions/?query=pizza
    
    Get AI-powered search suggestions using RAG
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('query', '').strip()
        
        if not query:
            return Response({
                'suggestions': []
            }, status=status.HTTP_200_OK)
        
        try:
            # Generate suggestions using RAG
            suggestions = ai_service.generate_search_suggestions(
                query=query,
                user_id=request.user.id
            )
            
            serializer = SearchSuggestionSerializer({
                'suggestions': suggestions
            })
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {str(e)}")
            return Response({
                'suggestions': []
            }, status=status.HTTP_200_OK)


class PersonalizedRecommendationsView(APIView):
    """
    GET /api/ai/recommendations/
    
    Get personalized place recommendations based on user history
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get user's review history
        user_reviews = Review.objects.filter(user=user).select_related('place')[:20]
        
        if not user_reviews:
            return Response({
                'recommendations': [],
                'message': 'Start reviewing places to get personalized recommendations!'
            }, status=status.HTTP_200_OK)
        
        # Prepare review history
        review_history = [
            {
                'place_name': review.place.name,
                'rating': review.rating,
                'text': review.text
            }
            for review in user_reviews
        ]
        
        try:
            # Generate recommendations
            recommendations = ai_service.generate_recommendations(
                user_review_history=review_history
            )
            
            serializer = RecommendationSerializer(recommendations, many=True)
            
            return Response({
                'recommendations': serializer.data,
                'based_on_reviews': len(review_history)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return Response({
                'recommendations': [],
                'error': 'Unable to generate recommendations'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PlaceQuestionAnswerView(APIView):
    """
    POST /api/ai/places/{place_id}/ask/
    
    Ask questions about a place using RAG
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, place_id):
        place = get_object_or_404(Place, id=place_id)
        
        serializer = PlaceQuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        question = serializer.validated_data['question']
        
        try:
            # Get answer using RAG
            result = ai_service.answer_question_about_place(
                place_id=place.id,
                place_name=place.name,
                question=question
            )
            
            response_serializer = QuestionAnswerSerializer({
                'question': question,
                **result
            })
            
            return Response(response_serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            return Response({
                'error': 'Unable to answer question',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RAGStatsView(APIView):
    """
    GET /api/ai/rag-stats/
    
    Get RAG system statistics (for debugging/admin)
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            stats = rag_service.get_collection_stats()
            return Response(stats, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting RAG stats: {str(e)}")
            return Response({
                'error': 'Unable to fetch stats'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)