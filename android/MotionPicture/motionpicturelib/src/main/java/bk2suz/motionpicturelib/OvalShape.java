package bk2suz.motionpicturelib;

import android.graphics.Path;
import android.graphics.RectF;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;
import java.util.HashMap;

/**
 * Created by sujoy on 8/10/16.
 */
public class OvalShape extends Shape {
    public static final String TYPE_NAME = "oval";
    protected Float mSweepAngle;

    @Override
    public void copyAttributesFromXml(XmlPullParser parser) {
        super.copyAttributesFromXml(parser);
        try {
            mSweepAngle = Float.parseFloat(parser.getAttributeValue(null, "sweep_angle"));
        } catch (NumberFormatException e) {
        }
    }

    @Override
    public Path getPath() {
        if (mPath != null) return mPath;
        Path path = new Path();
        if (mSweepAngle == 360) {
            path.addOval(new RectF(0, 0, mWidth, mHeight), Path.Direction.CW);
        } else {
            path.moveTo(mWidth*.5F, mHeight*.5F);
            path.arcTo(new RectF(0, 0, mWidth, mHeight), 0, mSweepAngle, false);
            path.lineTo(mWidth*.5F, mHeight*.5F);
            path.close();
        }
        mPath = path;
        return path;
    }

    @Override
    public void setProperty(PropName propName, Object value, HashMap<PropName, PropData> propDataMap) {
        super.setProperty(propName, value, propDataMap);
        switch (propName) {
            case SWEEP_ANGLE:
                mSweepAngle = (float) value;
                mPath = null;
                break;
        }
    }

    public static OvalShape createFromXml(XmlPullParser parser)
            throws XmlPullParserException, IOException {
        if (isShapeTagType(parser, TYPE_NAME)) return null;
        OvalShape ovalShape = new OvalShape();
        ovalShape.copyAttributesFromXml(parser);
        return ovalShape;
    }
}
