import tempfile

import moviepy.editor as mve
import PIL.Image
import numpy
from moviepy.video.tools.segmenting import findObjects

from .effect import Effect
from .effect_param import EffectParam

class CoolText(Effect):
    TYPE_NAME = "cool_text"
    APPLY_ON = Effect.APPLY_TYPE_TEXT

    def __init__(self):
        super().__init__()

    def transform(self, image, slide, progress, **kwargs):
        screensize = (image.width, image.height)
        # text_file = tempfile.NamedTemporaryFile(mode="w")
        # text_file.write(slide.caption.text)
        # text_file.seek(0)
        txtClip = mve.TextClip(filename=slide.caption.text, color='white', font="Amiri-Bold",
                           kerning = 5, fontsize=100, temptxt="")
        cvc = mve.CompositeVideoClip( [txtClip.set_position('center')],
                                size=screensize)

        # helper function
        rotMatrix = lambda a: numpy.array( [[numpy.cos(a),numpy.sin(a)],
                                         [-numpy.sin(a),numpy.cos(a)]] )

        def vortex(screenpos,i,nletters):
            d = lambda t : 1.0/(0.3+t**8) #damping
            a = i*numpy.pi/ nletters # angle of the movement
            v = rotMatrix(a).dot([-1,0])
            if i%2 : v[1] = -v[1]
            return lambda t: screenpos+400*d(t)*rotMatrix(0.5*d(t)*a).dot(v)

        def cascade(screenpos,i,nletters):
            v = numpy.array([0,-1])
            d = lambda t : 1 if t<0 else abs(numpy.sinc(t)/(1+t**4))
            return lambda t: screenpos+v*400*d(t-0.15*i)

        def arrive(screenpos,i,nletters):
            v = numpy.array([-1,0])
            d = lambda t : max(0, 3-3*t)
            return lambda t: screenpos-400*v*d(t-0.2*i)

        def vortexout(screenpos,i,nletters):
            d = lambda t : max(0,t) #damping
            a = i*numpy.pi/ nletters # angle of the movement
            v = rotMatrix(a).dot([-1,0])
            if i%2 : v[1] = -v[1]
            return lambda t: screenpos+400*d(t-0.1*i)*rotMatrix(-0.2*d(t)*a).dot(v)



        # WE USE THE PLUGIN findObjects TO LOCATE AND SEPARATE EACH LETTER

        letters = findObjects(cvc) # a list of ImageClips
        print(letters)
        # WE ANIMATE THE LETTERS

        def moveLetters(letters, funcpos):
            return [ letter.set_position(funcpos(letter.screenpos,i,len(letters)))
                      for i,letter in enumerate(letters)]

        clips = [ mve.CompositeVideoClip( moveLetters(letters,funcpos),
                                      size = screensize).subclip(0,5)
                  for funcpos in [vortex, cascade, arrive, vortexout] ]

        print(progress)
        # WE CONCATENATE EVERYTHING AND WRITE TO A FILE
        final_clip = mve.concatenate_videoclips(clips)
        img_data = final_clip.get_frame(min(final_clip.duration, final_clip.duration*progress*.5))
        img_data = img_data.astype(numpy.uint8)
        return PIL.Image.fromarray(img_data).convert('RGBA')
