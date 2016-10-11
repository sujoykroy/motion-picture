package bk2suz.motionpicturelib;

import android.graphics.Path;
import android.util.Log;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;

/**
 * Created by sujoy on 9/10/16.
 */
public class Polygon {
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

    public void setClosed(boolean closed) {
        mClosed = closed;
    }

    public boolean getClosed() {
        return mClosed;
    }

    public static Polygon createFromXml(XmlPullParser parser)
            throws XmlPullParserException, IOException {
        parser.require(XmlPullParser.START_TAG, null, "polygon");
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
