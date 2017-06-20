from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

CATEGORY_CHOICES = (
    ("OTHERS", 'Others'),
    ("VIDEOS & FILMS", 'Videos & Films'),
    ("MUSIC", 'Music'),
    ("WRITING", 'Writing'),
    ("ARTS & CRAFTS", 'Arts & Crafts'),
    ("GAMES", 'Games'),
    ("PHOTOGRAPHY", 'Photography'),
    ("SCIENCE & TECHNOLOGY", 'Science & Technology'),
    ("EDUCATION", 'Education'),
    ("DANCE & THEATER", 'Dance & Theater'),
    ("CODING", 'Coding'),
)


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    username = models.CharField(max_length=20, unique=True)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    full_name = models.CharField(max_length=30, blank=True)
    short_bio = models.CharField(max_length=50, blank=True)
    profile_description = models.CharField(max_length=1000, blank=True)
    picture = models.ImageField(upload_to='profile_images', default="profile_images/profile_b.jpg")
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default="Coding",
        blank=False,
    )
    featured_video = models.URLField(blank=True)
    social_links = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_creator = models.BooleanField(default=False)
    last_login = models.DateTimeField(default=timezone.now)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = MyUserManager()

    USERNAME_FIELD = 'username'

    # REQUIRED_FIELDS = 'username'

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.full_name

    def get_username(self):
        return self.username

    def get_email(self):
        return self.email

    def __str__(self):  # __unicode__ on Python 2
        return self.full_name

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
