#!/usr/bin/env python3


from modusa import excp
from modusa.decorators import validate_args_type
from modusa.io.base import ModusaIO
from typing import Any
from pathlib import Path
import yt_dlp

class YoutubeDownloader(ModusaIO):
	"""
	Download highest quality audio/video from YouTube.

	Note
	----
	- The engine uses `yt_dlp` python package to download content from YouTube.

	"""
	
	#--------Meta Information----------
	_name = "Youtube Downloader"
	_description = "Download highest quality audio/video from YouTube."
	_author_name = "Ankit Anand"
	_author_email = "ankit0.anand0@gmail.com"
	_created_at = "2025-07-05"
	#----------------------------------
	
	def __init__(self):
		super().__init__()
	
	@staticmethod
	@validate_args_type()
	def _download_audio(url: str, output_dir: str | Path):
		"""
		Download the highest quality audio from a given YouTube URL.

		Parameters
		----------
		url: str
			URL for the YouTube video.
		output_dir:
			Directory where the audio will be saved.

		Returns
		-------
		Path
			Path to the downloaded audio file.
		"""
		output_dir = Path(output_dir)
		output_dir.mkdir(parents=True, exist_ok=True)
		
		ydl_opts = {
				'format': 'bestaudio/best',
				'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
				'quiet': True,
			}
		
		with yt_dlp.YoutubeDL(ydl_opts) as ydl:
			info = ydl.extract_info(url, download=True)
			return Path(info['requested_downloads'][0]['filepath'])
	
	@staticmethod
	@validate_args_type()
	def _download_video(url: str, output_dir: str | Path):
		"""
		Download the highest quality video from a YouTube URL using yt-dlp.
	
		Parameters
		----------
		url: str
			URL for the YouTube video.
		output_dir:
			Directory where the video will be saved.

		Returns
		-------
		Path
			Path to the downloaded audio file
		"""
		output_dir = Path(output_dir)
		output_dir.mkdir(parents=True, exist_ok=True)
		
		ydl_opts = {
			'format': 'bestvideo+bestaudio/best',  # High quality
			'outtmpl': str(output_dir / '%(title)s.%(ext)s'),
			'merge_output_format': 'mp4',
			'quiet': True,  # Hide verbose output
		}
		
		with yt_dlp.YoutubeDL(ydl_opts) as ydl:
			info = ydl.extract_info(url, download=True)
			return Path(info['requested_downloads'][0]['filepath'])
	
	@staticmethod
	@validate_args_type()
	def download(url: str, content_type: str, output_dir: str | Path) -> Path:
		"""
		Downloads audio/video from YouTube.

		.. code-block:: python
			
			# To download audio
			from modusa.io import YoutubeDownloader
			audio_fp = YoutubeDownloader.download(
				url="https://www.youtube.com/watch?v=lIpw9-Y_N0g", 
				content_type="audio", 
				output_dir="."
			)
		
			# To download video
			from modusa.engines import YoutubeDownloaderEngine
			video_fp = YoutubeDownloader.download(
				url="https://www.youtube.com/watch?v=lIpw9-Y_N0g", 
				content_type="audio", 
				output_dir="."
			)

		Parameters
		----------
		url: str
			Link to the YouTube video.
		content_type: str
			"audio" or "video"
		output_dir: str | Path
			Directory to save the YouTube content.
		
		Returns
		-------
		Path
			File path of the downloaded content.
		
		"""
		if content_type == "audio":
			return YoutubeDownloader._download_audio(url=url, output_dir=output_dir)
		elif content_type == "video":
			return YoutubeDownloader._download_video(url=url, output_dir=output_dir)
		else:
			raise excp.InputValueError(f"`content_type` can either take 'audio' or 'video' not {content_type}")