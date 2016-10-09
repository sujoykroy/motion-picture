package bk2suz.motionpicturelib;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;

/**
 * Created by sujoy on 8/10/16.
 */
public class CurveShape extends Shape {
    public static final String TYPE_NAME = "curve_shape";

    public static CurveShape createFromXml(XmlPullParser parser)
            throws XmlPullParserException, IOException {
        if (isShapeTagType(parser, TYPE_NAME)) return null;
        CurveShape curveShape = new CurveShape();
        curveShape.copyAttributesFromXml(parser);
        return curveShape;
    }
}
