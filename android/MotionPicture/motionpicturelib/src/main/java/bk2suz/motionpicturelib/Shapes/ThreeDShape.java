package bk2suz.motionpicturelib.Shapes;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;

import bk2suz.motionpicturelib.Commons.Camera3D;
import bk2suz.motionpicturelib.Commons.Color;
import bk2suz.motionpicturelib.Commons.Container3D;
import bk2suz.motionpicturelib.Commons.Helper;

/**
 * Created by sujoy on 29/5/17.
 */
public class ThreeDShape extends RectangleShape {
    public static final String TYPE_NAME = "threed";

    protected Camera3D mCamera3D = new Camera3D();
    protected Container3D mD3Object;
    protected Color mWireColor;
    protected Float mWireWidth;

    @Override
    public void copyAttributesFromXml(XmlPullParser parser) {
        super.copyAttributesFromXml(parser);
        //read "camera_rotation-tbd
        setWireColor(Helper.parseColor(parser.getAttributeValue(null, "wire_color")));
        try {
            mWireWidth = Float.parseFloat(parser.getAttributeValue(null, "wire_width"));
        } catch (NumberFormatException e) {
        }
    }

    public void setWireColor(Color color) {
        if (color != null && color.getClass().isInstance(mWireColor)) {
            mWireColor.copyFrom(color);
        } else {
            mWireColor = color;
        }
    }

    public static ThreeDShape createFromXml(XmlPullParser parser)
            throws XmlPullParserException, IOException {
        if (isShapeTagType(parser, TYPE_NAME)) return null;
        ThreeDShape threeDShape = new ThreeDShape();
        threeDShape.copyAttributesFromXml(parser);

        while (parser.next() != XmlPullParser.END_TAG) {
            if (parser.getEventType() != XmlPullParser.START_TAG) {
                continue;
            }
            if (parser.getName().equals(Container3D.TAG_NAME)) {
                threeDShape.mD3Object = Container3D.createFromXml(parser);
            }
            Helper.skipTag(parser);
        }
        return threeDShape;
    }
}
