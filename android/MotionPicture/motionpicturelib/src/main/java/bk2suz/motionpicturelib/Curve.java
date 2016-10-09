package bk2suz.motionpicturelib;

import android.graphics.Path;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;
import java.util.ArrayList;

/**
 * Created by sujoy on 9/10/16.
 */
public class Curve {
    private Point mOrigin = new Point(0F, 0F);
    private ArrayList<BezierPoint> mBezierPoints = new ArrayList<>();
    private Boolean mClosed;

    public Path getPath(Float width, Float height) {
        Path path = new Path();
        path.moveTo(mOrigin.x*width, mOrigin.y*height);
        for(int i=0; i<mBezierPoints.size(); i++) {
            BezierPoint bezierPoint = mBezierPoints.get(i);
            bezierPoint.addToPath(path, width, height);
        }
        if (mClosed) {
            path.close();
        }
        return path;
    }

    public static Curve createFromXml(XmlPullParser parser)
            throws XmlPullParserException, IOException {
        parser.require(XmlPullParser.START_TAG, null, "curve");
        Curve curve = new Curve();
        curve.mClosed = Boolean.parseBoolean(parser.getAttributeValue(null, "closed"));
        curve.mOrigin.copyFromText(parser.getAttributeValue(null, "origin"));
        while (parser.next() != XmlPullParser.END_TAG) {
            if (parser.getEventType() != XmlPullParser.START_TAG) {
                continue;
            }

            if (parser.getName().equals("bp")) {
                BezierPoint bezierPoint = BezierPoint.createFromXml(parser);
                if (bezierPoint != null) {
                    curve.mBezierPoints.add(bezierPoint);
                }
            } else {
                Helper.skipTag(parser);
            }
        }
        return curve;
    }
}
