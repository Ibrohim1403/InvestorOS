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


# --- News model ---
class News(models.Model):
    CATEGORY_CHOICES = [
        ('tech', 'Texnologiya'),
        ('business', 'Biznes'),
        ('finance', 'Moliya'),
        ('startup', 'Startaplar'),
        ('investment', 'Investitsiya'),
        ('market', 'Bozor'),
        ('crypto', 'Kripto'),
        ('other', 'Boshqa'),
    ]

    title = models.CharField(max_length=300, verbose_name="Sarlavha")
    content = models.TextField(verbose_name="Mazmun")
    summary = models.TextField(max_length=500, blank=True, verbose_name="Qisqacha")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other', verbose_name="Kategoriya")
    source_url = models.URLField(blank=True, null=True, verbose_name="Manba havolasi")
    source_name = models.CharField(max_length=100, blank=True, verbose_name="Manba nomi")
    image_url = models.URLField(blank=True, null=True, verbose_name="Rasm havolasi")

    # Real-time yangiliklar uchun
    is_breaking = models.BooleanField(default=False, verbose_name="Tezkor yangilik")
    is_featured = models.BooleanField(default=False, verbose_name="Asosiy yangilik")
    is_published = models.BooleanField(default=True, verbose_name="Nashr qilingan")

    # Vaqt ma'lumotlari
    published_at = models.DateTimeField(auto_now_add=True, verbose_name="Nashr vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqt")

    # Autor ma'lumoti
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Muallif"
    )

    # Statistika
    views_count = models.PositiveIntegerField(default=0, verbose_name="Ko'rishlar soni")

    class Meta:
        ordering = ['-published_at']
        verbose_name = "Yangilik"
        verbose_name_plural = "Yangiliklar"

    def __str__(self):
        return self.title

    def get_short_content(self):
        """Qisqartilgan mazmun qaytaradi"""
        if self.summary:
            return self.summary
        return self.content[:200] + "..." if len(self.content) > 200 else self.content


# --- NewsCategory model ---
class NewsCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Kategoriya nomi")
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, verbose_name="Tavsif")
    color = models.CharField(max_length=7, default="#007bff", help_text="Hex rang kodi")
    is_active = models.BooleanField(default=True, verbose_name="Faol")

    class Meta:
        verbose_name = "Yangilik kategoriyasi"
        verbose_name_plural = "Yangilik kategoriyalari"

    def __str__(self):
        return self.name