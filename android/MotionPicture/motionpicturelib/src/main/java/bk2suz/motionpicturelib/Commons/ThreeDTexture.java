package bk2suz.motionpicturelib.Commons;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.opengl.GLES20;
import android.opengl.GLUtils;
import android.util.Log;

import java.util.HashMap;

/**
 * Created by sujoy on 27/5/17.
 */
public class ThreeDTexture {
    private Context mContext;
    private HashMap<String, Integer> mTextureHandleMaps = new HashMap<>();

    public ThreeDTexture(Context context) {
        mContext = context;
    }

    public int getTextureHandle(String resourceName) {
        if (!mTextureHandleMaps.containsKey(resourceName)) {
            loadTextureFromResource(resourceName);
        }
        return mTextureHandleMaps.get(resourceName);
    }

    public void loadTextureFromResource(String resoureName) {
        int[] textureHandles = new int[1];
        GLES20.glGenTextures(1, textureHandles, 0);

        int resId = mContext.getResources().getIdentifier(resoureName, null, mContext.getPackageName());
        Log.d("GALA", String.format("resId=%d", resId));
        Bitmap bitmap = BitmapFactory.decodeResource(mContext.getResources(), resId);

        GLES20.glActiveTexture(GLES20.GL_TEXTURE0);
        GLES20.glBindTexture(GLES20.GL_TEXTURE_2D, textureHandles[0]);

        GLES20.glTexParameteri(GLES20.GL_TEXTURE_2D, GLES20.GL_TEXTURE_MIN_FILTER, GLES20.GL_LINEAR);
        GLES20.glTexParameteri(GLES20.GL_TEXTURE_2D, GLES20.GL_TEXTURE_MAG_FILTER, GLES20.GL_LINEAR);

        GLES20.glTexParameteri(GLES20.GL_TEXTURE_2D, GLES20.GL_TEXTURE_WRAP_S, GLES20.GL_CLAMP_TO_EDGE);
        GLES20.glTexParameteri(GLES20.GL_TEXTURE_2D, GLES20.GL_TEXTURE_WRAP_T, GLES20.GL_CLAMP_TO_EDGE);

        GLUtils.texImage2D(GLES20.GL_TEXTURE_2D, 0, bitmap, 0);

        bitmap.recycle();

        mTextureHandleMaps.put(resoureName, textureHandles[0]);
    }
}
