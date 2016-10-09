package bk2suz.motionpicturelib;

import android.graphics.Paint;

/**
 * Created by sujoy on 9/10/16.
 */
public class LinearGradientColor extends GradientColor {
    public static final String TYPE_NAME = "linear";

    @Override
    public void setPaint(Paint paint) {

    }

    @Override
    public Color copy() {
        LinearGradientColor linearColor = new LinearGradientColor();
        linearColor.copyFrom(this);
        return linearColor;
    }

    public static LinearGradientColor createFromText(String text) {
        LinearGradientColor linearColor = new LinearGradientColor();
        linearColor.copyFromText(text);
        return linearColor;
    }
}
