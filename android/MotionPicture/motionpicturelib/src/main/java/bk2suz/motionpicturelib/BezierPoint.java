package bk2suz.motionpicturelib;

import android.graphics.Path;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;

/**
 * Created by sujoy on 9/10/16.
 */
public class BezierPoint {
    private Point mControl1 = new Point(0F, 0F);
    private Point mControl2 = new Point(0F, 0F);
    private Point mDest = new Point(0F, 0F);

    public void addToPath(Path path, Float width, Float height) {
        path.cubicTo(
                mControl1.x*width, mControl1.y*height,
                mControl2.x*width, mControl2.y*height,
                mDest.x*width, mDest.y*height);
    }

    public static BezierPoint createFromXml(XmlPullParser parser)
            throws XmlPullParserException, IOException {
        parser.require(XmlPullParser.START_TAG, null, "bp");
        BezierPoint bezierPoint = new BezierPoint();
        bezierPoint.mControl1.copyFromText(parser.getAttributeValue(null, "c1"));
        bezierPoint.mControl2.copyFromText(parser.getAttributeValue(null, "c2"));
        bezierPoint.mDest.copyFromText(parser.getAttributeValue(null, "d"));
        while (parser.next() != XmlPullParser.END_TAG) {
            if (parser.getEventType() != XmlPullParser.START_TAG) {
                continue;
            }
        }
        return bezierPoint;
    }
}
