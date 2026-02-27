from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    
    class Meta:
        model = UserProfile
        fields = [
            'bio', 'avatar', 'location', 
            'review_count', 'places_visited', 'helpful_votes_received',
            'notification_enabled', 'email_notifications'
        ]
        read_only_fields = ['review_count', 'places_visited', 'helpful_votes_received']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    
    Why separate serializer?
    - Different validation for registration vs other operations
    - Password should be write-only (security)
    - Clean separation of concerns
    """
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=6,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ['id', 'phone_number', 'name', 'email', 'password', 'password_confirm']
        read_only_fields = ['id']
        extra_kwargs = {
            'email': {'required': False}
        }
    
    def validate_phone_number(self, value):
        """
        Custom validation for phone number.
        Why? Ensure uniqueness with clear error message.
        """
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError(
                "A user with this phone number already exists."
            )
        return value
    
    def validate(self, attrs):
        """Validate that passwords match"""
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({
                "password_confirm": "Passwords do not match."
            })
        return attrs
    
    def create(self, validated_data):
        """
        Create user with hashed password.
        Why override? Need to use set_password() for proper hashing.
        """
        validated_data.pop('password_confirm')
        
        user = User.objects.create_user(
            phone_number=validated_data['phone_number'],
            name=validated_data['name'],
            password=validated_data['password']
        )
        
        # Set optional email if provided
        if validated_data.get('email'):
            user.email = validated_data['email']
            user.save()
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    
    Why separate? Login doesn't use User model directly,
    it validates credentials and returns tokens.
    """
    
    phone_number = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, data):
        """
        Validate credentials and return user.
        Why here? DRF best practice - validation in serializer.
        """
        phone_number = data.get('phone_number')
        password = data.get('password')
        
        if not phone_number or not password:
            raise serializers.ValidationError(
                "Both phone number and password are required."
            )
        
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "Invalid credentials. Please check your phone number and password."
            )
        
        if not user.check_password(password):
            raise serializers.ValidationError(
                "Invalid credentials. Please check your phone number and password."
            )
        
        if not user.is_active:
            raise serializers.ValidationError(
                "This account has been deactivated."
            )
        
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    """
    Basic user serializer for displaying user info.
    Used in review listings, etc.
    """
    
    profile = UserProfileSerializer(read_only=True)
    total_reviews = serializers.IntegerField(read_only=True)
    average_rating_given = serializers.FloatField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'name', 'phone_number', 'email', 
            'date_joined', 'total_reviews', 'average_rating_given',
            'profile'
        ]
        read_only_fields = ['id', 'phone_number', 'date_joined']


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Detailed user serializer for profile page.
    Includes statistics and preferences.
    """
    
    profile = UserProfileSerializer(read_only=True)
    total_reviews = serializers.SerializerMethodField()
    average_rating_given = serializers.SerializerMethodField()
    places_visited = serializers.SerializerMethodField()
    recent_reviews = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'name', 'phone_number', 'email',
            'date_joined', 'last_login', 'is_verified',
            'total_reviews', 'average_rating_given', 'places_visited',
            'profile', 'recent_reviews', 'preferences'
        ]
        read_only_fields = ['id', 'phone_number', 'date_joined', 'last_login', 'is_verified']
    
    def get_total_reviews(self, obj):
        return obj.total_reviews
    
    def get_average_rating_given(self, obj):
        return obj.average_rating_given
    
    def get_places_visited(self, obj):
        return obj.reviews.values('place').distinct().count()
    
    def get_recent_reviews(self, obj):
        """Get 5 most recent reviews"""
        from apps.places.serializers import ReviewSerializer
        recent = obj.reviews.select_related('place').order_by('-created_at')[:5]
        return ReviewSerializer(recent, many=True, context=self.context).data


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    
    profile = UserProfileSerializer(required=False)
    
    class Meta:
        model = User
        fields = ['name', 'email', 'preferences', 'profile']
    
    def update(self, instance, validated_data):
        """Update user and profile"""
        profile_data = validated_data.pop('profile', None)
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update profile if data provided
        if profile_data and hasattr(instance, 'profile'):
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        
        return instance


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing password"""
    
    old_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate_old_password(self, value):
        """Verify old password is correct"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
    
    def validate(self, attrs):
        """Validate new passwords match"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                "new_password_confirm": "New passwords do not match."
            })
        return attrs
    
    def save(self):
        """Update user password"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user