from django.contrib import admin
from .models import Quiz, Question, Choice, QuizAttempt, Answer, Leaderboard


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1  
    show_change_link = True 


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'creator', 'start_time', 'end_time', 'is_active')  
    list_filter = ('is_active', 'start_time', 'end_time') 
    search_fields = ('title', 'description', 'creator__username') 
    inlines = [QuestionInline] 
    prepopulated_fields = {'title': ('description',)}  
    date_hierarchy = 'start_time'  


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz')  
    list_filter = ('quiz',)  
    search_fields = ('text', 'quiz__title')  


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct')  
    list_filter = ('is_correct', 'question')  
    search_fields = ('text', 'question__text')  


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0  
    readonly_fields = ('is_correct',)  
    show_change_link = True


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'start_time', 'end_time') 
    list_filter = ('quiz', 'user')  
    search_fields = ('user__username', 'quiz__title')  
    inlines = [AnswerInline] 
    readonly_fields = ('score', 'start_time', 'end_time')  


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'selected_choice', 'is_correct') 
    list_filter = ('is_correct', 'question') 
    search_fields = ('question__text', 'attempt__user__username')  


@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'user', 'score', 'rank')  
    list_filter = ('quiz',)  
    search_fields = ('quiz__title', 'user__username')  
    readonly_fields = ('rank',) 
