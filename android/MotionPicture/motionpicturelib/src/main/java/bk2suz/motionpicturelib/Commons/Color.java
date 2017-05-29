package bk2suz.motionpicturelib.Commons;

import android.graphics.Paint;

/**
 * Created by sujoy on 8/10/16.
 */
public abstract class Color {
    public abstract void setPaint(Paint paint);
    public abstract void copyFrom(Color color);
    public abstract Color copy();
    public abstract void setInBetween(Color startColor, Color endColor, float frac);
}
