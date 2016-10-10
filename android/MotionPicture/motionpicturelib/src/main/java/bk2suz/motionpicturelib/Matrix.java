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
