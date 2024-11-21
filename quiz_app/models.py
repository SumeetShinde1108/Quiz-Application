from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils.timezone import now, make_aware
from datetime import datetime


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
    points = models.IntegerField(default=0, blank=True)

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
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Attempt by {self.user.username} for Quiz: {self.quiz.title}"

    class Meta:
        unique_together = ('user', 'quiz')
        verbose_name = "Quiz Attempt"
        verbose_name_plural = "Quiz Attempts"
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['quiz', 'user']),
        ]


class Answer(models.Model):
    attempt = models.ForeignKey(
        QuizAttempt, 
        on_delete=models.CASCADE, 
        related_name="answers"
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    is_correct = models.BooleanField()

    def save(self, *args, **kwargs):
        self.is_correct = self.selected_choice.is_correct
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Answer: {self.selected_choice.text} (Correct: {self.is_correct})"

    class Meta:
        verbose_name = "Answer"
        verbose_name_plural = "Answers"
        ordering = ['id']


class Leaderboard(models.Model):
    quiz = models.ForeignKey(
        Quiz, 
        on_delete=models.CASCADE, 
        related_name="leaderboard"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    rank = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"Leaderboard Entry: {self.user.username} (Quiz: {self.quiz.title}, Rank: {self.rank})"

    def save(self, *args, **kwargs):
        if not kwargs.pop('skip_rank_update', False):
            super().save(*args, **kwargs)
            self.update_ranks()
        else:
            super().save(*args, **kwargs)

    def update_ranks(self):
        leaderboard_entries = Leaderboard.objects.filter(
            quiz=self.quiz
        ).order_by('-score', 'id')

        previous_score = None
        rank = 0

        for index, entry in enumerate(leaderboard_entries, start=1):
            if entry.score != previous_score:
                rank = index

            if entry.rank != rank:
                entry.rank = rank
                entry.save(skip_rank_update=True)

            previous_score = entry.score

    class Meta:
        unique_together = ('quiz', 'user')
        ordering = ['rank']
        verbose_name = "Leaderboard Entry"
        verbose_name_plural = "Leaderboard Entries"
        indexes = [
            models.Index(fields=['quiz']),
            models.Index(fields=['rank']),
        ]
