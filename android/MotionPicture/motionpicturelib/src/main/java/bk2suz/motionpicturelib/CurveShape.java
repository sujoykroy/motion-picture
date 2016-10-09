package bk2suz.motionpicturelib;

import android.graphics.Path;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;
import java.util.ArrayList;

/**
 * Created by sujoy on 8/10/16.
 */
public class CurveShape extends Shape {
    public static final String TYPE_NAME = "curve_shape";
    private ArrayList<Curve> mCurves = new ArrayList<>();

    @Override
    public Path getPath() {
        Path path = new Path();
        for (Curve curve: mCurves) {
            path.addPath(curve.getPath(mWidth, mHeight));
        }
        return path;
    }

    public static CurveShape createFromXml(XmlPullParser parser)
            throws XmlPullParserException, IOException {
        if (isShapeTagType(parser, TYPE_NAME)) return null;
        CurveShape curveShape = new CurveShape();
        curveShape.copyAttributesFromXml(parser);
        while (parser.next() != XmlPullParser.END_TAG) {
            if (parser.getEventType() != XmlPullParser.START_TAG) {
                continue;
            }
            if (parser.getName().equals("curve")) {
                Curve curve = Curve.createFromXml(parser);
                curveShape.mCurves.add(curve);
            }
            Helper.skipTag(parser);
        }
        return curveShape;
    }
}
