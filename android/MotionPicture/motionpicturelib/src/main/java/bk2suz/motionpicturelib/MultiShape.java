package bk2suz.motionpicturelib;

import android.graphics.Canvas;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Created by sujoy on 8/10/16.
 */
public class MultiShape extends Shape {
    public static final String TYPE_NAME = "multi_shape";
    private LinkedHashMap<String, Shape> mChildShapes = new LinkedHashMap<>();
    private HashMap<String, Pose> mPoses;
    private HashMap<String, MultiShapeTimeLine> mMultiShapeTimeLines;

    public void addChildShape(Shape shape) {
        mChildShapes.put(shape.getName(), shape);
        shape.setParentShape(this);
    }

    public Shape getChildShape(String shapeName) {
        return mChildShapes.get(shapeName);
    }

    public void setPose(String poseName) {
        if (!mPoses.containsKey(poseName)) return;
        for(Map.Entry<String, PoseShape> poseEntry: mPoses.get(poseName).mPoseShapes.entrySet()) {
            Shape shape = getChildShape(poseEntry.getKey());
            if(shape == null) continue;
            for(Map.Entry<PropName, Object> poseShapeEntry: poseEntry.getValue().mPropMap.entrySet()) {
                shape.setProperty(poseShapeEntry.getKey(), poseShapeEntry.getValue(), null);
            }
        }
    }

    public void setPoseInBetween(Pose startPose, Pose endPose, float frac) {
        Point anchorAt = mAnchortAt.copy();
        for(Map.Entry<String, PoseShape> startPoseEntry: startPose.mPoseShapes.entrySet()) {
            String shapeName = startPoseEntry.getKey();
            if(!endPose.mPoseShapes.containsKey(shapeName)) continue;

            Shape shape = getChildShape(shapeName);
            if(shape == null) continue;

            PoseShape endPoseShape = endPose.mPoseShapes.get(shapeName);

            for(Map.Entry<PropName, Object> startPoseShapeEntry: startPoseEntry.getValue().mPropMap.entrySet()) {
                PropName propName = startPoseShapeEntry.getKey();
                if(!endPoseShape.mPropMap.containsKey(propName)) continue;
                Object startValue = startPoseEntry.getValue();
                Object endValue = endPoseShape.mPropMap.containsKey(propName);

                Object propValue = null;
                if (Float.class.isInstance(startValue)) {
                    propValue = (Float) startValue + (((Float) endValue)-((Float) startValue))*frac;
                    shape.setProperty(propName, propValue, null);
                } else if(propName == PropName.ANCHOR_AT) {
                    mAnchortAt.setInBetween((Point) startValue, (Point) endValue, frac);
                } else if(propName == PropName.TRANSLATION) {
                    mTranslation.setInBetween((Point) startValue, (Point) endValue, frac);
                } else if(propName == PropName.BORDER_COLOR && mBorderColor != null) {
                    mBorderColor.setInBetween((Color) startValue, (Color) endValue, frac);
                    mBorderColor.setPaint(mBorderPaint);
                } else if(propName == PropName.FILL_COLOR && mFillColor != null) {
                    mFillColor.setInBetween((Color) startValue, (Color) endValue, frac);
                    mFillColor.setPaint(mFillPaint);
                } else if(propName == PropName.PRE_MATRIX) {
                    mPreMatrix.setInBetween((Matrix) startValue, (Matrix) endValue, frac);
                }
            }
        }
    }

    @Override
    public void setProperty(PropName propName, Object value, HashMap<PropName, PropData> propDataMap) {
        super.setProperty(propName, value, propDataMap);
        if (propName == PropName.INTERNAL) {
            if("pose".equals(propDataMap.get(PropName.TYPE))) {
                String startPoseName = propDataMap.get(PropName.START_POSE).getStringValue();
                String endPoseName = propDataMap.get(PropName.END_POSE).getStringValue();
                if(endPoseName == null || !mPoses.containsKey(endPoseName)) {
                    setPose(startPoseName);
                } else {
                    setPoseInBetween(mPoses.get(startPoseName),mPoses.get(endPoseName), (float) value);
                }
            } else if("timeline".equals(propDataMap.get(PropName.TYPE))) {
                setPose(propDataMap.get(PropName.POSE).getStringValue());
                MultiShapeTimeLine timeline = mMultiShapeTimeLines.get(
                        propDataMap.get(PropName.TIMELINE).getStringValue());
                if(timeline != null) {
                    timeline.moveTo(timeline.getDuration()*((float) value));
                }
            }
        }
    }

    @Override
    public void draw(Canvas canvas) {
        for(Map.Entry<String, Shape> entry: mChildShapes.entrySet()) {
            entry.getValue().draw(canvas);
        }
    }

