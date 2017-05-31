package bk2suz.motionpicture;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.widget.SeekBar;

import bk2suz.motionpicturelib.Commons.Object3D;
import bk2suz.motionpicturelib.Commons.PolygonGroup3D;
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

    Object3D mObject3D1;
    PolygonGroup3D mPolygonGroup2;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_open_gl);

        mSeekBarObjectRotateX = (SeekBar) findViewById(R.id.seekBarObjectRotateX);
        mSeekBarObjectRotateY = (SeekBar) findViewById(R.id.seekBarObjectRotateY);
        mSeekBarObjectRotateZ = (SeekBar) findViewById(R.id.seekBarObjectRotateZ);


        Document mDoc = Document.loadFromResource(getResources(), R.xml.threed);
        Shape shape = mDoc.getShapeFromPath("myob");
        if(shape != null) {
            mObject3D1 = ((ThreeDShape) shape).getContainer3D();
        } else {
            mObject3D1 = PolygonGroup3D.createCube(.25f);
        }
        //mObject3D1 = PolygonGroup3D.createAxes(.5f);
        //mPolygonGroup2 = PolygonGroup3D.createCube(.8f);

        mSurfaceView1 = (ThreeDSurfaceView) findViewById(R.id.surfaceView1);
        //mSurfaceView2 = (ThreeDSurfaceView) findViewById(R.id.surfaceView2);

        mSurfaceView1.setObject3D(mObject3D1);
        //mSurfaceView2.setPolygonGroup3D(mPolygonGroup2);

        mSeekBarObjectRotateX.setOnSeekBarChangeListener(new ObjectRotationSeekerBarChangeListener("x"));
        mSeekBarObjectRotateY.setOnSeekBarChangeListener(new ObjectRotationSeekerBarChangeListener("y"));
        mSeekBarObjectRotateZ.setOnSeekBarChangeListener(new ObjectRotationSeekerBarChangeListener("z"));

        //m3DSurfaceView = new ThreeDSurfaceView(this);
        //setContentView(m3DSurfaceView);
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
