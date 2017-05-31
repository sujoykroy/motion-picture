package bk2suz.motionpicturelib.Commons;

import android.opengl.GLES20;
import android.util.Log;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.FloatBuffer;
import java.nio.ShortBuffer;
import java.util.Arrays;

public class Polygon3D {
    public static final String TAG_NAME = "pl3";
    private static int FLOAT_BYTE_COUNT = 4;
    private static int SHORT_BYTE_COUNT = 2;
    private static int COORDS_PER_VERTEX = 3;
    private static int VERTEX_STRIDE = COORDS_PER_VERTEX*FLOAT_BYTE_COUNT;
    private static int COORDS_PER_TEXTURE = 2;
    private static int TEXTURE_STRIDE = COORDS_PER_TEXTURE*FLOAT_BYTE_COUNT;

    private int[] mPointIndices;
    private Color mFillColor;
    private boolean mIsLineDrawing = false;

    private FloatBuffer mVertexBuffer;
    private ShortBuffer mVertexOrderBuffer;
    private FloatBuffer mTexCoordBuffer;

    private PolygonGroup3D mParentGroup = null;
    private Color mActiveFillColor;

    private int mVertexOrderCount;

    private Polygon3D() {}

    public Polygon3D(int[] pointIndices) {
        mPointIndices = pointIndices;
    }

    public void setParentGroup(PolygonGroup3D parentGroup) {
        mParentGroup = parentGroup;
    }

    public void buildBuffers() {
        if (mParentGroup == null || mPointIndices == null) {
            return;
        }
         //Build Vertices
        float[] vertices = new float[mPointIndices.length*COORDS_PER_VERTEX];
        for(int i=0; i<mPointIndices.length; i++) {
            Point3D point3D = mParentGroup.getPoint(mPointIndices[i]);
            vertices[3*i+0] = point3D.getX();
            vertices[3*i+1] = point3D.getY();
            vertices[3*i+2] = point3D.getZ();
        }
        //Log.d("GALA", String.format(Arrays.toString(vertices)));
        //Build vertex order
        if(mPointIndices.length<=3) {
            mVertexOrderCount = mPointIndices.length;
        } else {
            mVertexOrderCount = 3+(mPointIndices.length-3)*3;
        }
        short[] vertexOrder = new short[mVertexOrderCount];
        int startCounter = 1;
        for(int i=0; i<mVertexOrderCount; i+=3) {
            vertexOrder[i] = 0;
            vertexOrder[i+1] = (short) startCounter;
            if((i+2)<mVertexOrderCount) {
                vertexOrder[i + 2] = (short) (startCounter + 1);
            }
            startCounter += 1;
        }

        ByteBuffer bb;

        //build vertices buffers
        bb = ByteBuffer.allocateDirect(vertices.length*FLOAT_BYTE_COUNT);
        bb.order(ByteOrder.nativeOrder());
        mVertexBuffer = bb.asFloatBuffer();
        mVertexBuffer.put(vertices);
        mVertexBuffer.position(0);

        //build vertex order buffer
        bb = ByteBuffer.allocateDirect(vertexOrder.length*SHORT_BYTE_COUNT);
        bb.order(ByteOrder.nativeOrder());
        mVertexOrderBuffer = bb.asShortBuffer();
        mVertexOrderBuffer.put(vertexOrder);
        mVertexOrderBuffer.position(0);

        //build texture coordinate buffer
        if (mFillColor != null && TextureMapColor.class.isInstance(mFillColor)) {
            float[] texCoords = ((TextureMapColor) mFillColor).getTexCoords();
            bb = ByteBuffer.allocateDirect(texCoords.length * FLOAT_BYTE_COUNT);
            bb.order(ByteOrder.nativeOrder());
            mTexCoordBuffer = bb.asFloatBuffer();
            mTexCoordBuffer.put(texCoords);
            mTexCoordBuffer.position(0);
        } else {
            mTexCoordBuffer = null;
        }
    }

    public void setIsLineDrawing(boolean value) {
        mIsLineDrawing = value;
    }

    public void setFillColor(Color color) {
        if (color != null && color.getClass().isInstance(mFillColor)) {
            mFillColor.copyFrom(color);
        } else {
            mFillColor = color;
        }
    }

