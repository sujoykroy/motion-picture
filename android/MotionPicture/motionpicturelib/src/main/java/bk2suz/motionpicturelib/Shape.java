package bk2suz.motionpicturelib;


import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Path;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;

/**
 * Created by sujoy on 8/10/16.
 */
public abstract class Shape {
    protected Point mAnchortAt = new Point(0F, 0F);
    protected Color mBorderColor, mFillColor;
    protected Float mBorderWidth = 0F;
    protected Float mWidth, mHeight;
    protected Float mScaleX = 1F, mScaleY = 1F;
    protected Float mPostScaleX = 1F, mPostScaleY = 1F;
    protected Point mTranslation = new Point(0F, 0F);
    protected Float mAngle = 0F;
    protected Matrix mPreMatrix = null;
    protected Shape mParentShape = null;
    protected String mName;

    protected Paint mBorderPaint, mFillPaint;

    public Shape() {
        mFillPaint = new Paint();
        mFillPaint.setStyle(Paint.Style.FILL);
        mBorderPaint = new Paint();
        mBorderPaint.setFlags(Paint.ANTI_ALIAS_FLAG);
        mBorderPaint.setDither(true);
        mBorderPaint.setStyle(Paint.Style.STROKE);
    }

    public void setParentShape(Shape parentShape) {
        mParentShape = parentShape;
    }

    public void copyAttributesFromXml(XmlPullParser parser) {
        mAnchortAt.copyFromText(parser.getAttributeValue(null, "anchor_at"));
        mTranslation.copyFromText(parser.getAttributeValue(null, "translation"));
        try {
            mWidth = Float.parseFloat(parser.getAttributeValue(null, "width"));
        } catch (NumberFormatException e) {
        }
        try {
            mHeight = Float.parseFloat(parser.getAttributeValue(null, "height"));
        } catch (NumberFormatException e) {
        }
        try {
            mScaleX = Float.parseFloat(parser.getAttributeValue(null, "scale_x"));
        } catch (NumberFormatException e) {
        }
        try {
            mScaleY = Float.parseFloat(parser.getAttributeValue(null, "scale_y"));
        } catch (NumberFormatException e) {
        }
        try {
            mPostScaleX = Float.parseFloat(parser.getAttributeValue(null, "post_scale_x"));
        } catch (NumberFormatException e) {
        }
        try {
            mPostScaleY = Float.parseFloat(parser.getAttributeValue(null, "post_scale_y"));
        } catch (NumberFormatException e) {
        }
        try {
            mAngle = Float.parseFloat(parser.getAttributeValue(null, "angle"));
        } catch (NumberFormatException e) {
        }
        mPreMatrix = Matrix.createFromText(parser.getAttributeValue(null, "pre_matrix"));
        setBorderColor(parseColor(parser.getAttributeValue(null, "border_color")));
        setFillColor(parseColor(parser.getAttributeValue(null, "fill_color")));
        try {
            setBorderWidth(Float.parseFloat(parser.getAttributeValue(null, "border_width")));
        } catch (NumberFormatException e) {
        }
        mName = parser.getAttributeValue(null, "name");
    }

    public void setBorderColor(Color color) {
        if (color != null && color.getClass().isInstance(mBorderColor)) {
            mBorderColor.copyFrom(color);
        } else {
            mBorderColor = color;
        }
        if (mBorderColor != null) {
            mBorderColor.setPaint(mBorderPaint);
        }
    }

    public void setFillColor(Color color) {
        if (color != null && color.getClass().isInstance(mFillColor)) {
            mFillColor.copyFrom(color);
        } else {
            mFillColor = color;
        }
        if (mFillColor != null) {
            mFillColor.setPaint(mFillPaint);
        }
    }

    public void setBorderWidth(Float borderWidth) {
        mBorderWidth = borderWidth;
        mBorderPaint.setStrokeWidth(mBorderWidth);
    }

    public void preDraw(Canvas canvas) {
        if (mParentShape != null) {
            mParentShape.preDraw(canvas);
        }
        canvas.translate(mTranslation.x, mTranslation.y);
        if (mPreMatrix != null) {
            //canvas.setMatrix(mPreMatrix.get);
        }
        canvas.scale(mScaleX, mScaleY);
        canvas.rotate(mAngle);
        canvas.scale(mPostScaleX, mPostScaleY);
    }

    public Path getPath() {
        return null;
    }

    public void drawFill(Canvas canvas) {
        if (mFillColor != null) {
            canvas.drawPath(getPath(), mFillPaint);
        }
    }

    public void drawBorder(Canvas canvas) {
        if (mBorderColor != null && mBorderWidth > 0) {
            canvas.drawPath(getPath(), mBorderPaint);
        }
    }

    public void draw(Canvas canvas) {
        if (getPath() == null) return;
        if (mFillColor != null) {
            canvas.save();
            preDraw(canvas);
            drawFill(canvas);
            canvas.restore();
        }
        if (mBorderColor != null) {
            canvas.save();
            preDraw(canvas);
            drawBorder(canvas);
            canvas.restore();
        }
    }

    public static Color parseColor(String text) {
        if (text == null) return null;
        String[] segments = text.split(":");
        if (segments.length == 1) {
            return FlatColor.createFromText(segments[0]);
        } else if (segments[0].equals(LinearGradientColor.TYPE_NAME)) {
            return LinearGradientColor.createFromText(segments[1]);
        } else if (segments[0].equals(RadialGradientColor.TYPE_NAME)) {
            return RadialGradientColor.createFromText(segments[1]);
        }
        return null;
    }

    public static boolean isShapeTagType(XmlPullParser parser, String shapeTypeName)
            throws XmlPullParserException, IOException {
        parser.require(XmlPullParser.START_TAG, null, "shape");
        String shapeType = parser.getAttributeValue(null, "type");
        return !shapeType.equals(shapeTypeName);
    }
}
