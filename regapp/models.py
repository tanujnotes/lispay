from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

CATEGORY_CHOICES = (
    ("OTHERS", 'Others'),
    ("VIDEOS AND FILMS", 'Videos and Films'),
    ("MUSIC", 'Music'),
    ("WRITING", 'Writing'),
    ("ARTS AND CRAFTS", 'Arts and Crafts'),
    ("GAMES", 'Games'),
    ("MEDIA", 'Media'),
    ("PHOTOGRAPHY", 'Photography'),
    ("SCIENCE AND TECHNOLOGY", 'Science and Technology'),
    ("EDUCATION", 'Education'),
    ("DANCE AND THEATER", 'Dance and Theater'),
    ("CODING", 'Coding'),
)

SUBS_STATUS = (
    ("unknown", 'unknown'),
    ("live", 'live'),
    ("trial", 'trial'),
    ("dunning", 'dunning'),
    ("unpaid", 'unpaid'),
    ("non_renewing", 'non_renewing'),
    ("cancelled", 'cancelled'),
    ("creation_failed", 'creation_failed'),
    ("cancelled_from_dunning", 'cancelled_from_dunning'),
    ("expired", 'expired'),
    ("trial_expired", 'trial_expired'),
    ("future", 'future')
)

SUBS_CHANNEL = (
    ("NA", "na"),
    ("ZOHO", "zoho"),
    ("PAYTM", "paytm")
)

FEATURED_TEXT = "Thank you for your help!"


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
    thumbnail = models.ImageField(upload_to='profile_images', default="profile_images/profile_b.jpg")
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default="Coding",
        blank=False,
    )
    card_ids = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    customer_id = models.CharField(max_length=20, blank=True)
    featured_video = models.URLField(default="https://www.youtube.com/embed/oc_vB5Xcx1o")
    featured_text = models.CharField(max_length=1000, default=FEATURED_TEXT)
    social_links = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
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
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        # Simplest possible answer: All admins are staff
        return self.is_admin


class SubscriptionModel(models.Model):
    subscription_id = models.CharField(max_length=20, blank=False)
    subscriber = models.CharField(max_length=20, blank=False)
    creator = models.CharField(max_length=20, blank=False)
    status = models.CharField(
        max_length=30,
        choices=SUBS_STATUS,
        default="unknown",
        blank=False,
    )
    subs_channel = models.CharField(
        max_length=10,
        choices=SUBS_CHANNEL,
        default="NA",
        blank=False,
    )
    amount = models.PositiveSmallIntegerField(blank=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(blank=True, null=True)
