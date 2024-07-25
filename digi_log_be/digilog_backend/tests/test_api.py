

from django.test import TestCase
from digilog_backend.models import Course, User, Attendee
from rest_framework.test import APIRequestFactory, RequestsClient, APIClient
import json
# from digilog_backend.views import CourseViewSet, UserViewSet

factory = APIRequestFactory()

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
        # cls.UserViewSet = UserViewSet.as_view({'post': 'create', 'get': 'list'})
        cls.client=APIClient()
        cls.userResponse = cls.client.post('/api/users/', json.dumps(cls.host), content_type='application/json')
        # cls.userResponse = cls.UserViewSet(request)

        cls.userResponse2 = cls.client.post('/api/users/', json.dumps(cls.nonhost), content_type='application/json')
        # cls.userResponse2 = cls.UserViewSet(request)

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

    def test_get_user(self):
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
        cls.course = Course.objects.create(title="Test course", host=cls.host_cls)



    def setUp(self) -> None:
        return super().setUp()
    
    
    def test_create_course(self):
        
        newCourse = {'title':'Test course', 'host':self.host_cls.id, 'description_short':'short description', 'content_list':'content list', 'methods':'methods', 'material':'material', 'dates':'dates'}
        response = self.client.post('/api/courses/', json.dumps(newCourse), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(newCourse.title, "Test course")
        self.assertEqual(newCourse.host, self.host_cls)
        self.assertIsNotNone(Course.objects.get(title=newCourse["title"]))
    
    def test_list_courses(self):
        response = self.client.get('/api/courses/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
    
    def test_get_course(self):
        pk = Course.objects.get(title="Test course").id
        response = self.client.get(f'/api/courses/{pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("title"), "Test course")