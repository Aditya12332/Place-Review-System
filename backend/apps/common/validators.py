from rest_framework import serializers
import re


def validate_phone_number(value):
    """Validate phone number format"""
    phone_regex = re.compile(r'^\+?1?\d{9,15}$')
    if not phone_regex.match(value):
        raise serializers.ValidationError(
            "Phone number must be in format: '+999999999'. Up to 15 digits allowed."
        )
    return value


def validate_rating(value):
    """Validate rating is between 1 and 5"""
    if not 1 <= value <= 5:
        raise serializers.ValidationError("Rating must be between 1 and 5")
    return value


def sanitize_text(text):
    """Sanitize text input to prevent XSS"""
    # Remove potentially dangerous HTML tags
    dangerous_tags = ['<script', '<iframe', '<object', '<embed', '<link']
    for tag in dangerous_tags:
        text = text.replace(tag, '&lt;script')
    return text.strip()