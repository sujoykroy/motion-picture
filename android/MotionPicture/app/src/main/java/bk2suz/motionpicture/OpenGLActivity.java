package bk2suz.motionpicture;

import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.RectF;
import android.opengl.GLES20;
import android.os.Handler;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.widget.ImageView;
import android.widget.SeekBar;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.IntBuffer;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.ThreadPoolExecutor;

import bk2suz.motionpicturelib.Commons.Object3D;
import bk2suz.motionpicturelib.Commons.PolygonGroup3D;
import bk2suz.motionpicturelib.Commons.ThreeDGLBitmapRenderer;
import bk2suz.motionpicturelib.Commons.ThreeDSurfaceRenderer;
import bk2suz.motionpicturelib.Document;
import bk2suz.motionpicturelib.Shapes.Shape;
import bk2suz.motionpicturelib.Shapes.ThreeDShape;
import bk2suz.motionpicturelib.ThreeDSurfaceView;

public class OpenGLActivity extends AppCompatActivity {
    private ThreeDSurfaceView m3DSurfaceView;
    private SeekBar mSeekBarObjectRotateX;
    private SeekBar mSeekBarObjectRotateY;
    private SeekBar mSeekBarObjectRotateZ;

    private ThreeDSurfaceView mSurfaceView1;
    private ThreeDSurfaceView mSurfaceView2;

    private ImageView mImageView;

    Object3D mObject3D1;
    PolygonGroup3D mPolygonGroup2;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_open_gl);

        mSeekBarObjectRotateX = (SeekBar) findViewById(R.id.seekBarObjectRotateX);
        mSeekBarObjectRotateY = (SeekBar) findViewById(R.id.seekBarObjectRotateY);
        mSeekBarObjectRotateZ = (SeekBar) findViewById(R.id.seekBarObjectRotateZ);

        mImageView = (ImageView) findViewById(R.id.imageView);

        Document mDoc = Document.loadFromResource(getResources(), R.xml.threed2);
        Shape shape = mDoc.getShapeFromPath("myob");
        if(shape != null && !false) {
            mObject3D1 = ((ThreeDShape) shape).getContainer3D();
            mObject3D1.setScale(800f);
        } else {
            mObject3D1 = PolygonGroup3D.createCube(.25f);
            mObject3D1.setScale(800);
        }
        //mObject3D1 = PolygonGroup3D.createCube(.25f);
        mObject3D1.precalculate();
        //mObject3D1 = PolygonGroup3D.createAxes(.5f);
        //mPolygonGroup2 = PolygonGroup3D.createCube(.8f);

        mSurfaceView1 = (ThreeDSurfaceView) findViewById(R.id.surfaceView1);
        //mSurfaceView2 = (ThreeDSurfaceView) findViewById(R.id.surfaceView2);

        if (!MakeBitmap) {
            mSurfaceView1.setObject3D(mObject3D1);
        }
        //mSurfaceView2.setPolygonGroup3D(mPolygonGroup2);

        mSeekBarObjectRotateX.setOnSeekBarChangeListener(new ObjectRotationSeekerBarChangeListener("x"));
        mSeekBarObjectRotateY.setOnSeekBarChangeListener(new ObjectRotationSeekerBarChangeListener("y"));
        mSeekBarObjectRotateZ.setOnSeekBarChangeListener(new ObjectRotationSeekerBarChangeListener("z"));

        //m3DSurfaceView = new ThreeDSurfaceView(this);
        //setContentView(m3DSurfaceView);
        //glThread = new ThreeDGLBitmapRenderer.GLThread(this, mObject3D1);
        //glThread.start();

        handler = new Handler(this.getMainLooper());
        executor = (ThreadPoolExecutor) Executors.newFixedThreadPool(1);

        if(MakeBitmap) {
            mImageRendererThread = new ImageGLRender.GLThread(400, 400, this);
            mImageRendererThread.start();
            showBitmap();
        }

    }

    @Override
    protected void onResume() {
        super.onResume();

    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if(bitmapRenderer!=null) {
            bitmapRenderer.release();
        }
    }

    private static boolean MakeBitmap = true;
    Handler handler;
    ThreadPoolExecutor executor;
    ImageGLRender.GLThread mImageRendererThread;
    Object mLockObject = new Object();
    Object mRenderLock = new Object();
    ImageGLRender bitmapRenderer;
    ThreeDSurfaceRenderer surfaceRenderer;

    private void showBitmap() {
        ImageGLRender.GLImageFutureTask task = mImageRendererThread.requestBitmapFor(mObject3D1);
        try {
            mImageView.setImageBitmap(task.get());
        } catch (InterruptedException e) {
            e.printStackTrace();
        } catch (ExecutionException e) {
            e.printStackTrace();
        }
        mImageView.invalidate();
    }
    private void showBitmap2() {
        /*if(!executor.getQueue().isEmpty()) {
            return;
        }*/
        Runnable processBitmap = new Runnable() {
            @Override
            public void run() {
                //ThreeDGLBitmapRenderer bitmapRenderer= new ThreeDGLBitmapRenderer(100, 100);
                int w=400;
                int h = 400;
                Bitmap bmp;
                synchronized (mRenderLock) {
                    if(bitmapRenderer==null) {
                        bitmapRenderer = new ImageGLRender(w, h);
                        surfaceRenderer = new ThreeDSurfaceRenderer(getApplicationContext());
                        surfaceRenderer.onSurfaceCreated(null, null);
                        surfaceRenderer.onSurfaceChanged(null, w, h);
                    }
                    //Object3D object3D = PolygonGroup3D.createCube(.25f);
                    synchronized (mLockObject) {
                        Object3D object3D = mObject3D1;
                        //object3D.setScale(100);
                        object3D.precalculate();
                        surfaceRenderer.setObject3D(object3D);
                        surfaceRenderer.onDrawFrame(null);
                    }
                    bmp= bitmapRenderer.getBitmap();
                }
                final Bitmap bitmap = bmp;
                Canvas canvas = new Canvas(bitmap);
                Paint paint = new Paint();
                paint.setStrokeWidth(5);
                paint.setColor(Color.GRAY);
                paint.setStyle(Paint.Style.STROKE);
                canvas.drawRect(new RectF(0, 0, 30, 30), paint);
                handler.post(new Runnable() {
                    @Override
                    public void run() {
                        mImageView.setImageBitmap(bitmap);
                        mImageView.invalidate();
                    }
                });

            }
        };
        executor.execute(processBitmap);
    }

    class ObjectRotationSeekerBarChangeListener implements SeekBar.OnSeekBarChangeListener {
        String mAxis;

        public ObjectRotationSeekerBarChangeListener(String axis) {
            mAxis = axis;

        }

        @Override
        public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
            //Log.d("GALA", String.format("progress=%d", progress));
            float angle = 360f*progress*.01f;
            synchronized (mLockObject) {
                if (mAxis.equals("x")) {
                    mObject3D1.setRotatationX(angle);
                } else if (mAxis.equals("y")) {
                    mObject3D1.setRotatationY(angle);
                } else if (mAxis.equals("z")) {
                    mObject3D1.setRotatationZ(angle);
                }
                mObject3D1.precalculate();
            }
            mSurfaceView1.requestRender();
            if(MakeBitmap) showBitmap();
            //mSurfaceView1.invalidate();
        }

        @Override
        public void onStartTrackingTouch(SeekBar seekBar) {

        }

        @Override
        public void onStopTrackingTouch(SeekBar seekBar) {

        }
    }
}
