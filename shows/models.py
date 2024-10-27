from django.db import models
import uuid

# Create your models here.

class Show(models.Model):
    show_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=65536)

    class Meta:
      verbose_name_plural = "shows"

    def __str__(self):
        return self.name

class Episode(models.Model):
    #episode_id = models.AutoField(primary_key=True)
    show_id = models.ForeignKey('Show', on_delete=models.CASCADE)
    path = models.CharField(max_length=65536, primary_key=True)
    class Meta:
        verbose_name_plural = "episodes"
    def __str__(self):
        return str(self.path)

class Quote(models.Model):
    quote_id = models.AutoField(primary_key=True)
    episode_id = models.ForeignKey('Episode', on_delete=models.CASCADE)
    quote_index = models.IntegerField()
    quote_text = models.CharField(max_length=65536)
    quote_start = models.TimeField(auto_now=False, auto_now_add=False)
    quote_end = models.TimeField(auto_now=False, auto_now_add=False)
    quote_thumb_path = models.CharField(max_length=65563)
    class Meta:
        verbose_name_plural = "quotes"
    def __str__(self):
        return str(self.quote_id)

class Clip(models.Model):
    clip_id = models.AutoField(primary_key=True)
    quote_id = models.ForeignKey('Quote', on_delete=models.CASCADE)
    clip_path = models.CharField(max_length=65536)
    clip_start = models.TimeField(auto_now=False, auto_now_add=False)
    clip_end = models.TimeField(auto_now=False, auto_now_add=False)
    clip_creation = models.TimeField(auto_now=True)
    class Meta:
        verbose_name_plural = "clips"
    def __str__(self):
        return str(self.clip_id)

