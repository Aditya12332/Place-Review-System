from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone


class UserManager(BaseUserManager):
    """
    Custom manager for User model.
    Why? Need to handle phone number as username instead of email.
    """
    
    def create_user(self, phone_number, name, password=None):
        if not phone_number:
            raise ValueError('Users must have a phone number')
        if not name:
            raise ValueError('Users must have a name')
        
        user = self.model(
            phone_number=phone_number,
            name=name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone_number, name, password=None):
        user = self.create_user(
            phone_number=phone_number,
            name=name,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model using phone number for authentication.
    
    Why custom model?
    - Requirement: Users register with name and phone number
    - Phone number must be unique
    - Django's default User uses email/username
    """
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        unique=True,
        db_index=True,
        help_text="User's phone number for authentication"
    )
    name = models.CharField(max_length=255, help_text="User's full name")
    email = models.EmailField(max_length=255, blank=True, null=True, help_text="Optional email address")
    
    # User status
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False, help_text="Whether phone is verified")
    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # User preferences (for AI features)
    preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text="User preferences for recommendations"
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['name']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['date_joined']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.phone_number})"
    
    def get_full_name(self):
        return self.name
    
    def get_short_name(self):
        return self.name.split()[0] if self.name else self.phone_number
    
    @property
    def total_reviews(self):
        """Get total number of reviews by this user"""
        return self.reviews.count()
    
    @property
    def average_rating_given(self):
        """Calculate average rating given by this user"""
        from django.db.models import Avg
        result = self.reviews.aggregate(avg_rating=Avg('rating'))
        return round(result['avg_rating'], 2) if result['avg_rating'] else 0


class UserProfile(models.Model):
    """
    Extended user profile for additional information.
    Separated to keep User model clean.
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    # Optional profile info
    bio = models.TextField(blank=True, max_length=500)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    
    # User statistics (denormalized for performance)
    review_count = models.IntegerField(default=0)
    places_visited = models.IntegerField(default=0)
    helpful_votes_received = models.IntegerField(default=0)
    
    # Preferences
    notification_enabled = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.name}'s Profile"
    
    def update_stats(self):
        """Update denormalized statistics"""
        from django.db.models import Sum
        
        self.review_count = self.user.reviews.count()
        self.places_visited = self.user.reviews.values('place').distinct().count()
        
        # Calculate helpful votes received
        helpful_votes = self.user.reviews.aggregate(
            total_helpful=Sum('helpful_count')
        )
        self.helpful_votes_received = helpful_votes['total_helpful'] or 0
        
        self.save(update_fields=['review_count', 'places_visited', 'helpful_votes_received'])