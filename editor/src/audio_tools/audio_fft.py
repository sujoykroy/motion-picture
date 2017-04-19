from audio_utils import *
import numpy

class AudioFFT(object):
    def __init__(self, samples, sample_rate):
        self.sample_rate = sample_rate

        self.fft_values = None
        self.fft_freqs = numpy.fft.rfftfreq(samples.shape[-1], 1./sample_rate)

        for i in range(samples.shape[0]):
            fft_values = numpy.fft.rfft(samples[i,:])
            if self.fft_values is None:
                self.fft_values = fft_values
            else:
                self.fft_values = numpy.stack((self.fft_values, fft_values), axis=0)
        self.xmin =  numpy.amin(self.fft_freqs)
        self.xmax =  numpy.amax(self.fft_freqs)
        self.ymin = numpy.amin(self.fft_values)
        self.ymax = numpy.amax(self.fft_values)

        self.ymin = -2000.
        self.ymax = 2000.


    def get_x_min_max(self):
        return [self.xmin, self.xmax]

    def get_y_min_max(self):
        return [self.ymin, self.ymax]

    def get_y_base(self):
        return 0.0

    def get_segment_count(self):
        return self.fft_values.shape[0]

    def get_sample_at_x(self, segment_index, x):
        #sample_index = numpy.argmax(self.fft_freqs>=x)
        sample_index = int(x*self.fft_freqs.shape[0]/self.sample_rate)
        if sample_index<0 or sample_index>= self.fft_freqs.shape[0]:
            return None
        return self.fft_values[segment_index, sample_index]

    def apply_y_mult_replace(self, start_x, end_x, mult, thresholds):
        start_index = int(start_x*self.fft_freqs.shape[0]/self.sample_rate)
        end_index = int(end_x*self.fft_freqs.shape[0]/self.sample_rate)

        start_index = max(0, start_index)
        end_index = min(end_index, self.fft_freqs.shape[0])

        self.fft_values = sample_segment_mult_replace(
                self.fft_values, start_index, end_index, mult, thresholds)

    def apply_freq_band(self, freq_band):
        if freq_band.cond_bands:
            for cond_band in freq_band.cond_bands:
                si = int(cond_band.start_freq*self.fft_freqs.shape[0]/self.sample_rate)
                ei = int(cond_band.end_freq*self.fft_freqs.shape[0]/self.sample_rate)
                si = max(0, si)
                ei = min(ei, self.fft_freqs.shape[0])
                cond_samples = self.fft_values[:, si:ei]
                maxv = numpy.amax(cond_samples)
                minv = numpy.amin(cond_samples)

                final_condition = True
                for threshold in cond_band.thresholds:
                    if threshold.threshold_type == ">":
                        if threshold.abs_threshold:
                            condition = (maxv>abs(threshold.threshold_value)) and \
                                        (minv<-abs(threshold.threshold_value))
                        elif threshold.value_type == "min":
                            condition = (minv>threshold.threshold_value)
                        else:
                            condition = (maxv>threshold.threshold_value)

                    elif threshold.threshold_type == "<":
                        if threshold.abs_threshold:
                            condition = (maxv<abs(threshold.threshold_value)) and \
                                        (minv>-abs(threshold.threshold_value))
                        elif threshold.value_type == "min":
                            condition = (minv<threshold.threshold_value)
                        else:
                            condition = (maxv<threshold.threshold_value)

                    if threshold.condition_type == "and":
                        final_condition = final_condition and condition
                    elif threshold.condition_type == "or":
                        final_condition = final_condition or condition
                if not final_condition:
                    return

        start_index = int(freq_band.start_freq*self.fft_freqs.shape[0]/self.sample_rate)
        end_index = int(freq_band.end_freq*self.fft_freqs.shape[0]/self.sample_rate)

        start_index = max(0, start_index)
        end_index = min(end_index, self.fft_freqs.shape[0])

        self.fft_values = sample_segment_mult_replace(
                self.fft_values, start_index, end_index, freq_band.mult, freq_band.thresholds)

    def get_reconstructed_samples(self):
        final_samples = None
        for i in range(self.fft_values.shape[0]):
            samples = numpy.fft.irfft(self.fft_values[i, :])
            if final_samples is None:
                final_samples = samples
            else:
                final_samples = numpy.stack((final_samples, samples), axis=0)
        return final_samples
