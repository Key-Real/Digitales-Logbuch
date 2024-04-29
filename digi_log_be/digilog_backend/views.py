from rest_framework import viewsets, serializers, exceptions
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from .models import Course, User
from django.http import HttpResponse, JsonResponse
from django_auth_ldap.backend import LDAPBackend
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
import json
from .authenticator import CustomAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView, TokenVerifyView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenVerifySerializer
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.views import exception_handler
from rest_framework import  status

# from django.views.decorators.vary import 


class AuthViewset(viewsets.ModelViewSet):
    authentication_classes = [CustomAuthentication]
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return super().get_permissions()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name",
                  "last_name", "email", "is_active"]


class UserViewSet(AuthViewset):
    queryset = User.objects.filter(is_active=True).order_by('id')
    serializer_class = UserSerializer


class CourseSerializer(serializers.ModelSerializer):
    host = UserSerializer()
    class Meta:
        model = Course
        fields = '__all__'

    def create(self, validated_data):
        host_obj = validated_data.pop('host')
        host, created = User.objects.get_or_create(
            **host_obj, defaults={})
        course = super().create({"host":host, **validated_data})
        return course
        

class CourseViewSet(AuthViewset):
    queryset = Course.objects.all().order_by('id')
    serializer_class = CourseSerializer



@csrf_exempt
def login_user(request):

    username = password = ""
    state = ""

    if request.method == "POST":
        body = json.loads(request.body)
        username = body.get('username')
        password = body.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            print("Valid account")
            return HttpResponse(status=200, content=user)
            
        else:
            print("Invalid account")
            return HttpResponse(status=400, content="Authentication failed")
        
    else:
        return render(request, 'digi_log/login.html')


class myTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data["refresh"] = str(refresh)   # comment out if you don't want this
        data["access"] = str(refresh.access_token)
        data["uname"] = self.user.get_username()

        """ Add extra responses here should you wish
        data["userid"] = self.user.id
        data["my_favourite_bird"] = "Jack Snipe"
        """
        return data

class myTokenObtainPairView(TokenObtainPairView):
    serializer_class = myTokenObtainPairSerializer
    def post(self, request, *args, **kwargs):
        # you need to instantiate the serializer with the request data
        serializer = self.get_serializer(data=request.data)
        # you must call .is_valid() before accessing validated_data
        serializer.is_valid(raise_exception=True)

        # get access and refresh tokens to do what you like with
        access = serializer.validated_data.get("access", None)
        refresh = serializer.validated_data.get("refresh", None)
        uname = serializer.validated_data.get("uname", None)

        # build your response and set cookie
        if access is not None:
            response = JsonResponse(
                {"access": access, "refresh": refresh, "uname": uname}, status=200)
            response.set_cookie('token', access, httponly=True)
            response.set_cookie('refresh', refresh, httponly=True)
            response.set_cookie('uname', uname, httponly=True)
            return response

        return HttpResponse({"Error": "Something went wrong"}, status = 400)


@csrf_exempt
def test(request):
    try:
        CustomAuthentication().authenticate(request)
        return HttpResponse("OK", status = 200)
    except TokenError as e:
        r= exception_handler(exceptions.PermissionDenied(e.args[0]), {})
        return r


class myTokenVerifyView(TokenVerifyView):
    serializer_class = TokenVerifySerializer
    
    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data={"token":request.COOKIES.get("access") or request.data.get("access")})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
