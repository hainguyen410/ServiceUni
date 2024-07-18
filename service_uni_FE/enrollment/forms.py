from django import forms

from helpers.helper_functions import make_request


def get_academic_sessions():
    session_detail = []
    session_url = 'institution/api/academic_session/'
    status, session_details = make_request('get', session_url)

    if status == 200:
        status_code = session_details['status_code']
        if status_code == 200:
            session_detail = session_details['data']
    choices = []
    for i in session_detail:
        lister = (i['id'], f"{i['month_start']} {i['year_start']} - {i['month_end']} {i['year_end']}")
        lister = tuple(lister)
        choices.append(lister)

    return tuple(choices)


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


class SubjectEnrollmentForm(forms.Form):

    session_id = forms.ChoiceField(choices=(), widget=forms.Select())
    subject_id = forms.ChoiceField(choices=(), widget=forms.Select())

    def __init__(self, *args, **kwargs):
        super(SubjectEnrollmentForm, self).__init__(*args, **kwargs)
        self.fields['subject_id'] = forms.ChoiceField(choices=get_subjects(), widget=forms.Select())
        self.fields['session_id'] = forms.ChoiceField(choices=get_academic_sessions(), widget=forms.Select())


class SessionEnrollmentForm(forms.Form):
    session_id = forms.ChoiceField(choices=get_subjects(), widget=forms.Select())
    student_id = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        super(SessionEnrollmentForm, self).__init__(*args, **kwargs)
        self.fields['session_id'] = forms.ChoiceField(choices=get_academic_sessions(), widget=forms.Select())
