package bk2suz.motionpicturelib.Commons;

import android.opengl.GLES20;

/**
 * Created by sujoy on 27/5/17.
 */
public class ThreeDShader {
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

    private static int sVertexShaderId=-1;
    private static int sFragmentShaderId=-1;


    public static int loadShader(int type, String shaderCode){
        int shader = GLES20.glCreateShader(type);

        GLES20.glShaderSource(shader, shaderCode);
        GLES20.glCompileShader(shader);

        return shader;
    }

    public static int getVertexShader() {
        return loadShader(GLES20.GL_VERTEX_SHADER, sVertexShaderCode);
        /*if (sVertexShaderId<0) {
            sVertexShaderId = loadShader(GLES20.GL_VERTEX_SHADER, sVertexShaderCode);
        }
        return sVertexShaderId;*/
    }

    public static int getFragmentShader() {
        return loadShader(GLES20.GL_FRAGMENT_SHADER, sFragmentShaderCode);
        /*if (sFragmentShaderId<0) {
            sFragmentShaderId = loadShader(GLES20.GL_FRAGMENT_SHADER, sFragmentShaderCode);
        }
        return sFragmentShaderId;*/
    }
}
