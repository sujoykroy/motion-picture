package bk2suz.motionpicture;

import android.graphics.Bitmap;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.ImageView;
import android.widget.SeekBar;

import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

import bk2suz.motionpicturelib.Commons.Object3D;
import bk2suz.motionpicturelib.Commons.PolygonGroup3D;
import bk2suz.motionpicturelib.Document;
import bk2suz.motionpicturelib.ImageGLRender;
import bk2suz.motionpicturelib.Shapes.Shape;
import bk2suz.motionpicturelib.Shapes.ThreeDShape;
import bk2suz.motionpicturelib.ThreeDSurfaceView;
import bk2suz.motionpicturelib.TimeLines.TimeLineTask;

public class OpenGLActivity extends AppCompatActivity {
    private SeekBar mSeekBarObjectRotateX;
    private SeekBar mSeekBarObjectRotateY;
    private SeekBar mSeekBarObjectRotateZ;

    private ThreeDSurfaceView mSurfaceView1;
    private ImageView mImageView;

    Document mDoc;
    Object3D mObject3D;
    ThreeDShape mThreeeDShape;
    PolygonGroup3D mPolygonGroup2;

    private static boolean sMakeDocBitmap = !true;
    private static boolean sShowGLSurface = true;
    private static boolean sShowAnimation = true;
    ImageGLRender.GLThread mImageRendererThread;

    TimeLineTask mTimeLineTask;
    ScheduledExecutorService mExecutor = Executors.newSingleThreadScheduledExecutor();
    Runnable mUpdateImageTask;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_open_gl);

        mSeekBarObjectRotateX = (SeekBar) findViewById(R.id.seekBarObjectRotateX);
        mSeekBarObjectRotateY = (SeekBar) findViewById(R.id.seekBarObjectRotateY);
        mSeekBarObjectRotateZ = (SeekBar) findViewById(R.id.seekBarObjectRotateZ);

        mImageView = (ImageView) findViewById(R.id.imageView);
        mSurfaceView1 = (ThreeDSurfaceView) findViewById(R.id.surfaceView1);

        mDoc = Document.loadFromResource(getResources(), R.xml.threed);
        Shape shape = mDoc.getShapeFromPath("coverob/myob");
        if(shape != null) {
            mThreeeDShape = (ThreeDShape) shape;
            mObject3D = mThreeeDShape.getContainer3D();
        } else {
            mObject3D = PolygonGroup3D.createCube(.25f);
            mObject3D.setScale(800);
        }
        mObject3D.precalculate();

        mSeekBarObjectRotateX.setOnSeekBarChangeListener(new ObjectRotationSeekerBarChangeListener("x"));
        mSeekBarObjectRotateY.setOnSeekBarChangeListener(new ObjectRotationSeekerBarChangeListener("y"));
        mSeekBarObjectRotateZ.setOnSeekBarChangeListener(new ObjectRotationSeekerBarChangeListener("z"));

        if(sShowGLSurface) {
            mSurfaceView1.setObject3D(mObject3D);
        } else {
            mSurfaceView1.setVisibility(View.GONE);
        }

        if(sMakeDocBitmap) {
            mDoc.createGLThread(this);
            showBitmap();
        } else {
            mDoc.createGLThread(this);
            mImageView.setImageBitmap(mDoc.getBitmap());
            //mDoc.deleteGLThread();
        }

        if (sShowAnimation) {
            mDoc.createGLThread(this);
            mTimeLineTask = new TimeLineTask(mDoc);
            mUpdateImageTask = new Runnable() {
                @Override
                public void run() {
                    showBitmap();
                }
            };
            mExecutor.scheduleAtFixedRate(new Runnable() {
                @Override
                public void run() {
                    try {
                        mTimeLineTask.moveTimeNext();
                        final Bitmap bitmap = mDoc.getBitmap();
                        mImageView.post(new Runnable() {
                            @Override
                            public void run() {
                                mImageView.setImageBitmap(bitmap);
                                mImageView.invalidate();
                            }
                        });
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }
            }, 0, 100, TimeUnit.MILLISECONDS);
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        mDoc.deleteGLThread();
    }

    private void showBitmap() {
        mDoc.clearBitmap();
        mImageView.setImageBitmap(mDoc.getBitmap());
        mImageView.invalidate();
    }

    class ObjectRotationSeekerBarChangeListener implements SeekBar.OnSeekBarChangeListener {
        String mAxis;

        public ObjectRotationSeekerBarChangeListener(String axis) {
            mAxis = axis;

        }

        @Override
        public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
            float angle = 360f*progress*.01f;
            if (mAxis.equals("x")) {
                mObject3D.setRotatationX(angle);
            } else if (mAxis.equals("y")) {
                mObject3D.setRotatationY(angle);
            } else if (mAxis.equals("z")) {
                mObject3D.setRotatationZ(angle);
            }
            mObject3D.precalculate();
            if(!sShowAnimation && sMakeDocBitmap) {
                showBitmap();
            }
            if(sShowGLSurface) {
                mSurfaceView1.requestRender();
            }
        }

        @Override
        public void onStartTrackingTouch(SeekBar seekBar) {

        }

        @Override
        public void onStopTrackingTouch(SeekBar seekBar) {

        }
    }
}
