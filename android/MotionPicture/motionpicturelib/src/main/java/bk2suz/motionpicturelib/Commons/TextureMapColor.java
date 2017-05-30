package bk2suz.motionpicturelib.Commons;

import android.graphics.Paint;

import java.util.Arrays;

/**
 * Created by sujoy on 29/5/17.
 */
public class TextureMapColor extends Color {
    public static final String TYPE_NAME = "tx";
    private TextureResources mTextureResources;
    private int mResourceIndex;
    private float[] mTexCoords;

    private TextureMapColor() {

    }

    public TextureMapColor(TextureResources textureResources, int resourceIndex, float[] texCoords) {
        mTextureResources = textureResources;
        mResourceIndex = resourceIndex;
        mTexCoords = Arrays.copyOf(texCoords, texCoords.length);
    }

    public TextureMapColor(int resourceIndex, float[] texCoords) {
        mResourceIndex = resourceIndex;
        mTexCoords = Arrays.copyOf(texCoords, texCoords.length);
    }

    public void setTextureResources(TextureResources textureResources) {
        mTextureResources = textureResources;
    }

    @Override
    public void copyFromText(String text) {
        String[] arr1 = text.split("/");
        mResourceIndex = Integer.parseInt(arr1[0]);
        String[] texcoords_text = arr1[1].split(",");
        mTexCoords = new float[texcoords_text.length];
        for(int i=0; i<texcoords_text.length; i++) {
            mTexCoords[i] = Float.parseFloat(texcoords_text[i]);
        }
    }

    public float[] getTexCoords() {
        return mTexCoords;
    }

    public String getResourcePath() {
        return mTextureResources.getResourcePath(mResourceIndex);
    }

    @Override
    public Color copy() {
        return null;
    }

    @Override
    public void setPaint(Paint paint) {

    }

    @Override
    public void copyFrom(Color color) {

    }

    @Override
    public void setInBetween(Color startColor, Color endColor, float frac) {

    }


    public static TextureMapColor createFromText(String text) {
        TextureMapColor textureMapColor = new TextureMapColor();
        textureMapColor.copyFromText(text);
        return textureMapColor;
    }
}
