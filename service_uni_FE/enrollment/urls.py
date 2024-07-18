from django.urls import path
from . import views as v

app_name = 'enrollment'


urlpatterns = [
    path('enrollment_list/', v.EnrollmentView.as_view(), name='enrollment_list'),
    path('student_enrollment_list/', v.StudentEnrollmentView.as_view(), name='student_enrollment_list'),
    path('session_enrollment/', v.SessionEnrollment.as_view(), name='session_enrollment'),
    path('subject_enrollment/', v.SubjectEnrollment.as_view(), name='subject_enrollment'),
]
