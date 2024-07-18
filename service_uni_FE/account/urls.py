from django.urls import path

from . import views as v


app_name = 'account'

urlpatterns = [
    path('', v.Login.as_view(), name='login'),
    path('register/', v.Register.as_view(), name='register'),
    path('apply_admission/', v.ApplyForAdmission.as_view(), name='apply_admission'),
    path('student_home/', v.StudentHome.as_view(), name='student_home'),
    path('staff_home/', v.StaffHome.as_view(), name='staff_home'),
    path('admin_home/', v.AdminHome.as_view(), name='admin_home'),
    path('admission_list/', v.AdmissionView.as_view(), name='admission_list'),
    path('logout/', v.logout, name='logout'),
    path('tester/', v.page_tester, name='page_tester'),
    path('create_account/', v.CreateAccount.as_view(), name='create_account'),
    path('profile/', v.ProfileView.as_view(), name='profile'),
]
