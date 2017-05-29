package bk2suz.motionpicturelib.Commons;

/**
 * Created by sujoy on 27/5/17.
 */
public class Point3D {
    private float mX;
    private float mY;
    private float mZ;

    public Point3D() {
        mX = 0F;
        mY = 0F;
        mZ = 0F;
    }

    public Point3D(float x, float y, float z) {
        mX = x;
        mY = y;
        mZ = z;
    }

    public float getX() {
        return mX;
    }

    public float getY() {
        return mY;
    }

    public float getZ() {
        return mZ;
    }

    public void setX(float x) {
        mX = x;
    }

    public void setY(float y) {
        mY = y;
    }

    public void setZ(float z) {
        mZ = z;
    }

    public void setXYZ(float x, float y, float z) {
        mX = x;
        mY = y;
        mZ = z;
    }

    public void addXYZ(float x, float y, float z) {
        mX += x;
        mY += y;
        mZ += z;
    }
}
