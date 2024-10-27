from django.contrib import admin

# Register your models here.

from django.contrib import admin

from .models import Show, Episode, Quote, Clip

class ShowAdmin(admin.ModelAdmin):
    list_display = ("show_id", "name", "path",)

class EpisodeAdmin(admin.ModelAdmin):
    list_display = ("path", "show_id")

class QuoteAdmin(admin.ModelAdmin):
    list_display = ("quote_id", "episode_id", "quote_index", "quote_start", "quote_end", "quote_thumb_path")

class ClipAdmin(admin.ModelAdmin):
    list_display = ("clip_id", "quote_id", "clip_path", "clip_start", "clip_end", "clip_creation")

admin.site.register(Show, ShowAdmin)
admin.site.register(Episode, EpisodeAdmin)
admin.site.register(Quote, QuoteAdmin)
admin.site.register(Clip, ClipAdmin)

