from django.urls import path, include

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt import views as jwt_views

from . import views as v

schema_view = get_schema_view(
    openapi.Info(
        title="Service Uni",
        default_version='v1',
        description="Service Uni Endpoint Arena",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny, ],

)

app_name = "service_user"

router = DefaultRouter()
router.register(r"student", v.StudentViewset, "student")
router.register(r"service_user", v.GeneralUserViewset, "service_user")
router.register(r"auth", v.ServiceUserAuthViewset, "auth")

urlpatterns = [
    # Docs
    path('docs<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Token and Login
    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', jwt_views.TokenVerifyView.as_view(), name='token_verify'),
    # path('login/', v.ServiceUserLogin.as_view(), name='user_login'),
    # path('logout/', v.ServiceUserLogout.as_view(), name='user_logout'),

    # Others

    # path('register_account/', v.CreateAccount.as_view()),
    # path('all_student/', v.AllStudent.as_view()),
    # path('future_student/', v.AdmissionApplication.as_view(), name='future_student'),
    # path('grant_future_student/<int:pk>/', v.GrantAdmission.as_view(), name='grant_future_student_admission'),
    path("", include(router.urls)),
]

