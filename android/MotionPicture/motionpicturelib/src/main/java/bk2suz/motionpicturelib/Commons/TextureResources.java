package bk2suz.motionpicturelib.Commons;

import org.xmlpull.v1.XmlPullParser;

import java.util.ArrayList;

/**
 * Created by sujoy on 29/5/17.
 */
public class TextureResources {
    public static final String TAG_NAME = "texture";
    private ArrayList<String> mNames = new ArrayList<>();

    public void add_resource_from_xml_element(XmlPullParser parser) {
        String resource_name = parser.getAttributeValue(null, "name");
        mNames.add(resource_name);
    }
}
