from xml.etree.ElementTree import Element as XmlElement

class TimeMarker(object):
    TAG_NAME = "tmarker"

    def __init__(self, at, text):
        self.at = at
        self.text = text
        self.fixed = False

    def copy(self):
        newob = TimeMarker(self.at, self.text)
        newob.fixed = self.fixed
        return newob

    def copy_from(self, other):
        self.at = other.at
        self.text = other.text
        self.fixed = other.fixed

    def set_fixed(self, value):
        self.fixed = value

    def set_text(self, text):
        text = text.strip()
        if text and len(text)>0:
            self.text =text

    def set_at(self, at):
        at = at.strip()
        if at and len(at)>0:
            try:
                at = float(at)
            except ValueError:
                return
            self.at = at

    def get_text(self):
        return self.text

    def get_formatted_at(self):
        return "{0:02}".format(self.at)

    def get_xml_element(self):
        elm = XmlElement(self.TAG_NAME)
        elm.attrib["text"] = self.text
        elm.attrib["at"] = "{0}".format(self.at)
        if not self.fixed:
            elm.attrib["fixed"] = "0"
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        text = elm.attrib.get("text", "").strip()
        at = elm.attrib.get("at", "").strip()
        if not text or not at:
            return None
        time_marker = cls(0, text)
        time_marker.set_at(at)
        time_marker.set_fixed(bool(int(elm.attrib.get("fixed", 1))))
        return time_marker

