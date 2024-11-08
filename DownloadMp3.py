from yt_dlp import YoutubeDL
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
import os


def youtube_to_mp3_with_cover(youtube_url, output_path='./', ffmpeg_path='path/to/ffmpeg'):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'ffmpeg_location': ffmpeg_path,
            'writethumbnail': True,
            'postprocessors': [
                {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '256'},
                {'key': 'EmbedThumbnail'}
            ],
            'postprocessor_args': ['-id3v2_version', '3']
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            title = info['title']
            mp3_file_path = os.path.join(output_path, f"{title}.mp3")
            thumbnail_file_path = os.path.join(output_path, f"{title}.jpg")

        audio = MP3(mp3_file_path, ID3=ID3)
        try:
            audio.add_tags()
        except error:
            pass

        with open(thumbnail_file_path, 'rb') as albumart:
            audio.tags.add(
                APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,
                    desc='Cover',
                    data=albumart.read()
                )
            )
        audio.save()
        print(f"MP3 with cover art saved at: {mp3_file_path}")
        os.remove(thumbnail_file_path)

    except Exception as e:
        print(f"An error occurred: {e}")


