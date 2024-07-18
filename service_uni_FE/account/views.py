import json

import requests
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View

from helpers.helper_functions import make_request, parse_response, get_program_school, combine_data_inclusive, \
    combine_data, generate_email, generate_coe, user_subject_program_combine
from . import forms as f
from .decorator import watch_login, must_authenticate


def page_tester(request):
    template = 'account/.html'
    return render(request, template_name=template, context={})


def home(request):
    template = 'account/index.html'
    institution_url = "http://service_uni_api_gateway:8000/institution/api/institution/"
    institution_url2 = "http://localhost:8000/institution/api/institution"
    institution_data = requests.get(institution_url)
    context = {
        "institution_data": institution_data
    }
    return render(request, template_name=template, context=context)


class Login(View):
    def get(self, request):
        refresh_token = request.session.get("refresh_token", None)
        user_type = request.session.get("user_type", None)
        user_id = request.session.get("user_id", None)
        status = watch_login(refresh_token)
        if not status and user_type and user_id:
            if user_type == "STUDENT":
                return redirect("account:student_home")

            elif user_type == "ADMIN":
                return redirect("account:admin_home")

            elif user_type == "STAFF":
                return redirect("account:staff_home")

        template = 'account/login.html'
        login_form = f.LoginForm()
        context = {
            "login_form": login_form
        }
        return render(request, template_name=template, context=context)

    def post(self, request):
        login_form = f.LoginForm(request.POST)
        if login_form.is_valid():
            request_json = json.dumps(login_form.cleaned_data)
            user_url = "user/api/auth/login_user/"
            status, user_details = make_request('post', user_url, request_json)

            if status == 200:
                status_code = user_details["status_code"]
                if status_code and status_code == 200:
                    user_detail = user_details["data"]
                    user_id = user_detail['id']
                    request.session['user_id'] = user_id
                    request.session['access_token'] = user_detail["token"]["access"]
                    request.session['refresh_token'] = user_detail["token"]["refresh"]
                    request.session['user_type'] = user_detail["user_type"]
                    request.session['institution_id'] = user_detail["institution_id"]

                    if user_detail.get("user_type") == "STUDENT":
                        return redirect("account:student_home")

                    elif user_detail.get("user_type") == "ADMIN":
                        return redirect("account:admin_home")

                    elif user_detail.get("user_type") == "STAFF":
                        return redirect("account:staff_home")
                    else:
                        messages.add_message(request, messages.ERROR, f"User type error")
                        return redirect(self.request.META.get('HTTP_REFERER'))
                else:
                    messages.add_message(request, messages.ERROR, f"Error {status_code} occurred!")
                    return redirect(self.request.META.get('HTTP_REFERER'))
            else:
                messages.add_message(request, messages.ERROR, f"Error {status} occurred!")
                return redirect(self.request.META.get('HTTP_REFERER'))
        else:
            return redirect(self.request.META.get('HTTP_REFERER'))


@method_decorator(must_authenticate, name='dispatch')
class StudentHome(View):
    def get(self, request):
        template = 'account/student_index.html'
        student_id = request.session.get('user_id')
        user_url = f"user/api/student/{student_id}/"
        status, student_details = make_request("get", user_url)
        error_list, student_detail = parse_response(status, student_details)
        student_data = None
        if error_list:
            for error in error_list:
                messages.add_message(request, messages.ERROR, error)
        else:
            program_url = "institution/api/program/"
            status, program_details = make_request('get', program_url)
            error_list, program_detail = parse_response(status, program_details)
            if error_list:
                for error in error_list:
                    messages.add_message(request, messages.ERROR, error)
            else:
                student_data = user_subject_program_combine(student_detail, program_detail, [])

        context = {
            "student_detail": student_data
        }

        return render(request, template_name=template, context=context)

    def post(self, request):
        ...


