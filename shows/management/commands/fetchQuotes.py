from django.core.management.base import BaseCommand
from shows.models import Show, Quote, Episode
from django.conf import settings
import os
import srt
import string

class Command(BaseCommand):
    help = "Fetch all quotes from shows in the database"

    def add_arguments(self, parser):
        parser.add_argument("-f", "--force", help="Force Show", nargs="?", default=False, type=int)

    def handle(self, *args, **options):

        def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
            """
            Call in a loop to create terminal progress bar
            @params:
                iteration   - Required  : current iteration (Int)
                total       - Required  : total iterations (Int)
                prefix      - Optional  : prefix string (Str)
                suffix      - Optional  : suffix string (Str)
                decimals    - Optional  : positive number of decimals in percent complete (Int)
                length      - Optional  : character length of bar (Int)
                fill        - Optional  : bar fill character (Str)
                printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
            """
            percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
            percent = ' '*(5-len(percent)) + percent
            filledLength = int(length * iteration // total)
            bar = fill * filledLength + '-' * (length - filledLength)
            width = os.get_terminal_size()[0]-4
            barLength = len(f' |{bar}| {percent}% {suffix}')
            prefix = prefix[:width-barLength-3] + (prefix[width-barLength-3:] and '...')
            fillSpaceLength = width - len(prefix) - barLength
            prefix = prefix + ' '*fillSpaceLength
            print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
            # Print New Line on Complete
            if iteration == total: 
                print()


        if options['force'] == None:
            Episode.objects.all().delete()
        elif options['force'] != False:
            show = Show.objects.get(pk=options['force'])
            Episode.objects.filter(show_id=show).all().delete()
        #return
        showlist = Show.objects.all()
        thumbPath = settings.CLIP_ROOT
        for show in showlist:
            showThumbPath = os.path.join(thumbPath, str(show.name))
            if not os.path.isdir(showThumbPath):
                os.mkdir(os.path.join(thumbPath, show.name))
            for root, dirs, files in os.walk(show.path):
                for file in files:
                    if file.endswith((".mkv", ".mp4", ".avi")):
                        vidPath = os.path.join(root, file)
                        existsCheck = Episode.objects.filter(path = vidPath)
                        if existsCheck:
                            print("DB Entry exists for " + vidPath + ". Skipping.")
                            continue
                        for rfile in files:
                            if os.path.splitext(file)[0] in rfile and rfile.endswith(".srt"):
                                subPath = os.path.join(root, rfile)
                        try:
                            Episode.objects.create(
                                    show_id = show,
                                    path = vidPath
                            )
                        except:
                            print("No sub for " + vidPath)
                            continue
                        episodeThumbPath = os.path.join(showThumbPath, os.path.splitext(file)[0])
                        if not os.path.isdir(episodeThumbPath):
                            os.mkdir(episodeThumbPath)
                        with open(subPath, 'r') as subFile:
                            sub = list(srt.parse(subFile.read()))
                            for i in range(len(sub)):
                                loadingLength = 50
                                printProgressBar(i, total=len(sub)-1, prefix=file, length=loadingLength, fill="#")
                                quoteThumbPath = os.path.join(episodeThumbPath, str(sub[i].index) + ".bmp")
                                #os.system("ffmpeg -y -i '" + vidPath + "' -ss " + str(sub[i].start) + " -s 150x85 -vframes 1 '" + quoteThumbPath + "' -loglevel error")
                                Quote.objects.create(
                                        episode_id=Episode.objects.get(path=vidPath),
                                        quote_index = sub[i].index,
                                        quote_text = sub[i].content,
                                        quote_searchable_text = sub[i].content.translate(str.maketrans('', '', string.punctuation)),
                                        quote_start = str(sub[i].start),
                                        quote_end = str(sub[i].end),
                                        quote_thumb_path = quoteThumbPath
                                        )
