package bk2suz.motionpicturelib;

import android.graphics.Path;
import android.graphics.RectF;
import android.util.Log;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;
import java.util.ArrayList;

/**
 * Created by sujoy on 8/10/16.
 */
public class PolygonShape extends Shape {
    public static final String TYPE_NAME = "polygon_shape";
    protected ArrayList<Polygon> mPolygons = new ArrayList<>();

    @Override
    public Path getPath() {
        Path path = new Path();
        for (Polygon polygon: mPolygons) {
            path.addPath(polygon.getPath(mWidth, mHeight));
        }
        return path;
    }

    public static PolygonShape createFromXml(XmlPullParser parser)
            throws XmlPullParserException, IOException {
        if (isShapeTagType(parser, TYPE_NAME)) return null;
        PolygonShape polygonShape = new PolygonShape();
        polygonShape.copyAttributesFromXml(parser);
        while (parser.next() != XmlPullParser.END_TAG) {
            if (parser.getEventType() != XmlPullParser.START_TAG) {
                continue;
            }
            if (parser.getName().equals("polygon")) {
                Polygon polygon = Polygon.createFromXml(parser);
                polygonShape.mPolygons.add(polygon);
            }
            Helper.skipTag(parser);
        }
        return polygonShape;
    }
}
