package bk2suz.motionpicturelib.Commons;

import android.opengl.GLES20;

/**
 * Created by sujoy on 30/5/17.
 */
public class Polygon3DGLDrawer {
    public static final String sVertexShaderCode = ""
            +   "attribute vec4 aPosition;"
            +   "attribute vec2 aTexCoords;"
            +   "varying vec2 vTexCoords;"
            +   "uniform mat4 uMVPMatrix;"
            +   "void main() {"
            +   "   vTexCoords = aTexCoords;"
            +   "   gl_Position = uMVPMatrix * aPosition;"
            +   "}";

    public static final String sFragmentShaderCode = ""
            +   "precision mediump float;"
            +   "uniform vec4 uColor;"
            +   "uniform bool uHasTexture;"
            +   "uniform sampler2D uTexture;"
            +   "varying vec2 vTexCoords;"
            +   "void main() {"
            +   "   if (uHasTexture == true) {"
            +   "       gl_FragColor = texture2D(uTexture, vTexCoords);"
            +   "   } else {"
            +   "       gl_FragColor = uColor;"
            +   "   }"
            +   "}";

    public final int GLProgram;
    public int GLPositionHandle;
    public int GLTexCoordsHandle;
    public int GLColorHandle;
    public int GLHasTextureHandle;
    public int GLTextureHandle;
    public int MVPMatrixHandle;

    public Polygon3DGLDrawer() {
        GLProgram = GLES20.glCreateProgram();
        GLES20.glAttachShader(GLProgram, loadShader(GLES20.GL_VERTEX_SHADER, sVertexShaderCode));
        GLES20.glAttachShader(GLProgram, loadShader(GLES20.GL_FRAGMENT_SHADER, sFragmentShaderCode));
        GLES20.glLinkProgram(GLProgram);
    }

    public static int loadShader(int type, String shaderCode){
        int shader = GLES20.glCreateShader(type);

        GLES20.glShaderSource(shader, shaderCode);
        GLES20.glCompileShader(shader);

        return shader;
    }
}
