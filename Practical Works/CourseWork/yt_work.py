import yt_dlp


class YtHelper:
    def search_youtube_videos(self, query, max_results=5):
        with yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': True, 'get_id': True}) as ydl:
            results = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
            videos = [(video['title'], self._get_duration(video['duration']), video['url']) for video in results.get('entries', [])]
        return videos

    def _get_duration(self, duration):
        if duration:
            return f"{int(duration//60)}:{int(duration)%60}"
        else:
            return "0"

