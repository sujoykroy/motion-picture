package bk2suz.motionpicturelib.Commons;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;

/**
 * Created by sujoy on 9/10/16.
 */
public class Helper {
    public static final Float RADIAN_PER_DEGREE = (float) Math.PI/180F;

    public static void skipTag(XmlPullParser parser) throws XmlPullParserException, IOException {
        if (parser.getEventType() != XmlPullParser.START_TAG || parser.getEventType() != XmlPullParser.TEXT) {
            return;
        }
        int depth = 1;
        while (depth != 0) {
            switch (parser.next()) {
                case XmlPullParser.END_TAG:
                    depth--;
                    break;
                case XmlPullParser.START_TAG:
                    depth++;
                    break;
            }
        }
    }

    public static Color parseColor(String text) {
        if (text == null) return null;
        String[] segments = text.split(":");
        if (segments.length == 1) {
            return FlatColor.createFromText(segments[0]);
        } else if (segments[0].equals(LinearGradientColor.TYPE_NAME)) {
            return LinearGradientColor.createFromText(segments[1]);
        } else if (segments[0].equals(RadialGradientColor.TYPE_NAME)) {
            return RadialGradientColor.createFromText(segments[1]);
        } else if (segments[0].equals(TextureMapColor.TYPE_NAME)) {
            return TextureMapColor.createFromText(segments[1]);
        }
        return null;
    }
}
