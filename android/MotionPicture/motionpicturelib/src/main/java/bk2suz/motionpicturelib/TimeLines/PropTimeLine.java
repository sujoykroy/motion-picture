package bk2suz.motionpicturelib.TimeLines;

import android.util.Log;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;
import java.util.ArrayList;

import bk2suz.motionpicturelib.Commons.Helper;
import bk2suz.motionpicturelib.Commons.PropName;
import bk2suz.motionpicturelib.Shapes.Shape;

/**
 * Created by sujoy on 11/10/16.
 */
public class PropTimeLine {
    public static final String TAG_NAME = "prop_time_line";
    private PropName mPropName;
    private Shape mShape;
    private Float mDuration = 0F;
    private ArrayList<TimeSlice> mTimeSlices = new ArrayList<>();

    public void moveTo(Float t) {
        float elapsed = 0F;
        for(TimeSlice timeSlice: mTimeSlices) {
            if (t<elapsed+timeSlice.getDuration()) {
                Float value = timeSlice.getValueAt(t-elapsed);
                mShape.setProperty(mPropName, value, timeSlice.getPropDataMap());
                break;
            }
            elapsed += timeSlice.getDuration();
        }
    }

    public Float getDuration() {
        return mDuration;
    }

    public static PropTimeLine createFromXml(XmlPullParser parser, Shape shape)
            throws XmlPullParserException, IOException {
        parser.require(XmlPullParser.START_TAG, null, TAG_NAME);
        PropTimeLine propTimeLine = new PropTimeLine();
        propTimeLine.mPropName = PropName.getByXmlName(parser.getAttributeValue(null, "prop_name"));
        propTimeLine.mShape = shape;

        while (parser.next() != XmlPullParser.END_TAG) {
            if (parser.getEventType() != XmlPullParser.START_TAG) {
                continue;
            }
            if (parser.getName().equals(TimeSlice.TAG_NAME)) {
                TimeSlice timeSlice = TimeSlice.createFromXml(parser);
                if (timeSlice != null) {
                    propTimeLine.mTimeSlices.add(timeSlice);
                    propTimeLine.mDuration += timeSlice.getDuration();
                }
            }
            Helper.skipTag(parser);
        }
        return propTimeLine;
    }
}
