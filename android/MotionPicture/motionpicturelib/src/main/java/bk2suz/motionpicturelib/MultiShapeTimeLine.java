package bk2suz.motionpicturelib;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;
import java.util.ArrayList;

/**
 * Created by sujoy on 11/10/16.
 */
public class MultiShapeTimeLine {
    public static final String TAG_NAME = "multi_shape_time_line";
    private ArrayList<ShapeTimeLine> mShapeTimeLines = new ArrayList<>();
    private Float mDuration = 0F;

    public void moveTo(Float t) {
        for(ShapeTimeLine shapeTimeLine: mShapeTimeLines) {
            shapeTimeLine.moveTo(t);
        }
    }

    public Float getDuration() {
        return mDuration;
    }

    public static MultiShapeTimeLine createFromXml(XmlPullParser parser, MultiShape multiShape)
                                                   throws XmlPullParserException, IOException {
        parser.require(XmlPullParser.START_TAG, null, TAG_NAME);
        MultiShapeTimeLine multiShapeTimeLine = new MultiShapeTimeLine();
        while (parser.next() != XmlPullParser.END_TAG) {
            if (parser.getEventType() != XmlPullParser.START_TAG) {
                continue;
            }
            if (parser.getName().equals(ShapeTimeLine.TAG_NAME)) {
                String shapeName = parser.getAttributeValue(null, "shape_name");
                Shape shape;
                if (shapeName == null) {
                    shape = multiShape;
                } else {
                    shape = multiShape.getChildShape(shapeName);
                }
                if (shape != null) {
                    ShapeTimeLine shapeTimeLine = ShapeTimeLine.createFromXml(parser, shape);
                    if (shapeTimeLine != null && shape != null) {
                        multiShapeTimeLine.mShapeTimeLines.add(shapeTimeLine);
                        if (multiShapeTimeLine.mDuration<shapeTimeLine.getDuration()) {
                            multiShapeTimeLine.mDuration = shapeTimeLine.getDuration();
                        }
                    }
                }
            }
            Helper.skipTag(parser);
        }
        return multiShapeTimeLine;
    }
}
