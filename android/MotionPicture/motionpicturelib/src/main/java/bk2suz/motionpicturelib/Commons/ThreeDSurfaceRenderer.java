package bk2suz.motionpicturelib.Commons;

import android.content.Context;
import android.opengl.GLES20;
import android.opengl.GLSurfaceView;
import android.opengl.Matrix;
import android.os.SystemClock;

import javax.microedition.khronos.egl.EGLConfig;
import javax.microedition.khronos.opengles.GL10;

/**
 * Created by sujoy on 26/5/17.
 */
public class ThreeDSurfaceRenderer implements GLSurfaceView.Renderer {
    private PolygonGroup3D mPolygonGroup3D = null;
    private PolygonGroup3D mAxes = null;

    private Camera3D mCamera3D = new Camera3D();
    private Projection3D mProjection3D = new Projection3D();

    private Context mContext;
    private ThreeDGLRenderContext mThreeDGLRenderContext;

    private float[] mVPMatrix = new float[16];
    private float[] mTempMatrix = new float[16];

    public ThreeDSurfaceRenderer(Context context) {
        super();
        mContext = context;

        mCamera3D.precalculate();
        mProjection3D.precalculate();
    }

    public void setPolygonGroup3D(PolygonGroup3D polygonGroup) {
        mPolygonGroup3D = polygonGroup;
    }

    @Override
    public void onDrawFrame(GL10 gl) {
        GLES20.glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
        GLES20.glClear(GLES20.GL_COLOR_BUFFER_BIT|GLES20.GL_DEPTH_BUFFER_BIT);
        Matrix.setIdentityM(mTempMatrix, 0);
        //mPolygon3D.draw(mModelMatrix, mTextureStore);

        if (mPolygonGroup3D == null) {
            return;
        }
        //Matrix.multiplyMM(mVPMatrix, 0, mCamera3D.getMatrix(), 0, mProjection3D.getMatrix(), 0);
        mVPMatrix = mProjection3D.getMatrix();
        //Matrix.multiplyMM(mVPMatrix, 0, mProjection3D.getMatrix(), 0, mTempMatrix, 0);
        //Log.d("GALA", String.format("mVPMatrix %s", Arrays.toString(mVPMatrix)));
        //Log.d("GALA", String.format("mProjection3D.getMatrix() %s", Arrays.toString(mProjection3D.getMatrix())));
        mPolygonGroup3D.setParentMatrix(mVPMatrix);
        long time = SystemClock.uptimeMillis() % 4000L;
        float angle = 0.090f * ((int) time);

        //mPolygonGroup3D.setRotatationX(angle);
        //mPolygonGroup3D.setRotatationY(angle);
        mPolygonGroup3D.precalculate();
        mPolygonGroup3D.draw(mThreeDGLRenderContext);

        //mAxes.setParentMatrix(mVPMatrix);
        mAxes.precalculate();
        mAxes.draw(mThreeDGLRenderContext);

    }

    @Override
    public void onSurfaceCreated(GL10 gl, EGLConfig config) {
        GLES20.glEnable( GLES20.GL_DEPTH_TEST );
        mThreeDGLRenderContext = new ThreeDGLRenderContext(mContext, gl);

        mAxes = PolygonGroup3D.createAxes(1.5f);
        //mPolygonGroup3D = PolygonGroup3D.createCube(.5f);
    }

    @Override
    public void onSurfaceChanged(GL10 gl, int width, int height) {
        GLES20.glViewport(0, 0, width, height);
        float ratio = (float) width / height;
        mProjection3D.setProjectionLeftRight(-ratio, ratio);
        mProjection3D.precalculate();
    }
}
