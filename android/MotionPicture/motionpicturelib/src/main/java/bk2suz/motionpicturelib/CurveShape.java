package bk2suz.motionpicturelib;

import android.graphics.Path;
import android.graphics.RectF;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;

/**
 * Created by sujoy on 8/10/16.
 */
public class CurveShape extends Shape {
    public static final String TYPE_NAME = "curve_shape";
    private ArrayList<Curve> mCurves = new ArrayList<>();
    private HashMap<String, Form> mForms;

    @Override
    public Path getPath() {
        Path path = new Path();
        for (Curve curve: mCurves) {
            path.addPath(curve.getPath(mWidth, mHeight));
        }
        return path;
    }

    public void fitSizeToIncludeAll() {
        RectF outline = null;
        for(Curve curve: mCurves) {
            if (outline == null) {
                outline = curve.getOutline();
            } else {
                outline.union(curve.getOutline());
            }
        }
        if (outline == null) return;
        if(outline.width() == 0) {
            outline.set(outline.left, outline.top, outline.left+1/mWidth, outline.bottom);
        }
        if(outline.height() == 0) {
            outline.set(outline.left, outline.top, outline.right, outline.top+1/mHeight);
        }
        Point absAnchorAt = getAbsoluteAnchorAt();
        mAnchortAt.translate(-mWidth*outline.left, -mHeight*outline.top);
        moveTo(absAnchorAt.x, absAnchorAt.y);
        mWidth = mWidth*outline.width();
        mHeight = mHeight*outline.height();

        float scaleX = 1/outline.width();
        float scaleY = 1/outline.height();

        for(Curve curve: mCurves) {
            curve.translate(-outline.left, -outline.top);
            curve.scale(scaleX, scaleY);
        }
    }

    public void setForm(String formName) {
        Form form = mForms.get(formName);
        if(form == null) return;

        float diffWidth = form.mWidth-this.mWidth;
        float diffHeight = form.mHeight-this.mHeight;
        Point absAnchorAt = getAbsoluteAnchorAt();

        this.mWidth = form.mWidth;
        this.mHeight = form.mHeight;

        Point anchorAt = this.mAnchortAt.copy();
        anchorAt.scale(1/this.mWidth, 1/this.mHeight);

        int minCurveCount = Math.min(form.mCurves.size(), this.mCurves.size());
        for(int i=0; i<minCurveCount; i++) {
            Point selfOrigin = this.mCurves.get(i).getOrigin();
            Point formOrigin = form.mCurves.get(i).getOrigin();
            selfOrigin.copyFrom(formOrigin);
            selfOrigin.translate(anchorAt.x, anchorAt.y);

            ArrayList<BezierPoint> selfBezierPoints = this.mCurves.get(i).getBezierPoints();
            ArrayList<BezierPoint> formBezierPoints = form.mCurves.get(i).getBezierPoints();
            int minBezierPointsCount = Math.min(selfBezierPoints.size(), formBezierPoints.size());

            for(int j=0; j<minBezierPointsCount; j++) {
                BezierPoint selfBezierPoint = selfBezierPoints.get(j);
                BezierPoint formBezierPoint = formBezierPoints.get(j);

                selfBezierPoint.getControl1Point().copyFrom(formBezierPoint.getControl1Point());
                selfBezierPoint.getControl2Point().copyFrom(formBezierPoint.getControl2Point());
                selfBezierPoint.getDestPoint().copyFrom(formBezierPoint.getDestPoint());

                selfBezierPoint.getControl1Point().translate(anchorAt.x, anchorAt.y);
                selfBezierPoint.getControl2Point().translate(anchorAt.x, anchorAt.y);
                selfBezierPoint.getDestPoint().translate(anchorAt.x, anchorAt.y);
            }
        }
        fitSizeToIncludeAll();
        moveTo(absAnchorAt.x, absAnchorAt.y);
    }

