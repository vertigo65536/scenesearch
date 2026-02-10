from django.http import HttpResponse
from django.shortcuts import render
from django.forms.models import model_to_dict
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
from .models import Quote, Clip, Episode, Show
from django.core import serializers
from django.db.models import Q
from django.conf import settings

import os
import string
import json
import shlex
import datetime

def home(request):
    context = {}
    context['showList'] = Show.objects.all()
    return render(request, "home.html", context)

def searchresults(request):
    show = request.GET.get("s")
    q = request.GET.get("q")
    vector = SearchVector('quote_text')
    query = SearchQuery(q, search_type="phrase")
    try:
        if q == None:
            q = ""
        q = q.translate(str.maketrans('', '', string.punctuation))
        object_list = Quote.objects.filter(quote_searchable_text__icontains=q)
        if not object_list:
            object_list = Quote.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.001).order_by()
        if show != "all":
            object_list = object_list.filter(episode_id__show_id__name = show)
        print(object_list)
        object_list = object_list[:50]
    except Quote.DoesNotExist:
        return None
    data = serializers.serialize('json', object_list)
    return HttpResponse(data, content_type="application/json")

def get_clipdata(request):
    error = ""
    template_name = 'genclip.html'
    variables = {}
    if request.method == 'POST':
        tValue = request.POST.get('t')
        qValue = request.POST.get('q')
        quote = Quote.objects.get(quote_id=qValue)
        if tValue == 's':
            start = quote.quote_start
            hour = start.hour
            end = add_time(start, 20)
        elif tValue == 'e':
            end = quote.quote_end
            start = add_time(end, -20)
        elif tValue == 'c':
            quoteTime = quote.quote_start
            start = add_time(quoteTime, -7)
            end = add_time(quoteTime, 13)
        elif tValue == 'j':
            start = quote.quote_start
            end = quote.quote_end
        existCheck = Clip.objects.filter(Q(quote_id=quote)).filter(Q(clip_start=start)).filter(Q(clip_end=end))
        if not existCheck.exists():
            episode = Episode.objects.get(path=quote.episode_id)
            newEntry = Clip.objects.create(
                    quote_id = quote,
                    clip_start = start,
                    clip_end = end
            )
            newEntry.refresh_from_db()
            outputname = str(newEntry.clip_id) + ".mp4"
            path = os.path.join(settings.CLIP_ROOT, outputname)
            ffmpegError = os.system("ffmpeg -y -ss "+str(start)+" -to "+str(end)+" -i " + shlex.quote(episode.path) + " -c:v libx264 -crf 27 -c:a aac -ac 1 -pix_fmt yuv420p -preset ultrafast -crf 27 -vf 'scale=720:-2' "+path+" -loglevel error")
            if ffmpegError != 0:
                newEntry.delete()
                variables['error'] = "ffmpeg encoding failed!"
            else:
                newEntry.clip_path = path
                newEntry.save()
            variables['video'] = settings.MEDIA_SERVER + outputname
            return render(request, template_name, variables)
        else:
            for clip in existCheck:
                videoLink = clip.clip_path.replace(settings.CLIP_ROOT, settings.MEDIA_SERVER)
                variables['video'] = videoLink
        return render(request, template_name, variables)
    else:
        return HttpResponseRedirect('/')

def add_time(time, value):
    hour = time.hour
    minute = time.minute
    second = time.second
    microsecond = time.second
    second = second + value
    if second >= 60:
        second -= 60
        minute += 1
        if minute >= 60:
            minute -= 60
            hour += 1
    elif second < 00:
        second += 60
        minute -= 1
        if minute < 00:
            minute += 60
            hour += 1
    return datetime.time(
            hour = hour,
            minute = minute,
            second = second,
            microsecond = microsecond
    )