    public void draw(float[] mvpMatrix, ThreeDGLRenderContext threeDGLRenderContext) {
        Polygon3DGLDrawer drawer = threeDGLRenderContext.getPolygon3DGLDrawer();
        GLES20.glUseProgram(drawer.GLProgram);

        drawer.MVPMatrixHandle = GLES20.glGetUniformLocation(drawer.GLProgram, "uMVPMatrix");
        GLES20.glUniformMatrix4fv(drawer.MVPMatrixHandle, 1, false, mvpMatrix, 0);
        drawer.GLPositionHandle = GLES20.glGetAttribLocation(drawer.GLProgram, "aPosition");
        GLES20.glEnableVertexAttribArray(drawer.GLPositionHandle);
        GLES20.glVertexAttribPointer(drawer.GLPositionHandle,
                COORDS_PER_VERTEX, GLES20.GL_FLOAT, false, VERTEX_STRIDE, mVertexBuffer);

        drawer.GLHasTextureHandle = GLES20.glGetUniformLocation(drawer.GLProgram, "uHasTexture");
        if (mTexCoordBuffer != null && !mIsLineDrawing) {
            GLES20.glUniform1i(drawer.GLHasTextureHandle, 1);

            drawer.GLTexCoordsHandle = GLES20.glGetAttribLocation(drawer.GLProgram, "aTexCoords");
            GLES20.glEnableVertexAttribArray(drawer.GLTexCoordsHandle);
            GLES20.glVertexAttribPointer(drawer.GLTexCoordsHandle,
                    COORDS_PER_TEXTURE, GLES20.GL_FLOAT, false, TEXTURE_STRIDE, mTexCoordBuffer);

            drawer.GLTextureHandle = GLES20.glGetUniformLocation(drawer.GLProgram, "uTexture");
            GLES20.glActiveTexture(GLES20.GL_TEXTURE0);
            GLES20.glBindTexture(GLES20.GL_TEXTURE_2D,
                    threeDGLRenderContext.getTextureHandle(
                           mParentGroup.getTextureResources().getResourcePath (
                                   ((TextureMapColor) mFillColor).getResourceIndex())));
            GLES20.glUniform1i(drawer.GLTextureHandle, 0);
        } else {
            GLES20.glUniform1i(drawer.GLHasTextureHandle, 0);
            mActiveFillColor = mFillColor;
            if (mActiveFillColor == null) {
                mActiveFillColor = mParentGroup.getFillColor();
            }
            if(FlatColor.class.isInstance(mFillColor)) {
                drawer.GLColorHandle = GLES20.glGetUniformLocation(drawer.GLProgram, "uColor");
                GLES20.glUniform4fv(drawer.GLColorHandle, 1,
                        ((FlatColor)mActiveFillColor).getFloatArrayValue(), 0);
            }

        }

        if (!mIsLineDrawing) {
            GLES20.glDrawElements(GLES20.GL_TRIANGLES, mVertexOrderCount,
                    GLES20.GL_UNSIGNED_SHORT, mVertexOrderBuffer);
        } else {
            GLES20.glDrawElements(GLES20.GL_LINES, mVertexOrderCount,
                    GLES20.GL_UNSIGNED_SHORT, mVertexOrderBuffer);
        }
        //GLES20.glDrawArrays(GLES20.GL_TRIANGLES, 0, mVertices.length/COORDS_PER_VERTEX);

        GLES20.glDisableVertexAttribArray(drawer.GLPositionHandle);
    }

    public static Polygon3D createFromXml(XmlPullParser parser)
            throws XmlPullParserException, IOException {
        Polygon3D polygon3D = new Polygon3D();
        polygon3D.mFillColor = Helper.parseColor(parser.getAttributeValue(null, "fc"));
        while (parser.next() != XmlPullParser.END_TAG) {
            if (parser.getEventType() != XmlPullParser.START_TAG) {
                continue;
            }
            if (parser.getName().equals("pi")) {
                if (parser.next() == XmlPullParser.TEXT) {
                    String[] indicesStringArray = parser.getText().split(",");
                    int[] pointIndices = new int[indicesStringArray.length];
                    for (int i = 0; i < indicesStringArray.length; i++) {
                        try {
                            pointIndices[i] = Integer.parseInt(indicesStringArray[i]);
                        } catch (NumberFormatException e) {
                            pointIndices[i] = 0;
                        }
                    }
                    polygon3D.mPointIndices = pointIndices;
                }
            }
            Helper.skipTag(parser);
        }
        return polygon3D;
    }
}