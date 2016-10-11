package bk2suz.motionpicturelib;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;

/**
 * Created by sujoy on 11/10/16.
 */
public class LoopChangeType extends PeriodicChangeType {
    public static final String TYPE_NAME = "loop";

    @Override
    public Float getValueAt(Float startValue, Float endValue, Float t, Float duration) {
        Float value = super.getValueAt(startValue, endValue, t, duration);
        Float frac =  t/duration;
        frac += mPhase/360F;
        frac %= 1F;
        value += mAmplitude * frac;
        return value;
    }

    public static LoopChangeType createFromXml(XmlPullParser parser)
            throws XmlPullParserException, IOException {
        parser.require(XmlPullParser.START_TAG, null, TAG_NAME);
        LoopChangeType changeType = new LoopChangeType();
        changeType.copyFromXml(parser);
        return changeType;
    }
}
