package bk2suz.motionpicturelib.Commons;

import android.util.Log;

import org.xmlpull.v1.XmlPullParser;

import java.util.ArrayList;

/**
 * Created by sujoy on 29/5/17.
 */
public class TextureResources {
    public static final String TAG_NAME = "texture";
    private ArrayList<String> mNames = new ArrayList<>();
    private ArrayList<String> mPaths = new ArrayList<>();

    public void addResourceFromXmlElement(XmlPullParser parser) {
        String resourceName = parser.getAttributeValue(null, "name");
        int dotIndex = resourceName.indexOf(".");
        if (dotIndex>0) {
            resourceName = resourceName.substring(0, dotIndex);
        }
        addResource(resourceName, "raw/" + resourceName);
    }

    public void addResource(String resourceName, String resourcePath) {
        mNames.add(resourceName);
        mPaths.add(resourcePath);
    }

    public String getResourcePath(int index) {
        return mPaths.get(index);
    }
}
