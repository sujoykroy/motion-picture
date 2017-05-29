package bk2suz.motionpicturelib;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.RectF;
import android.opengl.GLSurfaceView;
import android.util.AttributeSet;

import bk2suz.motionpicturelib.Commons.PolygonGroup3D;
import bk2suz.motionpicturelib.Commons.ThreeDSurfaceRenderer;

/**
 * Created by sujoy on 26/5/17.
 */
public class ThreeDSurfaceView extends GLSurfaceView {
    private ThreeDSurfaceRenderer mRenderer;

    public ThreeDSurfaceView(Context context) {
        super(context);
        doInit();
    }

    public ThreeDSurfaceView(Context context, AttributeSet attrs) {
        super(context, attrs);
        doInit();
    }


    public void doInit() {
        setEGLContextClientVersion(2);
        mRenderer = new ThreeDSurfaceRenderer(getContext());
        setRenderer(mRenderer);
        //setRenderMode(GLSurfaceView.RENDERMODE_CONTINUOUSLY);
    }

    @Override
    protected void onAttachedToWindow() {
        super.onAttachedToWindow();
        setWillNotDraw(false);
    }

    public void setPolygonGroup3D(PolygonGroup3D polygonGroup) {
        mRenderer.setPolygonGroup3D(polygonGroup);
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        Paint paint = new Paint();
        paint.setColor(Color.BLUE);
        paint.setStyle(Paint.Style.STROKE);
        canvas.drawRect(new RectF(0, 0, 100, 100), paint);
    }
}
