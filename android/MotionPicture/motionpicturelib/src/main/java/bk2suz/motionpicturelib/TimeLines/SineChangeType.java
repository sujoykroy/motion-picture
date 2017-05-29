package bk2suz.motionpicturelib.TimeLines;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;

/**
 * Created by sujoy on 11/10/16.
 */
public class SineChangeType extends PeriodicChangeType {
    public static final String TYPE_NAME = "sine";

    @Override
    public Float getValueAt(Float startValue, Float endValue, Float t, Float duration) {
        Float value = super.getValueAt(startValue, endValue, t, duration);
        value += mAmplitude * (float) Math.sin(Math.PI*2*t/mPeriod+mPhase*Math.PI/180F);
        return value;
    }

    public static SineChangeType createFromXml(XmlPullParser parser)
            throws XmlPullParserException, IOException {
        parser.require(XmlPullParser.START_TAG, null, TAG_NAME);
        SineChangeType changeType = new SineChangeType();
        changeType.copyFromXml(parser);
        return changeType;
    }
}
