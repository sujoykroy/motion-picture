package bk2suz.motionpicturelib.Commons;

import android.opengl.Matrix;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;
import java.util.Arrays;

/**
 * Created by sujoy on 27/5/17.
 */
public abstract class Object3D {
    protected Point3D mTranslation = new Point3D();
    protected Point3D mRotation = new Point3D();
    protected Point3D mScale = new Point3D(1f, 1f, 1f);

    protected Color mBorderColor;
    protected Color mFillColor;
    protected Float mBorderWidth;

    protected TextureResources mTextureResources = null;
    //protected final float[] mTranslationMatrix = new float[16];
    //protected final float[] mRotationMatrix = new float[16];

    protected float[] mTempMatrix = new float[16];;
    protected final float[] mModelMatrix = new float[16];
    protected float[] mExtraMatrix =null;

    protected float[] mParentMatrix = null;
    protected Object3D mParentObject3D = null;

    public void precalculate() {
        Matrix.setIdentityM(mModelMatrix, 0);
        if (mExtraMatrix != null) {
            System.arraycopy(mExtraMatrix, 0, mModelMatrix, 0, mExtraMatrix.length);
        }
        Matrix.translateM(mModelMatrix, 0, mTranslation.getX(), mTranslation.getY(), mTranslation.getZ());

        //Matrix.setIdentityM(mRotationMatrix, 0);
        //Matrix.setRotateEulerM(mRotationMatrix, 0, mRotation.getX(), mRotation.getY(), mRotation.getZ());
        Matrix.rotateM(mModelMatrix, 0, mRotation.getX(), 1, 0, 0);
        Matrix.rotateM(mModelMatrix, 0, mRotation.getY(), 0, 1, 0);
        Matrix.rotateM(mModelMatrix, 0, mRotation.getZ(), 0, 0, 1);

        //Matrix.multiplyMM(mModelMatrix, 0, mTranslationMatrix, 0, mRotationMatrix, 0);

        Matrix.scaleM(mModelMatrix, 0, mScale.getX(), mScale.getY(), mScale.getZ());

        if (mParentObject3D != null) {
            mTempMatrix = mModelMatrix.clone();
            Matrix.multiplyMM(mModelMatrix, 0, mParentObject3D.getMatrix(), 0, mTempMatrix, 0);
        }

        if (mParentMatrix != null) {
            mTempMatrix = mModelMatrix.clone();
            Matrix.multiplyMM(mModelMatrix, 0, mParentMatrix, 0, mTempMatrix, 0);
        }
    }

    public void setFillColor(Color color) {
        if(color != null) {
            color = color.copy();
        }
        mFillColor = color;
    }

    public void setBorderWidth(Float value) {
        mBorderWidth = value;
    }

    public Color getActiveBorderColor() {
        if (mBorderColor == null && mParentObject3D != null) {
            return mParentObject3D.getActiveBorderColor();
        }
        return mBorderColor;
    }

    public Color getActiveFillColor() {
        if (mFillColor == null && mParentObject3D != null) {
            return mParentObject3D.getActiveFillColor();
        }
        return mFillColor;
    }

    public Float getActiveBorderWidth() {
        if (mBorderWidth == null && mParentObject3D != null) {
            return mParentObject3D.getActiveBorderWidth();
        }
        return mBorderWidth;
    }

    public void setBorderColor(Color color) {
        if(color != null) {
            color = color.copy();
        }
        mBorderColor = color;
    }

    public void setTextureResources(TextureResources textureResources) {
        mTextureResources = textureResources;
    }

    public TextureResources getTextureResources() {
        if(mTextureResources != null) return mTextureResources;
        if(mParentObject3D != null) return mParentObject3D.getTextureResources();
        return null;
    }

    public float[] getMatrix() {
        return mModelMatrix;
    }

    public void setParentMatrix(float[] matrix) {
        mParentMatrix = matrix;
    }

    public void setParentObject(Object3D parentObject) {
        mParentObject3D = parentObject;
    }

    public void setRotatationX(float x) {
        mRotation.setX(x);
    }

    public void setRotatationY(float y) {
        mRotation.setY(y);
    }

    public void setRotatationZ(float z) {
        mRotation.setZ(z);
    }

    public void setScale(float scale) {
        mScale.setXYZ(scale, scale, scale);
    }

    abstract public void draw(ThreeDGLRenderContext threeDGLRenderContext);

    public void load_from_xml_element(XmlPullParser parser)
            throws XmlPullParserException, IOException {
        mTranslation.copyFromText(parser.getAttributeValue(null, "tr"));
        mRotation.copyFromText(parser.getAttributeValue(null, "rot"));
        mScale.copyFromText(parser.getAttributeValue(null, "sc"));
        mBorderColor = Helper.parseColor(parser.getAttributeValue(null, "bc"));
        mFillColor = Helper.parseColor(parser.getAttributeValue(null, "fc"));
        try {
            mBorderWidth = Float.parseFloat(parser.getAttributeValue(null, "bw"));
        } catch (NumberFormatException e) {
            mBorderWidth = null;
        } catch (NullPointerException e) {
            mBorderWidth = null;
        }
        String extraMatrixText = parser.getAttributeValue(null, "mtx");
        if (extraMatrixText != null) {
            mExtraMatrix = new float[16];
            String[] values = extraMatrixText.split(",");


            //Matrix is stored in xml in row major format.
            //Opengl matrix is in column major format.
            //So, the fetched matrix needs to be transposed.
            for(int r=0; r<4; r++) {
                for(int c=0; c<4; c++) {
                    try {
                        mExtraMatrix[c*4+r] = Float.parseFloat(values[r*4+c]);
                    } catch (NumberFormatException e) {
                    }
                }
            }
        }
    }
}
