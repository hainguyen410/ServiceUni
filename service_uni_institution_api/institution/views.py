import json

from django.shortcuts import render, get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from . import models as m
from . import serializers as s


class Institution(viewsets.ModelViewSet):
    queryset = m.Institution.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            serializer = s.InstitutionDetailSerializer
        else:
            serializer = s.InstitutionCreateSerializer
        return serializer

    def create(self, request, *args, **kwargs):
        request_data = request.data
        if type(request_data) == str:
            request_data = json.loads(request_data)

        serializer = s.InstitutionCreateSerializer(data=request_data)
        if serializer.is_valid(raise_exception=True):
            institution = serializer.save()
            data = s.InstitutionDetailSerializer(institution).data
            return Response(data, status.HTTP_200_OK)
        return Response(serializer.data, status.HTTP_200_OK)

    def get_object(self):
        return super(Institution, self).get_object()

    @swagger_auto_schema(request_body=s.AddSchoolToInstitution, methods=['patch'])
    @action(detail=True, methods=['patch'])
    def add_school(self, request, pk=None):
        '''
            Add Course to Institution
            PATCH /institution/<int:pk>/add_school/
            PUT /institution/<int:pk>/add_school/
        '''
        instance = self.get_object()

        serializer = s.AddSchoolToInstitution(instance, request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            data = s.InstitutionDetailSerializer(instance).data
            return Response(data, status.HTTP_200_OK)
        return Response(serializer.data, status.HTTP_200_OK)

    @swagger_auto_schema(request_body=s.AddProgramToInstitution, methods=['patch'])
    @action(detail=True, methods=['patch'])
    def add_program(self, request, pk=None):
        '''
            Add Program to Institution
            PATCH /institution/<int:pk>/add_program/
            PUT /institution/<int:pk>/add_program/
        '''
        instance = self.get_object()

        serializer = s.AddProgramToInstitution(instance, request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            data = s.InstitutionDetailSerializer(instance).data
            return Response(data, status.HTTP_200_OK)
        return Response(serializer.data, status.HTTP_200_OK)

    @swagger_auto_schema(request_body=s.SetInstitutionCurrentSession, methods=['patch'])
    @action(detail=True, methods=['patch'])
    def set_current_session(self, request, pk=None):
        instance = self.get_object()
        serializer = s.SetInstitutionCurrentSession(instance, request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            data = s.InstitutionDetailSerializer(instance).data
            return Response(data, status.HTTP_200_OK)
        return Response(serializer.data, status.HTTP_200_OK)


class School(viewsets.ModelViewSet):
    queryset = m.School.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            serializer_class = s.SchoolDetailSerializer
        else:
            serializer_class = s.SchoolCreateSerializer
        return serializer_class

    def get_object(self):
        return super(School, self).get_object()

    @swagger_auto_schema(request_body=s.AddSubjectToSchool, methods=['patch'])
    @action(detail=True, methods=['patch'])
    def add_subject(self, request, pk=None):
        instance = self.get_object()
        serializer = s.AddSubjectToSchool(instance, request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            data = s.SchoolDetailSerializer(instance).data
            return Response(data, status.HTTP_200_OK)
        return Response(serializer.data, status.HTTP_200_OK)


class Subject(viewsets.ModelViewSet):
    serializer_class = s.SubjectSerializer
    queryset = m.Subject.objects.all()

    def get_object(self):
        return super(Subject, self).get_object()

    @swagger_auto_schema(request_body=s.AddSubjectPrerequisite, methods=['patch'])
    @action(detail=True, methods=['patch'])
    def add_prerequisite(self, request, pk=None):
        instance = self.get_object()
        serializer = s.AddSubjectPrerequisite(instance, request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            data = s.SubjectSerializer(instance).data
            return Response(data, status.HTTP_200_OK)
        return Response(serializer.data, status.HTTP_200_OK)


class AcademicSession(viewsets.ModelViewSet):
    serializer_class = s.AcademicSessionSerializer
    queryset = m.AcademicSession.objects.all()


class Program(viewsets.ModelViewSet):
    queryset = m.Program.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            serializer_class = s.ProgramDetailSerializer
        else:
            serializer_class = s.ProgramCreateSerializer
        return serializer_class
