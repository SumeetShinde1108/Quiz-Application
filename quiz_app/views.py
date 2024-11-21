from rest_framework.generics import RetrieveAPIView , ListAPIView
from .models import Quiz , Leaderboard , QuizAttempt
from .serializers import QuizDetailSerializer , QuizAttemptSerializer , LeaderboardSerializer , QuizCreateSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.renderers import JSONRenderer


class QuizDetailView(RetrieveAPIView):
    
    queryset = Quiz.objects.prefetch_related('questions', 'leaderboard', 'attempts')
    serializer_class = QuizDetailSerializer


class LeaderboardView(ListAPIView):
    
    serializer_class = LeaderboardSerializer

    def get_queryset(self):
        
        quiz_id = self.kwargs['quiz_id']  
        return Leaderboard.objects.filter(quiz_id=quiz_id).order_by('rank')  


class QuizAttemptListView(APIView):
    
    def get(self, request, quiz_id):

        quiz_attempts = QuizAttempt.objects.filter(quiz__id=quiz_id).select_related('quiz').prefetch_related(
            'answers__question', 'answers__selected_choice'
        )

        if not quiz_attempts.exists():
            return Response({"detail": "No attempts found for the specified quiz."}, status=status.HTTP_404_NOT_FOUND)
        
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
