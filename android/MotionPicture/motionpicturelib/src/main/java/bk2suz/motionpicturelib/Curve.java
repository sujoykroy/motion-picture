package bk2suz.motionpicturelib;

import android.graphics.Path;
import android.graphics.RectF;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;
import java.util.ArrayList;

/**
 * Created by sujoy on 9/10/16.
 */
public class Curve {
    public static final String TAG_NAME = "curve";

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

    public Point getOrigin() {
        return mOrigin;
    }

    public ArrayList<BezierPoint> getBezierPoints() {
        return mBezierPoints;
    }

    public RectF getOutline() {
        RectF outline = new RectF();
        for (BezierPoint bzp: mBezierPoints) {
            outline.union(bzp.getOutline());
        }
        if (mOrigin.x<outline.left) {
            outline.set(mOrigin.x, outline.top, outline.right, outline.bottom);
        } else if(mOrigin.x>outline.right) {
            outline.set(outline.left, outline.top, mOrigin.x, outline.bottom);
        }
        if (mOrigin.y<outline.top) {
            outline.set(outline.left, mOrigin.y, outline.right, outline.bottom);
        } else if(mOrigin.y>outline.bottom) {
            outline.set(outline.left, outline.top, outline.top, mOrigin.x);
        }
        return outline;
    }

    public void translate(float dx, float dy) {
        mOrigin.translate(dx, dy);
        for (BezierPoint bezierPoint: mBezierPoints) {
            bezierPoint.translate(dx, dy);
        }
    }

    public void scale(float scaleX, float scaleY) {
        mOrigin.scale(scaleX, scaleY);
        for (BezierPoint bezierPoint: mBezierPoints) {
            bezierPoint.scale(scaleX, scaleY);
        }
    }

    public static Curve createFromXml(XmlPullParser parser)
            throws XmlPullParserException, IOException {
        parser.require(XmlPullParser.START_TAG, null, TAG_NAME);
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
