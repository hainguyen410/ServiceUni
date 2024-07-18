from django.contrib.auth import password_validation
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from helper_functions.helper import generate_coe, generate_email, make_request
from . import models as m


class ServiceUserTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.ServiceUserType
        fields = ['id', 'user_type']


class PhoneContactSerializer(serializers.ModelSerializer):

    class Meta:
        model = m.PhoneContact
        fields = ['phone_contact', 'phone_type']


class AdmissionApplicationSerializer(serializers.ModelSerializer):
    contact_phone = PhoneContactSerializer()

    class Meta:
        model = m.ServiceUser
        fields = [
            "first_name", "last_name", "middle_name", "date_of_birth", "student_type", "user_type", "program_id",
            "contact_phone", "gender", "institution_id", "school_id", "student_status"
        ]

    def create(self, validated_data):
        validated_data["student_status"] = "FUTURE_STUDENT"
        contact_phone = validated_data.pop("contact_phone")
        instance = self.Meta.model.objects.create(**validated_data)

        contact = m.PhoneContact.objects.create(**contact_phone)
        instance.contact_phone.add(contact)
        instance.save()
        return instance


class CreateSUAccount(serializers.ModelSerializer):
    contact_phone = PhoneContactSerializer(many=True, required=False)

    class Meta:
        model = m.ServiceUser
        fields = [
            "email", "first_name", "last_name", "middle_name", "user_type", "contact_phone", "password"
        ]

    def create(self, validated_data):
        contact = validated_data.get('contact_phone', None)
        contact_phone = None
        if contact:
            contact_phone = validated_data.pop('contact_phone')
        password = validated_data.pop('password')
        instance = self.Meta.model.objects.create(**validated_data)
        instance.set_password(password)
        if contact:
            bulk_list = [m.PhoneContact(**phone_data) for phone_data in contact_phone]
            contacts = m.PhoneContact.objects.bulk_create(bulk_list)
            instance.contact_phone.add(*contacts)
        instance.save()
        return instance


class CreateStaffAccount(serializers.ModelSerializer):
    contact_phone = PhoneContactSerializer(many=True, required=False)

    class Meta:
        model = m.ServiceUser
        fields = [
            'first_name',
            'middle_name',
            'last_name',
            'email',
            'date_of_birth',
            'user_type',
            'current_course_handling',
            'city',
            'state',
            'country',
            'contact_phone',
            'institution_id',
        ]

    def create(self, validated_data):
        contact = validated_data.get('contact_phone', None)
        contact_phone = None
        if contact:
            contact_phone = validated_data.pop('contact_phone')
        password = "12345678"
        instance = self.Meta.model.objects.create(**validated_data)
        instance.set_password(password)
        if contact:
            bulk_list = [m.PhoneContact(**phone_data) for phone_data in contact_phone]
            contacts = m.PhoneContact.objects.bulk_create(bulk_list)
            instance.contact_phone.add(*contacts)
        instance.save()
        return instance


class GrantAdmissionSerializer(serializers.ModelSerializer):
    current_level = serializers.ChoiceField(choices=m.PROGRAM_LEVEL, required=False)

    class Meta:
        model = m.ServiceUser
        fields = ["current_level", "coe", "student_status", "email"]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.set_password("12345678")
        instance.save()
        return instance


class SoftGrantAdmissionSerializer(serializers.ModelSerializer):
    program_approval = serializers.BooleanField()
    soft_approval = serializers.CharField()

    class Meta:
        model = m.ServiceUser
        fields = ["program_approval", "soft_approval"]


class RejectAdmissionSerializer(serializers.ModelSerializer):
    student_status = serializers.CharField()

    class Meta:
        model = m.ServiceUser
        fields = ['student_status']

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        if new_password != confirm_password:
            raise serializers.ValidationError(detail='The two passwords does not match')

        password_validation.validate_password(new_password, self.context['student'])

        return attrs

    def apply_password(self):
        student = self.context['student']
        new_password = self.validated_data['new_password']
        student.set_password(new_password)
        student.save()


class AccountCreateSerializer(serializers.ModelSerializer):
    program_name = serializers.CharField(required=False)
    email_domain = serializers.CharField(required=False)
    contact_phone = PhoneContactSerializer()

    class Meta:
        model = m.ServiceUser
        fields = [
            "first_name", "last_name", "middle_name", "email", "coe", "date_of_birth", "school_id", "program_id", "street_address", "city",
            "state", "country", "contact_phone", "gender", "passport_photo", "student_type", "user_type",
            "current_level", "program_name", "email_domain", "institution"
        ]


class ServiceUserSerializer(serializers.ModelSerializer):
    contact_phone = PhoneContactSerializer(many=True)

    class Meta:
        model = m.ServiceUser
        exclude = ['is_active', 'is_staff', 'last_login', 'is_superuser']


class ServiceUserSerializerUpdate(serializers.ModelSerializer):

    class Meta:
        model = m.ServiceUser
        fields = ['institution_id',]
