package bk2suz.motionpicturelib;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;

/**
 * Created by sujoy on 11/10/16.
 */
public class TriangleChangeType extends PeriodicChangeType {
    public static final String TYPE_NAME = "triangle";

    @Override
    public Float getValueAt(Float startValue, Float endValue, Float t, Float duration) {
        Float value = super.getValueAt(startValue, endValue, t, duration);
        Float frac =  t/duration;
        frac += mPhase/360F;
        frac %= 1F;
        if (frac>.5F) frac = 1-frac;
        frac *= 2;
        value += mAmplitude * frac;
        return value;
    }

    public static TriangleChangeType createFromXml(XmlPullParser parser)
            throws XmlPullParserException, IOException {
        parser.require(XmlPullParser.START_TAG, null, TAG_NAME);
        TriangleChangeType changeType = new TriangleChangeType();
        changeType.copyFromXml(parser);
        return changeType;
    }
}
