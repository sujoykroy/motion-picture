package bk2suz.motionpicturelib;


import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Path;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;
import java.util.HashMap;

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
        mBorderPaint.setStrokeJoin(Paint.Join.ROUND);
        mBorderPaint.setStrokeCap(Paint.Cap.ROUND);
    }

    public String getName() {
        return mName;
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
            canvas.concat(mPreMatrix.getGraphicsMatrix());
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

    public void setX(Float x) {
        moveTo(x, getAbsoluteAnchorAt().y);
    }

    public void setY(Float y) {
        moveTo(getAbsoluteAnchorAt().x, y);
    }

    public void setStageX(Float x) {
        if (mParentShape != null) {
            x += mParentShape.mAnchortAt.x;
        }
        moveTo(x, getAbsoluteAnchorAt().y);
    }

    public void setStageY(Float y) {
        if (mParentShape != null) {
            y += mParentShape.mAnchortAt.y;
        }
        moveTo(getAbsoluteAnchorAt().x, y);
    }

    public void setAngle(Float angle) {
        Point relLefTopCorner = new Point(-mAnchortAt.x, -mAnchortAt.y);
        relLefTopCorner.scale(mPostScaleX, mPostScaleY);
        relLefTopCorner.rotateCoordinate(-angle);
        relLefTopCorner.scale(mScaleX, mScaleY);
        if (mPreMatrix != null) {
            relLefTopCorner.transform(mPreMatrix);
        }
        Point absAnchorAt = getAbsoluteAnchorAt();
        relLefTopCorner.translate(absAnchorAt.x, absAnchorAt.y);
        mAngle = angle;
        mTranslation.copyFrom(relLefTopCorner);
    }

    public void moveTo(float x, float y) {
        Point point = new Point(x, y);
        Point absAnchorAt = getAbsoluteAnchorAt();
        point.translate(-absAnchorAt.x, - absAnchorAt.y);
        mTranslation.translate(point.x, point.y);
    }

    public Point getAbsoluteAnchorAt() {
        Point absAnchorAt = mAnchortAt.copy();
        absAnchorAt.scale(mPostScaleX, mPostScaleY);
        absAnchorAt.rotateCoordinate(-mAngle);
        absAnchorAt.scale(mScaleX, mScaleY);
        if (mPreMatrix != null) {
            absAnchorAt.transform(mPreMatrix);
        }
        absAnchorAt.translate(mTranslation.x, mTranslation.y);
        return absAnchorAt;
    }


    public Point transformPoint(Point point) {
        point = point.copy();
        Point absAnchorAt = getAbsoluteAnchorAt();
        point.translate(-absAnchorAt.x, -absAnchorAt.y);
        if (mPreMatrix != null) {
            point.reverse_transform(mPreMatrix);
        }
        point.scale(1/mScaleX, 1/mScaleY);
        point.rotateCoordinate(mAngle);
        point.scale(mPostScaleX, mPostScaleY);
        point.translate(mAnchortAt.x, mAnchortAt.y);
        return point;
    }

    public void setProperty(PropName propName, Object value, HashMap<PropName, PropData> propDataMap) {
        switch (propName) {
            case ANGLE:
                setAngle((float) value);
                break;
            case ANCHOR_X:
                mAnchortAt.x = (float) value;
                break;
            case TRANSLATION:
                mTranslation.copyFrom((Point) value);
                break;
            case ANCHOR_Y:
                mAnchortAt.y = (float) value;
                break;
            case ANCHOR_AT:
                mAnchortAt.copyFrom((Point) value);
                break;
            case BORDER_COLOR:
                setBorderColor((Color) value);
                break;
            case BORDER_WIDTH:
                setBorderWidth((float) value);
                break;
            case FILL_COLOR:
                setFillColor((Color) value);
                break;
            case HEIGHT:
                mWidth = (float) value;
                break;
            case WIDTH:
                mHeight = (float) value;
                break;
            case POST_SCALE_X:
                mPostScaleX = (float) value;
                break;
            case POST_SCALE_Y:
                mPostScaleY = (float) value;
                break;
            case SCALE_X:
                mScaleX = (float) value;
                break;
            case SCALE_Y:
                mScaleY = (float) value;
                break;
            case X:
                setX((float) value);
                break;
            case Y:
                setY((float) value);
                break;
            case STAGE_X:
                setStageX((float) value);
                break;
            case PRE_MATRIX:
                mPreMatrix = (Matrix) value;
                break;
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
