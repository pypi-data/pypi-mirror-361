#!/usr/bin/env python3


#--------Meta Information----------
class_name = "YoutubeDownloaderEngine"
author_name = "Ankit Anand"
author_email = "ankit0.anand0@gmail.com"
created_at = "2025-07-05"
#----------------------------------
	
from modusa.engines import YoutubeDownloaderEngine

YTE = YoutubeDownloaderEngine()


def test_download_audio():
	YTE.download_audio(url="", output_dir="")
	
def test_download_video():
	YTE.download_video(url="", output_dir="")