package bk2suz.motionpicturelib;

import org.xmlpull.v1.XmlPullParser;

/**
 * Created by sujoy on 11/10/16.
 */
public abstract class PeriodicChangeType extends TimeChangeType {
    protected Float mPeriod;
    protected Float mPhase;
    protected Float mAmplitude;

    protected void copyFromXml(XmlPullParser parser) {
        try {
            mPeriod = Float.parseFloat(parser.getAttributeValue(null, "period"));
        } catch (NumberFormatException e) {
        }
        try {
            mPhase = Float.parseFloat(parser.getAttributeValue(null, "phase"));
        } catch (NumberFormatException e) {
        }
        try {
            mAmplitude = Float.parseFloat(parser.getAttributeValue(null, "amplitude"));
        } catch (NumberFormatException e) {
        }
    }

}
