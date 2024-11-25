from rest_framework import serializers
from .models import Quiz, Question, Choice, QuizAttempt, AttemptedAnswers


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct']
        read_only_fields = ['is_correct']


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'choices']


class AttemptedAnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.text', read_only=True)
    selected_choice_text = serializers.CharField(source='selected_choice.text', read_only=True)

    class Meta:
        model = AttemptedAnswers
        fields = ['id', 'question_text', 'selected_choice_text', 'is_correct', 'points_awarded']


class QuizAttemptSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    answers = AttemptedAnswerSerializer(many=True, read_only=True)
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)

    class Meta:
        model = QuizAttempt
        fields = ['id', 'user_username', 'quiz_title', 'start_time', 'end_time', 'score', 'feedback', 'answers']


class QuizDetailSerializer(serializers.ModelSerializer):
    creator_username = serializers.CharField(source='creator.username', read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'creator_username', 'start_time', 'end_time', 'is_active', 'questions']


class QuizCreateSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'start_time', 'end_time', 'is_active', 'questions']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        request = self.context.get('request')

        if request and hasattr(request, 'user'):
            validated_data['creator'] = request.user

        quiz = Quiz.objects.create(**validated_data)

        for question_data in questions_data:
            question_data['quiz'] = quiz
            Question.objects.create(**question_data)

        return quiz


class QuizAttemptCreateSerializer(serializers.ModelSerializer):
    answers = serializers.ListField(
        child=serializers.DictField(child=serializers.IntegerField()),
        write_only=True
    )

    class Meta:
        model = QuizAttempt
        fields = ['quiz', 'answers']

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        request = self.context.get('request')
        user = request.user if request and hasattr(request, 'user') else None

        quiz_attempt = QuizAttempt.objects.create(user=user, **validated_data)

        for answer_data in answers_data:
            AttemptedAnswers.objects.create(
                attempt=quiz_attempt,
                question_id=answer_data['question'],
                selected_choice_id=answer_data['selected_choice']
            )

        quiz_attempt.calculate_score()
        return quiz_attempt
