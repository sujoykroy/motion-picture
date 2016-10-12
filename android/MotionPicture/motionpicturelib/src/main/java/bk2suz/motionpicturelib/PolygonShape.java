package bk2suz.motionpicturelib;

import android.graphics.Path;
import android.graphics.Rect;
import android.graphics.RectF;
import android.util.Log;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;

/**
 * Created by sujoy on 8/10/16.
 */
public class PolygonShape extends Shape {
    public static final String TYPE_NAME = "polygon_shape";
    protected ArrayList<Polygon> mPolygons = new ArrayList<>();
    protected HashMap<String, Form> mForms;

    @Override
    public Path getPath() {
        Path path = new Path();
        for (Polygon polygon: mPolygons) {
            path.addPath(polygon.getPath(mWidth, mHeight));
        }
        return path;
    }

    public void fitSizeToIncludeAll() {
        RectF outline = null;
        for(Polygon polygon: mPolygons) {
            if (outline == null) {
                outline = polygon.getOutline();
            } else {
                outline.union(polygon.getOutline());
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

        for (Polygon polygon: mPolygons) {
            polygon.translate(-outline.left, -outline.top);
            polygon.scale(scaleX, scaleY);
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

        int minPolygonCount = Math.min(form.mPolygons.size(), this.mPolygons.size());
        for(int i=0; i<minPolygonCount; i++) {
            ArrayList<Point> selfPoints = this.mPolygons.get(i).getPoints();
            ArrayList<Point> formPoints = form.mPolygons.get(i).getPoints();
            int minPoinCount = Math.min(selfPoints.size(), formPoints.size());
            for(int j=0; j<minPoinCount; j++) {
                selfPoints.get(j).copyFrom(formPoints.get(j));
                selfPoints.get(j).translate(anchorAt.x, anchorAt.y);
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

            int minPolygonCount = Math.min(startForm.mPolygons.size(), endForm.mPolygons.size());
            minPolygonCount = Math.min(minPolygonCount, this.mPolygons.size());
            for(int i=0; i<minPolygonCount; i++) {
                ArrayList<Point> selfPoints = this.mPolygons.get(i).getPoints();
                ArrayList<Point> startFormPoints = startForm.mPolygons.get(i).getPoints();
                ArrayList<Point> endFormPoints = endForm.mPolygons.get(i).getPoints();
                int minPointCount = Math.min(selfPoints.size(), startFormPoints.size());
                minPointCount = Math.min(minPointCount, endFormPoints.size());
                for(int j=0; j<minPointCount; j++) {
                    selfPoints.get(j).setInBetween(startFormPoints.get(j), endFormPoints.get(j), frac);
                    selfPoints.get(j).translate(anchorAt.x, anchorAt.y);
                }
            }
            fitSizeToIncludeAll();
            moveTo(absAnchorAt.x, absAnchorAt.y);
        }
    }

    public static PolygonShape createFromXml(XmlPullParser parser)
            throws XmlPullParserException, IOException {
        if (isShapeTagType(parser, TYPE_NAME)) return null;
        PolygonShape polygonShape = new PolygonShape();
        polygonShape.copyAttributesFromXml(parser);
        while (parser.next() != XmlPullParser.END_TAG) {
            if (parser.getEventType() != XmlPullParser.START_TAG) {
                continue;
            }
            if (Polygon.TAG_NAME.equals(parser.getName())) {
                Polygon polygon = Polygon.createFromXml(parser);
                polygonShape.mPolygons.add(polygon);
            } else if (Form.TAG_NAME.equals(parser.getName())) {
                if (polygonShape.mForms == null) {
                    polygonShape.mForms = new HashMap<>();
                }
                String formName = parser.getAttributeValue(null, "name");
                Form form = Form.createFromXml(parser);
                if (form != null) {
                    polygonShape.mForms.put(formName, form);
                }
            }
            Helper.skipTag(parser);
        }
        return polygonShape;
    }


    public static class Form {
        public static final String TAG_NAME = "form";

        private Float mWidth;
        private Float mHeight;
        private ArrayList<Polygon> mPolygons = new ArrayList<>();

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
                if (Polygon.TAG_NAME.equals(parser.getName())) {
                    Polygon polygon = Polygon.createFromXml(parser);
                    if (polygon != null) {
                        form.mPolygons.add(polygon);
                    }
                }
            }
            return form;
        }
    }
}
