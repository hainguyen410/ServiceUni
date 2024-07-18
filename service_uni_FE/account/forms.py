import json

from django import forms

from helpers.helper_functions import make_request
from . import models as m

USER_TYPE = (
    ('ADMIN', 'ADMIN'),
    ('MANAGEMENT', 'MANAGEMENT'),
    ('STAFF', 'STAFF'),
)

GENDER = (
    ('MALE', 'MALE'),
    ('FEMALE', 'FEMALE'),
)


class LoginForm(forms.Form):
    email = forms.CharField(label='Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput())

    fields = ['email', 'password']

    # def clean_email(self):
    #     super(LoginForm, self).clean()
    #     email = self.cleaned_data.get('email')
    #
    #     return email.lower()


class RegisterForm(forms.Form):
    first_name = forms.CharField()
    middle_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(label='Password', widget=forms.PasswordInput())
    institution_name = forms.CharField()
    email_domain = forms.CharField()
    website = forms.URLField()
    street_address = forms.CharField(widget=forms.Textarea(attrs={"rows": 2, "cols": 20}))
    city = forms.CharField()
    state = forms.CharField()
    country = forms.CharField()


def get_courses():
    course_detail = []
    url = 'institution/api/subject/'
    status, course_details = make_request('get', url)

    if status == 200:
        status_code = course_details['status_code']
        if status_code == 200:
            course_detail = course_details['data']
    choices = []
    for i in course_detail:
        lister = [i['id'], i['name']]
        choices.append(lister)
    return choices


class CreateAccountForm(forms.Form):
    first_name = forms.CharField()
    middle_name = forms.CharField(required=False)
    last_name = forms.CharField()
    email = forms.EmailField()
    user_type = forms.ChoiceField(choices=USER_TYPE, widget=forms.Select())
    current_course_handling = forms.MultipleChoiceField(choices=[], widget=forms.SelectMultiple, required=False)
    street_address = forms.CharField()
    city = forms.CharField()
    state = forms.CharField()
    country = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['current_course_handling'] = forms.MultipleChoiceField(choices=get_courses(),
                                                                           widget=forms.SelectMultiple,
                                                                           required=False)


def get_programs():
    course_detail = []
    url = 'institution/api/program/'
    status, course_details = make_request('get', url)

    if status == 200:
        status_code = course_details['status_code']
        if status_code == 200:
            course_detail = course_details['data']
    choices = []
    for i in course_detail:
        lister = [i['id'], i['name']]
        choices.append(lister)
    return choices


def get_sessions():
    session_detail = []
    url = 'institution/api/academic_session/'
    status, session_details = make_request('get', url)

    if status == 200:
        status_code = session_details['status_code']
        if status_code == 200:
            session_detail = session_details['data']
    choices = []
    for i in session_detail:
        lister = [i['id'], f"{i['month_start']} {i['year_start']} - {i['month_end']} {i['year_end']}"]
        choices.append(lister)
    return choices


class AdmissionForm(forms.Form):
    first_name = forms.CharField()
    middle_name = forms.CharField(required=False)
    last_name = forms.CharField()
    gender = forms.ChoiceField(choices=GENDER, widget=forms.Select())
    street_address = forms.CharField(widget=forms.Textarea(attrs={"rows": 2, "cols": 20}))
    city = forms.CharField()
    state = forms.CharField()
    country = forms.CharField()
    date_of_birth = forms.DateField()
    contact_phone = forms.CharField()
    program_id = forms.ChoiceField(choices=[], widget=forms.Select())
    academic_session = forms.ChoiceField(choices=[], widget=forms.Select())

    def __init__(self, *args, **kwargs):
        super(AdmissionForm, self).__init__(*args, **kwargs)
        self.fields['program_id'] = forms.ChoiceField(choices=get_programs(), widget=forms.Select())
        self.fields['academic_session'] = forms.ChoiceField(choices=get_sessions(), widget=forms.Select())


class ProfileForm(forms.Form):
    first_name = forms.CharField()
    middle_name = forms.CharField(required=False)
    last_name = forms.CharField()
    email = forms.CharField()
    gender = forms.ChoiceField(choices=(("MALE", "MALE"), ("FEMALE", "FEMALE")), widget=forms.Select)
    coe = forms.CharField(required=False)
    current_course_handling = forms.MultipleChoiceField(choices=get_courses(), widget=forms.SelectMultiple, required=False)
    current_enrolled_courses = forms.MultipleChoiceField(choices=get_courses(), widget=forms.SelectMultiple, required=False)
    program = forms.ChoiceField(choices=get_programs(), widget=forms.Select, required=False)
