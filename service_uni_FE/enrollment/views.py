import json

from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View

from account.decorator import must_authenticate
from . import forms as f

from helpers.helper_functions import make_request, combine_data, combine_data_inclusive, combine_data_with_dict, \
    confirm_coe, parse_response


@method_decorator(must_authenticate, name='dispatch')
class EnrollmentView(View):
    def get(self, request):
        template = 'enrollment/enrollment_list.html'

        # Get session enrollment detail list
        enrollment_url = "enrollment/api/session_enrollment/"
        context = {}
        status, enrollment_data = make_request('get', enrollment_url)
        user_list = []
        enrollment_list = []
        if status and status == 200:
            status_code = enrollment_data["status_code"]
            if status_code == 200:
                enrollment_list = enrollment_data["data"]
            else:
                messages.add_message(request, messages.ERROR, f"Error {status_code} occurred!")
        else:
            messages.add_message(request, messages.ERROR, f"Error {status} occurred!")

        # Get Subject Enrolled detail list
        e_subject_list = []
        e_subject_url = "enrollment/api/subject_enrollment/list_record/"
        status, subject_data = make_request('get', e_subject_url)

        if status and status == 200:
            status_code = subject_data["status_code"]
            if status_code == 200:
                e_subject_list = subject_data["data"]
            else:
                messages.add_message(request, messages.ERROR, f"Error {status_code} occurred!")
        else:
            messages.add_message(request, messages.ERROR, f"Error {status} occurred!")

        # Get Subject List
        subject_list = []
        subject_url = "institution/api/subject/"
        status, subject_data = make_request('get', subject_url)

        if status and status == 200:
            status_code = subject_data["status_code"]
            if status_code == 200:
                subject_list = subject_data["data"]
            else:
                messages.add_message(request, messages.ERROR, f"Error {status_code} occurred!")
        else:
            messages.add_message(request, messages.ERROR, f"Error {status} occurred!")

        # Get users detail list
        user_url = "user/api/student/get_current_student/"
        status, user_data = make_request('get', user_url)
        if status and status == 200:
            status_code = user_data["status_code"]
            if status_code == 200:
                user_list = user_data["data"]
            else:
                messages.add_message(request, messages.ERROR, f"Error {status_code} occurred!")
        else:
            messages.add_message(request, messages.ERROR, f"Error {status} occurred!")

        # Get Program detail list
        program_list = []
        program_url = "institution/api/program/"
        status, program_data = make_request('get', program_url)
        if status and status == 200:
            status_code = program_data["status_code"]
            if status_code == 200:
                program_list = program_data["data"]
            else:
                messages.add_message(request, messages.ERROR, f"Error {status_code} occurred!")
        else:
            messages.add_message(request, messages.ERROR, f"Error {status} occurred!")

        session_enrollment_list = combine_data(
            enrollment_list,
            user_list,
            "student_id",
            ("first_name", "middle_name", "last_name", "program_id", "current_level", "u_id"),
            ("fee_paid",)
        )

        session_enrollment_list_updated = combine_data_inclusive(
            session_enrollment_list,
            program_list,
            "program_id",
            ("name", "code")
        )

        subject_enrolled_list = combine_data_inclusive(
            e_subject_list,
            user_list,
            "student_id",
            ("first_name", "middle_name", "last_name", "u_id", "current_level"),
            ("enrollment_status",)
        )

        subject_enrolled_list_updated = combine_data_inclusive(
            subject_enrolled_list,
            subject_list,
            "subject_id",
            ("name", "code")
        )

        context["session_enrollment"] = session_enrollment_list_updated
        context["subject_enrolled"] = subject_enrolled_list_updated
        return render(request, template_name=template, context=context)


