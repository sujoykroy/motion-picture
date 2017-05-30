package bk2suz.motionpicturelib.Commons;

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
        for (ColorPoint colorPoint : gradientColor.mColorPoints) {
            mColorPoints.add(colorPoint.copy());
        }
    }

    public int[] getColors() {
        int[] colors = new int[mColorPoints.size()];
        for (int i = 0; i < mColorPoints.size(); i++) {
            colors[i] = mColorPoints.get(i).getColor().getIntValue();
        }
        return colors;
    }

    public float[] getPositions() {
        float[] positions = new float[mColorPoints.size()];
        float totalDistance = mColorPoints.get(mColorPoints.size() - 1).getPoint().distance(
                                mColorPoints.get(0).getPoint());
        for (int i = 0; i < mColorPoints.size(); i++) {
            positions[i] = mColorPoints.get(i).getPoint().distance(mColorPoints.get(0).getPoint()) / totalDistance;
        }
        return positions;
    }

    public void setInBetween(Color startColor, Color endColor, float frac) {
        if(!this.getClass().isInstance(startColor)) return;
        if(!this.getClass().isInstance(endColor)) return;

        GradientColor startGrad = (GradientColor) startColor;
        GradientColor endGrad = (GradientColor) endColor;

        float minPointCount = Math.min(startGrad.mColorPoints.size(), endGrad.mColorPoints.size());
        minPointCount = Math.min(minPointCount, this.mColorPoints.size());

        for(int i=0;i<minPointCount;i++) {
            this.mColorPoints.get(i).getColor().setInBetween(
                startGrad.mColorPoints.get(i).getColor(),
                startGrad.mColorPoints.get(i).getColor(), frac);
            this.mColorPoints.get(i).getPoint().setInBetween(
                    startGrad.mColorPoints.get(i).getPoint(),
                    startGrad.mColorPoints.get(i).getPoint(), frac);
        }
    }

    public void copyFromText(String text) {
        String[] values = text.split(";");
        for (int i = 0; i < values.length; i += 2) {
            FlatColor color = FlatColor.createFromText(values[i]);
            Point point = Point.createFromText(values[i + 1]);
            mColorPoints.add(new ColorPoint(color, point));
        }
    }
}
