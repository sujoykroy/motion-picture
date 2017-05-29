package bk2suz.motionpicturelib.Shapes;

import android.graphics.Path;
import android.graphics.RectF;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;
import java.util.HashMap;

import bk2suz.motionpicturelib.Commons.PropData;
import bk2suz.motionpicturelib.Commons.PropName;

/**
 * Created by sujoy on 8/10/16.
 */
public class RectangleShape extends Shape {
    public static final String TYPE_NAME = "rectangle";
    protected Float mCornerRadius = 0F;

    @Override
    public void copyAttributesFromXml(XmlPullParser parser) {
        super.copyAttributesFromXml(parser);
        try {
            mCornerRadius = Float.parseFloat(parser.getAttributeValue(null, "corner_radius"));
        } catch (NumberFormatException e) {
        }
    }

    @Override
    public Path getPath() {
        if (mPath != null) return mPath;
        Path path = new Path();
        path.addRoundRect(new RectF(0, 0, mWidth, mHeight), mCornerRadius, mCornerRadius, Path.Direction.CW);
        mPath = path;
        return path;
    }

    @Override
    public void setProperty(PropName propName, Object value, HashMap<PropName, PropData> propDataMap) {
        super.setProperty(propName, value, propDataMap);
        switch (propName) {
            case CORNER_RADIUS:
                mCornerRadius = (float) value;
                mPath = null;
                break;
        }
    }

    public static RectangleShape createFromXml(XmlPullParser parser)
            throws XmlPullParserException, IOException {
        if (isShapeTagType(parser, TYPE_NAME)) return null;
        RectangleShape rectangleShape = new RectangleShape();
        rectangleShape.copyAttributesFromXml(parser);
        return rectangleShape;
    }
}
