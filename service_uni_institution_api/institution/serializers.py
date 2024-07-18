import json

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from . import models as m


class PhoneContactSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = m.PhoneContact
        fields = ['id', 'phone_contact', 'phone_type']


class SubjectSerializer(serializers.ModelSerializer):
    slug = serializers.CharField(read_only=True)
    updated_at = serializers.DateField(required=False)

    class Meta:
        model = m.Subject
        fields = '__all__'


class InstitutionCreateSerializer(serializers.ModelSerializer):
    contact_phone = PhoneContactSerializer(many=True, required=False)

    class Meta:
        model = m.Institution
        fields = ['id', 'name', 'website', 'admin_user_id', 'street_address', 'city', 'state', 'country',
                  'contact_phone', 'email_domain']

    def create(self, validated_data):
        contact = validated_data.get('contact_phone', None)
        contact_phone_data = None
        if contact:
            contact_phone_data = validated_data.pop('contact_phone')
        instance = self.Meta.model.objects.create(**validated_data)
        if contact_phone_data:
            for data in contact_phone_data:
                contact = m.PhoneContact.objects.create(**data)
                instance.contact_phone.add(contact)
        instance.save()
        return instance


class SchoolCreateSerializer(serializers.ModelSerializer):
    institution = serializers.IntegerField(required=False)

    class Meta:
        model = m.School
        fields = [
            "name", "institution"
        ]

    def create(self, validated_data):
        institution = None
        if 'institution' in validated_data:
            institution_data = validated_data.pop('institution')
            institution = get_object_or_404(m.Institution, pk=int(institution_data))
        instance = self.Meta.model.objects.create(**validated_data)
        if institution:
            institution.schools.add(instance)
            institution.save()
        return instance


class ProgramCreateSerializer(serializers.ModelSerializer):
    school = serializers.IntegerField(required=False)

    class Meta:
        model = m.Program
        fields = [
            "id", "name", "code", "school"
        ]

    def create(self, validated_data):
        school_instance = None
        if 'school' in validated_data:
            school_data = validated_data.pop('school')
            school_instance = get_object_or_404(m.School, pk=int(school_data))
        instance = self.Meta.model.objects.create(**validated_data)

        if school_instance:
            school_instance.programs.add(instance)
        return instance


class ProgramDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.Program
        fields = '__all__'


class SchoolDetailSerializer(serializers.ModelSerializer):
    programs = ProgramDetailSerializer(many=True)
    subjects = SubjectSerializer(many=True)

    class Meta:
        model = m.School
        fields = '__all__'


class AcademicSessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.AcademicSession
        fields = '__all__'


class InstitutionDetailSerializer(serializers.ModelSerializer):
    contact_phone = PhoneContactSerializer(many=True)
    schools = SchoolDetailSerializer(many=True)
    current_session = AcademicSessionSerializer()

    class Meta:
        model = m.Institution
        fields = '__all__'


class AddSchoolToInstitution(serializers.ModelSerializer):
    schools = SchoolCreateSerializer(many=True)

    class Meta:
        model = m.Institution
        fields = ['schools']

    def update(self, instance, validated_data):
        schools = validated_data.pop('schools')
        bulk_list = [m.School(**school_data) for school_data in schools]
        school_list = m.School.objects.bulk_create(bulk_list)
        instance.schools.add(*school_list)
        instance.save()
        return instance


class SetInstitutionCurrentSession(serializers.ModelSerializer):
    current_session = AcademicSessionSerializer()

    class Meta:
        model = m.Institution
        fields = ['current_session']

    def update(self, instance, validated_data):
        session = validated_data.pop('current_session')
        session_instance = m.AcademicSession.objects.create(**session)
        instance.current_session = session_instance
        instance.save()
        return instance


class AddProgramToInstitution(serializers.ModelSerializer):
    school_id = serializers.IntegerField()
    programs = ProgramCreateSerializer(many=True)

    class Meta:
        model = m.Institution
        fields = ['school_id', 'programs']

    def update(self, instance, validated_data):
        school_id = validated_data.pop('school_id')
        school_instance = get_object_or_404(m.School, pk=int(school_id))
        programs = validated_data.pop('programs')
        bulk_list = [m.Program(**program_data) for program_data in programs]
        program_list = m.Program.objects.bulk_create(bulk_list)
        school_instance.programs.add(*program_list)
        school_instance.save()
        instance.programs.add(*program_list)
        instance.save()
        return instance


class AddSubjectToSchool(serializers.ModelSerializer):
    subject = SubjectSerializer()

    class Meta:
        model = m.School
        fields = ['subject']

    def update(self, instance, validated_data):
        subject = validated_data.pop('subject')
        pre_subjects = subject.pop('prerequisite_subjects')
        subject_instance = m.Subject.objects.create(**subject)
        subject_instance.prerequisite_subjects.set(pre_subjects)
        subject_instance.save()
        instance.subjects.add(subject_instance)
        instance.save()
        return instance


class AddSubjectPrerequisite(serializers.ModelSerializer):
    subject_list = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        model = m.Subject
        fields = ['subject_list']

    def update(self, instance, validated_data):
        subject_list = validated_data.pop('subject_list')
        subject_list = m.Subject.objects.filter(id__in=subject_list)
        instance.prerequisite_subjects.add(*subject_list)
        instance.save()
        return instance
