import moviepy.editor
import moviepy.video.fx.all
import PIL.Image
import numpy

from .effect import Effect
from .effect_param import EffectParam

class MoviePyEffect(Effect):
    TYPE_NAME = "moviepy"

    APPLY_ON =  Effect.APPLY_TYPE_ALL

    PARAMS = [
        EffectParam('effect_type', 'str', None),
        EffectParam('effect_params', 'json', None)
    ]

    def __init__(self, effect_type, effect_params, **kwargs):
        super().__init__(**kwargs)
        self.effect_type = effect_type
        if effect_params is None:
            effect_params = {}
        self.effect_params = dict(effect_params)

    def get_name(self):
        return "{0}_{1}".format(self.TYPE_NAME, self.effect_type)

    def transform(self, image, progress, rel_time, clip, **kwargs):
        if not image:
            return image
        mclip = moviepy.editor.ImageClip(numpy.array(image))
        mclip.duration = clip.duration
        effect = getattr(moviepy.video.fx.all, self.effect_type)
        mclip = mclip.fx(effect, **self.effect_params)
        return PIL.Image.fromarray(mclip.get_frame(rel_time)).convert('RGBA')