@method_decorator(must_authenticate, name='dispatch')
class StudentEnrollmentView(View):
    def get(self, request):
        template = 'enrollment/enrollment_list.html'
        student_id = request.session.get('user_id', None)

        context = {}
        # Get user detail
        user_url = f"user/api/student/{student_id}"
        status, user_details = make_request('get', user_url)
        user_data = None
        if status and status == 200:
            status_code = user_details["status_code"]
            if status_code == 200:
                user_data = user_details["data"]

        # Get subject list
        subject_list = []
        subject_url = "institution/api/subject/"
        status, subject_data = make_request('get', subject_url)

        if status and status == 200:
            status_code = subject_data["status_code"]
            if status_code == 200:
                subject_list = subject_data["data"]

        # Get session enrollment detail list
        enrollment_url = "enrollment/api/subject_enrollment/show_user_enrollment/"
        status, enrollment_details = make_request('post', enrollment_url, {'student_id': student_id})
        user_enrollment_list = []
        if status == 200:
            status_code = enrollment_details["status_code"]
            if status_code in [200, 201]:
                user_enrollment = enrollment_details["data"]

                user_enrollment_list = combine_data_with_dict(
                    user_enrollment,
                    subject_list,
                    "subject_id",
                    user_data,
                    ("first_name", "middle_name", "last_name", "current_level"),
                    ("name", "code")
                )
        context["subject_enrolled"] = user_enrollment_list
        return render(request, template_name=template, context=context)

    def post(self, request):
        student_id = request.session.get('user_id')
        if 'withdraw' in request.POST:
            enrollment_id = request.POST['withdraw']
            subject_id = request.POST['subject_id']

            withdraw_url = f"enrollment/api/subject_enrollment/{enrollment_id}/withdraw_from_course/"

            status, enrollment_details = make_request('patch', withdraw_url)
            error_list, enrollment_detail = parse_response(status, enrollment_details)

            if error_list:
                for error in error_list:
                    messages.add_message(request, messages.ERROR, error)
            else:
                user_url = f'user/api/student/{student_id}/update_user_courses/'
                request_json = {
                    "current_enrolled_courses": subject_id,
                    "operation": "remove",
                }
                status, make_request('patch', user_url, request_json)
                messages.add_message(request, messages.WARNING, "Withdrawn Successfully!")
        elif 'enroll' in request.POST:

            enrollment_id = request.POST["enrollment_id"]
            subject_id = request.POST['subject_id']
            request_json = {
                "enrollment_id": enrollment_id,
                "update": "update",
            }
            withdraw_url = "enrollment/api/subject_enrollment/enroll_to_course/"

            status, enrollment_details = make_request('post', withdraw_url, request_json)
            error_list, enrollment_detail = parse_response(status, enrollment_details)

            if error_list:
                for error in error_list:
                    messages.add_message(request, messages.ERROR, error)
            else:
                user_url = f'user/api/student/{student_id}/update_user_courses/'
                request_json = {
                    "current_enrolled_courses": subject_id,
                    "operation": "add",
                }
                status, make_request('patch', user_url, request_json)
                messages.add_message(request, messages.WARNING, "Enrolled Successfully!")
        return redirect(self.request.META.get('HTTP_REFERER'))


