package bk2suz.motionpicture;

import java.util.ArrayList;

/**
 * Created by sujoy on 27/5/17.
 */
public class PolygonGroup3D extends Object3D {
    private ArrayList<Polygon3D> mPolygons = new ArrayList<>();
    private float[] mDiffuseColor = { 0.63671875f, 0.76953125f, 0.22265625f, 1.0f };

    public void addPolygon(Polygon3D polygon) {
        mPolygons.add(polygon);
        polygon.setParentGroup(this);
    }

    public void draw(ThreeDTexture textureStore) {
        for(Polygon3D polygon: mPolygons) {
            polygon.draw(mViewMatrix, textureStore);
        }
    }

    public float[] getDiffuseColor() {
        return mDiffuseColor;
    }

    public static PolygonGroup3D createCube(float sideSize) {
        PolygonGroup3D cube = new PolygonGroup3D();
        float[] allVertices = {
                0f, 0f, 0f,
                sideSize, 0f, 0f,
                sideSize, sideSize, 0f,
                0f, sideSize, 0f,

                0f, 0f, sideSize,
                sideSize, 0f, sideSize,
                sideSize, sideSize, sideSize,
                0f, sideSize, sideSize,
        };
        int[][] faceIndices = {
                {0, 3, 2, 1}, //top
                {4, 5, 6, 7}, //bottom
                {0, 1, 5, 4},
                {1, 2, 6, 5},
                {2, 3, 7, 6},
                {3, 0, 4, 7}
        };
        for (int i=0; i<faceIndices.length; i++) {
            float[] vertices = new float[faceIndices[i].length*3];
            for(int j=0; j<faceIndices[i].length; j++) {
                int k = faceIndices[i][j]*3;
                vertices[j*3] = allVertices[k];
                vertices[j*3+1] = allVertices[k+1];
                vertices[j*3+2] = allVertices[k+2];
            }
            Polygon3D polygon = new Polygon3D(vertices);
            polygon.setTextureName("mipmap/ic_launcher");
            polygon.setTexCoords(new float[] {
                    0.0F, 1F,
                    0F, 0F,
                    1F, 0F,
                    1F, 1F
            });
            cube.addPolygon(polygon);
        }
        return cube;
    }
}