    @Override
    public void setProperty(PropName propName, Object value, HashMap<PropName, PropData> propDataMap) {
        super.setProperty(propName, value, propDataMap);
        if (propName == PropName.INTERNAL) {
            String startFormName = propDataMap.get(PropName.START_FORM).getStringValue();
            String endFormName = propDataMap.get(PropName.END_FORM).getStringValue();
            if (endFormName == null || endFormName.isEmpty() || !mForms.containsKey(endFormName)) {
                setForm(startFormName);
                return;
            }
            if (!mForms.containsKey(startFormName)) return;

            Form startForm = mForms.get(startFormName);
            Form endForm = mForms.get(endFormName);
            float frac = (float) value;

            float newWidth = startForm.mWidth + (endForm.mWidth - startForm.mWidth)*frac;
            float newHeight = startForm.mHeight + (endForm.mHeight - startForm.mHeight)*frac;

            float diffWidth = newWidth-this.mWidth;
            float diffHeight = newHeight-this.mHeight;
            Point absAnchorAt = getAbsoluteAnchorAt();

            this.mWidth = newWidth;
            this.mHeight = newHeight;

            Point anchorAt = this.mAnchortAt.copy();
            anchorAt.scale(1/this.mWidth, 1/this.mHeight);

            int minCurveCount = Math.min(startForm.mCurves.size(), endForm.mCurves.size());
            minCurveCount = Math.min(minCurveCount, this.mCurves.size());

            for(int i=0; i<minCurveCount; i++) {
                Point selfOrigin = this.mCurves.get(i).getOrigin();
                Point startFormOrigin = startForm.mCurves.get(i).getOrigin();
                Point endFormOrigin = endForm.mCurves.get(i).getOrigin();

                selfOrigin.setInBetween(startFormOrigin, endFormOrigin, frac);
                selfOrigin.translate(anchorAt.x, anchorAt.y);

                ArrayList<BezierPoint> selfBezierPoints = this.mCurves.get(i).getBezierPoints();
                ArrayList<BezierPoint> startFormBezierPoints = startForm.mCurves.get(i).getBezierPoints();
                ArrayList<BezierPoint> endFormBezierPoints = endForm.mCurves.get(i).getBezierPoints();

                int minBezierPointsCount = Math.min(startFormBezierPoints.size(), endFormBezierPoints.size());
                minBezierPointsCount = Math.min(minBezierPointsCount, selfBezierPoints.size());

                for(int j=0; j<minBezierPointsCount; j++) {
                    BezierPoint selfBezierPoint = selfBezierPoints.get(j);
                    BezierPoint startFormBezierPoint = startFormBezierPoints.get(j);
                    BezierPoint endFormBezierPoint = endFormBezierPoints.get(j);

                    selfBezierPoint.getControl1Point().setInBetween(
                            startFormBezierPoint.getControl1Point(),
                            endFormBezierPoint.getControl1Point(), frac);
                    selfBezierPoint.getControl2Point().setInBetween(
                            startFormBezierPoint.getControl2Point(),
                            endFormBezierPoint.getControl2Point(), frac);
                    selfBezierPoint.getDestPoint().setInBetween(
                            startFormBezierPoint.getDestPoint(),
                            endFormBezierPoint.getDestPoint(), frac);

                    selfBezierPoint.getControl1Point().translate(anchorAt.x, anchorAt.y);
                    selfBezierPoint.getControl2Point().translate(anchorAt.x, anchorAt.y);
                    selfBezierPoint.getDestPoint().translate(anchorAt.x, anchorAt.y);
                }
            }
            fitSizeToIncludeAll();
            moveTo(absAnchorAt.x, absAnchorAt.y);
        }
    }

    public static CurveShape createFromXml(XmlPullParser parser)
            throws XmlPullParserException, IOException {
        if (isShapeTagType(parser, TYPE_NAME)) return null;
        CurveShape curveShape = new CurveShape();
        curveShape.copyAttributesFromXml(parser);
        while (parser.next() != XmlPullParser.END_TAG) {
            if (parser.getEventType() != XmlPullParser.START_TAG) {
                continue;
            }
            if (Curve.TAG_NAME.equals(parser.getName())) {
                Curve curve = Curve.createFromXml(parser);
                curveShape.mCurves.add(curve);
            } else if (Form.TAG_NAME.equals(parser.getName())) {
                if (curveShape.mForms == null) {
                    curveShape.mForms = new HashMap<>();
                }
                String formName = parser.getAttributeValue(null, "name");
                Form form = Form.createFromXml(parser);
                if (form != null) {
                    curveShape.mForms.put(formName, form);
                }
            }
            Helper.skipTag(parser);
        }
        return curveShape;
    }

    public static class Form {
        public static final String TAG_NAME = "form";

        private Float mWidth;
        private Float mHeight;
        private ArrayList<Curve> mCurves = new ArrayList<>();

        public static Form createFromXml(XmlPullParser parser)
                throws XmlPullParserException, IOException {
            parser.require(XmlPullParser.START_TAG, null, TAG_NAME);
            Form form = new Form();
            try {
                form.mWidth = Float.parseFloat(parser.getAttributeValue(null, "width"));
            } catch (NumberFormatException e) {
            }
            try {
                form.mHeight = Float.parseFloat(parser.getAttributeValue(null, "height"));
            } catch (NumberFormatException e) {
            }
            while (parser.next() != XmlPullParser.END_TAG) {
                if (parser.getEventType() != XmlPullParser.START_TAG) {
                    continue;
                }
                if (Curve.TAG_NAME.equals(parser.getName())) {
                    Curve curve = Curve.createFromXml(parser);
                    if (curve != null) {
                        form.mCurves.add(curve);
                    }
                }
            }
            return form;
        }
    }
}
