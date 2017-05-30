package bk2suz.motionpicturelib.Commons;

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

    public float[] getFloatArrayValue() {
        return new float[] {mRed, mGreen, mBlue, mAlpha};
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

    public void setInBetween(Color startColor, Color endColor, float frac) {
        if(!FlatColor.class.isInstance(startColor)) return;
        if(!FlatColor.class.isInstance(endColor)) return;

        FlatColor startFlatColor = (FlatColor) startColor;
        FlatColor endFlatColor = (FlatColor) endColor;

        this.mRed = startFlatColor.mRed + (endFlatColor.mRed - startFlatColor.mRed)*frac;
        this.mGreen = startFlatColor.mGreen + (endFlatColor.mGreen - startFlatColor.mGreen)*frac;
        this.mBlue = startFlatColor.mBlue + (endFlatColor.mBlue - startFlatColor.mBlue)*frac;
        this.mAlpha = startFlatColor.mAlpha + (endFlatColor.mAlpha - startFlatColor.mAlpha)*frac;
    }

    @Override
    public void copyFromText(String text) {
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
        mRed = floatValues[0];
        mGreen = floatValues[1];
        mBlue = floatValues[2];
        mAlpha = floatValues[3];
    }

    public static FlatColor createFromText(String text) {
        FlatColor flatColor = new FlatColor(0f, 0f, 0f, 1f);
        flatColor.copyFromText(text);
        return flatColor;
    }
}