@method_decorator(must_authenticate, name='dispatch')
class StaffHome(View):
    def get(self, request):
        template = 'account/staff_index.html'
        staff_id = request.session.get('user_id')
        user_url = f"user/api/service_user/{staff_id}/"
        status, staff_details = make_request("get", user_url)
        error_list, staff_detail = parse_response(status, staff_details)

        institution_id = staff_detail["institution_id"]
        institution_url = f'institution/api/institution/{institution_id}'
        status, institution_details = make_request('get', institution_url)
        error_list, institution_detail = parse_response(status, institution_details)
        if error_list:
            for error in error_list:
                messages.add_message(request, messages.ERROR, error)

        context = {
            "staff_detail": staff_detail,
            "institution_detail": institution_detail,
        }

        return render(request, template_name=template, context=context)

    def post(self, request):
        ...


@method_decorator(must_authenticate, name='dispatch')
class AdminHome(View):
    def get(self, request):
        template = 'account/admin_index.html'
        admin_id = request.session.get('user_id')
        user_url = f"user/api/service_user/{admin_id}/"
        status, admin_details = make_request('get', user_url)
        error_list, admin_detail = parse_response(status, admin_details)

        institution_id = admin_detail['institution_id']
        institution_url = f'institution/api/institution/{institution_id}'
        status, institution_details = make_request('get', institution_url)
        error_list, institution_detail = parse_response(status, institution_details)
        if error_list:
            for error in error_list:
                messages.add_message(request, messages.ERROR, error)
        context = {
            "admin_detail": admin_detail,
            "institution_detail": institution_detail,
        }

        return render(request, template_name=template, context=context)

    def post(self, request):
        ...


@method_decorator(must_authenticate, name='dispatch')
class CreateAccount(View):
    def get(self, request):
        template = 'account/create_account.html'
        account_form = f.CreateAccountForm()
        context = {
            "account_form": account_form
        }
        return render(request, template_name=template, context=context)

    def post(self, request):
        account_form = f.CreateAccountForm(request.POST)
        if account_form.is_valid():
            # request_data = json.loads(json.dumps(account_form.cleaned_data))
            request_data = account_form.cleaned_data
            request_data['institution_id'] = request.session.get('institution_id')
            user_url = "user/api/service_user/create_staff_account/"
            status, user_details = make_request('post', user_url, request_data)
            if status in [200, 201]:
                status_code = user_details["status_code"]
                if status_code in [200, 201]:
                    messages.add_message(request, messages.SUCCESS, f"Account Created!")
                    return redirect(self.request.META.get('HTTP_REFERER'))
                else:
                    messages.add_message(request, messages.ERROR, f"Error {status_code} occurred!")
                    return redirect(self.request.META.get('HTTP_REFERER'))
            else:
                messages.add_message(request, messages.ERROR, f"Error {status} occurred!")
                return redirect(self.request.META.get('HTTP_REFERER'))
        else:
            if account_form.errors:
                for field in account_form:
                    for error in field.errors:
                        messages.add_message(request, messages.ERROR, f"{field.label} - {error}")
            return redirect(self.request.META.get('HTTP_REFERER'))


