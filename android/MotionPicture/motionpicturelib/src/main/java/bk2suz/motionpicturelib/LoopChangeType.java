package bk2suz.motionpicturelib;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;

/**
 * Created by sujoy on 11/10/16.
 */
public class LoopChangeType extends TimeChangeType {
    public static final String TYPE_NAME = "loop";
    protected Integer mLoopCount;

    @Override
    public Float getValueAt(Float startValue, Float endValue, Float t, Float duration) {
        Float loopDuration = duration/mLoopCount;
        t %= loopDuration;
        return super.getValueAt(startValue, endValue, t, loopDuration);
    }

    public static LoopChangeType createFromXml(XmlPullParser parser)
            throws XmlPullParserException, IOException {
        parser.require(XmlPullParser.START_TAG, null, TAG_NAME);
        LoopChangeType changeType = new LoopChangeType();
        try {
            changeType.mLoopCount = Integer.parseInt(parser.getAttributeValue(null, "count"));
        } catch (NumberFormatException e) {
            changeType.mLoopCount = 1;
        }
        return changeType;
    }
}
