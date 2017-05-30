package bk2suz.motionpicturelib.Commons;

import android.util.Log;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;
import java.util.ArrayList;

/**
 * Created by sujoy on 27/5/17.
 */
public class PolygonGroup3D extends Object3D {
    public static final String TAG_NAME = "polygrp3";
    private ArrayList<Polygon3D> mPolygons = new ArrayList<>();
    protected Color mFillColor = new FlatColor(0.63671875f, 0.76953125f, 0.22265625f, 1.0f);
    protected Color mBorderColor;
    protected Float mBorderWidth = null;
    protected ArrayList<Point3D> mPoints = new ArrayList<>();

    public void addPolygon(Polygon3D polygon) {
        mPolygons.add(polygon);
        polygon.setParentGroup(this);
    }

    public Point3D getPoint(int index) {
        return mPoints.get(index);
    }

    public void draw(ThreeDGLRenderContext threeDGLRenderContext) {
        for(Polygon3D polygon: mPolygons) {
            polygon.draw(mModelMatrix, threeDGLRenderContext);
        }
    }

    public Color getFillColor() {
        return mFillColor;
    }

    public void buildBuffers() {
        for(Polygon3D polygon: mPolygons) {
            polygon.buildBuffers();
        }
    }

    public static PolygonGroup3D createAxes(float lineLength) {
        PolygonGroup3D axes = new PolygonGroup3D();

        axes.mPoints.add(new Point3D(0f, 0f, 0f));
        axes.mPoints.add(new Point3D(lineLength, 0f, 0f));
        axes.mPoints.add(new Point3D(0f, lineLength, 0f));
        axes.mPoints.add(new Point3D(0f, 0f, lineLength));

        Polygon3D polygon;

        polygon = new Polygon3D(new int[] {0, 1});
        polygon.setFillColor(new FlatColor(1f, 0f, 0f, 1f));
        polygon.setIsLineDrawing(true);
        axes.addPolygon(polygon);

        polygon = new Polygon3D(new int[] {0, 2});
        polygon.setFillColor(new FlatColor(0f, 1f, 0f, 1f));
        polygon.setIsLineDrawing(true);
        axes.addPolygon(polygon);

        polygon = new Polygon3D(new int[] {0, 3});
        polygon.setFillColor(new FlatColor(0f, 0f, 1f, 1f));
        polygon.setIsLineDrawing(true);
        axes.addPolygon(polygon);

        axes.buildBuffers();

        return axes;
    }

    public static PolygonGroup3D createCube(float sideSize) {
        PolygonGroup3D cube = new PolygonGroup3D();
        TextureResources textureResources = new TextureResources();
        textureResources.addResource("someTexture", "mipmap/ic_launcher");
        cube.setTextureResources(textureResources);
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
                {0, 3, 2, 1}, //bottom
                {4, 5, 6, 7}, //top
                {0, 1, 5, 4},
                {1, 2, 6, 5},
                {2, 3, 7, 6},
                {3, 0, 4, 7}
        };
        for (int i=0; i<allVertices.length; i+=3) {
            Point3D point3D = new Point3D(allVertices[i], allVertices[i+1], allVertices[i+2]);
            cube.mPoints.add(point3D);
        }
        for (int i=0; i<faceIndices.length; i++) {
            Polygon3D polygon = new Polygon3D(faceIndices[i]);
            if (i==10) {
                polygon.setFillColor(new TextureMapColor(
                        textureResources,
                        0,
                        new float[]{
                        0, 0,
                        1, 0,
                        1, 1,
                        0, 1
                }));
            }
            cube.addPolygon(polygon);
        }

        cube.buildBuffers();
        return cube;
    }

    public static PolygonGroup3D createFromXml(XmlPullParser parser)
            throws XmlPullParserException, IOException {
        PolygonGroup3D polygonGroup3D = new PolygonGroup3D();
        polygonGroup3D.load_from_xml_element(parser);
        polygonGroup3D.mBorderColor = Helper.parseColor(parser.getAttributeValue(null, "bc"));
        polygonGroup3D.mFillColor = Helper.parseColor(parser.getAttributeValue(null, "fc"));
        try {
            polygonGroup3D.mBorderWidth = Float.parseFloat(parser.getAttributeValue(null, "bc"));
        } catch (NumberFormatException e) {
            polygonGroup3D.mBorderWidth = null;
        }
        while (parser.next() != XmlPullParser.END_TAG) {
            if (parser.getEventType() != XmlPullParser.START_TAG) {
                continue;
            }
            if (parser.getName().equals("points")) {
                if(parser.next() == XmlPullParser.TEXT) {
                    String[] pointsStringArray = parser.getText().split(",");
                    Float[] pointValues = new Float[pointsStringArray.length];
                    for(int i=0; i<pointsStringArray.length; i++) {
                        try {
                            pointValues[i] = Float.parseFloat(pointsStringArray[i]);
                        } catch (NumberFormatException e) {
                            pointValues[i] = 0F;
                        }
                    }
                    for(int i=0; i<pointsStringArray.length; i+=3) {
                        Point3D point3D = new Point3D(
                                pointValues[i], pointValues[i+1], pointValues[i+2]);
                        polygonGroup3D.mPoints.add(point3D);
                    }
                }
            } else if (parser.getName().equals(Polygon.TAG_NAME)) {
                Polygon3D polygon = Polygon3D.createFromXml(parser);
                polygonGroup3D.mPolygons.add(polygon);
            }
            Helper.skipTag(parser);
        }
        return polygonGroup3D;
    }
}
