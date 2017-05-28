package bk2suz.motionpicture;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.widget.SeekBar;

public class OpenGLActivity extends AppCompatActivity {
    private ThreeDSurfaceView m3DSurfaceView;
    private SeekBar mSeekBarObjectRotateX;
    private SeekBar mSeekBarObjectRotateY;
    private SeekBar mSeekBarObjectRotateZ;

    private ThreeDSurfaceView mSurfaceView1;
    private ThreeDSurfaceView mSurfaceView2;

    PolygonGroup3D mPolygonGroup1;
    PolygonGroup3D mPolygonGroup2;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_open_gl);

        mSeekBarObjectRotateX = (SeekBar) findViewById(R.id.seekBarObjectRotateX);
        mSeekBarObjectRotateY = (SeekBar) findViewById(R.id.seekBarObjectRotateY);
        mSeekBarObjectRotateZ = (SeekBar) findViewById(R.id.seekBarObjectRotateZ);

        mPolygonGroup1 = PolygonGroup3D.createCube(.5f);
        //mPolygonGroup1 = PolygonGroup3D.createAxes(.5f);
        //mPolygonGroup2 = PolygonGroup3D.createCube(.8f);

        mSurfaceView1 = (ThreeDSurfaceView) findViewById(R.id.surfaceView1);
        mSurfaceView2 = (ThreeDSurfaceView) findViewById(R.id.surfaceView2);

        mSurfaceView1.setPolygonGroup3D(mPolygonGroup1);
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
                mPolygonGroup1.setRotatationX(angle);
            } else if(mAxis.equals("y")) {
                mPolygonGroup1.setRotatationY(angle);
            } else if(mAxis.equals("z")) {
                mPolygonGroup1.setRotatationZ(angle);
            }
            mPolygonGroup1.precalculate();
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
