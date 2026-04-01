from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings


# --- Custom User Manager ---
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email kiritish majburiy!")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser is_staff=True bo‘lishi kerak.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser is_superuser=True bo‘lishi kerak.")

        return self.create_user(email, password, **extra_fields)


# --- Custom User ---
class CustomUser(AbstractUser):
    username = None  # username ishlatilmaydi
    email = models.EmailField(unique=True)

    # AbstractUser ichida allaqachon first_name va last_name bor
    # shuning uchun qayta yozish shart emas

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email


# --- Startup model ---
class Startup(models.Model):
    name = models.CharField(max_length=200)
    runway_months = models.FloatField(
        null=True, blank=True, help_text="Qancha oylar qolgan -> runway"
    )
    last_funding_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name


# --- Task model ---
class Task(models.Model):
    PRIORITY_CHOICES = [
        (1, "Low"),
        (2, "Medium"),
        (3, "High"),
    ]

    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    startup = models.ForeignKey(
        Startup,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    status = models.CharField(max_length=50, default="todo")
    ai_score = models.FloatField(
        null=True,
        blank=True,
        help_text="AI scoring placeholder (0-100)",
    )

    def __str__(self):
        return f"{self.title} ({self.startup or 'General'})"

    def get_runway_warning(self):
        if self.startup and self.startup.runway_months is not None:
            if self.startup.runway_months < 3:
                return "Critical"
            if self.startup.runway_months < 6:
                return "At Risk"
            return "OK"
        return None

    class Meta:
        ordering = ["-priority", "due_date", "created_at"]


# --- Project model ---
class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# --- Issue model ---
class Issue(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="issues"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[("open", "Open"), ("in_progress", "In Progress"), ("closed", "Closed")],
        default="open",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.status})"