    public static MultiShape createFromXml(XmlPullParser parser)
            throws XmlPullParserException, IOException {
        if (isShapeTagType(parser, TYPE_NAME)) return null;
        MultiShape multiShape = new MultiShape();
        multiShape.copyAttributesFromXml(parser);
        while (parser.next() != XmlPullParser.END_TAG) {
            if (parser.getEventType() != XmlPullParser.START_TAG) {
                continue;
            }
            if (parser.getName().equals("shape")) {
                String childShapeType = parser.getAttributeValue(null, "type");
                Shape childShape = null;
                if (childShapeType.equals(RectangleShape.TYPE_NAME)) {
                    childShape = RectangleShape.createFromXml(parser);
                } else if (childShapeType.equals(OvalShape.TYPE_NAME)) {
                    childShape = OvalShape.createFromXml(parser);
                } else if (childShapeType.equals(PolygonShape.TYPE_NAME)) {
                    childShape = PolygonShape.createFromXml(parser);
                } else if (childShapeType.equals(CurveShape.TYPE_NAME)) {
                    childShape = CurveShape.createFromXml(parser);
                } else if (childShapeType.equals(MultiShape.TYPE_NAME)) {
                    childShape = MultiShape.createFromXml(parser);
                } else if (childShapeType.equals(TextShape.TYPE_NAME)) {
                    childShape = TextShape.createFromXml(parser);
                }
                if (childShape != null) {
                    multiShape.addChildShape(childShape);
                }
            } else if (parser.getName().equals(MultiShapeTimeLine.TAG_NAME)) {
                String timeLineName = parser.getAttributeValue(null, "name");
                MultiShapeTimeLine multiShapeTimeLine = MultiShapeTimeLine.createFromXml(parser, multiShape);
                if(multiShape.mMultiShapeTimeLines == null) {
                    multiShape.mMultiShapeTimeLines = new HashMap<>();
                }
                if (multiShapeTimeLine != null) {
                    multiShape.mMultiShapeTimeLines.put(timeLineName, multiShapeTimeLine);
                }
            } else if (parser.getName().equals(Pose.TAG_NAME)) {
                String poseName = parser.getAttributeValue(null, "name");
                Pose pose = Pose.createFromXml(parser);
                if(multiShape.mPoses == null) {
                    multiShape.mPoses = new HashMap<>();
                }
                if (pose != null) {
                    multiShape.mPoses.put(poseName, pose);
                }
        }
            Helper.skipTag(parser);
        }
        return multiShape;
    }

    public static class Pose {
        public static final String TAG_NAME = "pose";

        private HashMap<String, PoseShape> mPoseShapes = new HashMap<>();

        public static Pose createFromXml(XmlPullParser parser)
                throws XmlPullParserException, IOException {
            parser.require(XmlPullParser.START_TAG, null, TAG_NAME);
            Pose pose = new Pose();
            while (parser.next() != XmlPullParser.END_TAG) {
                if (parser.getEventType() != XmlPullParser.START_TAG) {
                    continue;
                }
                if (PoseShape.TAG_NAME.equals(parser.getName())) {
                    String shapeName= parser.getAttributeValue(null, "name");
                    PoseShape poseShape = PoseShape.createFromXml(parser);
                    if (poseShape != null) {
                        pose.mPoseShapes.put(shapeName, poseShape);
                    }
                }
                Helper.skipTag(parser);
            }
            return pose;
        }
    }

    public static class PoseShape {
        public static final String TAG_NAME = "pose_shape";

        private LinkedHashMap<PropName, Object> mPropMap = new LinkedHashMap<>();

        public static PoseShape createFromXml(XmlPullParser parser)
                throws XmlPullParserException, IOException {
            parser.require(XmlPullParser.START_TAG, null, TAG_NAME);
            PoseShape poseShape = new PoseShape();

            for(int i=0; i<parser.getAttributeCount(); i++) {
                PropName propName = PropName.getByXmlName(parser.getAttributeName(i));
                String propValueText = parser.getAttributeValue(i);
                Object propValue= null;
                switch(propName) {
                    case ANCHOR_AT:
                    case TRANSLATION:
                        propValue = Point.createFromText(propValueText);
                        break;
                    case FILL_COLOR:
                    case BORDER_COLOR:
                        propValue = parseColor(propValueText);
                        break;
                    case PRE_MATRIX:
                        propValue = Matrix.createFromText(propValueText);
                        break;
                    default:
                        try {
                            propValue = Float.parseFloat(propValueText);
                        } catch (NumberFormatException e) {
                        }
                }
                poseShape.mPropMap.put(propName, propValue);
            }
            return poseShape;
        }
    }
}
