from django.contrib import admin
from .models import PlaceAISummary, ReviewAIAnalysis, UserSearchHistory


@admin.register(PlaceAISummary)
class PlaceAISummaryAdmin(admin.ModelAdmin):
    list_display = ['place', 'sentiment_label', 'sentiment_score', 'generated_at', 'needs_update']
    list_filter = ['sentiment_label', 'generated_at']
    search_fields = ['place__name', 'summary']
    readonly_fields = ['generated_at']
    
    def needs_update(self, obj):
        return obj.needs_update()
    needs_update.boolean = True


@admin.register(ReviewAIAnalysis)
class ReviewAIAnalysisAdmin(admin.ModelAdmin):
    list_display = ['review', 'sentiment', 'quality_score', 'is_spam', 'generated_at']
    list_filter = ['sentiment', 'is_spam', 'generated_at']
    search_fields = ['review__text']
    readonly_fields = ['generated_at']


@admin.register(UserSearchHistory)
class UserSearchHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'query', 'results_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__name', 'query']
    readonly_fields = ['created_at']