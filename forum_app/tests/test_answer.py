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

    def test_update_answer_without_permission(self):
        # Create a second user to try to edit the answer
        another_user = User.objects.create_user(username="anotheruser", password="password")
        token = Token.objects.create(user=another_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        url = reverse('answer-detail', args=[self.answer.id])
        data = {'content': 'Updated by Unauthorized User'}
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_answer_as_owner(self):
        url = reverse('answer-detail', args=[self.answer.id])
        data = {'content': 'Updated Answer by Owner'}
        response = self.client.patch(url, data, format='json')        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Updated Answer by Owner')
        self.answer.refresh_from_db()
        self.assertEqual(self.answer.content, 'Updated Answer by Owner')
        self.assertEqual(self.answer.author, self.user)

    def test_get_answer_detail(self):
        url = reverse('answer-detail', args=[self.answer.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], self.answer.content)
        # self.assertEqual(response.data['author'], self.user.username)
        
    def test_delete_answer_as_owner(self):
        url = reverse('answer-detail', args=[self.answer.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Answer.objects.count(), 0)
    
    def test_delete_answer_without_permission(self):
        another_user = User.objects.create_user(username="anotheruser2", password="password")
        token = Token.objects.create(user=another_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        url = reverse('answer-detail', args=[self.answer.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Answer.objects.count(), 1)
        
    def test_get_answer_list_filtered_by_author(self):
        # Create another answer by a different user
        another_user = User.objects.create_user(username="anotheruser3", password="password")
        Answer.objects.create(content="Another Answer", author=another_user, question=self.question)

        url = reverse('answer-list-create') + f'?author={self.user.username}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], self.answer.content)
    
    def test_get_answer_list_search_content(self):
        # Create another answer with different content
        Answer.objects.create(content="Different Content Answer", author=self.user, question=self.question)
        Answer.objects.create(content="different content answer", author=self.user, question=self.question) # Teste klein

        url = reverse('answer-list-create') + '?search=Content'  # Search for "Content"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_get_answer_list_ordering(self):
        # Create another answer
        Answer.objects.create(content="AAA Content", author=self.user, question=self.question)
        Answer.objects.create(content="BBB Content", author=self.user, question=self.question)

        url = reverse('answer-list-create') + '?ordering=content' # ASC
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['content'], "AAA Content")