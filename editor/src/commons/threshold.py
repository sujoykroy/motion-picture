from ..commons import Text
import re

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
                        threshold_value = Text.parse_number(item[2:-1])
                    else:
                        abs_threshold = False
                        threshold_value = Text.parse_number(item[1:])
            if threshold_value is None:
                continue
            threshold = Threshold(condition_type, threshold_value,
                        threshold_type, abs_threshold, value_type)
            thresholds.append(threshold)
        return thresholds


