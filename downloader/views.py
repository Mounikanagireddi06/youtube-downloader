from django.shortcuts import render, redirect
from django.http import HttpResponse
import yt_dlp
from urllib.parse import unquote
import mimetypes
import os

def home(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        if url:
            return redirect('download_video', url=url)
    return render(request, 'downloader/home.html')

def download_video(request, url):
    url = unquote(url)  # Decode the URL
    downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(downloads_dir, '%(title)s.%(ext)s'),
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_title = info_dict.get('title', None)
        video_filename = ydl.prepare_filename(info_dict)

    # Get the absolute path of the downloaded file
    video_path = os.path.join(os.getcwd(), video_filename)

    # Check if the file exists
    if os.path.exists(video_path):
        # Determine the content type and file extension
        content_type, _ = mimetypes.guess_type(video_path)
        if content_type is None:
            content_type = 'application/octet-stream'

        # Open the file for reading as binary
        with open(video_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type=content_type)
            # Set the HTTP headers for file attachment
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(video_path)}"'
            return response
    else:
        return HttpResponse("Failed to download the video.")

    return HttpResponse(f"Downloaded video: {video_title} - {video_filename}")
