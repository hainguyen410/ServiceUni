from django import forms

from helpers.helper_functions import make_request


def get_institutions(institution_id):
    subject_url = 'institution/api/institution/'
    status, institution_details = make_request('get', subject_url)
    institution_detail = []
    if status == 200:
        status_code = institution_details['status_code']
        if status_code == 200:
            institution_detail = institution_details['data']
    choices = []
    for i in institution_detail:
        if i['id'] == institution_id:
            lister = (i['id'], i['name'])
            lister = tuple(lister)
            choices.append(lister)

    return tuple(choices)


class SchoolForm(forms.Form):
    name = forms.CharField()

    def __init__(self, institution_id, *args, **kwargs):
        super(SchoolForm, self).__init__(*args, **kwargs)
        self.fields['institution'] = forms.ChoiceField(choices=get_institutions(institution_id), widget=forms.Select())


def get_schools():
    subject_url = 'institution/api/school/'
    status, school_details = make_request('get', subject_url)
    school_detail = []
    if status == 200:
        status_code = school_details['status_code']
        if status_code == 200:
            school_detail = school_details['data']
    choices = []
    for i in school_detail:
        lister = (i['id'], i['name'])
        lister = tuple(lister)
        choices.append(lister)

    return tuple(choices)


class ProgramForm(forms.Form):
    name = forms.CharField()
    code = forms.CharField()
    school = forms.ChoiceField(choices=[], widget=forms.Select())

    def __init__(self, *args, **kwargs):
        super(ProgramForm, self).__init__(*args, **kwargs)
        self.fields['school'] = forms.ChoiceField(choices=get_schools(), widget=forms.Select())


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


class SubjectForm(forms.Form):
    school = forms.ChoiceField(choices=get_schools(), widget=forms.Select())
    name = forms.CharField()
    code = forms.CharField()
    prerequisite_subjects = forms.MultipleChoiceField(choices=[], widget=forms.SelectMultiple, required=False)

    def __init__(self, *args, **kwargs):
        super(SubjectForm, self).__init__(*args, **kwargs)
        self.fields['prerequisite_subjects'] = forms.MultipleChoiceField(choices=get_subjects(),
                                                                         widget=forms.SelectMultiple,
                                                                         required=False)

