import json

from django import forms

from helpers.helper_functions import make_request
from . import models as m

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

def get_subjects():
    subject_url = 'institution/api/subject/'
    status, subject_details = make_request('get', subject_url)
    subject_detail = []
    if status == 200:
        status_code = subject_details['status_code']
        if status_code == 200:
            subject_detail = subject_details['data']
    choices = []
    for i in subject_detail:
        lister = (i['id'], i['name'])
        lister = tuple(lister)
        choices.append(lister)

    return tuple(choices)

class CreateAcademicConsiderationForm(forms.Form):
    ac_from = forms.CharField()
    ac_to = forms.CharField()
    subject_id = forms.ChoiceField(choices=get_subjects(), widget=forms.Select())
    assessment_item_affected = forms.ChoiceField(choices=ASSESSMENT_ITEMS, widget=forms.Select())
    assessment_type = forms.ChoiceField(choices=ASSESSMENT_TYPES, widget=forms.Select())
    weight = forms.CharField()
    group_work = forms.BooleanField(required=False)
    due_date = forms.CharField()
    subject_coordinator = forms.CharField()
    nature_of_assistance = forms.ChoiceField(choices=NATURE_OF_ASSISTANCE, widget=forms.Select())
    comment = forms.CharField(required=False)
    nature_of_assistance_date = forms.CharField(required=False)
    status = forms.CharField(required=False)
    student_id = forms.CharField()
    id = forms.CharField(required=False)

    fields = ['ac_from', 'ac_to', 'subject_id', 'assessment_item_affected', 'assessment_type', 'weight', 'group_work', 'due_date', 'subject_coordinator',
              'nature_of_assistance','nature_of_assistance_date', 'comment', 'student_id']