@method_decorator(must_authenticate, name='dispatch')
class SubjectEnrollment(View):
    def get(self, request):
        template = 'enrollment/subject_enrollment.html'
        enrollment_form = f.SubjectEnrollmentForm()
        context = {
            "enrollment_form": enrollment_form
        }
        return render(request, template_name=template, context=context)

    def post(self, request):
        enrollment_form = f.SubjectEnrollmentForm(request.POST)
        if enrollment_form.is_valid():
            student_id = request.session.get('user_id', None)
            user_type = request.session.get('user_type', None)
            if user_type and user_type == "STUDENT":
                # Make API call to know if user is not enrolled in the course already
                enrolled_subjects_url = "enrollment/api/subject_enrollment/show_user_enrollment/"
                status, enrolled_subject_details = make_request('post', enrolled_subjects_url, {'student_id': student_id})
                error_list, enrolled_subject_data = parse_response(status, enrolled_subject_details)
                if error_list:
                    for error in error_list:
                        messages.add_message(request, messages.ERROR, error)
                    return redirect(self.request.META.get('HTTP_REFERER'))
                else:
                    if enrolled_subject_data:
                        messages.add_message(request, messages.WARNING, "Already Enrolled!")
                        return redirect(self.request.META.get('HTTP_REFERER'))
                    else:
                        data = enrollment_form.cleaned_data
                        data["student_id"] = student_id
                        session_id = data["session_id"]
                        subject_id = data["subject_id"]

                        # Check Student Eligibility

                        # Make API calls to the user service to get the user details and the institution details

                        user_detail_endpoint = f'user/api/student/{student_id}/'
                        status, user_details = make_request('get', user_detail_endpoint)

                        error_list, user_data = parse_response(status, user_details)
                        if not error_list:
                            user_coe = user_data["coe"]
                            user_u_id = user_data["u_id"]
                            user_type = user_data["student_type"]
                            user_institution_id = user_data["institution_id"]
                            user_program_id = user_data["program_id"]

                            # Make API calls to the Institution service to get the program details
                            program_endpoint = f'institution/api/program/{user_program_id}'
                            status, program_details = make_request('get', program_endpoint)
                            error_list, program_data = parse_response(status, program_details)

                            if not error_list:
                                # Check if student has COE and it is valid
                                confirm_user_coe = confirm_coe(user_coe, user_type, program_data["code"], user_u_id)
                                if not confirm_user_coe:
                                    messages.add_message(request, messages.ERROR, "Student COE cannot be verified!")
                                    return redirect(self.request.META.get('HTTP_REFERER'))

                                # Make API calls to the Institution service to get the institution details
                                uni_endpoint = f'institution/api/institution/{user_institution_id}'
                                status, uni_details = make_request('get', uni_endpoint)
                                error_list, uni_data = parse_response(status, uni_details)

                                if not error_list:
                                    current_session = uni_data["current_session"]
                                    current_session = current_session["id"]

                                    if int(current_session) == int(session_id):
                                        # Make API calls to the Enrollment service to get the session enrollment status

                                        s_enrollment_endpoint = f'enrollment/api/session_enrollment/'
                                        status, s_enrollment_details = make_request('get', s_enrollment_endpoint)
                                        error_list, s_enrollment_data = parse_response(status, s_enrollment_details)

                                        if not error_list:
                                            session_data = None
                                            for enroll_data in s_enrollment_data:
                                                if enroll_data["student_id"] == student_id and int(current_session) == \
                                                        enroll_data['session_id']:
                                                    session_data = enroll_data

                                            if session_data:
                                                if not session_data["fee_paid"]:
                                                    messages.add_message(request, messages.ERROR,
                                                                         "You cannot enroll into this session without paying school fees!")
                                                    return redirect(self.request.META.get('HTTP_REFERER'))
                                            else:
                                                messages.add_message(request, messages.ERROR,
                                                                     "Please complete session enrollment first!")
                                                return redirect(self.request.META.get('HTTP_REFERER'))

                                            # Check for prerequisite
                                            # get the subject details
                                            subject_endpoint = f'institution/api/subject/{subject_id}/'
                                            status, subject_details = make_request('get', subject_endpoint)
                                            error_list, subject_data = parse_response(status, subject_details)
                                            if not error_list:
                                                subject_prerequisites = subject_data["prerequisite_subjects"]

                                                # Make API call to get student's enrollment history
                                                subject_enrollment_endpoint = "enrollment/api/subject_enrollment/show_user_enrollment/"
                                                status, subject_enrollment_details = make_request('post',
                                                                                                  subject_enrollment_endpoint,
                                                                                                  {'student_id': student_id})

                                                error_list, subject_enrollment_data = parse_response(status,
                                                                                                     subject_enrollment_details)

                                                if not error_list:

                                                    if subject_prerequisites:
                                                        prerequisites_cleared = False
                                                        for enrollment_record in subject_enrollment_data:
                                                            if enrollment_record["subject_id"] in subject_prerequisites:
                                                                prerequisites_cleared = True
                                                    else:
                                                        prerequisites_cleared = True

                                                    if prerequisites_cleared:
                                                        # Submit enrollment request
                                                        subject_enrollment_endpoint = "enrollment/api/subject_enrollment/enroll_to_course/"
                                                        status, enroll_to_course = make_request(
                                                            'post',
                                                            subject_enrollment_endpoint,
                                                            data
                                                        )
                                                        error_list, subject_enrollment_data = parse_response(status,
                                                                                                             enroll_to_course)
                                                        if not error_list:
                                                            # Update User detail with the enrolment record
                                                            user_url = f'user/api/student/{student_id}/update_user_courses/'
                                                            request_json = {
                                                                "current_enrolled_courses": subject_enrollment_data["id"],
                                                                "operation": "add",
                                                            }
                                                            status, make_request('patch', user_url, request_json)
                                                            messages.add_message(request, messages.SUCCESS,
                                                                                 "Enrollment Successful")
                                                            return redirect(self.request.META.get('HTTP_REFERER'))
                                                        else:
                                                            for error in error_list:
                                                                messages.add_message(request, messages.ERROR, error)
                                                            return redirect(self.request.META.get('HTTP_REFERER'))
                                                    else:
                                                        messages.add_message(request, messages.ERROR,
                                                                             "Please clear prerequisites!")
                                                        return redirect(self.request.META.get('HTTP_REFERER'))
                                                else:
                                                    for error in error_list:
                                                        messages.add_message(request, messages.ERROR, error)
                                                        return redirect(self.request.META.get('HTTP_REFERER'))
                                            for error in error_list:
                                                messages.add_message(request, messages.ERROR, error)
                                                return redirect(self.request.META.get('HTTP_REFERER'))
                                        else:
                                            for error in error_list:
                                                messages.add_message(request, messages.ERROR, error)
                                            return redirect(self.request.META.get('HTTP_REFERER'))
                                    else:
                                        messages.add_message(request, messages.ERROR, "You cannot enroll in past sessions!")
                                        return redirect(self.request.META.get('HTTP_REFERER'))
                                else:
                                    for error in error_list:
                                        messages.add_message(request, messages.ERROR, error)
                                    return redirect(self.request.META.get('HTTP_REFERER'))
                            else:
                                for error in error_list:
                                    messages.add_message(request, messages.ERROR, error)
                                return redirect(self.request.META.get('HTTP_REFERER'))
                        else:
                            for error in error_list:
                                messages.add_message(request, messages.ERROR, error)
                            return redirect(self.request.META.get('HTTP_REFERER'))
            else:
                messages.add_message(request, messages.ERROR, "You must be a student to enroll!")
                return redirect(self.request.META.get('HTTP_REFERER'))
        else:
            if enrollment_form.errors:
                for field in enrollment_form:
                    for error in field.errors:
                        messages.add_message(request, messages.ERROR, f"{field.label} - {error}")
            return redirect(self.request.META.get('HTTP_REFERER'))


