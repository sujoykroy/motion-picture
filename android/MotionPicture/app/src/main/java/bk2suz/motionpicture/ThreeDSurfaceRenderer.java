package bk2suz.motionpicture;

import android.content.Context;
import android.opengl.GLES20;
import android.opengl.GLSurfaceView;

import javax.microedition.khronos.egl.EGLConfig;
import javax.microedition.khronos.opengles.GL10;

/**
 * Created by sujoy on 26/5/17.
 */
public class ThreeDSurfaceRenderer implements GLSurfaceView.Renderer {
    private Polygon3D mPolygon3D;
    private Context mContext;
    private ThreeDTexture mTextureStore;

    public ThreeDSurfaceRenderer(Context context) {
        super();
        mContext = context;
        mTextureStore = new ThreeDTexture(mContext);
    }

    @Override
    public void onDrawFrame(GL10 gl) {
        GLES20.glClearColor(1.0f, 0.0f, 0.0f, 1.0f);
        mPolygon3D.draw(mTextureStore);
    }

    @Override
    public void onSurfaceCreated(GL10 gl, EGLConfig config) {
        GLES20.glClear(GLES20.GL_COLOR_BUFFER_BIT);

        mPolygon3D = new Polygon3D(new float[] {
                -0.5f,  0.9f, 0.0f,  // 0, Top Left
                -1.0f, -1.0f, 0.0f,  // 1, Bottom Left
                1.0f, -1.0f, 0.0f,  // 2, Bottom Right
                1.0f,  1.0f, 0.0f,  // 3, Top Right
        });
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
        mPolygon3D.setTextureName("mipmap/ic_launcher");
        mPolygon3D.setTexCoords(new float[] {
                0.0F, 1F,
                0F, 0F,
                1F, 0F,
                1F, 1F

        });
    }

    @Override
    public void onSurfaceChanged(GL10 gl, int width, int height) {
        GLES20.glViewport(0, 0, width, height);
    }
}
