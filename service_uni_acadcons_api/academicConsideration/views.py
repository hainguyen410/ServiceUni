from django.core.serializers import serialize
from django.http import HttpResponse
from .models import AcademicConsideration
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from .serializers import AC_serializer
from rest_framework.decorators import action
from rest_framework.response import Response

from . import serializers as s
from . import models as m


class AC_Views(viewsets.ModelViewSet):
    serializer_class = AC_serializer
    queryset = AcademicConsideration.objects.all()
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get_object(self):
        return super(AC_Views, self).get_object()


    @swagger_auto_schema(request_body=s.GetStudentACApplicationSerializer())
    @action(detail=False, methods=['POST'])
    def show_user_applications(self, request):
        student_id = request.data["student_id"]
        queryset = self.queryset.filter(student_id=student_id)
        data = s.AC_serializer(queryset, many=True).data
        return Response(data, status=status.HTTP_200_OK)