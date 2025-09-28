from django.shortcuts import render, redirect
from .models import Task
from django.utils import timezone
from .models import Project, Issue, Task
from datetime import date
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm




def morning_brief(request):
    today = date.today()


    tasks = Task.objects.filter(status__in=["todo", "doing"]).order_by("-ai_score", "-priority", "due_date")[:3]

 
    projects = Project.objects.filter(is_active=True).order_by("-start_date")[:3]

   
    issues = Issue.objects.filter(status="open").order_by("-created_at")[:3]

    context = {
        "tasks": tasks,
        "projects": projects,
        "issues": issues,
        "today": today,
    }
    return render(request, "morning_brief.html", context)


def heuristic_ai_score(task):
    score = (task.priority or 2) * 30.0
    if task.due_date:
        days = (task.due_date - date.today()).days
        if days <= 0:
            score += 20
        elif days <= 3:
            score += 10
    if task.startup:
        score += 5
    return min(100.0, max(0.0, score))


def analytics(request):
    return render(request, "analytics.html")

def reports(request):
    return render(request, "reports.html")

def settings_page(request):
    return render(request, "settings.html")


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect("login")
    else:
        form = CustomUserCreationForm()
    return render(request, "register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("morning_brief")
        else:
            messages.error(request, "Email yoki parol noto‘g‘ri!")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("login")
