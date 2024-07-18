from django.db import models
from django.utils.text import slugify

PHONE_TYPE = (
    ('MOBILE', 'MOBILE'),
    ('HOME', 'HOME'),
    ('WORK', 'WORK')
)


MONTH = (
    ("JAN", "JAN"),
    ("FEB", "FEB"),
    ("MAR", "MAR"),
    ("APR", "APR"),
    ("MAY", "MAY"),
    ("JUN", "JUN"),
    ("JUL", "JUL"),
    ("AUG", "AUG"),
    ("SEP", "SEP"),
    ("OCT", "OCT"),
    ("NOV", "NOV"),
    ("DEC", "DEC"),
)


class AcademicSession(models.Model):
    month_start = models.CharField(choices=MONTH, max_length=3)
    year_start = models.CharField(max_length=4)
    month_end = models.CharField(choices=MONTH, max_length=3)
    year_end = models.CharField(max_length=4)

    def __str__(self):
        return "Academic Session [{}{} - {}{}]".format(self.month_start, self.year_start, self.month_end, self.year_end)


class PhoneContact(models.Model):
    phone_contact = models.CharField(max_length=25)
    phone_type = models.CharField(choices=PHONE_TYPE, max_length=6, default='MOBILE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.phone_contact} - {self.phone_type}"


class Subject(models.Model):
    name = models.CharField(max_length=500)
    code = models.CharField(max_length=25, null=True, blank=True)
    prerequisite_subjects = models.ManyToManyField("self")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name


class Program(models.Model):
    name = models.CharField(max_length=500)
    code = models.CharField(max_length=10, null=True, blank=True)
    slug = models.SlugField(max_length=600)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Program - {self.name}"


class School(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(null=True, blank=True)
    programs = models.ManyToManyField(Program)
    subjects = models.ManyToManyField(Subject)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.slug)
        super(School, self).save(*args, **kwargs)

    def __str__(self):
        return f"School - {self.name}"


class Institution(models.Model):
    name = models.CharField(max_length=225)
    admin_user_id = models.IntegerField(blank=True, null=True)
    website = models.URLField()
    street_address = models.TextField(blank=True, null=True)
    city = models.CharField(null=True, blank=True, max_length=255)
    state = models.CharField(null=True, blank=True, max_length=255)
    country = models.CharField(null=True, blank=True, max_length=255)
    contact_phone = models.ManyToManyField(PhoneContact)
    email_domain = models.CharField(max_length=25)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(null=True, blank=True)
    # programs = models.ManyToManyField(Program)
    schools = models.ManyToManyField(School)
    current_session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

