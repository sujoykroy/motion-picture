package bk2suz.motionpicturelib.Shapes;


import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.RectF;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;
import java.util.HashMap;

import bk2suz.motionpicturelib.Commons.Color;
import bk2suz.motionpicturelib.Commons.Helper;
import bk2suz.motionpicturelib.Commons.Matrix;
import bk2suz.motionpicturelib.Commons.Point;
import bk2suz.motionpicturelib.Commons.PropData;
import bk2suz.motionpicturelib.Commons.PropName;

/**
 * Created by sujoy on 8/10/16.
 */
public abstract class Shape {
    protected Point mAnchorAt = new Point(0F, 0F);
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
    Path mPath = null;

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

    public static boolean isShapeTagType(XmlPullParser parser, String shapeTypeName)
            throws XmlPullParserException, IOException {
        parser.require(XmlPullParser.START_TAG, null, "shape");
        String shapeType = parser.getAttributeValue(null, "type");
        return !shapeType.equals(shapeTypeName);
    }

    public String getName() {
        return mName;
    }

    public void setParentShape(Shape parentShape) {
        mParentShape = parentShape;
    }

    public void copyAttributesFromXml(XmlPullParser parser) {
        mAnchorAt.copyFromText(parser.getAttributeValue(null, "anchor_at"));
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
        setBorderColor(Helper.parseColor(parser.getAttributeValue(null, "border_color")));
        setFillColor(Helper.parseColor(parser.getAttributeValue(null, "fill_color")));
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
        return mPath;
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

    public Float getAnchorX() {
        return mAnchorAt.x;
    }

    public Float getAnchorY() {
        return mAnchorAt.y;
    }

    public Point getXY() {
        Point xy = getAbsoluteAnchorAt();
        if (mParentShape != null) {
            xy.x -= mParentShape.mAnchorAt.x;
            xy.y -= mParentShape.mAnchorAt.y;
        }
        return xy;
    }

    public void setXY(Point xy) {
        if (mParentShape != null) {
            moveTo(xy.x+mParentShape.mAnchorAt.x, xy.y+mParentShape.mAnchorAt.y);
        } else {
            moveTo(xy.x, xy.y);
        }
    }

    public void setX(Float x) {
        Point xy = getXY();
        xy.x = x;
        setXY(xy);
    }

    public void setY(Float y) {
        Point xy = getXY();
        xy.y = y;
        setXY(xy);
    }

    public void setStageX(Float x) {
        if (mParentShape != null) {
            x += mParentShape.mAnchorAt.x;
        }
        moveTo(x, getAbsoluteAnchorAt().y);
    }

    public void setStageY(Float y) {
        if (mParentShape != null) {
            y += mParentShape.mAnchorAt.y;
        }
        moveTo(getAbsoluteAnchorAt().x, y);
    }

    public void setAngle(Float angle) {
        Point relLefTopCorner = new Point(-mAnchorAt.x, -mAnchorAt.y);
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
        Point absAnchorAt = mAnchorAt.copy();
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
        point.translate(mAnchorAt.x, mAnchorAt.y);
        return point;
    }

    public Point reverseTransformPoint(Point point) {
        point = point.copy();
        point.translate(-mAnchorAt.x, -mAnchorAt.y);
        point.scale(mPostScaleX, mPostScaleY);
        point.rotateCoordinate(-mAngle);
        point.scale(mScaleX, mScaleY);
        if (mPreMatrix != null) {
            point.transform(mPreMatrix);
        }
        Point absAnchorAt = getAbsoluteAnchorAt();
        point.translate(absAnchorAt.x, absAnchorAt.y);
        return point;
    }

    public RectF getAbsoluteOutline() {
        RectF outline = new RectF(0, 0, mWidth, mHeight);
        Point[] points = new Point[4];
        points[0] = new Point(outline.left, outline.top);
        points[1] = new Point(outline.right, outline.top);
        points[2] = new Point(outline.right, outline.bottom);
        points[3] = new Point(outline.left, outline.bottom);

        Point absAnchorAt = getAbsoluteAnchorAt();
        Float minX = null, minY=null, maxX=null, maxY=null;
        for (int i=0; i<points.length; i++) {
            Point point = reverseTransformPoint(points[i]);
            if (minX == null || minX>point.x) minX = point.x;
            if (minY == null || minY>point.y) minY = point.y;
            if (maxX == null || maxX<point.x) maxX = point.x;
            if (maxY == null || maxY<point.y) maxY = point.y;
        }
        outline.set(minX, minY, maxX, maxY);
        return outline;
    }

    public void setProperty(PropName propName, Object value, HashMap<PropName, PropData> propDataMap) {
        switch (propName) {
            case ANGLE:
                setAngle((float) value);
                break;
            case TRANSLATION:
                mTranslation.copyFrom((Point) value);
                break;
            case ANCHOR_X:
                mAnchorAt.x = (float) value;
                break;
            case ANCHOR_Y:
                mAnchorAt.y = (float) value;
                break;
            case ANCHOR_AT:
                mAnchorAt.copyFrom((Point) value);
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
            case WIDTH:
                mWidth = (float) value;
                mPath = null;
                break;
            case HEIGHT:
                mHeight = (float) value;
                mPath = null;
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
            case STAGE_Y:
                setStageY((float) value);
                break;
            case PRE_MATRIX:
                mPreMatrix = (Matrix) value;
                break;
        }
    }
}
