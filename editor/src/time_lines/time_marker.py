from xml.etree.ElementTree import Element as XmlElement

class TimeMarker(object):
    TAG_NAME = "tmarker"

    def __init__(self, at, text):
        self.at = at
        self.text = text

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

    def get_formatted_at(self):
        return "{0:02}".format(self.at)

    def get_xml_element(self):
        elm = XmlElement(self.TAG_NAME)
        elm.attrib["text"] = self.text
        elm.attrib["at"] = "{0}".format(self.at)
        return elm

    @classmethod
    def create_from_xml_element(cls, elm):
        text = elm.attrib.get("text", "").strip()
        at = elm.attrib.get("at", "").strip()
        if not text or not at:
            return None
        time_marker = cls(0, text)
        time_marker.set_at(at)
        return time_marker

