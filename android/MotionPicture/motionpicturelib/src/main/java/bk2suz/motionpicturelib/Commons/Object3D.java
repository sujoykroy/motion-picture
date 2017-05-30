package bk2suz.motionpicturelib.Commons;

import android.opengl.Matrix;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;

/**
 * Created by sujoy on 27/5/17.
 */
public class Object3D {
    protected Point3D mTranslation = new Point3D();
    protected Point3D mRotation = new Point3D();
    protected Point3D mScale = new Point3D(1f, 1f, 1f);

    protected TextureResources mTextureResources = null;
    //protected final float[] mTranslationMatrix = new float[16];
    //protected final float[] mRotationMatrix = new float[16];

    protected float[] mTempMatrix = new float[16];;
    protected final float[] mModelMatrix = new float[16];
    protected float[] mExtraMatrix =null;

    protected float[] mParentMatrix = null;

    public void precalculate() {
        Matrix.setIdentityM(mModelMatrix, 0);
        Matrix.translateM(mModelMatrix, 0, mTranslation.getX(), mTranslation.getY(), mTranslation.getZ());

        //Matrix.setIdentityM(mRotationMatrix, 0);
        //Matrix.setRotateEulerM(mRotationMatrix, 0, mRotation.getX(), mRotation.getY(), mRotation.getZ());
        Matrix.rotateM(mModelMatrix, 0, mRotation.getX(), 1, 0, 0);
        Matrix.rotateM(mModelMatrix, 0, mRotation.getY(), 0, 1, 0);
        Matrix.rotateM(mModelMatrix, 0, mRotation.getZ(), 0, 0, 1);

        //Matrix.multiplyMM(mModelMatrix, 0, mTranslationMatrix, 0, mRotationMatrix, 0);

        Matrix.scaleM(mModelMatrix, 0, mScale.getX(), mScale.getY(), mScale.getZ());

        if (mParentMatrix != null) {
            mTempMatrix = mModelMatrix.clone();
            Matrix.multiplyMM(mModelMatrix, 0, mParentMatrix, 0, mTempMatrix, 0);
        }
    }

    public void setTextureResources(TextureResources textureResources) {
        mTextureResources = textureResources;
    }

    public float[] getMatrix() {
        return mModelMatrix;
    }

    public void setParentMatrix(float[] matrix) {
        mParentMatrix = matrix;
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

    public void load_from_xml_element(XmlPullParser parser)
            throws XmlPullParserException, IOException {
        mTranslation.copyFromText(parser.getAttributeValue(null, "tr"));
        mRotation.copyFromText(parser.getAttributeValue(null, "rot"));
        mScale.copyFromText(parser.getAttributeValue(null, "sc"));
        String extraMatrixText = parser.getAttributeValue(null, "mtx");
        if (extraMatrixText != null) {
            mExtraMatrix = new float[16];
            String[] values = extraMatrixText.split(",");
            for(int i=0; i<values.length; i++) {
                try {
                    mExtraMatrix[i] = Float.parseFloat(values[i]);
                } catch (NumberFormatException e) {
                }
            }
        }
        while (parser.next() != XmlPullParser.END_TAG) {
            if (parser.getEventType() != XmlPullParser.START_TAG) {
                continue;
            }
            if (parser.getName().equals(TextureResources.TAG_NAME)) {
                if (mTextureResources == null) {
                    mTextureResources = new TextureResources();
                }
                mTextureResources.addResourceFromXmlElement(parser);
            }
            Helper.skipTag(parser);
        }
    }
}
