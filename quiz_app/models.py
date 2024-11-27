from datetime import datetime
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.utils.timezone import now, make_aware


class Quiz(models.Model):
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_quizzes"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.end_time:
            if isinstance(self.end_time, str):
                self.end_time = datetime.fromisoformat(self.end_time.replace("Z", "+00:00"))
            if self.end_time.tzinfo is None:
                self.end_time = make_aware(self.end_time)
            self.is_active = self.end_time > now()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quizzes"
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['start_time', 'end_time']),
        ]


class Question(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions"
    )
    text = models.CharField(max_length=500)

    def __str__(self):
        return f"Question: {self.text} (Quiz: {self.quiz.title})"

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ['id']


class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="choices"
    )
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Choice: {self.text} (Question: {self.question.text})"

    class Meta:
        verbose_name = "Choice"
        verbose_name_plural = "Choices"


class QuizAttempt(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="quiz_attempts"
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,    
        related_name="attempts"
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    score = models.FloatField(default=0)
    feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Attempt by {self.user.username} for Quiz: {self.quiz.title}"

    def calculate_score(self):
        total_score = self.answers.aggregate(total=Sum('points_awarded'))['total'] or 0
        self.score = total_score
        self.save()

    class Meta:
        unique_together = ('user', 'quiz')
        verbose_name = "Quiz Attempt"
        verbose_name_plural = "Quiz Attempts"
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['quiz', 'user']),
        ]


class AttemptedAnswers(models.Model):
    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name="answers"
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    is_correct = models.BooleanField()
    points_awarded = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        self.is_correct = self.selected_choice.is_correct
        if self.is_correct:
            correct_choices = self.question.choices.filter(is_correct=True)
            total_correct = correct_choices.count()
            if total_correct > 0:
                points_per_correct_choice = 10 / total_correct
                self.points_awarded = points_per_correct_choice
            else:
                self.points_awarded = 0
        else:
            self.points_awarded = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Answer: {self.selected_choice.text} (Correct: {self.is_correct})" 

    class Meta:
        verbose_name = "Answer"
        verbose_name_plural = "Answers"
        ordering = ['id']
