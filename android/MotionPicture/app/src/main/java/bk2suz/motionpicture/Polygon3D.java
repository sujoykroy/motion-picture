package bk2suz.motionpicture;

import android.opengl.GLES20;
import android.util.Log;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.FloatBuffer;
import java.nio.ShortBuffer;
import java.util.Arrays;

public class Polygon3D {
    private static int FLOAT_BYTE_COUNT = 4;
    private static int SHORT_BYTE_COUNT = 2;
    private static int COORDS_PER_VERTEX = 3;
    private static int VERTEX_STRIDE = COORDS_PER_VERTEX*FLOAT_BYTE_COUNT;
    private static int COORDS_PER_TEXTURE = 2;
    private static int TEXTURE_STRIDE = COORDS_PER_TEXTURE*FLOAT_BYTE_COUNT;

    private int mVertexCount = 0;
    private float[] mVertices = null;
    private short[] mVertexOrder = null;
    private float[] mTexCoords = null;
    private float[] mDiffuseColor = { 0.63671875f, 0.76953125f, 0.22265625f, 1.0f };
    private String mTextureName = null;

    private FloatBuffer mVertexBuffer;
    private ShortBuffer mVertexOrderBuffer;
    private FloatBuffer mTexCoordBuffer;

    private final int mGLProgram;
    private int mGLPositionHandle;
    private int mGLTexCoordsHandle;
    private int mGLColorHandle;
    private int mGLHasTextureHandle;
    private int mGLTextureHandle;

    public Polygon3D(float[] vertices) {
        setVertices(vertices);

        mGLProgram = GLES20.glCreateProgram();
        GLES20.glAttachShader(mGLProgram, ThreeDShader.getVertexShader());
        GLES20.glAttachShader(mGLProgram, ThreeDShader.getFragmentShader());
        GLES20.glLinkProgram(mGLProgram);
    }

    public void setTextureName(String textureName) {
        mTextureName = textureName;
    }

    public void setVertices(float[] vertices) {
        mVertices = Arrays.copyOf(vertices, vertices.length);
        mVertexCount = vertices.length/COORDS_PER_VERTEX;
        mVertexOrder = new short[3+(mVertexCount-3)*3];
        int startCounter = 1;
        for(int i=0; i<mVertexOrder.length; i+=3) {
            mVertexOrder[i] = 0;
            mVertexOrder[i+1] = (short) startCounter;
            mVertexOrder[i+2] = (short) (startCounter+1);
            startCounter += 1;
        }

        ByteBuffer bb;

        bb = ByteBuffer.allocateDirect(mVertices.length*FLOAT_BYTE_COUNT);
        bb.order(ByteOrder.nativeOrder());
        mVertexBuffer = bb.asFloatBuffer();
        mVertexBuffer.put(mVertices);
        mVertexBuffer.position(0);

        bb = ByteBuffer.allocateDirect(mVertexOrder.length*SHORT_BYTE_COUNT);
        bb.order(ByteOrder.nativeOrder());
        mVertexOrderBuffer = bb.asShortBuffer();
        mVertexOrderBuffer.put(mVertexOrder);
        mVertexOrderBuffer.position(0);
    }

    public void setTexCoords(float[] texCoords) {
        mTexCoords = Arrays.copyOf(texCoords, texCoords.length);

        ByteBuffer bb;
        bb = ByteBuffer.allocateDirect(mTexCoords.length*FLOAT_BYTE_COUNT);
        bb.order(ByteOrder.nativeOrder());
        mTexCoordBuffer = bb.asFloatBuffer();
        mTexCoordBuffer.put(mTexCoords);
        mTexCoordBuffer.position(0);
    }

    public void draw(ThreeDTexture textureStore) {
        GLES20.glUseProgram(mGLProgram);

        mGLPositionHandle = GLES20.glGetAttribLocation(mGLProgram, "aPosition");
        GLES20.glEnableVertexAttribArray(mGLPositionHandle);
        GLES20.glVertexAttribPointer(mGLPositionHandle,
                COORDS_PER_VERTEX, GLES20.GL_FLOAT, false, VERTEX_STRIDE, mVertexBuffer);

        mGLColorHandle = GLES20.glGetUniformLocation(mGLProgram, "uColor");
        GLES20.glUniform4fv(mGLColorHandle, 1, mDiffuseColor, 0);

        mGLHasTextureHandle = GLES20.glGetUniformLocation(mGLProgram, "uHasTexture");
        if (mTextureName != null) {
            GLES20.glUniform1i(mGLHasTextureHandle, 1);

            mGLTexCoordsHandle = GLES20.glGetAttribLocation(mGLProgram, "aTexCoords");
            GLES20.glEnableVertexAttribArray(mGLTexCoordsHandle);
            GLES20.glVertexAttribPointer(mGLTexCoordsHandle,
                    COORDS_PER_TEXTURE, GLES20.GL_FLOAT, false, TEXTURE_STRIDE, mTexCoordBuffer);

            mGLTextureHandle = GLES20.glGetUniformLocation(mGLProgram, "uTexture");
            GLES20.glActiveTexture(GLES20.GL_TEXTURE0);
            GLES20.glBindTexture(GLES20.GL_TEXTURE_2D, textureStore.getTextureHandle(mTextureName));
            GLES20.glUniform1i(mGLTextureHandle, 0);
        } else {
            GLES20.glUniform1i(mGLHasTextureHandle, 0);
        }

        GLES20.glDrawElements(GLES20.GL_TRIANGLES, mVertexOrder.length,
                GLES20.GL_UNSIGNED_SHORT, mVertexOrderBuffer);
        //GLES20.glDrawArrays(GLES20.GL_TRIANGLES, 0, mVertices.length/COORDS_PER_VERTEX);

        GLES20.glDisableVertexAttribArray(mGLPositionHandle);
    }
}