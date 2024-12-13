import yt_dlp


class YtHelper:
    def search_youtube_videos(self, query, max_results=5):
        with yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': True, 'get_id': True}) as ydl:
            results = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
            videos = [(video['title'], f"{int(video['duration']//60)}:{int(video['duration']%60)}", video['url']) for video in results.get('entries', [])]
        return videos

