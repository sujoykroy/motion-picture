package bk2suz.motionpicturelib;

import android.graphics.Paint;

/**
 * Created by sujoy on 8/10/16.
 */
public class FlatColor extends Color {
    float mRed, mGreen, mBlue, mAlpha;

    public FlatColor(Float red, Float green, Float blue, Float alpha) {
        mRed = red;
        mGreen = green;
        mBlue = blue;
        mAlpha = alpha;
    }

    @Override
    public void setPaint(Paint paint) {
        paint.setShader(null);
        paint.setARGB((int)(mAlpha*255), (int)(mRed*255), (int)(mGreen*255), (int)(mBlue*255));
    }

    public int getIntValue() {
        return android.graphics.Color.argb(
                (int)(mAlpha*255), (int)(mRed*255), (int)(mGreen*255), (int)(mBlue*255));
    }

    @Override
    public FlatColor copy() {
        return new FlatColor(mRed, mGreen, mBlue, mAlpha);
    }

    @Override
    public void copyFrom(Color color) {
        if(!FlatColor.class.isInstance(color)) return;
        FlatColor flatColor = (FlatColor) color;
        mRed = flatColor.mRed;
        mGreen = flatColor.mGreen;
        mBlue = flatColor.mBlue;
        mAlpha = flatColor.mAlpha;
    }

    public static FlatColor createFromText(String text) {
        String[] values = text.split(",");
        Float[] floatValues = new Float[4];
        for (int i=0; i<4; i++) {
            floatValues[i] = 1F;
            if (i>=values.length) {
                continue;
            }
            try {
                floatValues[i] = Float.parseFloat(values[i]);
            } catch (NumberFormatException e) {
            }
        }
        return new FlatColor(floatValues[0], floatValues[1], floatValues[2], floatValues[3]);
    }
}
