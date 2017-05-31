package bk2suz.motionpicture;

import android.graphics.Bitmap;
import android.opengl.GLES20;
import android.os.Handler;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.widget.ImageView;
import android.widget.SeekBar;

import java.nio.IntBuffer;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import javax.microedition.khronos.opengles.GL10;

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
        if(shape != null) {
            mObject3D1 = ((ThreeDShape) shape).getContainer3D();
            mObject3D1.setScale(800f);
        } else {
            mObject3D1 = PolygonGroup3D.createCube(.25f);
            mObject3D1.setScale(200);
        }
        //mObject3D1 = PolygonGroup3D.createCube(.25f);
        mObject3D1.precalculate();
        //mObject3D1 = PolygonGroup3D.createAxes(.5f);
        //mPolygonGroup2 = PolygonGroup3D.createCube(.8f);

        mSurfaceView1 = (ThreeDSurfaceView) findViewById(R.id.surfaceView1);
        //mSurfaceView2 = (ThreeDSurfaceView) findViewById(R.id.surfaceView2);

        //mSurfaceView1.setObject3D(mObject3D1);
        //mSurfaceView2.setPolygonGroup3D(mPolygonGroup2);

        mSeekBarObjectRotateX.setOnSeekBarChangeListener(new ObjectRotationSeekerBarChangeListener("x"));
        mSeekBarObjectRotateY.setOnSeekBarChangeListener(new ObjectRotationSeekerBarChangeListener("y"));
        mSeekBarObjectRotateZ.setOnSeekBarChangeListener(new ObjectRotationSeekerBarChangeListener("z"));

        //m3DSurfaceView = new ThreeDSurfaceView(this);
        //setContentView(m3DSurfaceView);
        //glThread = new ThreeDGLBitmapRenderer.GLThread(this, mObject3D1);
        //glThread.start();

        handler = new Handler(this.getMainLooper());
        executor = Executors.newSingleThreadExecutor();
        Runnable processBitmap = new Runnable() {
            @Override
            public void run() {
                ThreeDGLBitmapRenderer bitmapRenderer= new ThreeDGLBitmapRenderer(100, 100);
                ThreeDSurfaceRenderer surfaceRenderer = new ThreeDSurfaceRenderer(getApplicationContext());
                surfaceRenderer.onSurfaceCreated(null, null);
                surfaceRenderer.onSurfaceChanged(null, 100, 100);
                surfaceRenderer.setObject3D(mObject3D1);
                surfaceRenderer.onDrawFrame(null);
                int mWidth=100;
                int mHeight=100;
                IntBuffer ib = IntBuffer.allocate(100*100);
                IntBuffer ibt = IntBuffer.allocate(100*100);
                GLES20.glReadPixels(0, 0, mWidth, mHeight, GL10.GL_RGBA, GL10.GL_UNSIGNED_BYTE, ib);

                // Convert upside down mirror-reversed image to right-side up normal image.
                /*for (int i = 0; i < mHeight; i++) {
                    for (int j = 0; j < mWidth; j++) {
                        ibt.put((mHeight-i-1)*mWidth + j, ib.get(i*mWidth + j));
                    }
                }*/

                final Bitmap bitmap = Bitmap.createBitmap(mWidth, mHeight, Bitmap.Config.ARGB_8888);
                bitmap.copyPixelsFromBuffer(ibt);

                handler.post(new Runnable() {
                    @Override
                    public void run() {
                        mImageView.setImageBitmap(bitmap);
                        mImageView.invalidate();
                        Log.d("GALA", String.format("w=%d", bitmap.getWidth()));
                    }
                });
            }
        };
        executor.execute(processBitmap);
    }
    Handler handler;
    ExecutorService executor;
    ThreeDGLBitmapRenderer.GLThread glThread;

    class ObjectRotationSeekerBarChangeListener implements SeekBar.OnSeekBarChangeListener {
        String mAxis;

        public ObjectRotationSeekerBarChangeListener(String axis) {
            mAxis = axis;

        }

        @Override
        public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
            //Log.d("GALA", String.format("progress=%d", progress));
            float angle = 360f*progress*.01f;
            if(mAxis.equals("x")) {
                mObject3D1.setRotatationX(angle);
            } else if(mAxis.equals("y")) {
                mObject3D1.setRotatationY(angle);
            } else if(mAxis.equals("z")) {
                mObject3D1.setRotatationZ(angle);
            }
            mObject3D1.precalculate();
            mSurfaceView1.requestRender();
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
