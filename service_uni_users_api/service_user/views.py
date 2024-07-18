import json

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from . import models as m
from . import serializers as s
from .utils import get_tokens_for_user


class GeneralUserViewset(viewsets.ViewSet):
    queryset = m.ServiceUser.objects.all()
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get_object(self, id):
        return get_object_or_404(m.ServiceUser, id=id)

    def get_permissions(self):
        return []

    @swagger_auto_schema(request_body=s.CreateSUAccount)
    @action(detail=False, methods=['POST'])
    def create_admin_account(self, request):
        '''
            Post create admin account
            POST /student/create_admin_account/
        '''

        request_data = request.data
        if type(request_data) == str:
            request_data = json.loads(request_data)

        serializer = s.CreateSUAccount(data=request_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            email = serializer.data.get('email')
            password = request_data.get('password')
            user = authenticate(email=email, password=password)
            login(request, user)
            user_data = s.ServiceUserSerializer(user).data
            return Response(user_data, status.HTTP_200_OK)
        return Response(serializer.data, status.HTTP_200_OK)

    @swagger_auto_schema(request_body=s.CreateStaffAccount)
    @action(detail=False, methods=['POST'])
    def create_staff_account(self, request):
        '''
            Post create staff account
            POST /student/create_staff_account/
        '''

        request_data = request.data
        if type(request_data) == str:
            request_data = json.loads(request_data)

        serializer = s.CreateStaffAccount(data=request_data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data, status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def get_all_staff(self, request):
        '''
            Get staff list
            GET /service_user/get_all_staff/
        '''
        self.queryset = m.ServiceUser.objects.get_all_staffs()
        data = s.ServiceUserSerializer(self.queryset, many=True).data

        return Response(data=data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=s.PhoneContactSerializer(many=True))
    @action(detail=True, methods=['POST'])
    def add_phone_number(self, request, pk=None):
        '''
            Post add phone number
            POST /student/add_phone_number/

            param pk - student pk

        '''
        user_instance = self.get_object(pk)

        serializer = s.PhoneContactSerializer(data=request.data, many=True)
        if serializer.is_valid(raise_exception=True):
            phone_data = serializer.save()
            user_instance.contact_phone.add(*phone_data)
            user_instance.save()
            data = s.ServiceUserSerializer(user_instance).data
            return Response(data, status.HTTP_200_OK)
        return Response(serializer.data, status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: s.ServiceUserSerializer})
    def retrieve(self, request, pk=None):
        '''
        Get a user details
        GET /service_user/<int:pk>/
        param pk - user pk
        '''

        user = self.get_object(id=pk)
        data = s.ServiceUserSerializer(user).data
        return Response(data=data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=s.ServiceUserSerializerUpdate())
    @action(detail=True, methods=['PATCH'])
    def update_service_user_account(self, request, pk=None):
        instance = self.get_object(pk)
        serializer = s.ServiceUserSerializerUpdate(instance, request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            data = s.ServiceUserSerializer(instance).data
            return Response(data, status.HTTP_200_OK)
        return Response(serializer.data, status.HTTP_200_OK)


class StudentViewset(viewsets.ViewSet):
    queryset = m.ServiceUser.objects.get_all_students()
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get_object(self, id):
        return get_object_or_404(m.ServiceUser, id=id)

    def get_permissions(self):
        return []

    @action(detail=False, methods=['get'])
    def get_all_student(self, request):
        '''
            Get student list
            GET /student/get_all_student/
        '''
        data = s.ServiceUserSerializer(self.queryset, many=True).data

        return Response(data=data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=s.AdmissionApplicationSerializer)
    @action(detail=False, methods=['post'])
    def apply_for_admission(self, request):
        '''
            Update student information
            POST /student/apply_for_admission/
        '''
        serializer = s.AdmissionApplicationSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'data': 'Application submitted successfully'}, status.HTTP_200_OK)
        return Response(serializer.data, status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def update_user_courses(self, request, pk=None):
        instance = self.get_object(id=pk)
        operation = request.data["operation"]
        if operation == 'add':
            if 'current_enrolled_courses' in request.data:
                if not instance.current_enrolled_courses:
                    instance.current_enrolled_courses = []
                data = request.data["current_enrolled_courses"]
                if int(data) not in instance.current_enrolled_courses:
                    instance.current_enrolled_courses.append(int(data))
            elif 'current_course_handling' in request.data:
                if not instance.current_course_handling:
                    instance.current_course_handling = []
                data = request.data["current_course_handling"]
                if int(data) not in instance.current_course_handling:
                    instance.current_course_handling.append(int(data))
        else:
            if 'current_enrolled_courses' in request.data:
                data = request.data["current_enrolled_courses"]
                if int(data) in instance.current_enrolled_courses:
                    instance.current_enrolled_courses.remove(int(data))

            elif 'current_course_handling' in request.data:
                data = request.data["current_course_handling"]
                if int(data) in instance.current_course_handling:
                    instance.current_course_handling.remove(int(data))

        instance.save()
        data = s.ServiceUserSerializer(instance).data
        return Response(data, status.HTTP_200_OK)

    @swagger_auto_schema(request_body=s.GrantAdmissionSerializer, methods=['patch'])
    @action(detail=True, methods=['patch'])
    def grant_admission(self, request, pk=None):
        '''
            Update student information
            PATCH /student/<int:pk>/grant_admission/
            PUT /student/<int:pk>/grant_admission/
        '''
        instance = self.get_object(id=pk)

        # if instance.user_type == "STUDENT":
        #     if instance.student_status == "CURRENT_STUDENT":
        #         return Response({'detail': "Student already granted admission!"}, status.H)
        #
        # if not instance.program_approval:
        #     return Response({'detail': "Application pending soft approval from department!"},
        #                     status.HTTP_400_BAD_REQUEST)

        serializer = s.GrantAdmissionSerializer(instance, request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            data = s.ServiceUserSerializer(instance).data
            return Response(data, status.HTTP_200_OK)
        return Response(serializer.data, status.HTTP_200_OK)

    @swagger_auto_schema(request_body=s.SoftGrantAdmissionSerializer, methods=['patch'])
    @action(detail=True, methods=['patch'])
    def soft_grant_admission(self, request, pk=None):
        '''
            Update student information
            PATCH /student/<int:pk>/soft_grant_admission/
            PUT /student/<int:pk>/soft_grant_admission/
        '''
        instance = self.get_object(id=pk)
        serializer = s.SoftGrantAdmissionSerializer(instance, request.data)
        if instance.user_type == "STUDENT":
            if instance.student_status == "CURRENT_STUDENT":
                return Response({'detail': "Student already granted admission!"}, status.HTTP_304_NOT_MODIFIED)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            data = s.ServiceUserSerializer(instance).data
            return Response(data, status.HTTP_200_OK)
        return Response(serializer.data, status.HTTP_200_OK)

    @swagger_auto_schema(request_body=s.GrantAdmissionSerializer, methods=['patch'])
    @action(detail=True, methods=['patch'])
    def deny_admission(self, request, pk=None):
        '''
            Update student information
            PATCH /student/<int:pk>/deny_admission/
            PUT /student/<int:pk>/deny_admission/
        '''
        instance = self.get_object(id=pk)
        serializer = s.RejectAdmissionSerializer(instance, request.data)
        if instance.user_type == "STUDENT":
            if instance.student_status == "CURRENT_STUDENT":
                return Response({'detail': "Student already granted admission!"}, status.HTTP_100_CONTINUE)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            data = s.ServiceUserSerializer(instance).data
            return Response(data, status.HTTP_200_OK)
        return Response(serializer.data, status.HTTP_200_OK)

    @swagger_auto_schema(request_body=s.ChangePasswordSerializer)
    @action(detail=True, methods=['patch'])
    def change_password(self, request, pk=None):
        '''
        Change a student password
        PUT /student/<int:pk>/change_password/
        param pk - student account id
        '''

        student = self.get_object(id=pk)
        serializer = s.ChangePasswordSerializer(data=request.data, context={'student': student})
        if serializer.is_valid(raise_exception=True):
            serializer.apply_password()

            return Response({'detail': 'Password changed successfully'}, status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: s.ServiceUserSerializer})
    def retrieve(self, request, pk=None):
        '''
        Get a student details
        GET /student/<int:pk>/
        param pk - student pk
        '''

        student = self.get_object(id=pk)
        data = s.ServiceUserSerializer(student).data
        return Response(data=data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def get_future_students(self, request):
        '''
            Get student seeking admission list
            GET /student/get_future_students/
        '''
        self.queryset = m.ServiceUser.objects.get_future_student()
        data = s.ServiceUserSerializer(self.queryset, many=True).data
        return Response(data=data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def get_current_student(self, request):
        '''
            Get current student list
            GET /student/get_current_student/
        '''
        self.queryset = m.ServiceUser.objects.get_current_student()
        data = s.ServiceUserSerializer(self.queryset, many=True).data
        return Response(data=data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def get_graduate_student(self, request):
        '''
            Get graduated student list
            GET /student/get_graduate_student/
        '''
        self.queryset = m.ServiceUser.objects.get_graduate_student()
        data = s.ServiceUserSerializer(self.queryset, many=True).data
        return Response(data=data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'])
    def delete(self, request, pk=None):
        '''
            Delete student account
            DELETE /student/<int:pk>/delete/
            param pk - student account id
        '''

        instance = self.get_object(id=pk)
        try:
            instance.delete()
            return Response({'detail': 'Staff deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response({'detail': 'An error occurred while trying to delete staff'},
                            status.HTTP_400_BAD_REQUEST)


class ServiceUserAuthViewset(viewsets.ViewSet):
    queryset = m.ServiceUser.objects.all()
    http_method_names = ['post']

    @swagger_auto_schema(request_body=s.LoginSerializer)
    @action(detail=False, methods=['post'])
    def login_user(self, request):
        print(f"request_data: {request.data}", flush=True)
        request_data = request.data
        if type(request_data) == str:
            request_data = json.loads(request_data)
        email = request_data.get("email")
        password = request_data.get("password")

        if email is None or password is None:
            return Response(
                {'detail': 'Please provide both email and password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = authenticate(email=email, password=password)
        if not user:
            return Response(
                {'detail': 'Invalid credentials'},
                status=status.HTTP_404_NOT_FOUND
            )

        login(request, user)

        data = s.ServiceUserSerializer(user).data

        data['token'] = get_tokens_for_user(user)
        data['detail'] = 'Login successful'
        data['success'] = True
        return Response(data, status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def logout_user(self, request):
        logout(request)
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class ServiceUserLogin(APIView):
    '''
    Login to an account
    POST /service_users/auth/login/
    '''
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=s.LoginSerializer, responses={200: s.ServiceUserSerializer})
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if email is None or password is None:
            return Response(
                {'detail': 'Please provide both email and password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = authenticate(email=email, password=password)
        if not user:
            return Response(
                {'detail': 'Invalid credentials'},
                status=status.HTTP_404_NOT_FOUND
            )

        login(request, user)

        data = s.ServiceUserSerializer(user).data

        data['token'] = get_tokens_for_user(user)
        data['detail'] = 'Login successful'
        data['success'] = True
        return Response(data, status.HTTP_200_OK)


class ServiceUserLogout(APIView):
    '''
    Log out users
    POST /service_users/auth/logout/
    '''

    def post(self, request):
        logout(request)
        return Response(None, status=status.HTTP_204_NO_CONTENT)

# class StudentAdmissionApplication(generics.ListCreateAPIView):
#     queryset = m.ServiceUser.objects.get_future_student()
#     serializer_class = s.StudentAdmissionSerializer
#     # permission_classes = [adminForGet]
#
#
# class GrantStudentAdmission(generics.UpdateAPIView):
#     queryset = m.ServiceUser.objects.get_future_student()
#     serializer_class = s.FutureStudentUpdateSerializer
#     # permission_classes = []
#
#     def perform_update(self, serializer):
#         instance = serializer.save()
#         instance.student_status = "CURRENT_STUDENT"
#         instance.email = generate_email(instance)
#         instance.coe = generate_coe(instance)
#         serializer.save()

#
# class StudentCreateViewSet(viewsets.ModelViewSet):
#     """
#     Service User model viewset
#     Admin permissions
#     """
#
#     queryset = m.ServiceUser.objects.all()
#     serializer_class = s.StudentCreateSerializer
#     # permission_classes = [
#     #     permissions.IsAuthenticated,
#     #     perm.IsEmployee,
#     # ]
#     http_method_names = ["post"]
#
#     def create(self, request, *args, **kwargs):
#         if type(request.data) != dict:
#             data = request.data.dict()
#         else:
#             data = request.data
#
#         # ensure that user does not already exist
#         if len(self.queryset.filter(email=data.get("email")) > 0):
#             return Response(
#                 data={"message": f"User Already exists with email {data.get('email')}"},
#                 status=status.HTTP_409_CONFLICT
#             )
#
#         # create new user
#         u_id = get_my_u_id([data["first_name"], data["middle_name"], data["last_name"]])
#         data["u_id"] = u_id
#
#         email = f"{u_id}@{data['institution']['email_domain']}.com"
#         data["email"] = email
#         data["user_type"] = "STUDENT"
#         data["institution"] = "institution"
#         data["is_active"] = True
#         serializer = self.serializer_class(data=data)
#         if not serializer.is_valid():
#             return Response(
#                 data={"message": str(serializer.errors)},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         student = serializer.save()
#
#         res = self.serializer_class(student)
#         return Response(
#             data=res.data,
#             status=status.HTTP_201_CREATED
#         )
