from audio_utils import *
import numpy

class AudioFFT(object):
    def __init__(self, samples, sample_rate):
        self.sample_rate = sample_rate
        self.fft_values = None
        self.fft_freqs = numpy.fft.rfftfreq(samples.shape[-1], 1./sample_rate)
        self.all_sample_indices = numpy.arange(0, self.fft_freqs.shape[0], 1)
        for i in range(samples.shape[0]):
            fft_values = numpy.fft.rfft(samples[i,:])
            if self.fft_values is None:
                self.fft_values = fft_values
            else:
                self.fft_values = numpy.stack((self.fft_values, fft_values), axis=0)
        self.zero_fft_values = numpy.zeros(self.fft_values.shape, dtype="f")

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

    def apply_freq_bands(self, freq_bands):
        for freq_band in freq_bands:
            self.apply_freq_band(freq_band)

    def apply_freq_band(self, freq_band):
        if freq_band.cond_bands:
            for cond_band in freq_band.cond_bands:
                sample_indices = None
                for freq in cond_band.freqs:
                    si = int(freq.start*self.fft_freqs.shape[0]/self.sample_rate)
                    ei = int(freq.end*self.fft_freqs.shape[0]/self.sample_rate)
                    si = max(0, si)
                    ei = min(ei, self.fft_freqs.shape[0])
                    seg_indices = numpy.arange(si, ei, 1)
                    if sample_indices is None:
                        sample_indices = seg_indices
                    else:
                        sample_indices = numpy.concatenate((sample_indices, seg_indices))
                    seg_indices = None

                if len(sample_indices) == 0:
                    continue

                if cond_band.negate:
                    sample_indices = numpy.setdiff1d(self.all_sample_indices, sample_indices)

                cond_samples = self.fft_values[:, sample_indices]
                if not Threshold.check_application(cond_samples, cond_band.thresholds):
                    return

        sample_indices = None
        for freq in freq_band.freqs:
            start_index = int(freq.start*self.fft_freqs.shape[0]/self.sample_rate)
            end_index = int(freq.end*self.fft_freqs.shape[0]/self.sample_rate)

            start_index = max(0, start_index)
            end_index = min(end_index, self.fft_freqs.shape[0])
            seg_indices = numpy.arange(start_index, end_index, 1)
            if sample_indices is None:
                sample_indices = seg_indices
            else:
                sample_indices = numpy.concatenate((sample_indices, seg_indices))
            seg_indices = None

        if freq_band.negate:
            sample_indices = numpy.setdiff1d(self.all_sample_indices, sample_indices)

        if len(sample_indices) == 0:
            return
        picked_condition = numpy.zeros(self.fft_values.shape, dtype=numpy.bool)
        picked_condition[:, sample_indices] = True

        picked_samples = numpy.where(picked_condition, self.fft_values, self.zero_fft_values)
        if freq_band.thresholds:
            theshold_condition = Threshold.get_condition(picked_samples, freq_band.thresholds)
            picked_condition = (theshold_condition & picked_condition)
            picked_samples = numpy.where(picked_condition, picked_samples, self.zero_fft_values)

        non_picked_samples = numpy.where(picked_condition, self.zero_fft_values, self.fft_values)

        if isinstance(freq_band.mult, float) or isinstance(freq_band.mult, int):
            picked_samples = picked_samples*freq_band.mult
        else:
            x = picked_samples
            picked_samples = eval(freq_band.mult)
            x = None
        self.fft_values = picked_samples + non_picked_samples

    def get_reconstructed_samples(self):
        final_samples = None
        for i in range(self.fft_values.shape[0]):
            samples = numpy.fft.irfft(self.fft_values[i, :])
            if final_samples is None:
                final_samples = samples
            else:
                final_samples = numpy.stack((final_samples, samples), axis=0)
        return final_samples
