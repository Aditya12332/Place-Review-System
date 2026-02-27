from django.db import models
from apps.places.models import Place, Review


class PlaceAISummary(models.Model):
    """AI-generated summaries for places using RAG"""
    
    place = models.OneToOneField(
        Place,
        on_delete=models.CASCADE,
        related_name='ai_summary'
    )
    summary = models.TextField()
    sentiment_score = models.FloatField()  # -1 to 1
    sentiment_label = models.CharField(max_length=20)  # positive/negative/neutral
    
    # Sentiment breakdown
    positive_percentage = models.FloatField(default=0)
    negative_percentage = models.FloatField(default=0)
    neutral_percentage = models.FloatField(default=0)
    
    # Keywords and insights
    top_keywords = models.JSONField(default=list)
    highlights = models.JSONField(default=list)  # Top positive aspects
    concerns = models.JSONField(default=list)  # Common concerns
    
    # Metadata
    generated_at = models.DateTimeField(auto_now=True)
    review_count_at_generation = models.IntegerField()
    
    class Meta:
        db_table = 'place_ai_summaries'
        verbose_name = 'Place AI Summary'
        verbose_name_plural = 'Place AI Summaries'
        indexes = [
            models.Index(fields=['-generated_at']),
        ]
    
    def __str__(self):
        return f"AI Summary for {self.place.name}"
    
    def needs_update(self):
        """Check if summary needs regeneration"""
        current_review_count = self.place.reviews.count()
        return current_review_count != self.review_count_at_generation


class ReviewAIAnalysis(models.Model):
    """AI analysis for individual reviews using RAG"""
    
    review = models.OneToOneField(
        Review,
        on_delete=models.CASCADE,
        related_name='ai_analysis'
    )
    sentiment = models.CharField(max_length=20)  # positive/negative/neutral
    sentiment_score = models.FloatField()  # -1 to 1
    quality_score = models.FloatField()  # 0 to 1 (helpfulness)
    is_spam = models.BooleanField(default=False)
    keywords = models.JSONField(default=list)
    helpful_reason = models.TextField(blank=True)  # Why this review is helpful
    
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'review_ai_analyses'
        verbose_name = 'Review AI Analysis'
        verbose_name_plural = 'Review AI Analyses'
        indexes = [
            models.Index(fields=['quality_score']),
            models.Index(fields=['is_spam']),
        ]
    
    def __str__(self):
        return f"AI Analysis for Review #{self.review.id}"


class UserSearchHistory(models.Model):
    """Track user searches for personalized suggestions"""
    
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='search_history'
    )
    query = models.CharField(max_length=255)
    filters = models.JSONField(default=dict, blank=True)  # Category, rating, etc.
    results_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_search_history'
        verbose_name = 'Search History'
        verbose_name_plural = 'Search Histories'
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.name} searched '{self.query}'"