from moviepy.editor import VideoFileClip

class FileCache:
    _VideoObjects = {}

    @classmethod
    def get_video_clip(cls, filepath):
        if filepath not in cls._VideoObjects:
            cls.clear_cache()
            cls._VideoObjects[filepath] = VideoFileClip(filepath, has_mask=True)
        return cls._VideoObjects[filepath]

    @classmethod
    def clear_cache(cls):
        cls._VideoObjects.clear()
