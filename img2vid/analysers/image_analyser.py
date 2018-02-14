import wand.image

class ImageAnalyser:
    KEY_EXIF_ORIENTATION = "Orientation"

    @staticmethod
    def get_exif(filepath):
        exif = {}
        with wand.image.Image(filename=filepath) as image:
            for key, value in image.metadata.items():
                if key.startswith("exif:"):
                    exif[key[5:]] = value
        return exif
