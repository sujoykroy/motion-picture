package bk2suz.motionpicturelib;

import android.graphics.Canvas;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;
import java.util.ArrayList;

/**
 * Created by sujoy on 8/10/16.
 */
public class MultiShape extends Shape {
    public static final String TYPE_NAME = "multi_shape";
    private ArrayList<Shape> mChildShapes = new ArrayList<>();

    public void addChildShape(Shape shape) {
        mChildShapes.add(shape);
        shape.setParentShape(this);
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
                }
                if (childShape != null) {
                    multiShape.addChildShape(childShape);
                }
            }
            Helper.skipTag(parser);
        }
        return multiShape;
    }

    @Override
    public void draw(Canvas canvas) {
        for(Shape shape: mChildShapes) {
            shape.draw(canvas);
        }
    }
}
