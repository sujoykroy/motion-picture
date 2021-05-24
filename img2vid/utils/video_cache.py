import sys
from moviepy.editor import VideoFileClip

class VideoCache:
    _VideoObjects = {}

    @classmethod
    def get_video_clip(cls, filepath):
        if filepath not in cls._VideoObjects:
            cls.clear_cache()
            cls._VideoObjects[filepath] = VideoFileClip(filepath, has_mask=True)
        return cls._VideoObjects[filepath]

    @classmethod
    def clear_cache(cls):
        for clip in cls._VideoObjects.values():
            cls.close_clip(clip)
        cls._VideoObjects.clear()

    @classmethod
    def close_clip(cls, clip):
        try:
            clip.reader.close()
            del clip.reader
            if clip.audio != None:
                clip.audio.reader.close_proc()
                del clip.audio
            del clip
        except Exception as e:
            pass

