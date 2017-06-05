package bk2suz.motionpicturelib.TimeLines;

import android.util.Log;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;
import java.util.Arrays;

/**
 * Created by sujoy on 11/10/16.
 */
public class TriangleChangeType extends PeriodicChangeType {
    public static final String TYPE_NAME = "triangle";

    @Override
    public TimeSliceValue getValueAt(TimeSliceValue startValue, TimeSliceValue endValue, Float t, Float duration) {
        TimeSliceValue timeSliceValue = super.getValueAt(startValue, endValue, t, duration);
        Float frac =  t/mPeriod;
        frac += mPhase/360F;
        frac %= 1F;
        if (frac>.5F) frac = 1-frac;
        frac *= 2;
        //value += mAmplitude * frac;
        timeSliceValue.add(mAmplitude * frac);
        return timeSliceValue;
    }

    public static TriangleChangeType createFromXml(XmlPullParser parser)
            throws XmlPullParserException, IOException {
        parser.require(XmlPullParser.START_TAG, null, TAG_NAME);
        TriangleChangeType changeType = new TriangleChangeType();
        changeType.copyFromXml(parser);
        return changeType;
    }
}
