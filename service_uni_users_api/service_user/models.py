from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Q
from django.utils.text import slugify

from helper_functions.helper import get_my_u_id, generate_email, generate_coe

GENDER = (
    ('MALE', 'MALE'),
    ('FEMALE', 'FEMALE'),
    ('OTHERS', 'OTHERS')
)

PHONE_TYPE = (
    ('MOBILE', 'MOBILE'),
    ('HOME', 'HOME'),
    ('WORK', 'WORK')
)

USER_TYPE = (
    ('ADMIN', 'ADMIN'),
    ('MANAGEMENT', 'MANAGEMENT'),
    ('STAFF', 'STAFF'),
    ('STUDENT', 'STUDENT'),
)

STUDENT_STATUS = (
    ('FUTURE_STUDENT', 'FUTURE_STUDENT'),
    ('CURRENT_STUDENT', 'CURRENT_STUDENT'),
    ('GRADUATE', 'GRADUATE'),
    ('DENIED', 'DENIED'),
)

SOFT_APPROVAL = (
    ('APPROVED', 'APPROVED'),
    ('REJECTED', 'REJECTED'),
)

STUDENT_TYPE = (
    ('PG', 'PG'),
    ('UG', 'UG'),
)

PROGRAM_LEVEL = (
    ('100', '100'),
    ('200', '200'),
    ('300', '300'),
    ('400', '400'),
    ('500', '500'),
    ('600', '600'),
    ('700', '700'),
    ('800', '800'),
    ('900', '900'),

)


def set_default_currency():
    user_type, _ = ServiceUserType.objects.get_or_create(user_type="ADMIN")
    return user_type.pk


class CustomUserManager(BaseUserManager, ):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('user_type', True)
        extra_fields.setdefault('institution', None)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

    def get_all_students(self):
        qs = super(CustomUserManager, self).get_queryset().filter(user_type="STUDENT")
        return qs

    def get_future_student(self):
        qs = self.get_all_students().filter(student_status="FUTURE_STUDENT")
        return qs

    def get_current_student(self):
        qs = self.get_all_students().filter(student_status="CURRENT_STUDENT")
        return qs

    def get_graduate_student(self):
        qs = self.get_all_students().filter(student_status="GRADUATE")
        return qs

    def get_all_staffs(self):
        qs = self.filter(user_type__in=["ADMIN", "STAFF", "MANAGEMENT"])
        return qs


class ServiceUserType(models.Model):
    user_type = models.CharField(max_length=25, choices=USER_TYPE, default='STUDENT')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Service UserType - {self.user_type}"


class PhoneContact(models.Model):
    phone_contact = models.CharField(max_length=25)
    phone_type = models.CharField(choices=PHONE_TYPE, max_length=6, default='MOBILE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.phone_contact} - {self.phone_type}"


class ServiceUser(AbstractBaseUser, PermissionsMixin):
    # Bio Data
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    middle_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    u_id = models.CharField(unique=True, editable=False, null=True, blank=True, max_length=5)
    date_of_birth = models.DateField(blank=True, null=True)
    street_address = models.TextField(blank=True, null=True)
    city = models.CharField(null=True, blank=True, max_length=255)
    state = models.CharField(null=True, blank=True, max_length=255)
    country = models.CharField(null=True, blank=True, max_length=255)
    contact_phone = models.ManyToManyField(PhoneContact, blank=True)
    gender = models.CharField(choices=GENDER, max_length=6, default='MALE')
    passport_photo = models.ImageField(upload_to='passport/', null=True, blank=True)

    # Official
    institution_id = models.IntegerField(null=True, blank=True)
    user_type = models.CharField(choices=USER_TYPE, max_length=10, default="STUDENT")

    # Student
    program_id = models.IntegerField(null=True, blank=True)
    student_type = models.CharField(choices=STUDENT_TYPE, max_length=2, default="UG", null=True, blank=True)
    current_level = models.CharField(choices=PROGRAM_LEVEL, max_length=3, default="100", null=True, blank=True)
    current_enrolled_courses = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)
    program_approval = models.BooleanField(default=False)
    soft_approval = models.CharField(choices=SOFT_APPROVAL, null=True, blank=True, max_length=8)
    student_status = models.CharField(choices=STUDENT_STATUS, max_length=16, null=True, blank=True)
    coe = models.CharField(max_length=20, null=True, blank=True)
    # Staff
    current_course_handling = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)

    # Student and Staff
    school_id = models.IntegerField(null=True, blank=True)
    # Django
    date_joined = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'

    def save(self, *args, **kwargs):
        if not self.is_superuser:
            if self._state.adding:
                existing_users = ServiceUser.objects.all()
                self.u_id = get_my_u_id([self.first_name, self.middle_name, self.last_name], existing_users)
        super(ServiceUser, self).save(*args, **kwargs)

    @property
    def get_full_name(self):
        if self.first_name is not None and self.last_name is not None:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name is None and self.last_name is not None:
            return f"{self.last_name}"
        elif self.first_name is not None and self.last_name is None:
            return f"{self.first_name}"
        else:
            return f"{self.email} Name not set"

    def __str__(self):
        return f"{self.user_type} - {self.get_full_name}"
