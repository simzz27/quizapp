from django.db import models

# Create your models here.

class Question(models.Model):
    text = models.CharField(max_length=255)
    option_1 = models.CharField(max_length=100)
    option_2 = models.CharField(max_length=100)
    option_3 = models.CharField(max_length=100)
    option_4 = models.CharField(max_length=100)
    correct_option = models.IntegerField()

    def __str__(self):
        return self.text

class QuizSession(models.Model):
    player_name = models.CharField(max_length=100, blank=True, null=True)
    total_questions = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    incorrect_answers = models.IntegerField(default=0)

    def __str__(self):
        return f"Session: {self.id}"