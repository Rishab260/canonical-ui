# Register your models here.
from django.contrib import admin
from .models import User, Team, Category, App, Screenshot, Rating, Feedback, Artifact

admin.site.register(User)
admin.site.register(Team)
admin.site.register(Category)
admin.site.register(App)
admin.site.register(Screenshot)
admin.site.register(Rating)
admin.site.register(Feedback)
admin.site.register(Artifact)
