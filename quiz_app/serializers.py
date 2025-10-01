from rest_framework import serializers
from quiz_app.models import (
    Quiz, 
    Question, 
    Choice, 
    QuizAttempt, 
    AttemptedAnswers
)
    
    
class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct']
        read_only_fields = ['is_correct']


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'choices']


class AttemptedAnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.text', read_only=True)
    selected_choice_text = serializers.CharField(source='selected_choice.text', read_only=True)

    class Meta:
        model = AttemptedAnswers
        fields = ['id', 'question_text', 'selected_choice_text',
                  'is_correct', 'points_awarded']


class QuizAttemptSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username',
                                          read_only=True)
    answers = AttemptedAnswerSerializer(many=True,
                                        read_only=True)
    quiz_title = serializers.CharField(source='quiz.title',
                                       read_only=True)

    class Meta:
        model = QuizAttempt
        fields = ['id', 'user_username', 'quiz_title',
                  'start_time', 'end_time', 'score',
                  'feedback', 'answers']


class QuizDetailSerializer(serializers.ModelSerializer):
    creator_username = serializers.CharField(source='creator.username',
                                             read_only=True)
    questions = QuestionSerializer(many=True,
                                   read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description',
                  'creator_username', 'start_time', 'end_time',
                  'is_active', 'questions']


class QuizCreateSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description',
                  'start_time', 'end_time', 'is_active',
                  'questions']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        request = self.context.get('request')

        if request and hasattr(request, 'user'):
            validated_data['creator'] = request.user

        quiz = Quiz.objects.create(**validated_data)

        for question_data in questions_data:
            choices_data = question_data.pop('choices', [])
            question = Question.objects.create(quiz=quiz,
                                               **question_data)

            for choice_data in choices_data:
                Choice.objects.create(question=question,
                                      **choice_data)

        return quiz


class QuizAttemptCreateSerializer(serializers.ModelSerializer):
    answers = serializers.ListField(
        child=serializers.DictField(child=serializers.IntegerField()),
        write_only=True
    )

    class Meta:
        model = QuizAttempt
        fields = ['quiz', 'answers']

    def validate_answers(self, value):
        if not value:
            raise serializers.ValidationError("Answers cannot be empty.")

        for answer in value:
            if 'question' not in answer or 'selected_choice' not in answer:
                raise serializers.ValidationError(
                    "Each answer must contain 'question' and 'selected_choice' keys."
                )

            try:
                question = Question.objects.get(id=answer['question'])
                if not (question.choices.filter(id=answer['selected_choice'])
                        .exists()):
                    raise serializers.ValidationError(
                        f"Invalid choice for question ID {answer['question']}."
                    )
            except Question.DoesNotExist:
                raise serializers.ValidationError(f"Question ID {answer['question']} does not exist.")

        return value

    def create(self, validated_data):
        answers_data = validated_data.pop('answers', [])
        request = self.context.get('request')
        user = request.user if request and hasattr(request, 'user') else None
        validated_data.pop('user', None)
        quiz_attempt = QuizAttempt.objects.create(user=user, **validated_data)
        
        for answer_data in answers_data:
            AttemptedAnswers.objects.create(
            attempt=quiz_attempt,
            question_id=answer_data['question'],
            selected_choice_id=answer_data['selected_choice']
        )
        quiz_attempt.calculate_score()
    
        return quiz_attempt

    def update(self, instance, validated_data):
        answers_data = validated_data.pop('answers', [])
        instance.answers.all().delete()
        attempted_answers = []
        
        for answer_data in answers_data:
            question_id = answer_data['question']
            selected_choice_id = answer_data['selected_choice']

            question = Question.objects.get(id=question_id)
            correct_choice = question.choices.filter(is_correct=True).first()

            is_correct = correct_choice.id == selected_choice_id if correct_choice else False

            attempted_answers.append(
                AttemptedAnswers(
                    attempt=instance,
                    question_id=question_id,
                    selected_choice_id=selected_choice_id,
                    is_correct=is_correct
                )
            )
        AttemptedAnswers.objects.bulk_create(attempted_answers)
        
        instance.calculate_score()
        instance.save()
        
        return instance
