package bk2suz.motionpicturelib;

import android.graphics.Path;
import android.graphics.Rect;
import android.graphics.RectF;

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

    public Point getControl1Point() {
        return mControl1;
    }

    public Point getControl2Point() {
        return mControl2;
    }

    public Point getDestPoint() {
        return mDest;
    }

    public RectF getOutline() {
        float left, top, right, bottom;
        left = right = mControl1.x;
        top = bottom = mControl1.y;

        if (left>mControl2.x) left = mControl2.x;
        if (right<mControl2.x) right = mControl2.x;
        if (top>mControl2.y) top = mControl2.y;
        if (bottom<mControl2.y) bottom = mControl2.y;

        if (left>mDest.x) left = mDest.x;
        if (right<mDest.x) right = mDest.x;
        if (top>mDest.y) top = mDest.y;
        if (bottom<mDest.y) bottom = mDest.y;

        return new RectF(left, top, right, bottom);
    }

    public void translate(float dx, float dy) {
        mControl1.translate(dx, dy);
        mControl2.translate(dx, dy);
        mDest.translate(dx, dy);
    }

    public void scale(float scaleX, float scaleY) {
        mControl1.scale(scaleX, scaleY);
        mControl2.scale(scaleX, scaleY);
        mDest.scale(scaleX, scaleY);
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
