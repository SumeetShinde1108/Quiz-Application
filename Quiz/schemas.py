import graphene
from graphene_django.types import DjangoObjectType
from quiz_app.models import (
    Quiz, 
    Question,
    Choice, 
    QuizAttempt, 
    AttemptedAnswers
)

class QuizType(DjangoObjectType):
    class Meta:
        model = Quiz

class QuestionType(DjangoObjectType):
    class Meta:
        model = Question

class ChoiceType(DjangoObjectType):
    class Meta:
        model = Choice

class QuizAttemptType(DjangoObjectType):
    class Meta:
        model = QuizAttempt

class AttemptedAnswersType(DjangoObjectType):
    class Meta:
        model = AttemptedAnswers

class Query(graphene.ObjectType):
    all_quizzes = graphene.List(QuizType)
    all_questions = graphene.List(QuestionType)
    all_choices = graphene.List(ChoiceType)
    all_attempts = graphene.List(QuizAttemptType)
    all_answers = graphene.List(AttemptedAnswersType)

    def resolve_all_quizzes(self, info):
        return Quiz.objects.all()

    def resolve_all_questions(self, info):
        return Question.objects.all()

    def resolve_all_choices(self, info):
        return Choice.objects.all()

    def resolve_all_attempts(self, info):
        return QuizAttempt.objects.all()

    def resolve_all_answers(self, info):
        return AttemptedAnswers.objects.all()

schema = graphene.Schema(query=Query)
