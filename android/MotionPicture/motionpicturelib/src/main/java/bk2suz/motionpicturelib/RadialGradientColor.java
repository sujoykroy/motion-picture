package bk2suz.motionpicturelib;

import android.graphics.Paint;

/**
 * Created by sujoy on 9/10/16.
 */
public class RadialGradientColor extends GradientColor {
    public static final String TYPE_NAME = "radial";

    @Override
    public void setPaint(Paint paint) {

    }

    @Override
    public Color copy() {
        RadialGradientColor radialColor = new RadialGradientColor();
        radialColor.copyFrom(this);
        return radialColor;
    }

    public static RadialGradientColor createFromText(String text) {
        RadialGradientColor radialColor = new RadialGradientColor();
        radialColor.copyFromText(text);
        return radialColor;
    }
}
