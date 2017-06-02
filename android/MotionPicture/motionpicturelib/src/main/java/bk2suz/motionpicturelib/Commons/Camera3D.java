package bk2suz.motionpicturelib.Commons;

import android.opengl.Matrix;

/**
 * Created by sujoy on 27/5/17.
 */
public class Camera3D {
    private Point3D mEyePoint = new Point3D(0F, 0F, 0F);
    private Point3D mCenter = new Point3D();
    private Point3D mUpVector = new Point3D(0F, 1F, 0F);

    private final float[] mViewMatrix = new float[16];


    public void precalculate() {
        Matrix.setLookAtM(
                mViewMatrix, 0,
                mEyePoint.getX(), mEyePoint.getY(), mEyePoint.getZ(),
                mCenter.getX(), mCenter.getY(), mCenter.getZ(),
                mUpVector.getX(), mUpVector.getY(), mUpVector.getZ()
        );
    }

    public float[] getMatrix() {
        return mViewMatrix;
    }
}
