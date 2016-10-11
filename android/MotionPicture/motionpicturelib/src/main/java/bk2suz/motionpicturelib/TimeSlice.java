package bk2suz.motionpicturelib;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;

/**
 * Created by sujoy on 11/10/16.
 */
public class TimeSlice {
    public static final String TAG_NAME = "time_slice";
    private Float mStartValue;
    private Float mEndValue;
    private Float mDuration;
    private TimeChangeType mTimeChangeType;
    private HashMap<PropName, PropData> mPropDataMap;

    public Float getDuration() {
        return mDuration;
    }

    public Float getValueAt(Float t) {
        return mTimeChangeType.getValueAt(mStartValue, mEndValue, t, mDuration);
    }

    public HashMap<PropName, PropData> getPropDataMap() {
        return mPropDataMap;
    }

    public static TimeSlice createFromXml(XmlPullParser parser)
            throws XmlPullParserException, IOException {
        parser.require(XmlPullParser.START_TAG, null, TAG_NAME);
        TimeSlice timeSlice = new TimeSlice();
        try {
            timeSlice.mStartValue = Float.parseFloat(parser.getAttributeValue(null, "start_value"));
        } catch (NumberFormatException e) {
        }
        try {
            timeSlice.mEndValue = Float.parseFloat(parser.getAttributeValue(null, "end_value"));
        } catch (NumberFormatException e) {
        }
        try {
            timeSlice.mDuration = Float.parseFloat(parser.getAttributeValue(null, "duration"));
        } catch (NumberFormatException e) {
        }
        TimeChangeType timeChangeType = null;
        while (parser.next() != XmlPullParser.END_TAG) {
            if (parser.getEventType() != XmlPullParser.START_TAG) {
                continue;
            }
            if (parser.getName().equals(PropData.TAG_NAME)) {
                if (timeSlice.mPropDataMap == null) {
                    timeSlice.mPropDataMap = new HashMap<>();
                }
                PropData propData = PropData.createFromXml(parser);
                if (propData != null) {
                    timeSlice.mPropDataMap.put(propData.getKey(), propData);
                }
            } else if (parser.getName().equals(TimeChangeType.TAG_NAME)) {
                String changeTypeName = parser.getAttributeValue(null, "type");

                if (SineChangeType.TYPE_NAME.equals(changeTypeName)) {
                    timeChangeType = SineChangeType.createFromXml(parser);

                } else if (TriangleChangeType.TYPE_NAME.equals(changeTypeName)) {
                    timeChangeType = TriangleChangeType.createFromXml(parser);

                } else if (LoopChangeType.TYPE_NAME.equals(changeTypeName)) {
                    timeChangeType = LoopChangeType.createFromXml(parser);
                }
            }
            Helper.skipTag(parser);
        }
        if (timeChangeType == null) {
            timeChangeType = new TimeChangeType();
        }
        timeSlice.mTimeChangeType = timeChangeType;
        return timeSlice;
    }
}
