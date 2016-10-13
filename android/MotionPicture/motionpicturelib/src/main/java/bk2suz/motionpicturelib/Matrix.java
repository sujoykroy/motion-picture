package bk2suz.motionpicturelib;

/**
 * Created by sujoy on 8/10/16.
 */
public class Matrix {
    Float mXX, mYX, mXY, mYY, mX0, mY0;

    public Matrix(Float xx, Float yx, Float xy, Float yy, Float x0, Float y0) {
        mXX = xx;
        mYX = yx;
        mXY = xy;
        mYY = yy;
        mX0 = x0;
        mY0 = y0;
    }

    public android.graphics.Matrix getGraphicsMatrix() {
        android.graphics.Matrix graphicsMatrix = new android.graphics.Matrix();
        graphicsMatrix.setValues(new float[] {mXX, mXY, mX0, mYX, mYY, mY0, 0F, 0F, 1F});
        return graphicsMatrix;
    }

    public void setInBetween(Matrix startMatrix, Matrix endMatrix, float frac) {
        this.mXX = startMatrix.mXX + (endMatrix.mXX-startMatrix.mXX)*frac;
        this.mYX = startMatrix.mYX + (endMatrix.mYX-startMatrix.mYX)*frac;
        this.mXY = startMatrix.mXY + (endMatrix.mXY-startMatrix.mXY)*frac;
        this.mYY = startMatrix.mYY + (endMatrix.mYY-startMatrix.mYY)*frac;
        this.mX0 = startMatrix.mX0 + (endMatrix.mX0-startMatrix.mX0)*frac;
        this.mY0 = startMatrix.mY0 + (endMatrix.mY0-startMatrix.mY0)*frac;
    }

    public static Matrix createFromText(String text) {
        if (text == null) return null;
        String[] values = text.split(",");
        if (values.length<6) {
            return null;
        }
        Float[] floatValues = new Float[6];
        for(int i=0; i<6; i++) {
            try {
                floatValues[i] = Float.parseFloat(values[i]);
            } catch (NumberFormatException e) {
                return null;
            }
        }
        return new Matrix(floatValues[0], floatValues[1], floatValues[2], floatValues[3], floatValues[4], floatValues[5]);
    }
}