class Register(View):
    def get(self, request):
        template = 'account/register.html'
        register_form = f.RegisterForm()
        context = {
            'register_form': register_form
        }

        return render(request, template_name=template, context=context)

    def post(self, request):
        register_form = f.RegisterForm(request.POST)
        if register_form.is_valid():
            request_data = json.loads(json.dumps(register_form.cleaned_data))
            user_data = {
                "first_name": request_data.pop("first_name"),
                "middle_name": request_data.pop("middle_name"),
                "last_name": request_data.pop("last_name"),
                "email": request_data.pop("email"),
                "password": request_data.pop("password"),
                "user_type": "ADMIN"
            }

            user_request_data = json.dumps(user_data)
            user_url = "user/api/service_user/create_admin_account/"
            status, user_details = make_request('post', user_url, user_request_data)

            if status == 200:
                status_code = user_details["status_code"]
                if status_code and status_code in [200, 201]:
                    user_detail = user_details["data"]
                    user_id = user_detail['id']

                    institution_data = {
                        "name": request_data.pop("institution_name"),
                        "admin_user_id": user_id,
                        "email_domain": request_data.pop("email_domain"),
                        "website": request_data.pop("website"),
                        "street_address": request_data.pop("street_address"),
                        "city": request_data.pop("city"),
                        "state": request_data.pop("state"),
                        "country": request_data.pop("country"),
                    }
                    institution_data = json.dumps(institution_data)
                    institution_url = "institution/api/institution/"
                    status, institution_details = make_request('post', institution_url, institution_data)

                    if status == 200:
                        status_code = institution_details["status_code"]
                        if status_code and status_code in [200, 201]:
                            institution_detail = institution_details["data"]

                            # Update institution ID for the user
                            url = f"user/api/service_user/{user_id}/update_service_user_account/"
                            make_request('patch', url, {'institution_id': institution_detail['id']})

                            if user_detail.get("user_type") == "STUDENT":
                                return redirect("account:student_home")
                            elif user_detail.get("user_type") == "ADMIN":
                                return redirect("account:admin_home")
                            elif user_detail.get("account:user_type") == "STAFF":
                                return redirect("account:staff_home")
                            else:
                                messages.add_message(request, messages.ERROR, f"User type error")
                                return redirect(self.request.META.get('HTTP_REFERER'))
                        else:
                            messages.add_message(request, messages.ERROR, f"Error {status_code} occurred!")
                            return redirect(self.request.META.get('HTTP_REFERER'))
                    else:
                        messages.add_message(request, messages.ERROR, f"Error {status} occurred!")
                        return redirect(self.request.META.get('HTTP_REFERER'))
                else:
                    messages.add_message(request, messages.ERROR, f"Error {status_code} occurred!")
                    return redirect(self.request.META.get('HTTP_REFERER'))
            else:
                messages.add_message(request, messages.ERROR, f"Error {status} occurred!")
                return redirect(self.request.META.get('HTTP_REFERER'))
        else:
            if register_form.errors:
                for field in register_form:
                    for error in field.errors:
                        messages.add_message(request, messages.ERROR, f"{field.label} - {error}")
            return redirect(self.request.META.get('HTTP_REFERER'))


class ApplyForAdmission(View):
    def get(self, request):
        template = 'account/apply_for_admission.html'
        admission_form = f.AdmissionForm()
        context = {
            'admission_form': admission_form
        }

        return render(request, template_name=template, context=context)

    def post(self, request):
        admission_form = f.AdmissionForm(request.POST)
        if admission_form.is_valid():
            admission_url = 'user/api/student/apply_for_admission/'
            request_json = admission_form.cleaned_data
            contact_phone = request_json.pop('contact_phone')
            contact_phone_v = {
                "phone_contact": contact_phone,
                "phone_type": "MOBILE"
            }

            request_json['contact_phone'] = contact_phone_v

            dob = request_json.pop('date_of_birth')
            dob_str = dob.strftime("%Y-%m-%d")
            dob_str = json.dumps(dob_str)
            request_json['date_of_birth'] = json.loads(dob_str)
            program_id = request_json['program_id']

            school_url = 'institution/api/school/'
            status, school_details = make_request('get', school_url, )
            error_list, school_detail = parse_response(status, school_details)

            school = get_program_school(program_id, school_detail)
            request_json['school_id'] = school['id']
            request_json['institution_id'] = 1

            status, admission_details = make_request('post', admission_url, request_json)
            error_list, admission_detail = parse_response(status, admission_details)
            if error_list:
                for error in error_list:
                    messages.add_message(request, messages.ERROR, error)
            else:
                messages.add_message(request, messages.SUCCESS, "Application submitted successfully")
            return redirect(self.request.META.get('HTTP_REFERER'))
        else:
            if admission_form.errors:
                for field in admission_form:
                    for error in field.errors:
                        messages.add_message(request, messages.ERROR, f"{field.label} - {error}")
            return redirect(self.request.META.get('HTTP_REFERER'))


