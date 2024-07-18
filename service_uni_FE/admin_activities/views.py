import json

from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View

from account.decorator import must_authenticate
from helpers.helper_functions import make_request, parse_response, update_record, combine_data_inclusive
from . import forms as f


@method_decorator(must_authenticate, name='dispatch')
class CreateSchool(View):
    def get(self, request):
        template = 'admin_activities/new_school.html'
        institution_id = request.session.get("institution_id")

        school_form = f.SchoolForm(institution_id)
        context = {
            "school_form": school_form
        }
        return render(request, template_name=template, context=context)

    def post(self, request):
        institution_id = request.session.get("institution_id")
        school_form = f.SchoolForm(institution_id, request.POST)
        if school_form.is_valid():
            school_url = "institution/api/school/"
            request_json = school_form.cleaned_data

            status, school_details = make_request('post', school_url, request_json)
            error_list, enrolled_subject_data = parse_response(status, school_details)
            if error_list:
                for error in error_list:
                    messages.add_message(request, messages.ERROR, error)
                return redirect(self.request.META.get('HTTP_REFERER'))
            else:
                messages.add_message(request, messages.SUCCESS, "School / Faculty created Successfully")
                return redirect(self.request.META.get('HTTP_REFERER'))
        else:
            if school_form.errors:
                for field in school_form:
                    for error in field.errors:
                        messages.add_message(request, messages.ERROR, f"{field.label} - {error}")
            return redirect(self.request.META.get('HTTP_REFERER'))


@method_decorator(must_authenticate, name='dispatch')
class CreateProgram(View):
    def get(self, request):
        template = 'admin_activities/new_program.html'
        program_form = f.ProgramForm()
        context = {
            "program_form": program_form
        }
        return render(request, template_name=template, context=context)

    def post(self, request):
        program_form = f.ProgramForm(request.POST)
        if program_form.is_valid():
            request_json = program_form.cleaned_data
            program_url = "institution/api/program/"

            status, program_details = make_request('post', program_url, request_json)
            error_list, program_detail = parse_response(status, program_details)
            if error_list:
                for error in error_list:
                    messages.add_message(request, messages.ERROR, error)
                return redirect(self.request.META.get('HTTP_REFERER'))
            else:
                messages.add_message(request, messages.SUCCESS, "Program created Successfully")
                return redirect(self.request.META.get('HTTP_REFERER'))
        else:
            if program_form.errors:
                for field in program_form:
                    for error in field.errors:
                        messages.add_message(request, messages.ERROR, f"{field.label} - {error}")
            return redirect(self.request.META.get('HTTP_REFERER'))


@method_decorator(must_authenticate, name='dispatch')
class CreateSubject(View):
    def get(self, request):
        template = 'admin_activities/new_subject.html'
        subject_form = f.SubjectForm()
        context = {
            "subject_form": subject_form
        }
        return render(request, template_name=template, context=context)

    def post(self, request):
        subject_form = f.SubjectForm(request.POST)
        if subject_form.is_valid():
            request_json = subject_form.cleaned_data
            school_id = request_json.pop('school')
            request_json = {
                "subject": request_json,
            }

            url = f'institution/api/school/{school_id}/add_subject/'

            status, subject_details = make_request('patch', url, request_json)
            error_list, program_detail = parse_response(status, subject_details)
            if error_list:
                for error in error_list:
                    messages.add_message(request, messages.ERROR, error)
                return redirect(self.request.META.get('HTTP_REFERER'))
            else:
                messages.add_message(request, messages.SUCCESS, "Subject created Successfully")
                return redirect(self.request.META.get('HTTP_REFERER'))
        if subject_form.errors:
            for field in subject_form:
                for error in field.errors:
                    messages.add_message(request, messages.ERROR, f"{field.label} - {error}")
        return redirect(self.request.META.get('HTTP_REFERER'))


@method_decorator(must_authenticate, name='dispatch')
class ListSchool(View):
    def get(self, request):
        template = 'admin_activities/list_school.html'
        school_url = 'institution/api/school/'
        status, school_details = make_request('get', school_url,)
        error_list, school_detail = parse_response(status, school_details)
        if error_list:
            for error in error_list:
                messages.add_message(request, messages.ERROR, error)

        context = {
            "schools": school_detail
        }
        return render(request, template_name=template, context=context)


@method_decorator(must_authenticate, name='dispatch')
class ListProgram(View):
    def get(self, request):
        template = 'admin_activities/list_program.html'
        school_detail = []
        program_detail = []
        program_url = 'institution/api/program/'
        status, program_details = make_request('get', program_url, )
        error_list, program_detail = parse_response(status, program_details)

        if error_list:
            for error in error_list:
                messages.add_message(request, messages.ERROR, error)
        else:
            school_url = 'institution/api/school/'
            status, school_details = make_request('get', school_url, )
            error_list, school_detail = parse_response(status, school_details)
            if error_list:
                for error in error_list:
                    messages.add_message(request, messages.ERROR, error)

        program_detail_updated = update_record(school_detail, program_detail)
        context = {
            "programs": program_detail
        }

        return render(request, template_name=template, context=context)


@method_decorator(must_authenticate, name='dispatch')
class ListSubject(View):
    def get(self, request):
        template = 'admin_activities/list_subject.html'
        subject_url = 'institution/api/subject/'
        status, subject_details = make_request('get', subject_url, )
        error_list, subject_detail = parse_response(status, subject_details)
        if error_list:
            for error in error_list:
                messages.add_message(request, messages.ERROR, error)

        context = {
            "subjects": subject_detail
        }
        return render(request, template_name=template, context=context)


class ListCurrentStudent(View):
    def get(self, request):
        template = 'admin_activities/list_current_student.html'
        student_url = 'user/api/student/get_current_student/'
        student_detail_v = []
        status, student_details = make_request('get', student_url, )
        error_list, student_detail = parse_response(status, student_details)

        if error_list:
            for error in error_list:
                messages.add_message(request, messages.ERROR, error)
        else:
            program_url = 'institution/api/program/'
            status, program_details = make_request('get', program_url, )
            error_list, program_detail = parse_response(status, program_details)

            if error_list:
                for error in error_list:
                    messages.add_message(request, messages.ERROR, error)
            else:
                student_detail_v = combine_data_inclusive(student_detail, program_detail, "program_id", ("name",), ())

        context = {
            "record": student_detail_v
        }

        return render(request, template_name=template, context=context)