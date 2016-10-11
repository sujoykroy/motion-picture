package bk2suz.motionpicturelib;

import android.graphics.Canvas;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Created by sujoy on 8/10/16.
 */
public class MultiShape extends Shape {
    public static final String TYPE_NAME = "multi_shape";
    private LinkedHashMap<String, Shape> mChildShapes = new LinkedHashMap<>();
    private HashMap<String, MultiShapeTimeLine> mMultiShapeTimeLines = new HashMap<>();

    public void addChildShape(Shape shape) {
        mChildShapes.put(shape.getName(), shape);
        shape.setParentShape(this);
    }

    public Shape getChildShape(String shapeName) {
        return mChildShapes.get(shapeName);
    }

    @Override
    public void setProperty(PropName propName, Object value, HashMap<PropName, PropData> propDataMap) {
        super.setProperty(propName, value, propDataMap);
        if (propName == PropName.INTERNAL) {
            //TODO
        }
    }

    @Override
    public void draw(Canvas canvas) {
        for(Map.Entry<String, Shape> entry: mChildShapes.entrySet()) {
            entry.getValue().draw(canvas);
        }
    }

    public static MultiShape createFromXml(XmlPullParser parser)
            throws XmlPullParserException, IOException {
        if (isShapeTagType(parser, TYPE_NAME)) return null;
        MultiShape multiShape = new MultiShape();
        multiShape.copyAttributesFromXml(parser);
        while (parser.next() != XmlPullParser.END_TAG) {
            if (parser.getEventType() != XmlPullParser.START_TAG) {
                continue;
            }
            if (parser.getName().equals("shape")) {
                String childShapeType = parser.getAttributeValue(null, "type");
                Shape childShape = null;
                if (childShapeType.equals(RectangleShape.TYPE_NAME)) {
                    childShape = RectangleShape.createFromXml(parser);
                } else if (childShapeType.equals(OvalShape.TYPE_NAME)) {
                    childShape = OvalShape.createFromXml(parser);
                } else if (childShapeType.equals(PolygonShape.TYPE_NAME)) {
                    childShape = PolygonShape.createFromXml(parser);
                } else if (childShapeType.equals(CurveShape.TYPE_NAME)) {
                    childShape = CurveShape.createFromXml(parser);
                } else if (childShapeType.equals(MultiShape.TYPE_NAME)) {
                    childShape = MultiShape.createFromXml(parser);
                } else if (childShapeType.equals(TextShape.TYPE_NAME)) {
                    childShape = TextShape.createFromXml(parser);
                }
                if (childShape != null) {
                    multiShape.addChildShape(childShape);
                }
            } else if (parser.getName().equals(MultiShapeTimeLine.TAG_NAME)) {
                String timeLineName = parser.getAttributeValue(null, "name");
                MultiShapeTimeLine multiShapeTimeLine = MultiShapeTimeLine.createFromXml(parser, multiShape);
                if (multiShapeTimeLine != null) {
                    multiShape.mMultiShapeTimeLines.put(timeLineName, multiShapeTimeLine);
                }
            }
            Helper.skipTag(parser);
        }
        return multiShape;
    }
}
