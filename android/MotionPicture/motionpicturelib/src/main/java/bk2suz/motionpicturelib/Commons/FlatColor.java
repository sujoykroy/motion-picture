package bk2suz.motionpicturelib.Commons;

import android.graphics.Paint;

/**
 * Created by sujoy on 8/10/16.
 */
public class FlatColor extends Color {
    private float[] mRGBA = new float[4];

    public FlatColor(Float red, Float green, Float blue, Float alpha) {
        mRGBA[0] = red;
        mRGBA[1] = green;
        mRGBA[2] = blue;
        mRGBA[3] = alpha;
    }

    @Override
    public void setPaint(Paint paint) {
        paint.setShader(null);
        paint.setARGB((int)(mRGBA[3]*255), (int)(mRGBA[0]*255), (int)(mRGBA[1]*255), (int)(mRGBA[2]*255));
    }

    public int getIntValue() {
        return android.graphics.Color.argb(
                (int)(mRGBA[3]*255), (int)(mRGBA[0]*255), (int)(mRGBA[1]*255), (int)(mRGBA[2]*255));
    }

    public float[] getFloatArrayValue() {
        return mRGBA;
    }

    @Override
    public FlatColor copy() {
        return new FlatColor(mRGBA[0], mRGBA[1], mRGBA[2], mRGBA[3]);
    }

    @Override
    public void copyFrom(Color color) {
        if(!FlatColor.class.isInstance(color)) return;
        FlatColor flatColor = (FlatColor) color;
        mRGBA[0] = flatColor.mRGBA[0];
        mRGBA[1] = flatColor.mRGBA[1];
        mRGBA[2] = flatColor.mRGBA[2];
        mRGBA[3] = flatColor.mRGBA[3];
    }

    public void setInBetween(Color startColor, Color endColor, float frac) {
        if(!FlatColor.class.isInstance(startColor)) return;
        if(!FlatColor.class.isInstance(endColor)) return;

        FlatColor startFlatColor = (FlatColor) startColor;
        FlatColor endFlatColor = (FlatColor) endColor;

        for (int i =0; i<4; i++) {
            mRGBA[i] = startFlatColor.mRGBA[i] + (endFlatColor.mRGBA[i] - startFlatColor.mRGBA[i]) * frac;
        }
    }

    @Override
    public void copyFromText(String text) {
        String[] values = text.split(",");
        for (int i=0; i<4 && i< values.length; i++) {
            try {
                mRGBA[i] = Float.parseFloat(values[i]);
            } catch (NumberFormatException e) {
            }
        }
    }

    public static FlatColor createFromText(String text) {
        FlatColor flatColor = new FlatColor(0f, 0f, 0f, 1f);
        flatColor.copyFromText(text);
        return flatColor;
    }
}
