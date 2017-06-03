package bk2suz.motionpicturelib.Shapes;

import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.PorterDuff;
import android.graphics.PorterDuffXfermode;
import android.graphics.RectF;
import android.opengl.Matrix;
import android.util.Log;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;
import java.util.Arrays;
import java.util.concurrent.ExecutionException;

import bk2suz.motionpicturelib.Commons.Camera3D;
import bk2suz.motionpicturelib.Commons.Color;
import bk2suz.motionpicturelib.Commons.Container3D;
import bk2suz.motionpicturelib.Commons.Helper;
import bk2suz.motionpicturelib.Commons.Point;
import bk2suz.motionpicturelib.Commons.Projection3D;
import bk2suz.motionpicturelib.ImageGLRender;

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

    @Override
    public float[] getGLMatrix() {
        float[] selfMatrix = new float[16];
        float[] tempMatrix;

        android.opengl.Matrix.setIdentityM(selfMatrix, 0);
        android.opengl.Matrix.translateM(selfMatrix, 0, mTranslation.x, -mTranslation.y, 0);
        if (mPreMatrix != null) {
            tempMatrix = selfMatrix.clone();
            android.opengl.Matrix.multiplyMM(selfMatrix, 0, tempMatrix, 0, mPreMatrix.getGLMatrix(), 0);
        }
        android.opengl.Matrix.scaleM(selfMatrix, 0, mScaleX, mScaleY, 1);
        android.opengl.Matrix.rotateM(selfMatrix, 0, -mAngle, 0, 0, 1);
        android.opengl.Matrix.scaleM(selfMatrix, 0, mPostScaleX, mPostScaleY, 1);
        android.opengl.Matrix.translateM(selfMatrix, 0, mAnchorAt.x, -mAnchorAt.y, 0);

        if(mParentShape != null) {
            tempMatrix = selfMatrix.clone();
            android.opengl.Matrix.multiplyMM(selfMatrix, 0, mParentShape.getGLMatrix(), 0, tempMatrix, 0);
        }
        return selfMatrix;
    }

    public Bitmap getBitmap(Canvas canvas) {
        int w = canvas.getWidth();
        int h = canvas.getHeight();
        ImageGLRender.GLThread thread = ImageGLRender.GLThreadManager.getThread(w, h);
        if(thread == null) {
            return null;
        }
        float[] selfMatrix = getGLMatrix();
        float[] tempMatrix = selfMatrix.clone();

        Point point = mAnchorAt.copy();
        point = absoluteReverseTransformPoint(point);

        Projection3D projection3D = new Projection3D();
        projection3D.setProjectionLeftRight(0, w);
        projection3D.setProjectionTopBottom(0, -h);

        int depth = Math.max(w, h)/2;
        projection3D.setProjectionNearFar(-depth, depth);
        projection3D.precalculate();

        Matrix.multiplyMM(tempMatrix, 0, projection3D.getMatrix(), 0, selfMatrix, 0);
        //tempMatrix = null;
        ImageGLRender.GLImageFutureTask task = thread.requestBitmapFor(tempMatrix, mD3Object);

        try {
            return task.get();
        } catch (InterruptedException e) {
            return null;
        } catch (ExecutionException e) {
            return null;
        }
    }

    @Override
    public void draw(Canvas canvas) {
        if (getPath() == null) return;
        if (mFillColor != null) {
            canvas.save();
            preDraw(canvas);
            drawFill(canvas);
            canvas.restore();
        }
        Bitmap bitmap = getBitmap(canvas);
        if(bitmap != null) {
            canvas.save();
            Path path = new Path(getPath());
            path.transform(getGraphicsMatrix());
            canvas.clipPath(path);
            Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
            //paint.setXfermode(new PorterDuffXfermode(PorterDuff.Mode.SRC_OVER));
            canvas.drawBitmap(bitmap, 0, 0, paint);
            canvas.restore();
        }
        if (mBorderColor != null) {
            /*
            canvas.save();
            Path path = new Path(getPath());
            path.transform(getGraphicsMatrix());
            canvas.drawPath(path, mBorderPaint);
            canvas.restore();
            */

            canvas.save();
            preDraw(canvas);
            drawBorder(canvas);
            canvas.restore();

            /*
            canvas.save();
            preDraw(canvas);
            canvas.translate(mAnchorAt.x, mAnchorAt.y);
            canvas.drawRect(new RectF(-5, -5, 5, 5), mBorderPaint);
            canvas.restore();
            */
        }
    }

    public Container3D getContainer3D() {
        return mD3Object;
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
                threeDShape.mD3Object.precalculate();
            }
            Helper.skipTag(parser);
        }
        return threeDShape;
    }
}
