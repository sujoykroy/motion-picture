package bk2suz.motionpicturelib;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Matrix;
import android.opengl.EGL14;
import android.opengl.EGLConfig;
import android.opengl.EGLContext;
import android.opengl.EGLDisplay;
import android.opengl.EGLSurface;
import android.opengl.GLES20;
import android.util.Log;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.FutureTask;
import java.util.concurrent.TimeUnit;

import bk2suz.motionpicturelib.Commons.Object3D;
import bk2suz.motionpicturelib.Commons.ThreeDSurfaceRenderer;

/**
 * Created by sujoy on 1/6/17.
 */
public class ImageGLRender {
    private EGLDisplay mEGLDisplay = EGL14.EGL_NO_DISPLAY;
    private EGLContext mEGLContext = EGL14.EGL_NO_CONTEXT;
    private EGLSurface mEGLSurface = EGL14.EGL_NO_SURFACE;
    int mWidth;
    int mHeight;
    private ByteBuffer mPixelBuf;

    public ImageGLRender(int width, int height) {
        mWidth = width;
        mHeight = height;

        mPixelBuf = ByteBuffer.allocateDirect(mWidth * mHeight * 4);
        mPixelBuf.order(ByteOrder.LITTLE_ENDIAN);
        eglSetup();
        if (!EGL14.eglMakeCurrent(mEGLDisplay, mEGLSurface, mEGLSurface, mEGLContext)) {
            throw new RuntimeException("eglMakeCurrent failed");
        }
    }

    public void release() {
        if (mEGLDisplay != EGL14.EGL_NO_DISPLAY) {
            EGL14.eglDestroySurface(mEGLDisplay, mEGLSurface);
            EGL14.eglDestroyContext(mEGLDisplay, mEGLContext);
            EGL14.eglReleaseThread();
            EGL14.eglTerminate(mEGLDisplay);
        }
        mEGLDisplay = EGL14.EGL_NO_DISPLAY;
        mEGLContext = EGL14.EGL_NO_CONTEXT;
        mEGLSurface = EGL14.EGL_NO_SURFACE;
    }

    private void eglSetup() {
        mEGLDisplay = EGL14.eglGetDisplay(EGL14.EGL_DEFAULT_DISPLAY);
        if (mEGLDisplay == EGL14.EGL_NO_DISPLAY) {
            throw new RuntimeException("unable to get EGL14 display");
        }
        int[] version = new int[2];
        if (!EGL14.eglInitialize(mEGLDisplay, version, 0, version, 1)) {
            mEGLDisplay = null;
            throw new RuntimeException("unable to initialize EGL14");
        }

        // Configure EGL for pbuffer and OpenGL ES 2.0, 24-bit RGB.
        int[] attribList = {
                EGL14.EGL_RED_SIZE, 8,
                EGL14.EGL_GREEN_SIZE, 8,
                EGL14.EGL_BLUE_SIZE, 8,
                EGL14.EGL_ALPHA_SIZE, 8,
                EGL14.EGL_RENDERABLE_TYPE, EGL14.EGL_OPENGL_ES2_BIT,
                EGL14.EGL_SURFACE_TYPE, EGL14.EGL_PBUFFER_BIT,
                EGL14.EGL_DEPTH_SIZE, 16,
                EGL14.EGL_NONE
        };
        EGLConfig[] configs = new EGLConfig[1];
        int[] numConfigs = new int[1];
        if (!EGL14.eglChooseConfig(mEGLDisplay, attribList, 0, configs, 0, configs.length,
                numConfigs, 0)) {
            throw new RuntimeException("unable to find RGB888+recordable ES2 EGL config");
        }

        // Configure context for OpenGL ES 2.0.
        int[] attrib_list = {
                EGL14.EGL_CONTEXT_CLIENT_VERSION, 2,
                EGL14.EGL_NONE
        };
        mEGLContext = EGL14.eglCreateContext(mEGLDisplay, configs[0], EGL14.EGL_NO_CONTEXT,
                attrib_list, 0);
        checkEglError("eglCreateContext");
        if (mEGLContext == null) {
            throw new RuntimeException("null context");
        }

        // Create a pbuffer surface.
        int[] surfaceAttribs = {
                EGL14.EGL_WIDTH, mWidth,
                EGL14.EGL_HEIGHT, mHeight,
                EGL14.EGL_NONE
        };
        mEGLSurface = EGL14.eglCreatePbufferSurface(mEGLDisplay, configs[0], surfaceAttribs, 0);
        checkEglError("eglCreatePbufferSurface");
        if (mEGLSurface == null) {
            throw new RuntimeException("surface was null");
        }
    }

