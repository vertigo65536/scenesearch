from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.db.models import Q
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
from django.conf import settings
from django.contrib.postgres.search import TrigramWordDistance
import os
from django.http import HttpResponseRedirect
import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework import permissions

from .serializers import QuoteSerializer 
# Create your views here.

from .models import Quote, Clip, Episode

def add_time(time, value):
    hour = time.hour
    minute = time.minute
    second = time.second
    microsecond = time.second
    second = second + value
    if second > 60:
        second -= 60
        minute += 1
        if minute > 60:
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

def searchQuote(query, show=None):
    try:
        object_list = Quote.objects.annotate(
            distance=TrigramWordDistance(query, 'quote_text'),
        ).filter(distance__lte=0.5).order_by('distance')
        if show != None:
            object_list = object_list.filter(episode_id__show_id__name = show)
        return object_list
    except Quote.DoesNotExist:
        return None


class HomePageView(TemplateView):
    template_name = 'home.html'
    videoPath = "/home/david/Videos/TV Shows/Season 06/South Park - S06E17 - Red Sleigh Down.mp4"
    #print(os.path.isfile(videoPath))
    #print(settings.MEDIA_ROOT)
    #ffmpeg_extract_subclip(videoPath, 33, 53, targetname="test.mp4")
    #os.system("ffmpeg -y -ss 00:00:30 -to 00:00:50 -i '" + videoPath + "' -c copy test.mp4")

class SearchResultsView(ListView):
    model = Quote
    template_name = 'search_results.html'
    def get_queryset(self):
        q = self.request.GET.get("q")
        object_list = Quote.objects.annotate(
            distance=TrigramWordDistance(q, 'quote_text'),
        ).filter(distance__lte=0.5).order_by('distance')
        return object_list

class GenClipView(TemplateView):
    template_name = 'genclip.html'

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
                ffmpegError = os.system("ffmpeg -y -ss "+str(start)+" -to "+str(end)+" -i '" + episode.path + "' -vcodec libx264 -f mp4 "+path+" -loglevel error")
                if ffmpegError != 0:
                    newEntry.delete()
                    variables['error'] = "ffmpeg encoding failed!"
                else:
                    print(newEntry.clip_id)
                    newEntry.clip_path = path
                    newEntry.save()
                variables['video'] = settings.MEDIA_SERVER + outputname
                return render(request, template_name, variables)
            else:
                print("Triggered")
                for clip in existCheck:
                    videoLink = clip.clip_path.replace(settings.CLIP_ROOT, settings.MEDIA_SERVER)
                    variables['video'] = videoLink
            return render(request, template_name, variables)
        else:
            return HttpResponseRedirect('/')

class ShowsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    print(permission_classes)
    def get(self, request, show=None, query = None, *args, **kwargs):
        '''
        Retrieves the Todo with given todo_id
        '''
        quote_objects = searchQuote(query, show)
        if not quote_objects:
            return Response(
                {"res": "Object matching quote does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = QuoteSerializer(quote_objects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

