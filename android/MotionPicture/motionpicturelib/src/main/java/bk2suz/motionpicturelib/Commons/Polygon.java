package bk2suz.motionpicturelib.Commons;

import android.graphics.Path;
import android.graphics.RectF;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;
import java.util.ArrayList;

/**
 * Created by sujoy on 9/10/16.
 */
public class Polygon {
    public static final String TAG_NAME = "polygon";
    private ArrayList<Point> mPoints = new ArrayList<>();
    private Boolean mClosed = false;

    public void addPoint(Point point) {
        mPoints.add(point);
    }

    public Path getPath(Float width, Float height) {
        Path path = new Path();
        for(int i=0; i<mPoints.size(); i++) {
            Point point = mPoints.get(i);
            if(i == 0) {
                path.moveTo(point.x*width, point.y*height);
            } else {
                path.lineTo(point.x*width, point.y*height);
            }
        }
        if (mClosed) {
            path.close();
        }
        return path;
    }

    public ArrayList<Point> getPoints() {
        return mPoints;
    }

    public void setClosed(boolean closed) {
        mClosed = closed;
    }

    public boolean getClosed() {
        return mClosed;
    }

    public RectF getOutline() {
        RectF outline = new RectF();
        for(int i=1; i<mPoints.size(); i++) {
            float x1 = mPoints.get(i-1).x;
            float x2 = mPoints.get(i).x;
            float y1 = mPoints.get(i-1).y;
            float y2 = mPoints.get(i).y;
            RectF rect = new RectF(Math.min(x1, x2), Math.min(y1, y2), Math.max(x1, x2), Math.max(y1, y2));
            outline.union(rect);
        }
        return outline;
    }

    public void translate(float dx, float dy) {
        for(Point point: mPoints) {
            point.translate(dx, dy);
        }
    }

    public void scale(float scaleX, float scaleY) {
        for(Point point: mPoints) {
            point.scale(scaleX, scaleY);
        }
    }

    public static Polygon createFromXml(XmlPullParser parser)
            throws XmlPullParserException, IOException {
        parser.require(XmlPullParser.START_TAG, null, TAG_NAME);
        Polygon polygon = new Polygon();
        polygon.mClosed = Boolean.parseBoolean(parser.getAttributeValue(null, "closed"));
        while (parser.next() != XmlPullParser.END_TAG) {
            if (parser.getEventType() != XmlPullParser.START_TAG) {
                continue;
            }

            if (parser.getName().equals("point")) {
                Point point = Point.createFromXml(parser);
                if (point != null) {
                    polygon.mPoints.add(point);
                }
            } else {
                Helper.skipTag(parser);
            }
        }
        return polygon;
    }
}
