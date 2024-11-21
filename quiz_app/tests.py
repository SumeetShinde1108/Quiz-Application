from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase
from .models import Quiz, User
from django.utils import timezone


class QuizApiTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.quiz1 = Quiz.objects.create(
            creator=self.user,
            title="Test Quiz 1",
            description="A sample quiz",
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=1)
        )
        self.quiz2 = Quiz.objects.create(
            creator=self.user,
            title="Test Quiz 2",
            description="Another sample quiz",
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=1)
        )


    def test_get_single_quiz(self):
        url = reverse('quiz-detail', kwargs={'pk': self.quiz1.pk})  
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_quiz_leaderboard(self):
        url = reverse('quiz-leaderboard', kwargs={'quiz_id': self.quiz1.pk})  
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_quiz(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quiz-create')
        payload = {
            "title": "New Quiz",
            "description": "Test Quiz",
            "start_time": (timezone.now()).isoformat(),
            "end_time": (timezone.now() + timezone.timedelta(hours=1)).isoformat(),
            "is_active": True,
            "questions": [
                {
                    "text": "Sample Question?",
                    "choices": [
                        {"text": "Option 1", "is_correct": False},
                        {"text": "Option 2", "is_correct": True},
                    ]
                }
            ]
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('quiz_id', response.data)  
