package bk2suz.motionpicturelib;

import android.content.Context;
import android.content.res.Resources;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.PorterDuff;
import android.graphics.PorterDuffXfermode;
import android.graphics.RectF;
import android.util.Log;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;

import bk2suz.motionpicturelib.Commons.Point;
import bk2suz.motionpicturelib.Shapes.BlankShape;
import bk2suz.motionpicturelib.Shapes.MultiShape;
import bk2suz.motionpicturelib.Shapes.Shape;
import bk2suz.motionpicturelib.TimeLines.MultiShapeTimeLine;

/**
 * Created by sujoy on 8/10/16.
 */
public class Document {
    private Float mWidth, mHeight;
    private MultiShape mMainMultiShape;
    private MultiShapeTimeLine mMainTimeLine;

    private Bitmap mBitmap = null;
    private float mBitmapWidth, mBitmapHeight;

    private Point mDrawEntryPoint = new Point(0F, 0F);
    private Point mDrawScale = null;
    private boolean mClip = false;

    private final Object BitmapLock = new Object();

    public Document(Float width, Float height) {
        mWidth = width;
        mHeight = height;
        mBitmapWidth = width;
        mBitmapHeight = height;
    }

    public MultiShapeTimeLine getMainTimeLine() {
        if (mMainMultiShape == null) return null;
        return mMainMultiShape.getLastTimeLine();
    }


    public Shape getShapeFromPath(String path) {
        String[] paths = path.split("/");
        Shape shape = mMainMultiShape;
        for (int i=0; i<paths.length; i++) {
            if(!MultiShape.class.isInstance(shape)) {
                shape = null;
                break;
            }
            shape = ((MultiShape) shape).getChildShape(paths[i]);
        }
        return shape;
    }

    public void setBitmapSize(float width, float height) {
        synchronized (BitmapLock) {
            mBitmapWidth = width;
            mBitmapHeight = height;
            mBitmap = null;
        }
    }

    public void clearBitmap() {
        synchronized (BitmapLock) {
            mBitmap = null;
        }
    }


    private boolean mGLThreadCreated = false;

    public void createGLThread(Context context) {
        if(!mMainMultiShape.hasThreeDShape()) return;
        mGLThreadCreated = ImageGLRender.GLThreadManager.createThread((int)mBitmapWidth, (int)mBitmapHeight, context);
    }

    public void deleteGLThread() {
        if(!mGLThreadCreated) return;
        ImageGLRender.GLThreadManager.deleteThread((int)mBitmapWidth, (int)mBitmapHeight);
        mGLThreadCreated = false;
    }

    public Bitmap getBitmap() {
        synchronized (BitmapLock) {
            if (mBitmap == null) {
                Bitmap bitmap = Bitmap.createBitmap((int) mBitmapWidth, (int) mBitmapHeight, Bitmap.Config.ARGB_8888);
                Canvas canvas = new Canvas(bitmap);

                float scale = Math.min(mBitmapWidth / mWidth, mBitmapHeight / mHeight);
                float dx = (mBitmapWidth - scale * mWidth) * .5F;
                float dy = (mBitmapHeight - scale * mHeight) * .5F;

                BlankShape bitmapShape = null;
                if(scale!=1) {
                    bitmapShape = new BlankShape();
                    bitmapShape.translate(dx, dy);
                    bitmapShape.scale(scale, scale);
                }
                if (mMainMultiShape != null) {
                    if(bitmapShape != null) {
                        mMainMultiShape.setParentShape(bitmapShape);
                    }
                    canvas.save();
                    mMainMultiShape.draw(canvas);
                    canvas.restore();
                    if(bitmapShape != null) {
                        mMainMultiShape.setParentShape(null);
                    }
                }
                if(bitmapShape != null) {
                    Paint clearPaint = new Paint();
                    clearPaint.setStyle(Paint.Style.FILL_AND_STROKE);
                    clearPaint.setXfermode(new PorterDuffXfermode(PorterDuff.Mode.MULTIPLY));
                    clearPaint.setARGB(0, 0, 0, 0);
                    Path coverPath = new Path();
                    coverPath.addRect(0, 0, mBitmapWidth, mBitmapHeight, Path.Direction.CW);
                    Path actualImagePath = new Path();
                    actualImagePath.addRect(new RectF(dx, dy, dx+scale*mWidth, dy+scale*mHeight), Path.Direction.CW);
                    coverPath.op(actualImagePath, Path.Op.DIFFERENCE);
                    canvas.drawPath(coverPath, clearPaint);
                }
                mBitmap = bitmap;
            }
        }
        return  mBitmap;
    }

    public void setDrawPosition(float x, float y) {
        mDrawEntryPoint.x = x;
        mDrawEntryPoint.y = y;
    }

    public void setDrawScale(float scale) {
        if (mDrawScale == null) {
            mDrawScale = new Point(1F, 1F);
        }
        mDrawScale.x = scale;
        mDrawScale.y = scale;
    }

    public void setDrawClip(boolean clip) {
        mClip = clip;
    }

    public void draw(Canvas canvas) {
        if(mMainMultiShape == null) return;
        canvas.save();
        canvas.translate(mDrawEntryPoint.x, mDrawEntryPoint.y);
        if(mDrawScale != null) {
            canvas.scale(mDrawScale.x, mDrawScale.y);
        }
        if(mClip) {
            canvas.clipRect(0, 0, mWidth, mHeight);
        }
        canvas.translate(-mMainMultiShape.getAnchorX(), -mMainMultiShape.getAnchorY());
        mMainMultiShape.draw(canvas);
        canvas.restore();
    }


    private static Document loadFromParser(XmlPullParser parser) {
        Document document = null;
        try {
            boolean rootFound = false;
            while (parser.next() != XmlPullParser.END_DOCUMENT) {
                if (parser.getEventType() != XmlPullParser.START_TAG) {
                    continue;
                }
                String name = parser.getName();
                if (!rootFound) {
                    if (name.equals("root")) {
                        rootFound = true;
                    } else {
                        continue;
                    }
                }
                if (name.equals("app")) {
                    String appName = parser.getAttributeValue(null, "name");
                    Float appVersion = 0F;
                    try {
                        appVersion = Float.parseFloat(parser.getAttributeValue(null, "version"));
                    } catch (NumberFormatException e) {
                    }
                    if (!appName.equals("MotionPicture") || appVersion < 0.1F) {
                        return null;
                    }
                } else if (name.equals("doc")) {
                    Float docWidth = 100F;
                    Float docHeight = 100F;
                    try {
                        docWidth = Float.parseFloat(parser.getAttributeValue(null, "width"));
                        docHeight = Float.parseFloat(parser.getAttributeValue(null, "height"));
                    } catch (NumberFormatException e) {
                    }
                    document = new Document(docWidth, docHeight);
                } else if (name.equals("shape") && document != null) {
                    document.mMainMultiShape = MultiShape.createFromXml(parser);
                }
            }
        } catch (XmlPullParserException e) {
        } catch (IOException e) {
        }
        return document;
    }

    public static Document loadFromResource(Resources resources, int resourceId) {
        XmlPullParser parser;
        try {
            parser = resources.getXml(resourceId);
        } catch (Resources.NotFoundException e) {
            return null;
        }
        return loadFromParser(parser);
    }
}
