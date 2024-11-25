from rest_framework import serializers
from .models import Quiz, Choice, Question, QuizAttempt, AttemptedAnswers


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


class QuizAttemptSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    answers = serializers.SerializerMethodField()
    quiz_name = serializers.CharField(source='quiz.title', read_only=True)

    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'user', 'user_username', 'quiz_name',
            'start_time', 'end_time', 'answers'
        ]

    def get_answers(self, obj):
        answers = obj.answers.all()
        return [
            {
                "question": answer.question.text,
                "selected_choice": answer.selected_choice.text,
                "Answer_is": answer.is_correct,
                "correct_answer": self.get_correct_answer(answer.question)
            }
            for answer in answers
        ]

    def get_correct_answer(self, question):
        correct_choices = question.choices.filter(is_correct=True)
        return [choice.text for choice in correct_choices] if correct_choices.exists() else None


class QuizDetailSerializer(serializers.ModelSerializer):
    creator_username = serializers.CharField(source='creator.username', read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)
    leaderboard = serializers.SerializerMethodField()
    attempts = QuizAttemptSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'creator_username', 'start_time', 'end_time',
            'is_active', 'questions', 'leaderboard', 'attempts'
        ]

    def get_leaderboard(self, obj):
        leaderboard_entries = obj.leaderboard.all().order_by('rank')
        return [
            {
                "user": entry.user.username,
                "score": entry.score,
                "rank": entry.rank
            }
            for entry in leaderboard_entries
        ]


class QuizCreateSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'start_time', 'end_time',
            'is_active', 'questions'
        ]

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        request = self.context.get('request')

        if request and hasattr(request, 'user'):
            validated_data['creator'] = request.user

        quiz = Quiz.objects.create(**validated_data)

        for question_data in questions_data:
            question_data['quiz'] = quiz
            QuestionSerializer().create(question_data)

        return quiz


class QuizAttemptCreateSerializer(serializers.ModelSerializer):
    answers = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField(),
            help_text="Each answer must include question and selected_choice IDs."
        ),
        write_only=True,
        help_text="Provide a list of answers with question and selected_choice IDs."
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
