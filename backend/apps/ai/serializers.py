from rest_framework import serializers
from .models import PlaceAISummary, ReviewAIAnalysis, UserSearchHistory


class PlaceAISummarySerializer(serializers.ModelSerializer):
    """Serializer for place AI summaries"""
    
    needs_update = serializers.SerializerMethodField()
    
    class Meta:
        model = PlaceAISummary
        fields = [
            'id', 'summary', 'sentiment_score', 'sentiment_label',
            'positive_percentage', 'negative_percentage', 'neutral_percentage',
            'top_keywords', 'highlights', 'concerns',
            'generated_at', 'review_count_at_generation', 'needs_update'
        ]
        read_only_fields = ['id', 'generated_at']
    
    def get_needs_update(self, obj):
        """Check if summary is outdated"""
        return obj.needs_update()


class ReviewAIAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for review AI analysis"""
    
    class Meta:
        model = ReviewAIAnalysis
        fields = [
            'id', 'sentiment', 'sentiment_score', 'quality_score',
            'is_spam', 'keywords', 'helpful_reason', 'generated_at'
        ]
        read_only_fields = ['id', 'generated_at']


class SearchSuggestionSerializer(serializers.Serializer):
    """Serializer for AI-generated search suggestions"""
    
    suggestions = serializers.ListField(
        child=serializers.CharField(max_length=255)
    )


class RecommendationSerializer(serializers.Serializer):
    """Serializer for AI recommendations"""
    
    type = serializers.CharField()
    reason = serializers.CharField()


class PlaceQuestionSerializer(serializers.Serializer):
    """Serializer for asking questions about a place"""
    
    question = serializers.CharField(max_length=500)
    
    def validate_question(self, value):
        """Validate question is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Question cannot be empty")
        return value.strip()


class QuestionAnswerSerializer(serializers.Serializer):
    """Serializer for Q&A responses"""
    
    question = serializers.CharField()
    answer = serializers.CharField()
    confidence = serializers.CharField()
    sources = serializers.ListField(
        child=serializers.CharField()
    )


class RegenerateSummarySerializer(serializers.Serializer):
    """Serializer for triggering summary regeneration"""
    
    force = serializers.BooleanField(default=False)