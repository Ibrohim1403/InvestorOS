from django.shortcuts import render, redirect
from .models import Task
from django.utils import timezone
from .models import Project, Issue, Task
from datetime import date
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from django.core.files.storage import FileSystemStorage
import re
import docx
import imaplib
import email

def settings_view(request):
    users = User.objects.all()
    return render(request, "settings.html", {"users": users})
    
def send_email(request, user_id):
    if request.method == "POST":
        user = User.objects.get(id=user_id)
        subject = request.POST.get("subject")
        message = request.POST.get("message")
        uploaded_file = request.FILES.get("file")

        email = EmailMessage(
            subject,
            message,
            "zerikkan2004@gmail.com",  # jo‘natuvchi
            [user.email],  # qabul qiluvchi
        )

        if uploaded_file:
            email.attach(uploaded_file.name, uploaded_file.read(), uploaded_file.content_type)

        email.send()
        messages.success(request, f"{user.email} manziliga xabar yuborildi ✅")
        return redirect("settings")

    return redirect("settings")

def check_email():
    # Gmail IMAP serveriga ulanish
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login("zerikkan2004@gmail.com", "locd bsit yzkw xrzu")  # ⚠️ Gmail uchun "App password" ishlatish kerak
    mail.select("inbox")

    # Eng so‘nggi xabarni olish
    result, data = mail.search(None, "ALL")
    mail_ids = data[0].split()
    latest_email_id = mail_ids[-1]

    result, msg_data = mail.fetch(latest_email_id, "(RFC822)")
    raw_email = msg_data[0][1]
    msg = email.message_from_bytes(raw_email)

    subject = msg["subject"]
    body = ""

    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode()
                break
    else:
        body = msg.get_payload(decode=True).decode()

    return subject, body




def morning_brief(request):
    today = date.today()

    tasks = Task.objects.filter(status__in=["todo", "doing"]).order_by("-ai_score", "-priority", "due_date")[:3]
    projects = Project.objects.filter(is_active=True).order_by("-start_date")[:3]
    issues = Issue.objects.filter(status="open").order_by("-created_at")[:3]

    # 📩 Email qo‘shamiz
    subject, body = None, None
    try:
        subject, body = check_email()
    except Exception as e:
        body = f"❌ Emailni o‘qib bo‘lmadi: {e}"

    context = {
        "tasks": tasks,
        "projects": projects,
        "issues": issues,
        "today": today,
        "subject": subject,
        "body": body,
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
    parsed_data = {}
    error = None

    if request.method == "POST" and request.FILES.get("file"):
        file = request.FILES["file"]
        try:
            # TXT faylni o‘qish
            if file.name.endswith(".txt"):
                content = file.read().decode("utf-8")

            # DOCX faylni o‘qish
            elif file.name.endswith(".docx"):
                doc = docx.Document(file)
                content = "\n".join([para.text for para in doc.paragraphs])

            else:
                error = "❌ Faqat .txt yoki .docx fayllar qabul qilinadi."
                content = ""

            # Fayldagi ma’lumotlarni ajratish (regex orqali)
            if content:
                parsed_data["fullname"]   = re.search(r"To‘liq ism-familiya:\s*(.*)", content)
                parsed_data["company"]    = re.search(r"Tashkilot.*:\s*(.*)", content)
                parsed_data["contact"]    = re.search(r"Bog‘lanish.*:\s*(.*)", content)
                parsed_data["investment"] = re.search(r"Investitsiya miqdori.*:\s*(.*)", content)
                parsed_data["project"]    = re.search(r"Loyiha nomi.*:\s*(.*)", content)
                parsed_data["doclink"]    = re.search(r"Loyiha taqdimoti.*:\s*(.*)", content)
                parsed_data["comment"]    = re.search(r"Izoh.*:\s*(.*)", content)

                # Regex natijalaridan matn olish
                for key, match in parsed_data.items():
                    parsed_data[key] = match.group(1).strip() if match else "—"

        except Exception as e:
            error = f"❌ Xatolik: {e}"

    return render(request, "reports.html", {
        "parsed_data": parsed_data,
        "error": error,
    })

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
