from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from rest_framework.authtoken.models import Token

from django.contrib.auth.models import User
from forum_app.models import Question, Answer


class AnswerApiTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.question = Question.objects.create(
            title="Test Question", content="Test Content", author=self.user)
        # self.client.login(username='testuser', password='password')

        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.answer = Answer.objects.create(
            content="Test Answer", author=self.user, question=self.question)

    def test_get_answer_list(self):
        url = reverse('answer-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    