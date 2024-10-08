

from django.http import SimpleCookie
from django.test import TestCase
from digilog_backend.models import Course, User
from rest_framework.test import APIRequestFactory, APIClient
import json

factory = APIRequestFactory()


class AuthAPITest(TestCase):
    """
    Note: For Authentication, access and refresh tokens are required in cookies.
        They are automatically when sucessfully loggin in with /api/token/.
        Thus, we don't need to set them manually.
    """
    @classmethod
    def setUpTestData(cls) -> None:
        cls.host = {
            "username": "test_user",
            "email": "test_email@test.com",
            "first_name": "test_first_name",
            "last_name": "test_last_name",
            "password": "test_password",
        }
        cls.user = User.objects.create(**cls.host)
        cls.user.set_password(cls.host['password'])
        cls.user.save()
        cls.client = APIClient()
    
    def test_login(self):
        response = self.client.post('/api/token/', json.dumps({"username":self.host["username"], "password":self.host["password"]}), content_type='application/json')
        data = json.loads(response.content)
        self.assertIsInstance(data, dict)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data.get("uname"), self.host["username"])
        self.assertIn("access", data.keys())

    def test_refresh(self):
        tokenresponse = self.client.post(
            '/api/token/',
            json.dumps({"username": self.host["username"], "password": self.host["password"]}),
            content_type='application/json')
        self.assertEqual(tokenresponse.status_code, 200)
        self.assertContains(tokenresponse, "access")

        refreshresponse = self.client.get('/api/token/refresh/', headers={'refresh': tokenresponse.json()['refresh']})
        self.assertEqual(refreshresponse.status_code, 200)
        self.assertContains(refreshresponse, "access")


    def test_refresh_cycling(self):
        tokenresponse = self.client.post(
            '/api/token/',
            json.dumps({"username": self.host["username"], "password": self.host["password"]}),
            content_type='application/json')
        self.assertEqual(tokenresponse.status_code, 200)
        self.assertContains(tokenresponse, "access")

        first_refreshresponse = self.client.get('/api/token/refresh/')
        self.assertEqual(first_refreshresponse.status_code, 200)
        self.assertContains(first_refreshresponse, "access")
        self.assertNotEqual(first_refreshresponse.cookies.get('refresh').value, tokenresponse.cookies.get('refresh').value)

        outdated_refresh = tokenresponse.cookies.get('refresh').value
        outdated_response = self.client.post(
            '/api/authTest/', {"token": outdated_refresh})
        self.assertEqual(outdated_response.status_code, 400)

        second_refreshresponse = self.client.get('/api/token/refresh/')
        self.assertEqual(second_refreshresponse.status_code, 200)
        self.assertContains(second_refreshresponse, "access")
        self.assertNotEqual(
    second_refreshresponse.cookies.get('refresh').value, first_refreshresponse.cookies.get('refresh').value
        )

        outdated_refresh = first_refreshresponse.cookies.get('refresh').value
        outdated_response = self.client.post(
            '/api/authTest/', {"token": outdated_refresh})
        self.assertEqual(outdated_response.status_code, 400)

    def test_invalid_refresh(self):
        # empty refresh
        empty_tokenresponse = self.client.post('/api/token/refresh/', headers={'refresh': '1234'})
        self.assertEqual(empty_tokenresponse.status_code, 400)


        login_response = self.client.post(
            '/api/token/',
            json.dumps({"username": self.host["username"], "password": self.host["password"]}),
            content_type='application/json')
        self.assertEqual(login_response.status_code, 200)
        self.assertContains(login_response, "refresh")

        authtestresponse = self.client.post('/api/authTest/', {"token": login_response.json()['refresh']})
        self.assertEqual(authtestresponse.status_code, 200)

        logoutresponse = self.client.post('/api/logout/')
        self.assertEqual(logoutresponse.status_code, 200)

        # Blacklisted refresh token after logout
        self.client.cookies = login_response.cookies   # outdated after logout
        _authtestresponse = self.client.post('/api/authTest/')
        self.assertEqual(_authtestresponse.status_code, 400)

        refreshresponse = self.client.get('/api/token/refresh/')
        self.assertEqual(refreshresponse.status_code, 401)

        

    def test_get_token_user(self):
        response = self.client.post('/api/token/', {"username":self.host["username"], "password":self.host["password"]}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "access")

        authtestresponse = self.client.get('/api/getUser/')
        self.assertEqual(authtestresponse.status_code, 200)
        self.assertEqual(authtestresponse.json().get("username"), self.host["username"])



