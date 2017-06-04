package bk2suz.motionpicturelib.Commons;

import android.opengl.Matrix;

/**
 * Created by sujoy on 27/5/17.
 */
public class Camera3D {
    private Point3D mEyePoint = new Point3D(0, 0, 1f);
    private Point3D mCenter = new Point3D();
    private Point3D mUpVector = new Point3D(0f, 1f, 0f);

    private float[] mViewMatrix = new float[16];
    private Point3D mRotation = new Point3D();

    public void precalculate() {
        Matrix.setLookAtM(
                mViewMatrix, 0,
                mEyePoint.getX(), mEyePoint.getY(), mEyePoint.getZ(),
                mCenter.getX(), mCenter.getY(), mCenter.getZ(),
                mUpVector.getX(), mUpVector.getY(), mUpVector.getZ()
        );
        Matrix.rotateM(mViewMatrix, 0, -mRotation.getX(), 1, 0, 0);
        Matrix.rotateM(mViewMatrix, 0, -mRotation.getY(), 0, 1, 0);
        Matrix.rotateM(mViewMatrix, 0, -mRotation.getZ(), 0, 0, 1);
    }

    public void rotate(Point3D point3D) {
        mRotation.setXYZ(point3D.getX(), point3D.getY(), point3D.getZ());
    }

    public float[] getMatrix() {
        return mViewMatrix;
    }
}
