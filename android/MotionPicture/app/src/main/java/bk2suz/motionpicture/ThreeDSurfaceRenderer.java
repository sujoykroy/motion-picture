package bk2suz.motionpicture;

import android.content.Context;
import android.opengl.GLES20;
import android.opengl.GLSurfaceView;
import android.opengl.Matrix;
import android.os.SystemClock;
import android.util.Log;

import javax.microedition.khronos.egl.EGLConfig;
import javax.microedition.khronos.opengles.GL10;

/**
 * Created by sujoy on 26/5/17.
 */
public class ThreeDSurfaceRenderer implements GLSurfaceView.Renderer {
    private PolygonGroup3D mPolygonGroup3D = null;
    private Polygon3D mPolygon3D;
    private Camera3D mCamera3D = new Camera3D();
    private Projection3D mProjection3D = new Projection3D();
    private Context mContext;
    private ThreeDTexture mTextureStore;

    private float[] mViewMatrix = new float[16];

    public ThreeDSurfaceRenderer(Context context) {
        super();
        mContext = context;
        mTextureStore = new ThreeDTexture(mContext);

        mCamera3D.precalculate();
        mProjection3D.precalculate();
    }

    public void setPolygonGroup3D(PolygonGroup3D polygonGroup) {
        mPolygonGroup3D = polygonGroup;
    }

    @Override
    public void onDrawFrame(GL10 gl) {
        GLES20.glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
        GLES20.glClear(GLES20.GL_COLOR_BUFFER_BIT);
        Matrix.setIdentityM(mViewMatrix, 0);
        //mPolygon3D.draw(mViewMatrix, mTextureStore);

        if (mPolygonGroup3D == null) {
            return;
        }
        //Matrix.multiplyMM(mViewMatrix, 0, mProjection3D.getMatrix(), 0, mCamera3D.getMatrix(), 0);
        mViewMatrix = mProjection3D.getMatrix();
        mPolygonGroup3D.setParentMatrix(mViewMatrix);
        long time = SystemClock.uptimeMillis() % 4000L;
        float angle = 0.090f * ((int) time);

        //mPolygonGroup3D.rotateDeg(30f, 30f, angle);
        mPolygonGroup3D.precalculate();
        mPolygonGroup3D.draw(mTextureStore);

    }

    @Override
    public void onSurfaceCreated(GL10 gl, EGLConfig config) {
        Polygon3D.createProgram();
        //mPolygonGroup3D = PolygonGroup3D.createCube(.5f);

        mPolygon3D = new Polygon3D(new float[] {
                -0.5f,  0.9f, 0.0f,  // 0, Top Left
                -1.0f, -1.0f, 0.0f,  // 1, Bottom Left
                1.0f, -1.0f, 0.0f,  // 2, Bottom Right
                1.0f,  1.0f, 0.0f,  // 3, Top Right
        });
        mPolygon3D.setDiffuseColor(new float[] {1, 0, 0, 1});
        /*
         mPolygon3D = new Polygon3D(new float[] {
                -0.5f,  0.5f, 0.0f,  // 0, Top Left
                -0.5f, -0.5f, 0.0f,  // 1, Bottom Left
                0.5f, -0.5f, 0.0f,  // 2, Bottom Right
                0.5f,  0.5f, 0.0f,  // 3, Top Right
        });
        */
        /*
        mPolygon3D = new Polygon3D(new float[] {
                0.0f,  0.622008459f, 0.0f, // top
                -0.5f, -0.311004243f, 0.0f, // bottom left
                0.5f, -0.311004243f, 0.0f  // bottom right

        });
        */
        /*
        mPolygon3D.setTextureName("mipmap/ic_launcher");
        mPolygon3D.setTexCoords(new float[] {
                0.0F, 1F,
                0F, 0F,
                1F, 0F,
                1F, 1F

        });
        */
    }

    @Override
    public void onSurfaceChanged(GL10 gl, int width, int height) {
        GLES20.glViewport(0, 0, width, height);
        float ratio = (float) width / height;
        mProjection3D.setProjectionLeftRight(-ratio, ratio);
        mProjection3D.precalculate();
    }
}
