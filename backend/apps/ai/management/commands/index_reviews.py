from django.core.management.base import BaseCommand
from apps.places.models import Review
from apps.ai.rag_service import rag_service
from apps.ai.services import ai_service
from apps.ai.models import ReviewAIAnalysis


class Command(BaseCommand):
    help = 'Index all existing reviews into RAG system'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of reviews to process in each batch'
        )
        parser.add_argument(
            '--analyze',
            action='store_true',
            help='Also run AI analysis on reviews'
        )
    
    def handle(self, *args, **options):
        batch_size = options['batch_size']
        analyze = options['analyze']
        
        self.stdout.write(self.style.SUCCESS('Starting review indexing...'))
        
        # Get all reviews
        reviews = Review.objects.select_related('place', 'user').all()
        total = reviews.count()
        
        self.stdout.write(f'Found {total} reviews to index')
        
        # Process in batches
        for i in range(0, total, batch_size):
            batch = reviews[i:i + batch_size]
            
            # Prepare data for RAG
            rag_data = [
                {
                    'id': review.id,
                    'text': review.text,
                    'place_id': review.place.id,
                    'rating': review.rating
                }
                for review in batch
            ]
            
            # Batch index
            rag_service.batch_index_reviews(rag_data)
            
            # Optionally analyze reviews
            if analyze:
                for review in batch:
                    # Skip if already analyzed
                    if hasattr(review, 'ai_analysis'):
                        continue
                    
                    try:
                        analysis_result = ai_service.analyze_review_sentiment(
                            review_text=review.text,
                            rating=review.rating
                        )
                        
                        ReviewAIAnalysis.objects.create(
                            review=review,
                            sentiment=analysis_result.get('sentiment', 'neutral'),
                            sentiment_score=analysis_result.get('sentiment_score', 0),
                            quality_score=analysis_result.get('quality_score', 0.5),
                            is_spam=analysis_result.get('is_spam', False),
                            keywords=analysis_result.get('keywords', []),
                            helpful_reason=analysis_result.get('helpful_reason', '')
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'Failed to analyze review {review.id}: {str(e)}')
                        )
            
            processed = min(i + batch_size, total)
            self.stdout.write(f'Processed {processed}/{total} reviews')
        
        self.stdout.write(self.style.SUCCESS('✓ Indexing complete!'))
        
        # Show stats
        stats = rag_service.get_collection_stats()
        self.stdout.write(self.style.SUCCESS(f'\nRAG Stats: {stats}'))