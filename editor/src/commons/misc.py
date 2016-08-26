class Keyboard(object):
    def __init__(self):
        self.shift_key_pressed = False
        self.control_key_pressed = False

class Text(object):
    @staticmethod
    def markup(text, color, weight="normal"):
        text = '<span color="#{0}" weight="{1}">{2}</span>'.format(color, weight, text)
        return text

def format_time(value):
    hour = int(math.floor(value / 3600.))
    value -= hour*60
    minute = int(math.floor(value / 60.))
    value -= minute*60
    value = round(value, 2)
    if hour>0:
        return "{0:02}h:{1:02}m:{2:02.2f}s".format(hour, minute, value)
    elif minute>0:
        return "{0:02}m:{1:02.2f}s".format(minute, value)
    else:
        return "{0:02.2f}s".format(value)

