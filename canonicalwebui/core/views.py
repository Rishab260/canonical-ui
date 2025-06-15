from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    AppForm,
    CustomUserCreationForm,
    FeedbackForm,
    RatingForm,
)
from .models import (
    App,
    Artifact,
    Category,
    Screenshot,
    Team,
    Rating,
)

# -------------------------------
# Auth & Registration Views
# -------------------------------

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_admin = False  # Prevent self-registering as admin
            user.save()
            return redirect('core:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('core:login')


# -------------------------------
# Utility Functions
# -------------------------------

def is_developer(user):
    return user.is_authenticated and user.role == 'developer'


# -------------------------------
# Public Views
# -------------------------------

def landing_page(request):
    categories = Category.objects.all()
    teams = Team.objects.all()

    search_query = request.GET.get('search', '')
    selected_category = request.GET.get('category', '')
    

    apps = App.objects.filter(is_approved=True)

    if search_query:
        apps = apps.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))
    if selected_category:
        apps = apps.filter(category__id=selected_category)
    

    top_rated_apps = sorted(apps, key=lambda x: x.average_rating() or 0, reverse=True)[:4]
    featured_apps = apps.order_by('-created_at')[:4]

    context = {
        'apps': apps,
        'top_rated_apps': top_rated_apps,
        'featured_apps': featured_apps,
        'categories': categories,
        'search_query': search_query,
        'selected_category': selected_category,
    }

    return render(request, 'core/landing_page.html', context)


def app_details(request, app_id):
    app = get_object_or_404(App, id=app_id)

    ratings = app.ratings.select_related('user')
    feedbacks = app.feedbacks.select_related('user')
    feedback_form = FeedbackForm()
    rating_form = RatingForm()

    if request.method == 'POST':
        if 'comment' in request.POST and request.user.is_authenticated:
            feedback_form = FeedbackForm(request.POST)
            if feedback_form.is_valid():
                feedback = feedback_form.save(commit=False)
                feedback.app = app
                feedback.user = request.user
                feedback.save()
                messages.success(request, "Thanks for your feedback!")
                return redirect('core:app_details', app_id=app_id)

        if 'rating' in request.POST and request.user.is_authenticated:
            existing = Rating.objects.filter(app=app, user=request.user).first()
            rating_form = RatingForm(request.POST, instance=existing)
            if rating_form.is_valid():
                rating = rating_form.save(commit=False)
                rating.app = app
                rating.user = request.user
                rating.save()
                messages.success(request, "Thanks for your rating!")
                return redirect('core:app_details', app_id=app_id)

    context = {
        'app': app,
        'screenshots': app.screenshots.all(),
        'artifacts': app.artifacts.all(),
        'ratings': ratings,
        'feedbacks': feedbacks,
        'teams': app.teams_involved.all(),
        'feedback_form': feedback_form,
        'rating_form': rating_form,
    }

    return render(request, 'core/app_details.html', context)


def view_app(request, id):
    app = get_object_or_404(App, id=id)
    teams_involved = app.teams_involved.all()
    return render(request, 'core/view_app.html', {
        'app': app,
        'teams_involved': teams_involved,
    })


# -------------------------------
# Developer Views
# -------------------------------

@login_required
@user_passes_test(is_developer)
def submit_app(request):
    if request.method == 'POST':
        form = AppForm(request.POST)

        if form.is_valid():
            app = form.save(commit=False)
            app.developer = request.user
            app.icon = request.FILES.get('icon')
            app.save()
            form.save_m2m()

            # Save screenshots
            for screenshot in request.FILES.getlist('screenshots'):
                Screenshot.objects.create(app=app, image=screenshot)

            # Save artifact files
            artifact_files = request.FILES.getlist('artifacts_files')
            artifact_descriptions = request.POST.getlist('artifacts_descriptions')
            for file, desc in zip(artifact_files, artifact_descriptions):
                Artifact.objects.create(app=app, document=file, description=desc)

            # Save artifact links
            artifact_links = request.POST.getlist('artifact_links')
            link_descriptions = request.POST.getlist('artifact_link_descriptions')
            for url, desc in zip(artifact_links, link_descriptions):
                if url.strip():
                    Artifact.objects.create(app=app, hyperlink=url.strip(), description=desc)

            messages.success(request, 'App submitted successfully. Awaiting admin approval.')
            return redirect('core:landing_page')
    else:
        form = AppForm()

    return render(request, 'core/submit_app.html', {'form': form})


# -------------------------------
# Admin Views
# -------------------------------

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('core:landing_page')

    pending_apps = App.objects.filter(is_approved=False)
    return render(request, 'core/admin_dashboard.html', {'pending_apps': pending_apps})


@login_required
def view_app_details(request, app_id):
    app = get_object_or_404(App, id=app_id)
    if not request.user.is_superuser:
        return redirect('core:landing_page')

    teams_involved = app.teams_involved.all()
    return render(request, 'core/app_details.html', {
        'app': app,
        'teams_involved': teams_involved,
    })


@login_required
def approve_app(request, app_id):
    app = get_object_or_404(App, id=app_id)
    if not request.user.is_superuser:
        return redirect('core:landing_page')

    app.is_approved = True
    app.save()
    return redirect('core:admin_dashboard')
