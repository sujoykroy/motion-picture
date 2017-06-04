package bk2suz.motionpicturelib.Commons;

import android.content.Context;
import android.opengl.GLES20;
import android.opengl.GLSurfaceView;
import android.opengl.Matrix;
import android.os.SystemClock;
import android.util.Log;

import java.util.Arrays;

import javax.microedition.khronos.egl.EGLConfig;
import javax.microedition.khronos.opengles.GL10;

/**
 * Created by sujoy on 26/5/17.
 */
public class ThreeDSurfaceRenderer implements GLSurfaceView.Renderer {
    private Object3D mObject3D = null;
    private PolygonGroup3D mAxes = null;


    private boolean mShowAxes = false;
    private Camera3D mCamera3D = new Camera3D();
    private Projection3D mProjection3D = new Projection3D();

    private Context mContext;
    private ThreeDGLRenderContext mThreeDGLRenderContext;

    private float[] mVPMatrix = new float[16];
    private float[] mTempMatrix = new float[16];
    private float[] mPreMatrix;

    public ThreeDSurfaceRenderer(Context context) {
        super();
        mContext = context;

        mCamera3D.precalculate();
        mProjection3D.precalculate();
    }

    public void setPreMatrix(float[] preMatrix) {
        mPreMatrix = preMatrix;
    }

    public void setObject3D(Object3D object3D) {
        mObject3D = object3D;
    }

    @Override
    public void onDrawFrame(GL10 gl) {
        GLES20.glClearColor(0.0f, 0.0f, 0.0f, 0.0f);
        GLES20.glClear(GLES20.GL_COLOR_BUFFER_BIT|GLES20.GL_DEPTH_BUFFER_BIT);

        Matrix.setIdentityM(mTempMatrix, 0);
        if (mPreMatrix != null) {
            Matrix.multiplyMM(mVPMatrix, 0, mPreMatrix, 0, mTempMatrix, 0);
        } else {
            mTempMatrix = mCamera3D.getMatrix();
            Matrix.multiplyMM(mVPMatrix, 0, mProjection3D.getMatrix(), 0, mTempMatrix, 0);
        }
        if (mObject3D != null) {
            mObject3D.setParentMatrix(mVPMatrix);
            mObject3D.precalculate();
            mObject3D.draw(mThreeDGLRenderContext);

        }
        if(mShowAxes) {
            mAxes.setParentMatrix(mVPMatrix);
            mAxes.precalculate();
            mAxes.draw(mThreeDGLRenderContext);
        }
    }

    @Override
    public void onSurfaceCreated(GL10 gl, EGLConfig config) {
        GLES20.glEnable( GLES20.GL_DEPTH_TEST );
        mThreeDGLRenderContext = new ThreeDGLRenderContext(mContext);

        mAxes = PolygonGroup3D.createAxes(.5f);
        mAxes.setScale(500);
    }

    @Override
    public void onSurfaceChanged(GL10 gl, int width, int height) {
        GLES20.glViewport(0, 0, width, height);
        float ratio = (float) width / height;
        mProjection3D.setProjectionLeftRight(-width*.5f, width*.5f);
        mProjection3D.setProjectionTopBottom(height/2, -height/2);
        int depth = Math.max(width, height)/2;
        mProjection3D.setProjectionNearFar(-depth, depth);
        mProjection3D.precalculate();
    }
}
