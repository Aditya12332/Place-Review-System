from django.core.management.base import BaseCommand
from apps.places.models import Review
from apps.ai.rag_service import rag_service
from apps.ai.services import ai_service
from apps.ai.models import ReviewAIAnalysis


class Command(BaseCommand):
    def _analyze_batch(self, batch):
        for review in batch:
            # Skip already analyzed reviews
            if ReviewAIAnalysis.objects.filter(review=review).exists():
                continue

            try:
                result = ai_service.analyze_review_sentiment(
                    review_text=review.text,
                    rating=review.rating,
                )

                ReviewAIAnalysis.objects.create(
                    review=review,
                    sentiment=result.get("sentiment", "neutral"),
                    sentiment_score=result.get("sentiment_score", 0),
                    quality_score=result.get("quality_score", 0.5),
                    is_spam=result.get("is_spam", False),
                    keywords=result.get("keywords", []),
                    helpful_reason=result.get("helpful_reason", ""),
                )

            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"Failed to analyze review {review.id}: {str(e)}")
                )
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
    
    from django.db import transaction

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        analyze = options['analyze']

        self.stdout.write(self.style.SUCCESS("Starting review indexing..."))

        queryset = (
            Review.objects
            .select_related('place', 'user')
            .order_by('id')
        )

        total = queryset.count()
        self.stdout.write(f"Found {total} reviews to index")

        last_id = 0
        processed = 0

        while True:
            batch = list(
                queryset.filter(id__gt=last_id)[:batch_size]
            )

            if not batch:
                break

            # Prepare RAG payload
            rag_data = [
                {
                    "id": str(review.id),  # string safer for vector DB
                    "text": review.text,
                    "place_id": review.place_id,
                    "rating": review.rating,
                }
                for review in batch
            ]

            # ---- RAG Indexing ----
            try:
                rag_service.batch_index_reviews(rag_data)
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"RAG indexing failed for batch starting at ID {last_id}: {str(e)}")
                )

            # ---- AI Analysis ----
            if analyze:
                self._analyze_batch(batch)

            last_id = batch[-1].id
            processed += len(batch)

            self.stdout.write(f"Processed {processed}/{total}")

        self.stdout.write(self.style.SUCCESS("✓ Indexing complete!"))

        stats = rag_service.get_collection_stats()
        self.stdout.write(self.style.SUCCESS(f"\nRAG Stats: {stats}"))