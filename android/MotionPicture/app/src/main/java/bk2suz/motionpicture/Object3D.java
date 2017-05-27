package bk2suz.motionpicture;

import android.opengl.Matrix;

/**
 * Created by sujoy on 27/5/17.
 */
public class Object3D {
    protected Point3D mTranslation = new Point3D();
    protected Point3D mRotation = new Point3D();
    protected Point3D mScale = new Point3D(1f, 1f, 1f);

    protected final float[] mTranslationMatrix = new float[16];
    protected final float[] mRotationMatrix = new float[16];

    protected float[] mTempMatrix = new float[16];;
    protected final float[] mViewMatrix = new float[16];

    protected float[] mParentMatrix = null;

    public void precalculate() {
        Matrix.setIdentityM(mTranslationMatrix, 0);
        Matrix.translateM(mTranslationMatrix, 0, mTranslation.getX(), mTranslation.getY(), mTranslation.getZ());

        Matrix.setRotateEulerM(mRotationMatrix, 0, mRotation.getX(), mRotation.getY(), mRotation.getZ());
        Matrix.multiplyMM(mViewMatrix, 0, mTranslationMatrix, 0, mRotationMatrix, 0);

        Matrix.scaleM(mViewMatrix, 0, mScale.getX(), mScale.getY(), mScale.getZ());

        if (mParentMatrix != null) {
            mTempMatrix = mViewMatrix.clone();
            Matrix.multiplyMM(mViewMatrix, 0, mTempMatrix, 0, mParentMatrix, 0);
        }
    }

    public float[] getMatrix() {
        return mViewMatrix;
    }

    public void setParentMatrix(float[] matrix) {
        mParentMatrix = matrix;
    }

    public void setRotatationX(float x) {
        mRotation.setX(x);
    }

    public void setRotatationY(float y) {
        mRotation.setY(y);
    }

    public void setRotatationZ(float z) {
        mRotation.setZ(z);
    }
}