class UserAPITest(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.host = {
            "username": "test_user",
            "email": "test_email@test.com",
            "first_name": "test_first_name",
            "last_name": "test_last_name",
            "password": "test_password",
        }
        cls.nonhost = {
            "username": "test_user2",
            "email": "test_email2@test.com",
            "first_name": "test_first_name2",
            "last_name": "test_last_name2",
            "password": "test_password2",
        }
        cls.client=APIClient()
        cls.userResponse = cls.client.post('/api/users/', json.dumps(cls.host), content_type='application/json')
        cls.userResponse2 = cls.client.post('/api/users/', json.dumps(cls.nonhost), content_type='application/json')

        cls.retHost = cls.userResponse.data
        cls.retNonHost = cls.userResponse2.data

    
    def setUp(self) -> None:
        return super().setUp()
    
    def test_create_user(self):
        self.assertEqual(self.userResponse.status_code, 201)
        self.assertEqual(self.userResponse.data.get('username'), self.host["username"])
        self.assertIsNotNone(User.objects.get(username=self.host["username"]))

    def test_list_users(self):
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_get_rest_user(self):
        pk = User.objects.get(username=self.host["username"]).id
        # vs = UserViewSet.as_view({'get': 'retrieve'})
        response = self.client.get(f'/api/users/{pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("username"), self.host["username"])


    def test_update_user(self):
        p2 = self.host.copy()
        p2["username"] = "test_user3"
        user = User.objects.get(username=self.host["username"])
        response = self.client.patch(f'/api/users/{user.id}/', json.dumps(p2), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("username"), p2["username"])
        self.assertIsNotNone(User.objects.get(username=p2["username"]).username)


class CourseAPITest(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.host = {
            "username": "test_user",
            "email": "test_email@test.com",
            "first_name": "test_first_name",
            "last_name": "test_last_name",
            "password": "test_password",
        }

        cls.host_cls = User.objects.create(**cls.host)
        cls.host_cls.set_password(cls.host['password'])
        cls.host_cls.save()
        cls.course = Course.objects.create(title="Test course", host=cls.host_cls)



    def setUp(self) -> None:
        return super().setUp()
    
    def test_create_course(self):
        # login required
        login_response = self.client.post(
            '/api/token/',
            json.dumps({"username": self.host["username"], "password": self.host["password"]}),
            content_type='application/json',
        )
        self.assertEqual(login_response.status_code, 200)
        newCourse = {'title':'Test course2', 'description_short':'short description', 'content_list':'content list', 'methods':'methods', 'material':'material', 'dates':'dates'}
        response = self.client.post('/api/courses/', json.dumps(newCourse), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["title"], newCourse["title"])
        self.assertEqual(response.data["host"]["username"], self.host["username"])
        self.assertIsNotNone(Course.objects.get(title=newCourse["title"]))

    def test_not_create_course_without_login(self):
        newCourse = {'title':'Test course2', 'description_short':'short description', 'content_list':'content list', 'methods':'methods', 'material':'material', 'dates':'dates'}
        response = self.client.post('/api/courses/', json.dumps(newCourse), content_type='application/json')
        self.assertEqual(response.status_code, 401)
    
    def test_update_course(self):
        login_response = self.client.post(
            '/api/token/',
            json.dumps({"username": self.host["username"], "password": self.host["password"]}),
            content_type='application/json',
        )
        p2 = {'title':'Test course2'}
        course = Course.objects.get(host=self.host_cls)
        response = self.client.patch(f'/api/courses/{course.id}/', json.dumps(p2), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("title"), p2["title"])
        self.assertIsNotNone(Course.objects.get(title=p2["title"]).title)

    def test_not_update_course_without_login(self):
        user2 = {
            "username": "test_user2",
            "email": "test_email2@test.com",
            "first_name": "test_first_name2",
            "last_name": "test_last_name2",
            "password": "test_password2",
        }

        user2_cls = User.objects.create(**user2)
        user2_cls.set_password(user2['password'])
        user2_cls.save()

        login_response = self.client.post(
            '/api/token/',
            json.dumps({"username": user2["username"], "password": user2["password"]}),
            content_type='application/json',
        )
        p2 = {'title':'Test course3'}
        course = Course.objects.first()
        response = self.client.patch(f'/api/courses/{course.id}/', json.dumps(p2), content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_list_courses(self):
        response = self.client.get('/api/courses/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
    
    def test_get_course(self):
        pk = Course.objects.get(title="Test course").id
        response = self.client.get(f'/api/courses/{pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("title"), "Test course")