package bk2suz.motionpicturelib.TimeLines;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;
import java.util.ArrayList;

import bk2suz.motionpicturelib.Commons.Helper;
import bk2suz.motionpicturelib.Shapes.Shape;

/**
 * Created by sujoy on 11/10/16.
 */
public class ShapeTimeLine {
    public static final String TAG_NAME = "shape_time_line";
    private Float mDuration = 0F;
    private ArrayList<PropTimeLine> mPropTimeLines = new ArrayList<>();

    public void moveTo(Float t) {
        for(PropTimeLine propTimeLine: mPropTimeLines) {
            propTimeLine.moveTo(t);
        }
    }

    public Float getDuration() {
        return mDuration;
    }

    public static ShapeTimeLine createFromXml(XmlPullParser parser, Shape shape)
            throws XmlPullParserException, IOException {
        parser.require(XmlPullParser.START_TAG, null, TAG_NAME);
        ShapeTimeLine shapeTimeLine = new ShapeTimeLine();
        while (parser.next() != XmlPullParser.END_TAG) {
            if (parser.getEventType() != XmlPullParser.START_TAG) {
                continue;
            }
            if (parser.getName().equals(PropTimeLine.TAG_NAME)) {
                PropTimeLine propTimeLine = PropTimeLine.createFromXml(parser, shape);
                if (propTimeLine != null) {
                    shapeTimeLine.mPropTimeLines.add(propTimeLine);
                    if (shapeTimeLine.mDuration<propTimeLine.getDuration()) {
                        shapeTimeLine.mDuration = propTimeLine.getDuration();
                    }
                }
            }
            Helper.skipTag(parser);
        }
        return shapeTimeLine;
    }
}
