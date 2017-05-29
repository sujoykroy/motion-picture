package bk2suz.motionpicturelib.Commons;

/**
 * Created by sujoy on 9/10/16.
 */
public class ColorPoint {
    private FlatColor mColor;
    private Point mPoint;

    public ColorPoint(FlatColor color, Point point) {
        mColor = color;
        mPoint = point;
    }

    public ColorPoint copy() {
        return new ColorPoint(mColor.copy(), mPoint.copy());
    }

    public FlatColor getColor() {
        return mColor;
    }

    public Point getPoint() {
        return mPoint;
    }
}
