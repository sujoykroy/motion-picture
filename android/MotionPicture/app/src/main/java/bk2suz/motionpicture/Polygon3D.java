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
    private float[] mDiffuseColor = null;
    private String mTextureName = null;

    private FloatBuffer mVertexBuffer;
    private ShortBuffer mVertexOrderBuffer;
    private FloatBuffer mTexCoordBuffer;

    private boolean mIsLineDrawing = false;

    static class Program3D {
        private final int mGLProgram;
        private int mGLPositionHandle;
        private int mGLTexCoordsHandle;
        private int mGLColorHandle;
        private int mGLHasTextureHandle;
        private int mGLTextureHandle;
        private int mMVPMatrixHandle;

        public Program3D() {
            mGLProgram = GLES20.glCreateProgram();
            GLES20.glAttachShader(mGLProgram, ThreeDShader.getVertexShader());
            GLES20.glAttachShader(mGLProgram, ThreeDShader.getFragmentShader());
            GLES20.glLinkProgram(mGLProgram);
        }
    }

    private static Program3D sProgram3D = null;

    public static void createProgram() {
        if (sProgram3D == null) {
            sProgram3D = new Program3D();
            //Log.d("GALA", "ssome");
        }
    }

    private PolygonGroup3D mParentGroup = null;
    private float[] mActiveDiffuseColor;

    public Polygon3D(float[] vertices) {
        setVertices(vertices);

    }

    public void setIsLineDrawing(boolean value) {
        mIsLineDrawing = value;
    }

    public void setParentGroup(PolygonGroup3D parentGroup) {
        mParentGroup = parentGroup;
    }

    public void setTextureName(String textureName) {
        mTextureName = textureName;
    }

    public void setDiffuseColor(float[] color) {
        mDiffuseColor = Arrays.copyOf(color, color.length);
    }

    public void setVertices(float[] vertices) {
        mVertices = Arrays.copyOf(vertices, vertices.length);
        mVertexCount = vertices.length/COORDS_PER_VERTEX;
        int vertexOrderSize;
        if(mVertexCount<=3) {
            vertexOrderSize = mVertexCount;
        } else {
            vertexOrderSize = 3+(mVertexCount-3)*3;
        }
        mVertexOrder = new short[vertexOrderSize];
        int startCounter = 1;
        for(int i=0; i<mVertexOrder.length; i+=3) {
            mVertexOrder[i] = 0;
            mVertexOrder[i+1] = (short) startCounter;
            if((i+2)<mVertexOrder.length) {
                mVertexOrder[i + 2] = (short) (startCounter + 1);
            }
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
        for(int i=1; i<mTexCoords.length; i+=2) {
            mTexCoords[i] = 1-mTexCoords[i];
        }

        ByteBuffer bb;
        bb = ByteBuffer.allocateDirect(mTexCoords.length*FLOAT_BYTE_COUNT);
        bb.order(ByteOrder.nativeOrder());
        mTexCoordBuffer = bb.asFloatBuffer();
        mTexCoordBuffer.put(mTexCoords);
        mTexCoordBuffer.position(0);
    }

    public void draw(float[] mvpMatrix, ThreeDTexture textureStore) {
        GLES20.glUseProgram(sProgram3D.mGLProgram);

        sProgram3D.mMVPMatrixHandle = GLES20.glGetUniformLocation(sProgram3D.mGLProgram, "uMVPMatrix");
        GLES20.glUniformMatrix4fv(sProgram3D.mMVPMatrixHandle, 1, false, mvpMatrix, 0);

        sProgram3D.mGLPositionHandle = GLES20.glGetAttribLocation(sProgram3D.mGLProgram, "aPosition");
        GLES20.glEnableVertexAttribArray(sProgram3D.mGLPositionHandle);
        GLES20.glVertexAttribPointer(sProgram3D.mGLPositionHandle,
                COORDS_PER_VERTEX, GLES20.GL_FLOAT, false, VERTEX_STRIDE, mVertexBuffer);

        sProgram3D.mGLHasTextureHandle = GLES20.glGetUniformLocation(sProgram3D.mGLProgram, "uHasTexture");
        if (mTextureName != null) {
            GLES20.glUniform1i(sProgram3D.mGLHasTextureHandle, 1);

            sProgram3D.mGLTexCoordsHandle = GLES20.glGetAttribLocation(sProgram3D.mGLProgram, "aTexCoords");
            GLES20.glEnableVertexAttribArray(sProgram3D.mGLTexCoordsHandle);
            GLES20.glVertexAttribPointer(sProgram3D.mGLTexCoordsHandle,
                    COORDS_PER_TEXTURE, GLES20.GL_FLOAT, false, TEXTURE_STRIDE, mTexCoordBuffer);

            sProgram3D.mGLTextureHandle = GLES20.glGetUniformLocation(sProgram3D.mGLProgram, "uTexture");
            GLES20.glActiveTexture(GLES20.GL_TEXTURE0);
            GLES20.glBindTexture(GLES20.GL_TEXTURE_2D, textureStore.getTextureHandle(mTextureName));
            GLES20.glUniform1i(sProgram3D.mGLTextureHandle, 0);
        } else {
            GLES20.glUniform1i(sProgram3D.mGLHasTextureHandle, 0);
            mActiveDiffuseColor = mDiffuseColor;
            if (mActiveDiffuseColor == null) {
                mActiveDiffuseColor = mParentGroup.getDiffuseColor();
            }
            sProgram3D.mGLColorHandle = GLES20.glGetUniformLocation(sProgram3D.mGLProgram, "uColor");
            GLES20.glUniform4fv(sProgram3D.mGLColorHandle, 1, mActiveDiffuseColor, 0);

        }

        if (!mIsLineDrawing) {
            GLES20.glDrawElements(GLES20.GL_TRIANGLES, mVertexOrder.length,
                    GLES20.GL_UNSIGNED_SHORT, mVertexOrderBuffer);
        } else {
            GLES20.glDrawElements(GLES20.GL_LINES, mVertexOrder.length,
                    GLES20.GL_UNSIGNED_SHORT, mVertexOrderBuffer);
        }
        //GLES20.glDrawArrays(GLES20.GL_TRIANGLES, 0, mVertices.length/COORDS_PER_VERTEX);

        GLES20.glDisableVertexAttribArray(sProgram3D.mGLPositionHandle);
    }
}