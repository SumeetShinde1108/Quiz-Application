from django.contrib import admin
from .models import Quiz, Question, Choice, QuizAttempt, AttemptedAnswers


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


class AttemptedAnswersInline(admin.TabularInline):
    model = AttemptedAnswers
    extra = 0


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'creator', 'start_time', 'end_time', 'is_active')
    list_filter = ('is_active', 'start_time', 'end_time')
    search_fields = ('title', 'creator__username')
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz')
    search_fields = ('text',)
    list_filter = ('quiz',)
    inlines = [ChoiceInline]


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct')
    list_filter = ('question', 'is_correct')
    search_fields = ('text',)


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'quiz', 'start_time', 'end_time', 'score')
    list_filter = ('quiz', 'start_time', 'end_time')
    search_fields = ('user__username', 'quiz__title')
    inlines = [AttemptedAnswersInline]


@admin.register(AttemptedAnswers)
class AttemptedAnswersAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'selected_choice', 'is_correct', 'points_awarded')
    list_filter = ('is_correct', 'question')
    search_fields = ('question__text', 'selected_choice__text')
