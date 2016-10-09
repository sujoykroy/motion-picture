package bk2suz.motionpicturelib;

import android.graphics.Paint;

/**
 * Created by sujoy on 8/10/16.
 */
public abstract class Color {
    public abstract void setPaint(Paint paint);
    public abstract void copyFrom(Color color);
    public abstract Color copy();
}
