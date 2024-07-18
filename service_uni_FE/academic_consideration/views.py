import json

import requests
from django.contrib import messages
from django.shortcuts import render,redirect
from django.views import View

from helpers.helper_functions import make_request, \
    parse_response, combine_and_remove_keys, combine_lists_2
from . import forms as f

class AcademicConsiderationView(View):
    def get(self, request):
        template = 'academic_consideration/application_list.html'
        print("getting data....", flush=True)
        context = {}
        a_applications_list = []

        # Get application list
        a_consideration_url = "academic_consideration/api/AcademicConsideration/"
        status, all_list = make_request('GET', a_consideration_url)

        list_ac = []
        if status and status == 200:
            status_code = all_list["status_code"]
            if status_code == 200:
                list_ac = all_list["data"]
        print(f"ac list {list_ac}", flush=True)

        # Get subject list
        subject_list = []
        subject_list = getsubjlist()
        print(f"subject list {subject_list}", flush=True)

        # Get users detail list
        user_list = []
        user_url = "user/api/student/get_current_student/"
        status, user_data = make_request('get', user_url)

        if status and status == 200:
            status_code = user_data["status_code"]
            if status_code == 200:
                user_list = user_data["data"]
                print(f"user list {user_list}", flush=True)

                ac_subject_combine = combine_and_remove_keys(
                    list_ac,
                    subject_list,
                    user_list
                )

            else:
                messages.add_message(request, messages.ERROR, f"Error {status_code} occurred!")
        else:
            messages.add_message(request, messages.ERROR, f"Error {status} occurred!")

        print(f"ac_subject_user_combine {ac_subject_combine}", flush=True)
        context["list_applications"] = ac_subject_combine
        return render(request, template_name=template, context=context)

class AcademicConsiderationStudentView(View):
    def get(self, request):
        template = 'academic_consideration/user_application_list.html'

        context = {}

        # Get subject list
        subject_list = []
        subject_list = getsubjlist()

        # Get Application list
        a_applications_list = []
        student_id = request.session.get('user_id', None)
        a_consideration_url = "academic_consideration/api/AcademicConsideration/show_user_applications/"
        status, application_details = make_request('POST',
                                                          a_consideration_url,
                                                          {'student_id': student_id})
        list_ac = []
        if status and status == 200:
            status_code = application_details["status_code"]
            if status_code == 200:
                list_ac = application_details["data"]
                a_applications_list = combine_lists_2(
                    list_ac,
                    subject_list,
                    "subject_id",
                    "id"
                )
                print(f"a_applications_list combined {a_applications_list}", flush=True)
            else:
                messages.add_message(request, messages.ERROR, f"Error {status_code} occurred!")
        else:
            messages.add_message(request, messages.ERROR, f"Error {status} occurred!")

        context["list_applications"] = a_applications_list
        return render(request, template_name=template, context=context)

class CreateAcademicConsideration(View):
    def get(self, request):
        template = 'academic_consideration/create_academic_consideration.html'
        create_ac_form = f.CreateAcademicConsiderationForm()
        context = {
            'create_ac_form': create_ac_form
        }

        return render(request, template_name=template, context=context)

class ApprovalDetailsAcademicConsideration(View):
    def get(self, request, id):
        template = 'academic_consideration/approval_academic_consideration.html'

        ac_data = getacdetails(id)
        ac_data_form = f.CreateAcademicConsiderationForm({
            "ac_from": ac_data["ac_from"],
            "ac_to": ac_data["ac_to"],
            "subject_id": ac_data["subject_id"],
            "assessment_item_affected": ac_data["assessment_item_affected"],
            "assessment_type": ac_data["assessment_type"],
            "weight": ac_data["weight"],
            "group_work": ac_data["group_work"],
            "due_date": ac_data["due_date"],
            "subject_coordinator": ac_data["subject_coordinator"],
            "nature_of_assistance": ac_data["nature_of_assistance"],
            "status": ac_data["status"],
            "comment": ac_data["comment"]
        })

        context = {
            'update_ac_form': ac_data_form,
            'id': id,
            'status' : str(ac_data["status"]),
            'student_id': ac_data["student_id"]
        }

        return render(request, template_name=template, context=context)

class DetailsAcademicConsideration(View):
    def get(self, request, id):
        template = 'academic_consideration/details_academic_consideration.html'
        ac_data = getacdetails(id)

        ac_data_form = f.CreateAcademicConsiderationForm({
            "student_id" : ac_data["student_id"],
            "ac_from": ac_data["ac_from"],
            "ac_to" : ac_data["ac_to"],
            "subject_id": ac_data["subject_id"],
            "assessment_item_affected": ac_data["assessment_item_affected"],
            "assessment_type": ac_data["assessment_type"],
            "weight": ac_data["weight"],
            "group_work": ac_data["group_work"],
            "due_date": ac_data["due_date"],
            "subject_coordinator": ac_data["subject_coordinator"],
            "nature_of_assistance": ac_data["nature_of_assistance"],
            "status": ac_data["status"],
            "comment": ac_data["comment"]
        })

        status_update = ac_data["status"]

        context = {
            'update_ac_form': ac_data_form,
            'status' : status_update,
            'id' : id,
            'student_id': ac_data["student_id"]
        }

        return render(request, template_name=template, context=context)