    public Bitmap getBitmap() {
        mPixelBuf.rewind();
        GLES20.glReadPixels(0, 0, mWidth, mHeight, GLES20.GL_RGBA, GLES20.GL_UNSIGNED_BYTE,
                mPixelBuf);

        Bitmap bmp = Bitmap.createBitmap(mWidth, mHeight, Bitmap.Config.ARGB_8888);
        mPixelBuf.rewind();
        bmp.copyPixelsFromBuffer(mPixelBuf);

        Matrix matrix = new Matrix();
        matrix.preScale(1.0f, -1.0f); // scaling: x = x, y = -y, i.e. vertically flip

        bmp = Bitmap.createBitmap(bmp, 0, 0, bmp.getWidth(), bmp.getHeight(), matrix, true); // new bitmap, using the matrix to flip it
        return bmp;
    }

    private void checkEglError(String msg) {
        int error;
        if ((error = EGL14.eglGetError()) != EGL14.EGL_SUCCESS) {
            throw new RuntimeException(msg + ": EGL error: 0x" + Integer.toHexString(error));
        }
    }

    public static class GLImageFutureTask extends FutureTask<Bitmap> {
        Object3D mObject3D;
        float[] mPreMatrix;

        public GLImageFutureTask(Callable<Bitmap> callable) {
            super(callable);
        }

        public void setObject3D(Object3D object3D) {
            mObject3D = object3D;
        }

        public void setPreMatrix(float[] preMatrix) {
            mPreMatrix = preMatrix;
        }

        public void setBitmap(Bitmap bitmap) {
            set(bitmap);
        }

        public void markComplete() {
            done();
        }
    }

    public static class GLThread extends Thread {
        ImageGLRender mImageGLRender;
        ThreeDSurfaceRenderer mSurfaceRenderer;
        Object mLock = new Object();
        boolean mShouldExit = false;
        ConcurrentLinkedQueue<GLImageFutureTask> mTaskQueue = new ConcurrentLinkedQueue<>();
        int mWidth, mHeight;
        Context mContext;

        public GLThread(int width, int height, Context context) {
            mWidth = width;
            mHeight = height;
            mContext = context;
        }

        @Override
        public void run() {
            mImageGLRender = new ImageGLRender(mWidth, mHeight);
            mSurfaceRenderer = new ThreeDSurfaceRenderer(mContext);
            mSurfaceRenderer.onSurfaceCreated(null, null);
            mSurfaceRenderer.onSurfaceChanged(null, mWidth, mHeight);

            while (!mShouldExit) {
                GLImageFutureTask task = mTaskQueue.poll();
                if(task != null) {
                    mSurfaceRenderer.setObject3D(task.mObject3D);
                    mSurfaceRenderer.setPreMatrix(task.mPreMatrix);
                    mSurfaceRenderer.onDrawFrame(null);
                    task.setBitmap(mImageGLRender.getBitmap());
                    task.markComplete();
                }
                try {
                    Thread.sleep(TimeUnit.MILLISECONDS.toMillis(100));
                } catch (InterruptedException e) {
                    break;
                }
            }
            mImageGLRender.release();
            mImageGLRender = null;
            mSurfaceRenderer = null;
        }

        public GLImageFutureTask requestBitmapFor(float[] preMatrix, final Object3D object3D) {
            GLImageFutureTask task = new GLImageFutureTask(new Callable<Bitmap>() {
                @Override
                public Bitmap call() throws Exception {
                    return null;
                }
            });
            task.setObject3D(object3D);
            task.setPreMatrix(preMatrix);
            mTaskQueue.add(task);
            return task;
        }

        public void makeExit() {
            synchronized (mLock) {
                mShouldExit = true;
            }
        }
    }

    public static class GLThreadManager {
        private static HashMap<String, GLThread> mThreads = new HashMap<>();

        private static String getKey(int width, int height) {
            String key = String.format("%dx%d", width, height);
            return key;
        }

        public static GLThread getThread(int width, int height) {
            String key = getKey(width, height);
            return mThreads.get(key);
        }

        public static boolean createThread(int width, int height, Context context) {
            String key = getKey(width, height);
            if (!mThreads.containsKey(key)) {
                GLThread thread = new GLThread(width, height, context);
                mThreads.put(key, thread);
                thread.start();
                return true;
            }
            return false;
        }

        public static void deleteThread(int width, int height) {
            String key = getKey(width, height);
            GLThread thread = mThreads.get(key);
            if (thread != null) {
                thread.makeExit();
            }
            mThreads.remove(key);
        }

        public void deleteAll() {
            for(GLThread thread: mThreads.values()) {
                thread.makeExit();
            }
            mThreads.clear();
        }
    }
}

