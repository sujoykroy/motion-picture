from ..audio_tools import *

class AVBase(object):
    DONT_PLAY_AUDIO = True

    def __init__(self):
        self.av_filename = None
        self.time_pos = 0.
        self.audio_queue = None
        self.audio_active = True
        self.last_played_at = 0

    def set_av_filename(self, av_filename):
        if av_filename != self.av_filename:
            self.last_played_at = 0
        self.av_filename = av_filename

    def can_draw_time_slice_for(self, prop_name):
        return True if prop_name == "time_pos" else False

    def set_time_pos(self, time_pos, prop_data):
        if prop_data:
            av_filename = prop_data.get("av_filename")
            self.set_av_filename(av_filename)

        if self.av_filename == "//":
            return

        old_time_pos = self.time_pos
        self.time_pos = time_pos
        current_time = time.time()

        if AVBase.DONT_PLAY_AUDIO or not self.av_filename:
            return

        audio_jack = AudioJack.get_thread()
        if not audio_jack:
            return
        if self.audio_queue is None:
            self.audio_queue = audio_jack.get_new_audio_queue()

        elapsed_time = current_time-self.last_played_at
        start_at = old_time_pos
        end_at = self.time_pos
        sample_duration = end_at-start_at

        if self.last_played_at>0 and sample_duration!=0 and \
            elapsed_time<1:# and abs(sample_duration)<1:
            audio_file = AudioFileCache.get_file(self.audio_path)

            scale = elapsed_time/sample_duration

            ts = numpy.arange(start_at, end_at, 1./(audio_jack.sample_rate*scale))
            samples = audio_file.get_samples(at=ts).copy()
            #AudioJack.get_thread().clear_audio_queue(self.audio_queue)
            try:
                self.audio_queue.put(samples, block=False)
            except Queue.Full as e:
                pass
        self.last_played_at = current_time

    def draw_for_time_slice(self, ctx, prop_name, prop_data, visible_time_span,
                                   time_slice, time_slice_box, pixel_per_second):
        if prop_name != "time_pos":
            return
        filename = prop_data["av_filename"] if prop_data else None
        if not filename:
            return
        wave_file = AudioFileCache.get_file(filename)
        diff_value = abs(time_slice.end_value - time_slice.start_value)
        if diff_value ==0:
            diff_value = 0.001
        slice_scale = time_slice.duration/diff_value

        time_start = time_slice.start_value + visible_time_span.start/slice_scale
        time_end = min(time_slice.end_value, (time_slice.start_value+visible_time_span.end/slice_scale))
        t_step = 1./(slice_scale*visible_time_span.scale*pixel_per_second)
        t_step = max((time_end-time_start)/1000., t_step)

        t = time_start

        ctx.save()
        time_slice_box.pre_draw(ctx)
        ctx.scale(pixel_per_second, time_slice_box.height)
        ctx.scale(slice_scale, 1)
        ctx.translate(-time_slice.start_value, 0)

        wave_started = False
        while t<time_end:
            sample = wave_file.get_sample_at(t)
            if sample is None:
                break
            if not wave_started:
                wave_started = True
                ctx.move_to(t, .5-sample[0]/2)
            else:
                ctx.line_to(t, .5-sample[0]/2)
            t += t_step
        ctx.restore()
        draw_stroke(ctx, 1, "000000")


    def cleanup(self):
        if self.audio_queue:
            audio_jack = AudioJack.get_thread()
            if audio_jack:
                audio_jack.remove_audio_queue(self.audio_queue)
        self.audio_queue = None

