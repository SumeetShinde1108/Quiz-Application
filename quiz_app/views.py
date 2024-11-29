from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from django.utils.timezone import now
from django.shortcuts import get_object_or_404

from .models import Quiz, QuizAttempt
from .serializers import (
    QuizDetailSerializer,
    QuizAttemptSerializer,
    QuizCreateSerializer,
    QuizAttemptCreateSerializer, 
)


class QuizDetailView(RetrieveAPIView):
    queryset = Quiz.objects.prefetch_related('questions')
    serializer_class = QuizDetailSerializer


class QuizAttemptListView(APIView):    
    def get(self, request, quiz_id):
        quiz_attempts = QuizAttempt.objects.filter(
            quiz__id=quiz_id
        ).select_related('quiz').prefetch_related(
            'answers__question', 'answers__selected_choice'
        )

        if not quiz_attempts.exists():
            return Response(
                {"detail": "No attempts found for the specified quiz."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = QuizAttemptSerializer(quiz_attempts, many=True)
        return Response(serializer.data)


class QuizCreateView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]

    def post(self, request, *args, **kwargs):
        serializer = QuizCreateSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            quiz = serializer.save()
            return Response(
                {"message": "Quiz created successfully!", "quiz_id": quiz.id},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuizAttemptCRUDView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        quiz_id = request.data.get("quiz")
        if not quiz_id:
            return Response({"detail": "Quiz ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            quiz = Quiz.objects.get(id=quiz_id)
            if not quiz.is_active or not (quiz.start_time <= now() <= quiz.end_time):
                return Response(
                    {"detail": "The quiz is not active or has expired."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Quiz.DoesNotExist:
            return Response({"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND)

        if QuizAttempt.objects.filter(quiz=quiz, user=request.user).exists():
            return Response(
                {"detail": "You have already attempted this quiz."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = QuizAttemptCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            quiz_attempt = serializer.save(user=request.user, quiz=quiz)
            return Response(
                {"message": "Quiz attempt created successfully!", "quiz_attempt_id": quiz_attempt.id},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        attempt_id = kwargs.get('attempt_id')
        if not attempt_id:
            return Response({"detail": "Attempt ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            quiz_attempt = QuizAttempt.objects.select_related('quiz', 'user').prefetch_related('answers').get(
                id=attempt_id, user=request.user
            )
        
        except QuizAttempt.DoesNotExist:
            return Response({"detail": "Quiz attempt not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = QuizAttemptSerializer(quiz_attempt)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        attempt_id = kwargs.get('attempt_id')
        if not attempt_id:
            return Response({"detail": "Attempt ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        print(f"Attempt ID received: {attempt_id}")
        print(f"User making the request: {request.user}")

        try:
            quiz_attempt = QuizAttempt.objects.get(id=attempt_id, user=request.user)
            print(f"QuizAttempt found: {quiz_attempt}")
        
        except QuizAttempt.DoesNotExist:
            print("QuizAttempt not found or user not authorized.")
            return Response(
                {"detail": "Quiz attempt not found or not authorized to update."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = QuizAttemptCreateSerializer(
            quiz_attempt, data=request.data, partial=True, context={'request': request}
        )
        if serializer.is_valid():
            quiz_attempt = serializer.save()
            return Response(
                {"message": "Quiz attempt updated successfully!", "quiz_attempt_id": quiz_attempt.id},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        attempt_id = kwargs.get('attempt_id')
        if not attempt_id:
            return Response({"detail": "Attempt ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            quiz_attempt = QuizAttempt.objects.get(id=attempt_id, user=request.user)
        
        except QuizAttempt.DoesNotExist:
            return Response(
                {"detail": "Quiz attempt not found or not authorized to delete."},
                status=status.HTTP_404_NOT_FOUND
            )

        quiz_attempt.delete()
        return Response(
            {"message": "Quiz attempt deleted successfully!"},
            status=status.HTTP_204_NO_CONTENT
        )


class LeaderboardView(APIView):
    def get(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, id=quiz_id)
        attempts = QuizAttempt.objects.filter(quiz=quiz).order_by('-score')
        leaderboard = [
            {
                "username": attempt.user.username,
                "score": attempt.score,
                "rank": rank + 1
            }
            for rank, attempt in enumerate(attempts)
        ]

        return Response(
            {
                "quiz_title": quiz.title,
                "leaderboard": leaderboard,
            },
            status=status.HTTP_200_OK
        )