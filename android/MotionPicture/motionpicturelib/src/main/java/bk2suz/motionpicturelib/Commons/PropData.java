package bk2suz.motionpicturelib.Commons;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;

/**
 * Created by sujoy on 11/10/16.
 */
public class PropData {
    public static final String TAG_NAME = "prop_data";
    private PropName mKey;
    private String mType;
    private String mValue;

    public PropName getKey() {
        return mKey;
    }

    public String getStringValue() {
        return mValue;
    }

    public static PropData createFromXml(XmlPullParser parser)
            throws XmlPullParserException, IOException {
        parser.require(XmlPullParser.START_TAG, null, TAG_NAME);
        PropData propData = new PropData();
        propData.mKey = PropName.getByXmlName(parser.getAttributeValue(null, "key"));
        propData.mType = parser.getAttributeValue(null, "type");
        propData.mValue = parser.getAttributeValue(null, "value");
        Helper.skipTag(parser);
        return propData;
    }
}
