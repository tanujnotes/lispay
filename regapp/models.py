from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.contrib.postgres.fields import ArrayField, JSONField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

from . import PaymentStatus

CATEGORY_CHOICES = (
    ("OTHERS", 'Others'),
    ("MUSIC", 'Music'),
    ("MEDIA", 'Media'),
    ("GAMES", 'Games'),
    ("COMEDY", 'Comedy'),
    ("WRITING", 'Writing'),
    ("PODCASTS", 'Podcasts'),
    ("EDUCATION", 'Education'),
    ("PHOTOGRAPHY", 'Photography'),
    ("PROGRAMMING", 'Programming'),
    ("CRAFTS AND DIY", 'Crafts and DIY'),
    ("VIDEOS AND FILMS", 'Videos and Films'),
    ("DANCE AND THEATER", 'Dance and Theater'),
    ("DRAWING AND PAINTING", 'Drawing and Painting'),
    ("SCIENCE AND TECHNOLOGY", 'Science and Technology'),
)

SUBS_STATUS = (
    ("unknown", 'unknown'),
    ("created", 'created'),
    ("authenticated", 'authenticated'),
    ("active", 'active'),
    ("pending", 'pending'),
    ("halted", 'halted'),
    ("cancelled", 'cancelled'),
    ("completed", 'completed'),
    ("expired", 'expired')
)

SUBS_CHANNEL = (
    ("NA", "na"),
    ("ZOHO", "zoho"),
    ("PAYTM", "paytm"),
    ("RAZORPAY", "razorpay"),
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
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    first_name = models.CharField(max_length=30, blank=True)  # Added for rest auth library
    last_name = models.CharField(max_length=30, blank=True)  # Added for rest auth library
    full_name = models.CharField(max_length=30, blank=True)
    mobile = models.CharField(max_length=20, blank=True)
    short_bio = models.CharField(max_length=50, blank=True)
    profile_description = models.CharField(max_length=1000, blank=True)
    featured_image = models.ImageField(upload_to='featured_images', default="featured_images/default_cover.jpg")
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
    featured_text = models.CharField(max_length=200, blank=True)  # Thank you note
    social_links = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_creator = models.BooleanField(default=False)
    club_2_reward = models.CharField(max_length=200, blank=True)
    club_3_reward = models.CharField(max_length=200, blank=True)
    club_4_reward = models.CharField(max_length=200, blank=True)
    last_login = models.DateTimeField(default=timezone.now)
    date_joined = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
        return self.username

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


class SubsPlanModel(models.Model):
    plan_id = models.CharField(max_length=255, blank=False, null=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    subscriber = models.ForeignKey(MyUser, related_name='plan_subscriber', on_delete=models.PROTECT)
    creator = models.ForeignKey(MyUser, related_name='plan_creator', on_delete=models.PROTECT)
    amount = models.PositiveSmallIntegerField(validators=[MinValueValidator(10), MaxValueValidator(9999)], blank=False)
    interval = models.PositiveSmallIntegerField(default=1)  # 1
    period = models.CharField(max_length=10, default='monthly')  # monthly
    currency = models.CharField(max_length=10, blank=True)
    notes = JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class SubscriptionModel(models.Model):
    subscription_id = models.CharField(max_length=20, blank=False)
    plan = models.ForeignKey(SubsPlanModel, related_name='plan', on_delete=models.PROTECT)
    subscriber = models.ForeignKey(MyUser, related_name='subscriber', on_delete=models.PROTECT)
    creator = models.ForeignKey(MyUser, related_name='creator', on_delete=models.PROTECT)
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
    amount = models.PositiveSmallIntegerField(validators=[MinValueValidator(10), MaxValueValidator(9999)], blank=False)
    paid_count = models.PositiveSmallIntegerField(blank=True, null=True)
    notes = JSONField(blank=True, null=True)
    start_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ended_at = models.DateTimeField(blank=True, null=True)


class PaymentModel(models.Model):
    invoice_id = models.CharField(max_length=255)
    subscription_id = models.CharField(max_length=255)
    payment_id = models.CharField(max_length=255)  # payment_id
    payment_type = models.CharField(max_length=255)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.CHOICES, default=PaymentStatus.WAITING)
    subscriber = models.ForeignKey(MyUser, related_name='subscriber_payment', on_delete=models.PROTECT, blank=True)
    creator = models.ForeignKey(MyUser, related_name='creator_payment', on_delete=models.PROTECT, blank=True)
    tax = models.DecimalField(max_digits=9, decimal_places=2, null=True)
    fee = models.DecimalField(max_digits=9, decimal_places=2, null=True)
    captured_amount = models.DecimalField(max_digits=9, decimal_places=2, default='0.0')
    total_amount = models.DecimalField(max_digits=9, decimal_places=2, default='0.0')
    currency = models.CharField(max_length=10)
    message = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class DataDumpModel(models.Model):
    event_type = models.CharField(max_length=100, blank=False)
    data = JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