@method_decorator(must_authenticate, name='dispatch')
class SessionEnrollment(View):
    def get(self, request):
        template = 'enrollment/session_enrollment.html'
        session_enrollment_form = f.SessionEnrollmentForm()
        enrollment_detail = None
        user_id = request.session.get('user_id')
        # get student detail
        user_url = f'user/api/student/{user_id}/'
        status, user_details = make_request('get', user_url)
        error_list, user_detail = parse_response(status, user_details)
        if error_list:
            for error in error_list:
                messages.add_message(request, messages.ERROR, error)
        else:
            institution_id = user_detail['institution_id']

            # Get current session id
            institution_url = f"institution/api/institution/{institution_id}/"
            status, institution_details = make_request('get', institution_url)
            error_list, institution_detail = parse_response(status, institution_details)
            if error_list:
                for error in error_list:
                    messages.add_message(request, messages.ERROR, error)
            else:
                current_session_id = institution_detail['current_session']['id']
                request_json = {'student_id': user_id, 'session_id': current_session_id}
                session_enroll_record_url = 'enrollment/api/session_enrollment/get_student_enrollment/'
                status, enrollment_details = make_request('get', session_enroll_record_url, request_json)

                error_list, enrollment_detail = parse_response(status, enrollment_details)

        context = {
            "session_enrollment_form": session_enrollment_form,
            "enrollment_detail": enrollment_detail,
        }
        return render(request, template_name=template, context=context)

    def post(self, request):
        if 'enrollment' in request.POST:
            subject_enrollment_form = f.SessionEnrollmentForm(request.POST)
            if subject_enrollment_form.is_valid():
                request_json = subject_enrollment_form.cleaned_data

                session_enroll_url = 'enrollment/api/session_enrollment/'
                status, enrollment_details = make_request('post', session_enroll_url, request_json)
                error_list, enrollment_detail = parse_response(status, enrollment_details)
                if error_list:
                    for error in error_list:
                        messages.add_message(request, messages.ERROR, error)
                else:
                    messages.add_message(request, messages.SUCCESS, "Enrollment Successful! Please make payment to start enrolling for subjects!")

                return redirect('enrollment:session_enrollment')

            else:
                if subject_enrollment_form.errors:
                    for field in subject_enrollment_form:
                        for error in field.errors:
                            messages.add_message(request, messages.ERROR, f"{field.label} - {error}")
        elif 'make_payment' in request.POST:
            enrollment_id = request.POST.get('enrollment_id')
            payment_url = f'enrollment/api/session_enrollment/{enrollment_id}/pay_fee/'
            request_json = {'fee_paid': True}
            status, enrollment_details = make_request('patch', payment_url, request_json)
            error_list, enrollment_detail = parse_response(status, enrollment_details)
            if error_list:
                for error in error_list:
                    messages.add_message(request, messages.ERROR, error)
            else:
                messages.add_message(request, messages.SUCCESS, "Payment Completed! Please proceed to enroll in courses!")

        return redirect(self.request.META.get('HTTP_REFERER'))
