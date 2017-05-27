package bk2suz.motionpicture;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;

public class OpenGLActivity extends AppCompatActivity {
    private ThreeDSurfaceView m3DSurfaceView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_open_gl);

        //m3DSurfaceView = new ThreeDSurfaceView(this);
        //setContentView(m3DSurfaceView);
    }
}
