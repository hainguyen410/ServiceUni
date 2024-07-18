from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

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

app_name = "institution"

router = DefaultRouter()

router.register(r"institution", v.Institution, "institution")
router.register(r"school", v.School, "school")
router.register(r"program", v.Program, "program")
router.register(r"subject", v.Subject, "subject")
router.register(r"academic_session", v.AcademicSession, "academic_session")

urlpatterns = [
    # Docs
    path('docs<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path("", include(router.urls)),
]
