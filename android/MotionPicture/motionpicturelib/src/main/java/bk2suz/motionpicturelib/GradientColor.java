package bk2suz.motionpicturelib;

import java.util.ArrayList;

/**
 * Created by sujoy on 9/10/16.
 */
public abstract class GradientColor extends Color {
    protected ArrayList<ColorPoint> mColorPoints = new ArrayList<>();

    @Override
    public void copyFrom(Color color) {
        GradientColor gradientColor = (GradientColor) color;
        mColorPoints.clear();
        for (ColorPoint colorPoint: gradientColor.mColorPoints) {
            mColorPoints.add(colorPoint.copy());
        }
    }

    protected void copyFromText(String text) {
        String[] values = text.split(";");
        for(int i=0; i<values.length; i+=2) {
            FlatColor color = FlatColor.createFromText(values[i]);
            Point point = Point.createFromText(values[i+1]);
            mColorPoints.add(new ColorPoint(color, point));
        }
    }
}
