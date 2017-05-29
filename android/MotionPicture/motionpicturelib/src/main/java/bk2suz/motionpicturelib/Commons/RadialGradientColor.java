package bk2suz.motionpicturelib.Commons;

import android.graphics.Paint;
import android.graphics.RadialGradient;
import android.graphics.Shader;

/**
 * Created by sujoy on 9/10/16.
 */
public class RadialGradientColor extends GradientColor {
    public static final String TYPE_NAME = "radial";

    @Override
    public void setPaint(Paint paint) {
        RadialGradient radialShader = new RadialGradient(
                mColorPoints.get(0).getPoint().x, mColorPoints.get(0).getPoint().y,
                mColorPoints.get(mColorPoints.size()-1).getPoint().distance(mColorPoints.get(0).getPoint()),
                getColors(),
                getPositions(),
                Shader.TileMode.CLAMP
        );
        paint.setShader(radialShader);
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
