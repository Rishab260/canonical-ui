from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from .forms import AppForm
from .forms import CustomUserCreationForm
from .models import App
from .models import Artifact
from .models import Category
from .models import Screenshot
from .models import Team


# User registration view
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, authenticate
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, CustomAuthenticationForm

def login_and_register(request):
    login_form = CustomAuthenticationForm(request, data=request.POST or None)
    register_form = CustomUserCreationForm(request.POST or None)
    active_tab = 'login'

    if request.method == 'POST':
        if 'login_submit' in request.POST:
            active_tab = 'login'
            if login_form.is_valid():
                user = login_form.get_user()
                auth_login(request, user)
                return redirect('core:landing_page')
        elif 'signup_submit' in request.POST:
            active_tab = 'signup'
            if register_form.is_valid():
                user = register_form.save(commit=False)
                user.is_admin = False
                user.save()
                return redirect('core:login')

    return render(request, 'core/login.html', {
        'form': login_form,
        'register_form': register_form,
        'active_tab': active_tab,
    })

# Landing page view displaying all approved apps
def landing_page(request):
    categories = Category.objects.all()
    teams = Team.objects.all()

    # Search and filter logic
    search_query = request.GET.get('search', '')
    selected_category = request.GET.get('category', '')
    selected_team = request.GET.get('team', '')

    apps = App.objects.filter(is_approved=True)  # Only show approved apps

    if search_query:
        apps = apps.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query),
        )
    if selected_category:
        apps = apps.filter(category__id=selected_category)
    if selected_team:
        apps = apps.filter(teams_involved__id=selected_team)

    context = {
        'apps': apps,
        'categories': categories,
        'teams': teams,
        'search_query': search_query,
        'selected_category': selected_category,
        'selected_team': selected_team,
    }

    return render(request, 'core/landing_page.html', context)


# Logout view
def logout_view(request):
    logout(request)
    return redirect('core:login')


# Check if the user is a developer
def is_developer(user):
    return user.is_authenticated and user.role == 'developer'


# View for viewing app details
def view_app(request, id):
    app = get_object_or_404(App, id=id)
    teams_involved = app.teams_involved.all()
    return render(
        request, 'core/view_app.html', {
            'app': app,
            'teams_involved': teams_involved,
        },
    )


# Submit an app (developer only)
@user_passes_test(is_developer)
@login_required
def submit_app(request):
    if request.method == 'POST':
        form = AppForm(request.POST)

        if form.is_valid():
            # Save the app instance first (without files)
            app = form.save(commit=False)
            app.developer = request.user  # Assign the developer to the app
            app.save()  # Save the app instance first to generate an ID

            # Handle the screenshots (multiple file upload)
            if 'screenshots' in request.FILES:
                screenshots = request.FILES.getlist('screenshots')
                for screenshot in screenshots:
                    Screenshot.objects.create(
                        app=app, image=screenshot,
                    )  # Save each screenshot

            # Handle the artifacts (file uploads)
            if 'artifacts_files' in request.FILES:
                artifacts_files = request.FILES.getlist('artifacts_files')
                for artifact_file in artifacts_files:
                    # Save document or file
                    Artifact.objects.create(app=app, document=artifact_file)

            # Handle the hyperlinks (comma-separated links)
            artifacts_links = request.POST.get('artifacts_links', '')
            if artifacts_links:
                links = [link.strip() for link in artifacts_links.split(',')]
                for link in links:
                    Artifact.objects.create(
                        app=app, hyperlink=link,
                    )  # Save hyperlink

            # Show success message and redirect
            messages.success(
                request, 'App submitted successfully. Awaiting admin approval.',
            )
            return redirect('core:landing_page')
    else:
        form = AppForm()

    return render(request, 'core/submit_app.html', {'form': form})

# Admin dashboard to view pending apps


def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('core:landing_page')  # Redirect if not an admin

    pending_apps = App.objects.filter(is_approved=False)
    return render(request, 'core/admin_dashboard.html', {'pending_apps': pending_apps})


# View for app details in admin dashboard
def view_app_details(request, app_id):
    app = get_object_or_404(App, id=app_id)
    if not request.user.is_superuser:
        return redirect('core:landing_page')  # Redirect if not an admin

    teams_involved = app.teams_involved.all()
    return render(
        request, 'core/app_details.html', {
            'app': app,
            'teams_involved': teams_involved,
        },
    )


# Approve app by admin
def approve_app(request, app_id):
    app = get_object_or_404(App, id=app_id)
    if not request.user.is_superuser:
        return redirect('core:landing_page')  # Redirect if not an admin

    app.is_approved = True
    app.save()

    return redirect('core:admin_dashboard')
