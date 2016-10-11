package bk2suz.motionpicturelib;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;

/**
 * Created by sujoy on 8/10/16.
 */
public class Point {
    public Float x;
    public Float y;

    public Point(Float x, Float y) {
        this.x = x;
        this.y = y;
    }

    public Point copy() {
        return new Point(x, y);
    }

    public void copyFromText(String text) {
        String[] values = text.split(",");
        if (values.length<2) {
            return;
        }
        try {
            this.x = Float.parseFloat(values[0]);
            this.y = Float.parseFloat(values[1]);
        } catch (NumberFormatException e) {
        }
    }

    public void copyFrom(Point other) {
        this.x = other.x;
        this.y = other.y;
    }

    public float distance(Point other) {
        float dx = this.x-other.x;
        float dy = this.y-other.y;
        return (float) Math.sqrt(dx*dx+dy*dy);
    }

    public void scale(float scaleX, float scaleY) {
        x *= scaleX;
        y *= scaleY;
    }

    public void reverse_transform(Matrix matrix) {
        float[] xyValues = {this.x, this.y};
        android.graphics.Matrix inverseMatrix = new android.graphics.Matrix();
        matrix.getGraphicsMatrix().invert(inverseMatrix);
        inverseMatrix.mapPoints(xyValues);
        this.x = xyValues[0];
        this.y = xyValues[0];
    }

    public void transform(Matrix matrix) {
        float[] xyValues = {this.x, this.y};
        matrix.getGraphicsMatrix().mapPoints(xyValues);
        this.x = xyValues[0];
        this.y = xyValues[0];
    }

    public void translate(float dx, float dy) {
        this.x += dx;
        this.y += dy;
    }

    public void rotateCoordinate(float angle) {
        angle *= Math.PI/Helper.RADIAN_PER_DEGREE;
        float newX = (float) (this.x*Math.cos(angle) + this.y*Math.sin(angle));
        float newY = (float) (-this.x*Math.sin(angle) + this.y*Math.cos(angle));
        this.x = newX;
        this.y = newY;
    }

    public static Point createFromText(String text) {
        String[] values = text.split(",");
        if (values.length<2) {
            return null;
        }
        Point point = new Point(0F, 0F);
        try {
            point.x = Float.parseFloat(values[0]);
            point.y = Float.parseFloat(values[1]);
        } catch (NumberFormatException e) {
        }
        return point;
    }

    public static Point createFromXml(XmlPullParser parser)
            throws XmlPullParserException, IOException {
        parser.require(XmlPullParser.START_TAG, null, "point");
        Point point = createFromText(parser.getAttributeValue(null, "p"));
        Helper.skipTag(parser);
        return point;
    }
}
