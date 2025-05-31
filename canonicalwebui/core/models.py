from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models

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
    description = models.TextField()
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True,
    )
    contributors = models.ManyToManyField(
        User, related_name='contributions', blank=True,
    )
    teams_involved = models.ManyToManyField(Team, blank=True)
    developer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='uploaded_apps',
    )
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/app/{self.id}/"
    
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return round(sum(r.rating for r in ratings) / ratings.count(), 2)
        return None



class Artifact(models.Model):
    app = models.ForeignKey(
        App, on_delete=models.CASCADE, related_name='artifacts',
    )
    # For file uploads (docs, PDFs, etc.)
    document = models.FileField(
        upload_to='artifacts/%Y/%m/%d/', blank=True, null=True,
    )
    # For hyperlinks (external URLs)
    hyperlink = models.URLField(blank=True, null=True)
    # Optional description for the artifact
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Artifact for {self.app.name} - {self.description if self.description else 'No description'}"

    def is_file_type(self):
        # Return True if it's a file (document, PDF, etc.), False if it's a hyperlink
        return bool(self.document)


# Screenshot model
class Screenshot(models.Model):
    app = models.ForeignKey(
        App, on_delete=models.CASCADE,
        related_name='screenshots',
    )
    image = models.ImageField(upload_to='screenshots/')

    def __str__(self):
        return f"Screenshot for {self.app.name}"


class Rating(models.Model):
    app = models.ForeignKey(App, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('app', 'user')

    def __str__(self):
        return f"{self.user} rated {self.app.name} - {self.rating}"



class Feedback(models.Model):
    app = models.ForeignKey(
        App, on_delete=models.CASCADE, related_name='feedbacks',
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()

    class Meta:
        unique_together = ('app', 'user')

    def __str__(self):
        return f"Feedback by {self.user} on {self.app.name}"
