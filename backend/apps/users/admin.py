from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms
from .models import User, UserProfile


class UserCreationForm(forms.ModelForm):
    """Form for creating new users in admin."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ('phone_number', 'name', 'email')
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """Form for updating users in admin."""
    password = ReadOnlyPasswordHashField()
    
    class Meta:
        model = User
        fields = ('phone_number', 'name', 'email', 'password', 'is_active', 'is_staff', 'is_superuser')


class UserProfileInline(admin.StackedInline):
    """Inline admin for user profile"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for User model."""
    
    form = UserChangeForm
    add_form = UserCreationForm
    
    list_display = ['phone_number', 'name', 'email', 'is_active', 'is_staff', 'is_verified', 'date_joined', 'review_count']
    list_filter = ['is_active', 'is_staff', 'is_verified', 'date_joined']
    search_fields = ['phone_number', 'name', 'email']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Preferences', {'fields': ('preferences',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'name', 'email', 'password1', 'password2'),
        }),
    )
    
    inlines = [UserProfileInline]
    
    def review_count(self, obj):
        """Display review count in list"""
        return obj.reviews.count()
    review_count.short_description = 'Reviews'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for UserProfile model"""
    
    list_display = ['user', 'location', 'review_count', 'places_visited', 'helpful_votes_received', 'notification_enabled']
    list_filter = ['notification_enabled', 'email_notifications']
    search_fields = ['user__name', 'user__phone_number', 'location']
    readonly_fields = ['review_count', 'places_visited', 'helpful_votes_received', 'created_at', 'updated_at']
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Profile Info', {'fields': ('bio', 'avatar', 'location')}),
        ('Statistics', {'fields': ('review_count', 'places_visited', 'helpful_votes_received')}),
        ('Preferences', {'fields': ('notification_enabled', 'email_notifications')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )