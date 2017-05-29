package bk2suz.motionpicturelib.Commons;

import android.graphics.LinearGradient;
import android.graphics.Paint;
import android.graphics.Shader;

/**
 * Created by sujoy on 9/10/16.
 */
public class LinearGradientColor extends GradientColor {
    public static final String TYPE_NAME = "linear";

    @Override
    public void setPaint(Paint paint) {
        LinearGradient linearShader = new LinearGradient(
                mColorPoints.get(0).getPoint().x, mColorPoints.get(0).getPoint().y,
                mColorPoints.get(mColorPoints.size()-1).getPoint().x,
                mColorPoints.get(mColorPoints.size()-1).getPoint().y,
                getColors(),
                getPositions(),
                Shader.TileMode.CLAMP
        );
        paint.setShader(linearShader);
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