class StudentAcademicConsiderationView(View):
    def get(self, request, pk):
        template = 'academic_consideration/create_academic_consideration.html'
        student_id = 1

        context = {}

        # Get session enrollment detail list
        academic_cons_details = []
        academic_consideration_url = "academic_consideration/api/academic_consideration/show_user_applications/"

        context["list_user_applications"] = academic_cons_details

        return render(request, template_name=template, context=context)

    def post(self, request):
        application_form = f.CreateAcademicConsiderationForm(request.POST)
        if application_form.is_valid():
            request_data = json.loads(json.dumps(application_form.cleaned_data))

            application_data = {
                "student_id" : request_data.pop("student_id"),
                "ac_from": request_data.pop("ac_from"),
                "ac_to": request_data.pop("ac_to"),
                "subject_id": request_data.pop("subject_id"),
                "assessment_item_affected": request_data.pop("assessment_item_affected"),
                "assessment_type": request_data.pop("assessment_type"),
                "weight":  request_data.pop("weight"),
                "group_work": request_data.pop("group_work"),
                "due_date": request_data.pop("due_date"),
                "subject_coordinator": request_data.pop("subject_coordinator"),
                "nature_of_assistance": request_data.pop("nature_of_assistance"),
                "nature_assistance_date": request_data.pop("nature_of_assistance_date"),
                "status": "LEVEL1_PENDING",
                "comment": "N/A" if len(request_data.pop("comment")) == 0 else request_data.pop("comment")
            }

            ac_url = "academic_consideration/api/AcademicConsideration/"
            status, ac_details = make_request('post', ac_url, application_data)
            if status in [200, 201]:
                status_code = ac_details["status_code"]
                if status_code in [200, 201]:
                    messages.add_message(request, messages.SUCCESS, f"Academic Consideration Application Created!")
                    return redirect(self.request.META.get('HTTP_REFERER'))
                else:
                    messages.add_message(request, messages.ERROR, f"Error {status_code} occurred!")
                    return redirect(self.request.META.get('HTTP_REFERER'))
            else:
                messages.add_message(request, messages.ERROR, f"Error {status} occurred!")
                return redirect(self.request.META.get('HTTP_REFERER'))
            return redirect(self.request.META.get('HTTP_REFERER'))
        else:
            if application_form.errors:
                for field in application_form:
                    for error in field.errors:
                        messages.add_message(request, messages.ERROR, f"{field.label} - {error}")
            return redirect(self.request.META.get('HTTP_REFERER'))

class AcademicConsiderationUpdateStatusView(View):

    def get(self):
        ...

    def post(self, request):
        application_form = f.CreateAcademicConsiderationForm(request.POST)

        if application_form.is_valid():

            request_data = json.loads(json.dumps(application_form.cleaned_data))
            application_id = request_data["id"]

            user_type = request.session.get('user_type', None)
            if user_type and user_type == "STUDENT" and request_data["status"] == "REQUEST_INFO":
                request_data["status"] = "LEVEL1_PENDING"
            elif user_type and user_type and user_type != "STUDENT":
                statusChk = request_data["status"]
                if statusChk == "Approve":
                    request_data["status"] = "LEVEL1_APPROVED"
                elif statusChk == "Reject":
                    request_data["status"] = "LEVEL1_DECLINED"
                elif statusChk == "Request Info":
                    request_data["status"] = "REQUEST_INFO"
                elif statusChk == "Grant":
                    request_data["status"] = "LEVEL2_APPROVED"
                elif statusChk == "Deny":
                    request_data["status"] = "LEVEL2_DECLINED"

            if len(request_data.pop("nature_of_assistance_date")) == 0:
                request_data["nature_of_assistance_date"] = None

            request_data["group_work"] = str(request_data.pop("group_work"))
            update_url = "academic_consideration/api/AcademicConsideration/" + str(application_id)

            print(f"request data for approval {request_data}", flush=True)
            status, ac_details = make_request('put', update_url, request_data)
            if status in [200, 201]:
                status_code = ac_details["status_code"]
                if status_code in [200, 201]:
                    messages.add_message(request, messages.SUCCESS, f"Approval Status Updated!")
                    return redirect(self.request.META.get('HTTP_REFERER'))
                else:
                    messages.add_message(request, messages.ERROR, f"Error {status_code} occurred!")
                    return redirect(self.request.META.get('HTTP_REFERER'))
            else:
                messages.add_message(request, messages.ERROR, f"Error {status} occurred!")
                return redirect(self.request.META.get('HTTP_REFERER'))
        else:
            if application_form.errors:
                for field in application_form:
                    for error in field.errors:
                        messages.add_message(request, messages.ERROR, f"{field.label} - {error}")
            return redirect(self.request.META.get('HTTP_REFERER'))

def getacdetails(id):
    ac_url = f"academic_consideration/api/AcademicConsideration/{id}"
    status, ac_details = make_request('get', ac_url)
    ac_data = None

    if status and status == 200:
        status_code = ac_details["status_code"]
        if status_code == 200:
            ac_data = ac_details["data"]

    return ac_data

def getsubjlist():
    subject_list = []
    subject_url = "institution/api/subject/"
    status, subject_data = make_request('get', subject_url)

    if status and status == 200:
        status_code = subject_data["status_code"]
        if status_code == 200:
            subject_list = subject_data["data"]

    return subject_list