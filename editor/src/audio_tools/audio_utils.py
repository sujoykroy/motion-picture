import numpy
from ..commons import Threshold

def sample_segment_mult_replace(samples, start_index, end_index, mult, thresholds):
    new_samples = samples[:, :start_index]
    sliced_samples = samples[:, start_index:end_index+1]
    if thresholds:
        final_condition = Threshold.get_condition(sliced_samples, thresholds)
        desired_samples = numpy.where(final_condition,
                            sliced_samples, numpy.zeros(sliced_samples.shape, dtype="f"))
        desired_samples = desired_samples* mult

        other_samples = numpy.where(final_condition,
                            numpy.zeros(sliced_samples.shape, dtype="f"), sliced_samples)
        sliced_samples =  desired_samples + other_samples
        desired_samples = None
        other_samples = None
    else:
        sliced_samples = sliced_samples*mult
    new_samples = numpy.concatenate((new_samples, sliced_samples), axis=1)
    new_samples = numpy.concatenate((new_samples, samples[:, end_index+1:]), axis=1)
    new_samples = new_samples[:, :samples.shape[1]]
    return new_samples

