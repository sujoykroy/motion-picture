package bk2suz.motionpicturelib.Commons;

import android.util.Log;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;
import java.util.ArrayList;

/**
 * Created by sujoy on 29/5/17.
 */
public class Container3D extends Object3D {
    public static final String TAG_NAME  = "container3d";

    protected ArrayList<PolygonGroup3D> mPolyGroups = new ArrayList<>();
    protected ArrayList<String> mPolyGroupNames = new ArrayList<>();

    @Override
    public void precalculate() {
        super.precalculate();
        for(PolygonGroup3D polygonGroup: mPolyGroups) {
            polygonGroup.precalculate();
        }
    }

    @Override
    public void draw(ThreeDGLRenderContext threeDGLRenderContext) {
        for(PolygonGroup3D polygonGroup: mPolyGroups) {
            polygonGroup.draw(threeDGLRenderContext);
        }
    }

    public static Container3D createFromXml(XmlPullParser parser)
            throws XmlPullParserException, IOException {
        parser.require(XmlPullParser.START_TAG, null, TAG_NAME);
        Container3D container3D = new Container3D();
        container3D.load_from_xml_element(parser);
        while (parser.next() != XmlPullParser.END_TAG) {
            if (parser.getEventType() != XmlPullParser.START_TAG) {
                continue;
            }
            if (parser.getName().equals(TextureResources.TAG_NAME)) {
                if (container3D.mTextureResources == null) {
                    container3D.mTextureResources = new TextureResources();
                }
                container3D.mTextureResources.addResourceFromXmlElement(parser);
            } else if (parser.getName().equals(PolygonGroup3D.TAG_NAME)) {
                PolygonGroup3D polygonGroup3D = PolygonGroup3D.createFromXml(parser);
                container3D.mPolyGroups.add(polygonGroup3D);
                polygonGroup3D.setParentObject(container3D);
                container3D.mPolyGroupNames.add(parser.getAttributeValue(null, "name"));
            }
            Helper.skipTag(parser);
        }
        return container3D;
    }
}
