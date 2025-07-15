from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg
from django.utils.text import slugify

# Custom User model
class User(AbstractUser):
    ROLE_CHOICES = (
        ('developer', 'Developer'),
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_approved = models.BooleanField(default=False)

# Team model
class Team(models.Model):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField('core.User', related_name='teams')

    def __str__(self):
        return self.name

# Category model
class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

# Use the custom user model for foreign keys below
User = get_user_model()

# App model
class App(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    contributors = models.ManyToManyField(User, related_name='contributions', blank=True)
    teams_involved = models.ManyToManyField(Team, blank=True)
    developer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_apps',null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    icon = models.ImageField(upload_to='app_icons/', blank=True, null=True)
    visit_count = models.PositiveIntegerField(default=0)
    tech_stack = models.CharField(max_length=255, blank=True)
    authors = models.CharField(max_length=255, blank=True, null=True)
    # submitter_name = models.CharField(max_length=100, blank=True, null=True)
    # submitter_gmail = models.EmailField(blank=True, null=True)
    VERSION_CHOICES = [
        ('beta', 'Beta'),
        ('developed', 'Developed'),
    ]
    version_type = models.CharField(max_length=20, choices=VERSION_CHOICES, default='beta')
    version_number = models.CharField(max_length=20, blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)


    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug or App.objects.exclude(id=self.id).filter(slug=self.slug).exists():
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while App.objects.exclude(id=self.id).filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def average_rating(self):
        avg = self.ratings.aggregate(avg_rating=Avg('rating'))['avg_rating']
        return round(avg, 2) if avg is not None else None

class Artifact(models.Model):
    app = models.ForeignKey(App, on_delete=models.CASCADE, related_name='artifacts')
    document = models.FileField(upload_to='artifacts/%Y/%m/%d/', blank=True, null=True)
    hyperlink = models.URLField(blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Artifact for {self.app.name} - {self.description if self.description else 'No description'}"

    def is_file_type(self):
        return bool(self.document)

    def clean(self):
        if not self.document and not self.hyperlink:
            raise ValidationError("Provide either a document or a hyperlink.")

# Screenshot model
class Screenshot(models.Model):
    app = models.ForeignKey(App, on_delete=models.CASCADE, related_name='screenshots')
    image = models.ImageField(upload_to='screenshots/')

    def __str__(self):
        return f"Screenshot for {self.app.name}"

class Rating(models.Model):
    app = models.ForeignKey(App, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    gmail = models.EmailField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} rated {self.app.name} - {self.rating}"

class Feedback(models.Model):
    app = models.ForeignKey(App, on_delete=models.CASCADE, related_name='feedbacks')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()

    class Meta:
        unique_together = ('app', 'user')

    def __str__(self):
        return f"Feedback by {self.user} on {self.app.name}"