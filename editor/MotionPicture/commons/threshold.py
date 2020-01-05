from ..commons import Text
import re, numpy

class Threshold(object):
    def __init__(self, condition_type, threshold_value,
                       threshold_type, abs_threshold, value_type):
        self.condition_type = condition_type
        self.threshold_value = threshold_value
        self.threshold_type = threshold_type
        self.abs_threshold = abs_threshold
        self.value_type = value_type

    @classmethod
    def parse(self, text):
        thresholds = []
        if not text:
            return thresholds
        condition_type = "and"
        for item in re.split("(and|or)", text):
            item = item.replace(" ", "")
            if not item:
                continue

            if item in ("and", "or"):
                condition_type = item
                continue

            threshold_type = None
            threshold_value = None
            abs_threshold = None

            if len(item)>1:
                if item.find("max") == 0:
                    item = item[3:]
                    value_type = "max"
                elif item.find("min") == 0:
                    item = item[3:]
                    value_type = "min"
                else:
                    value_type = None
                threshold_type = item[0]
                if threshold_type in ("<", ">"):
                    if item[1] == "|" and item[-1] == "|":
                        abs_threshold = True
                        threshold_value = Text.parse_number(item[2:-1], default=None)
                    else:
                        abs_threshold = False
                        threshold_value = Text.parse_number(item[1:], default=None)
            if threshold_value is None:
                continue
            threshold = Threshold(condition_type, threshold_value,
                        threshold_type, abs_threshold, value_type)
            thresholds.append(threshold)
        return thresholds

    @classmethod
    def get_condition(cls, samples, thresholds):
        final_condition = None
        for threshold in thresholds:
            if threshold.threshold_type == ">":
                if threshold.abs_threshold:
                    condition = (samples>abs(threshold.threshold_value)) | \
                                (samples<-abs(threshold.threshold_value))
                else:
                    condition = (samples>threshold.threshold_value)
            elif threshold.threshold_type == "<":
                if threshold.abs_threshold:
                    condition = (samples<abs(threshold.threshold_value)) & \
                                (samples>-abs(threshold.threshold_value))
                else:
                    condition = (samples<threshold.threshold_value)
            if final_condition is None:
                final_condition = condition
            else:
                if threshold.condition_type == "and":
                    final_condition = final_condition & condition
                elif threshold.condition_type == "or":
                    final_condition = final_condition | condition
            condition = None
        return final_condition

    @classmethod
    def check_application(cls, samples, thresholds):
        maxv = numpy.amax(samples)
        minv = numpy.amin(samples)

        final_condition = True
        for threshold in thresholds:
            if threshold.threshold_type == ">":
                if threshold.abs_threshold:
                    condition = (maxv>abs(threshold.threshold_value)) and \
                                (minv<-abs(threshold.threshold_value))
                elif threshold.value_type == "max":
                    condition = (maxv>threshold.threshold_value)
                else:
                    condition = (minv>threshold.threshold_value)

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
        return final_condition
