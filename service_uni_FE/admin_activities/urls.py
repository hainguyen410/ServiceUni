from django.urls import path

from . import views as v


app_name = "institution"

urlpatterns = [
    path('create_school/', v.CreateSchool.as_view(), name="create_school"),
    path('create_program/', v.CreateProgram.as_view(), name="create_program"),
    path('create_subject/', v.CreateSubject.as_view(), name="create_subject"),
    path('list_school/', v.ListSchool.as_view(), name="list_school"),
    path('list_program/', v.ListProgram.as_view(), name="list_program"),
    path('list_subject/', v.ListSubject.as_view(), name="list_subject"),
    path('list_current_student/', v.ListCurrentStudent.as_view(), name="list_current_student"),
]
