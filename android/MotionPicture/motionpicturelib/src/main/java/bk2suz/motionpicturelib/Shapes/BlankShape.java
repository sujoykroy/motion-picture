package bk2suz.motionpicturelib.Shapes;

/**
 * Created by sujoy on 3/6/17.
 */
public class BlankShape extends Shape {
    public BlankShape() {
        super();
    }

    public void translate(float dx, float dy) {
        mTranslation.x = dx;
        mTranslation.y = dy;
    }

    public void scale(float sx, float sy) {
        mScaleX = sx;
        mScaleY = sy;
    }

}
