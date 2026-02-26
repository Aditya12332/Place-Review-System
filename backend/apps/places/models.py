from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class Place(models.Model):
    
    name = models.CharField(max_length=255, db_index=True)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'places'

        constraints = [
            models.UniqueConstraint(
                fields=['name', 'address'],
                name='unique_place_name_address'
            )
        ]
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['-created_at']),
        ]
        verbose_name = 'Place'
        verbose_name_plural = 'Places'
    
    def __str__(self):
        return f"{self.name} - {self.address[:50]}"
    
    @property
    def average_rating(self):
        """
        Calculate average rating for this place.
        """
        from django.db.models import Avg
        result = self.reviews.aggregate(avg_rating=Avg('rating'))
        return round(result['avg_rating'], 2) if result['avg_rating'] else 0
    
    @property
    def total_reviews(self):
        """Total number of reviews for this place."""
        return self.reviews.count()


class Review(models.Model):
    
    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name='reviews'  
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1, message="Rating must be at least 1"),
            MaxValueValidator(5, message="Rating must be at most 5")
        ]
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reviews'
        indexes = [
            models.Index(fields=['place', 'user']),
            models.Index(fields=['place', '-created_at']),
        ]
        ordering = ['-created_at']
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
    
    def __str__(self):
        return f"{self.user.name} - {self.place.name} ({self.rating}/5)"