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

    def test_post_answer(self):
        url = reverse('answer-list-create')
        data = {
            'content': 'New Test Answer',
            'author': self.user.id,
            'question': self.question.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['question'], self.question.id)

    def test_post_answer_without_authentication(self):
        url = reverse('answer-list-create')
        data = {
            'content': 'Unauthenticated Test Answer',
            'author': self.user.id,
            'question': self.question.id
        }
        self.client.credentials()  # Clear the authorization header
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_answer_with_missing_content(self):
        url = reverse('answer-list-create')
        data = {
            'author': self.user.id,
            'question': self.question.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('content', response.data)

    def test_post_answer_with_invalid_question(self):
        url = reverse('answer-list-create')
        data = {
            'content': 'Test Answer for Invalid Question',
            'author': self.user.id,
            'question': 99999  # Invalid question ID
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_update_answer_without_permission(self):
    #     # Create a second user to try to edit the answer
    #     another_user = User.objects.create_user(username="anotheruser", password="password")
    #     token = Token.objects.create(user=another_user)
    #     self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    #     url = reverse('answer-detail', args=[self.answer.id])
    #     data = {'content': 'Updated by Unauthorized User'}
    #     response = self.client.put(url, data, format='json')

    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_update_answer_as_owner(self):
    #     url = reverse('answer-detail', args=[self.answer.id])
    #     data = {'content': 'Updated Answer by Owner'}
    #     response = self.client.put(url, data, format='json')        
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['content'], 'Updated Answer by Owner')
    #     self.answer.refresh_from_db()
    #     self.assertEqual(self.answer.content, 'Updated Answer by Owner')
    #     self.assertEqual(self.answer.author, self.user)
