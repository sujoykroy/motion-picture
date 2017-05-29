package bk2suz.motionpicturelib.Commons;

import android.opengl.Matrix;

/**
 * Created by sujoy on 27/5/17.
 */
public class Projection3D {
    private float mProjectionLeft = -1f;
    private float mProjectionRight = 1f;
    private float mProjectionTop = 1f;
    private float mProjectionBottom = -1f;
    private float mProjectionNear = -10;
    private float mProjectionFar = 2;

    private final float[] mProjectionMatrix = new float[16];


    public void precalculate() {
        Matrix.orthoM(
                mProjectionMatrix, 0,
                mProjectionLeft, mProjectionRight,
                mProjectionBottom, mProjectionTop,
                mProjectionNear, mProjectionFar
        );
    }

    public void setProjectionLeftRight(float left, float right) {
        mProjectionLeft = left;
        mProjectionRight = right;
    }

    public float[] getMatrix() {
        return mProjectionMatrix;
    }
}
