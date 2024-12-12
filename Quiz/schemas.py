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
        fields = "__all__"

class QuestionType(DjangoObjectType):
    class Meta:
        model = Question
        fields = "__all__"

class ChoiceType(DjangoObjectType):
    class Meta:
        model = Choice
        fields = "__all__"

class QuizAttemptType(DjangoObjectType):
    class Meta:
        model = QuizAttempt
        fields = "__all__"

class AttemptedAnswersType(DjangoObjectType):
    class Meta:
        model = AttemptedAnswers
        fields = "__all__"

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

class CreateQuiz(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=False)

    quiz = graphene.Field(QuizType)

    def mutate(self, info, name, description=None):
        quiz = Quiz.objects.create(name=name, description=description)
        return CreateQuiz(quiz=quiz)

class Mutation(graphene.ObjectType):
    create_quiz = CreateQuiz.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
