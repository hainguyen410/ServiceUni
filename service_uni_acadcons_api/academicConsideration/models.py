from django.db import models


STATUS = (
    ("NEW", "NEW"),
    ("REQUEST_INFO", "REQUEST_INFO"),
    ("LEVEL1_PENDING", "LEVEL1_PENDING"),
    ("LEVEL1_APPROVED", "LEVEL1_APPROVED"),
    ("LEVEL1_DECLINED", "LEVEL1_DECLINED"),
    ("LEVEL2_PENDING", "LEVEL2_PENDING"),
    ("LEVEL2_APPROVED", "LEVEL2_APPROVED"),
    ("LEVEL2_DECLINED", "LEVEL2_DECLINED")
)

ASSESSMENT_ITEMS = [
    ("Quiz", "Quiz"),
    ("Project", "Project"),
    ("Exam", "Exam"),
    ("Assignment", "Assignment"),
    ("Attendance/Participation", "Attendance/Participation"),
    ("End-of-session exam", "End-of-session exam"),
    ("Essay", "Essay"),
    ("Other", "Other")
]

ASSESSMENT_TYPES = [
    ("Quiz", "Quiz"),
    ("Project", "Project"),
    ("Exam", "Exam"),
    ("Assignment", "Assignment"),
    ("Attendance/Participation", "Attendance/Participation"),
    ("End-of-session exam", "End-of-session exam"),
    ("Essay", "Essay"),
    ("Other", "Other")
]

NATURE_OF_ASSISTANCE = [
    ("Extension of time to submit an assessment task", "Extension of time to submit an assessment task"),
    ("Permission to undertake a deferred assessment task or in-session test",
     "Permission to undertake a deferred assessment task or in-session test"),
    ("Permission to undertake a deferred end-of-session exam",
     "Permission to undertake a deferred end-of-session exam"),
    ("Consideration for compulsory attendance or participation requirement",
     "Consideration for compulsory attendance or participation requirement"),
]


# Create your models here.
class AcademicConsideration(models.Model):
    student_id = models.IntegerField()
    ac_from = models.DateField(null=True, blank=True)
    ac_to = models.DateField(null=True, blank=True)
    subject_id = models.IntegerField(default=0)
    assessment_item_affected = models.CharField(choices=ASSESSMENT_ITEMS, max_length=300, default='Quiz')
    assessment_type = models.CharField(choices=ASSESSMENT_TYPES, max_length=300, default='Quiz')
    weight = models.IntegerField(default=0)
    group_work = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)
    subject_coordinator = models.CharField(max_length=500)
    nature_of_assistance = models.CharField(choices=NATURE_OF_ASSISTANCE, max_length=300, default="Extension of time to submit an assessment task")
    nature_of_assistance_date = models.DateField(null=True, blank=True)
    status = models.CharField(choices=STATUS, max_length=20, default='NEW')
    comment = models.CharField(max_length=500)