class AdmissionView(View):
    def get(self, request):
        template = 'account/admission_list.html'
        student_url = 'user/api/student/get_future_students/'
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

    def post(self, request):
        student_id = request.POST.get('student_id')

        if 'grant_admission' in request.POST:

            user_program_id = request.POST.get('program_id')
            student_u_id = request.POST.get('student_u_id')
            student_type = request.POST.get('student_type')
            institution_id = request.POST.get('institution_id')
            # generate COE and Email
            program_code = None
            program_url = f'institution/api/program/{user_program_id}'
            status, program_details = make_request('get', program_url, )
            error_list, program_detail = parse_response(status, program_details)
            if error_list:
                for error in error_list:
                    messages.add_message(request, messages.ERROR, error)
            else:
                program_code = program_detail["code"]

            # make an API call to get the UNI data
            institution_domain = None
            institution_url = f'institution/api/institution/{institution_id}'
            status, institution_details = make_request('get', institution_url)
            error_list, institution_detail = parse_response(status, institution_details)
            if error_list:
                for error in error_list:
                    messages.add_message(request, messages.ERROR, error)
            else:
                institution_domain = institution_detail["email_domain"]

            if institution_domain and program_code:
                email = generate_email(student_u_id, institution_domain)
                coe = generate_coe(student_type, program_code, student_u_id)

                # make call to update student details
                request_json = {
                    'email': email,
                    'coe': coe,
                    'student_status': 'CURRENT_STUDENT',
                    'current_level': 100
                }
                grant_admission_url = f'user/api/student/{student_id}/grant_admission/'
                status, user_details = make_request('patch', grant_admission_url, request_json)
                print(status, user_details, flush=True)
                error_list, user_detail = parse_response(status, user_details)

                if error_list:
                    for error in error_list:
                        messages.add_message(request, messages.ERROR, error)
                else:
                    messages.add_message(request, messages.SUCCESS, "Admission granted!")
        elif 'soft_grant_admission' in request.POST:

            soft_grant_admission_url = f'user/api/student/{student_id}/soft_grant_admission/'
            request_json = {
                'program_approval': True,
                'soft_approval': "APPROVED",
            }
            status, user_details = make_request('patch', soft_grant_admission_url, request_json)
            error_list, user_detail = parse_response(status, user_details)

            if error_list:
                for error in error_list:
                    messages.add_message(request, messages.ERROR, error)
            else:
                messages.add_message(request, messages.SUCCESS, "Soft Admission Granted!")
        else:
            request_json = {
                'student_status': 'DENIED'
            }
            deny_admission_url = f'user/api/student/{student_id}/deny_admission/'
            status, user_details = make_request('patch', deny_admission_url, request_json)
            error_list, user_detail = parse_response(status, user_details)

            if error_list:
                for error in error_list:
                    messages.add_message(request, messages.ERROR, error)
            else:
                messages.add_message(request, messages.WARNING, "Admission rejected!")

        return redirect(self.request.META.get('HTTP_REFERER'))


class ProfileView(View):
    def get(self, request):
        template = 'account/profile.html'
        user_id = request.session.get("user_id")
        institution_id = request.session.get("institution_id")
        injected_user_detail = None
        # get user details
        user_url = f'user/api/service_user/{user_id}/'
        status, user_details = make_request('get', user_url)
        error_list, user_detail = parse_response(status, user_details)
        if error_list:
            for error in error_list:
                messages.add_message(request, messages.ERROR, error)
        else:
            institution_url = f'institution/api/institution/{institution_id}'
            status, institution_details = make_request('get', institution_url)
            error_list, institution_detail = parse_response(status, institution_details)
            if error_list:
                for error in error_list:
                    messages.add_message(request, messages.ERROR, error)
            program_url = "institution/api/program/"
            status, program_details = make_request('get', program_url)
            error_list, program_detail = parse_response(status, program_details)
            if error_list:
                for error in error_list:
                    messages.add_message(request, messages.ERROR, error)
            else:
                subject_url = "institution/api/subject/"
                status, subject_details = make_request('get', subject_url)
                error_list, subject_detail = parse_response(status, subject_details)
                if error_list:
                    for error in error_list:
                        messages.add_message(request, messages.ERROR, error)

                injected_user_detail = user_subject_program_combine(user_detail, program_detail, subject_detail)

        context = {
            "user_detail": injected_user_detail,
            "institution_detail": institution_detail,
        }
        return render(request, template_name=template, context=context)


def logout(request):
    request.session["user_id"] = None
    request.session["access_token"] = None
    request.session["refresh_token"] = None
    request.session["user_type"] = None

    return redirect('account:login')
