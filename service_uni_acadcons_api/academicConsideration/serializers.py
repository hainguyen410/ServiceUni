from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from . import models as m


class AC_serializer (serializers.ModelSerializer):
    class Meta:
        model = m.AcademicConsideration
        fields = '__all__'

class GetStudentACApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = m.AcademicConsideration
        fields = ['student_id']
