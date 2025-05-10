# Register your models here.
from __future__ import annotations

from django.contrib import admin

from .models import App
from .models import Artifact
from .models import Category
from .models import Feedback
from .models import Rating
from .models import Screenshot
from .models import Team
from .models import User

admin.site.register(User)
admin.site.register(Team)
admin.site.register(Category)
admin.site.register(App)
admin.site.register(Screenshot)
admin.site.register(Rating)
admin.site.register(Feedback)
admin.site.register(Artifact)
