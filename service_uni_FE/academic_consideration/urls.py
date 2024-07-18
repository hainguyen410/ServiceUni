from django.urls import path

from . import views as v


app_name = 'academic_consideration'

urlpatterns = [
    path('approvals/', v.AcademicConsiderationView.as_view(), name='list_applications'),
    path('create/', v.CreateAcademicConsideration.as_view(), name='create_user_applications'),
    path('create/application/', v.StudentAcademicConsiderationView.as_view(), name='submit_application'),
    path('list/', v.AcademicConsiderationStudentView.as_view(), name='user_list_applications'),
    path('approvals/details/<int:id>', v.ApprovalDetailsAcademicConsideration.as_view(), name='show_approval_details'),
    path('details/<int:id>', v.DetailsAcademicConsideration.as_view(), name='show_details'),
    path('update/application/', v.AcademicConsiderationUpdateStatusView.as_view(), name='update_application'),
]

