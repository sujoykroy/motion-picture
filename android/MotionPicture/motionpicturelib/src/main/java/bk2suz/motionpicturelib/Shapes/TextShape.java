package bk2suz.motionpicturelib.Shapes;

import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Typeface;
import android.text.Layout;
import android.text.StaticLayout;
import android.text.TextPaint;

import org.xmlpull.v1.XmlPullParser;
import org.xmlpull.v1.XmlPullParserException;

import java.io.IOException;

import bk2suz.motionpicturelib.Commons.Color;
import bk2suz.motionpicturelib.Commons.Helper;

/**
 * Created by sujoy on 10/10/16.
 */
public class TextShape extends RectangleShape {
    public static final String TYPE_NAME = "text";

    public static final int X_ALIGN_LEFT = 0;
    public static final int X_ALIGN_CENTER = 1;
    public static final int X_ALIGN_RIGHT = 2;

    public static final int Y_ALIGN_TOP = 0;
    public static final int Y_ALIGN_MIDDLE = 1;
    public static final int Y_ALIGN_BOTTOM = 2;

    public static final Layout.Alignment[] LINE_ALIGNMENTS = {
            Layout.Alignment.ALIGN_NORMAL,
            Layout.Alignment.ALIGN_CENTER,
            Layout.Alignment.ALIGN_OPPOSITE
    };

    protected Integer mXAlign;
    protected Integer mYAlign;
    protected Integer mLineAlign;
    protected String mText;
    protected String mFont;
    protected Color mFontColor;
    protected TextPaint mFontPaint;

    public TextShape() {
        super();
        mFontPaint = new TextPaint();
        mFontPaint.setTextAlign(Paint.Align.LEFT);
        mFontPaint.setStyle(Paint.Style.FILL_AND_STROKE);
    }

    @Override
    public void copyAttributesFromXml(XmlPullParser parser) {
        super.copyAttributesFromXml(parser);
        try {
            mXAlign = Integer.parseInt(parser.getAttributeValue(null, "x_align"));
        } catch (NumberFormatException e) {
        }
        try {
            mYAlign = Integer.parseInt(parser.getAttributeValue(null, "y_align"));
        } catch (NumberFormatException e) {
        }
        try {
            mLineAlign = Integer.parseInt(parser.getAttributeValue(null, "line_align"));
        } catch (NumberFormatException e) {
        }
        mText = parser.getAttributeValue(null, "text");
        setFont(parser.getAttributeValue(null, "font"));
        setFontColor(Helper.parseColor(parser.getAttributeValue(null, "font_color")));
    }

    public void setFont(String font) {
        mFont = font;
        if (font == null) return;
        String[] values = font.split(" ");
        String textSizeString = values[values.length - 1];
        try {
            mFontPaint.setTextSize(Float.parseFloat(textSizeString)*1.5F);
        } catch (NumberFormatException e) {
        }
        if (values.length > 1) {
            String fontName = font.substring(0, font.length() - textSizeString.length() - 1);
            Typeface typeFace = Typeface.create(fontName, Typeface.NORMAL);
            mFontPaint.setTypeface(typeFace);
        }
    }

    public void setFontColor(Color color) {
        if (color != null && color.getClass().isInstance(mFontColor)) {
            mFontColor.copyFrom(color);
        } else {
            mFontColor = color;
        }
        if (mFontColor != null) {
            mFontColor.setPaint(mFontPaint);
        }
    }

    @Override
    public void draw(Canvas canvas) {
        super.draw(canvas);
        if (mText == null) return;

        StaticLayout layout = new StaticLayout(mText,
                mFontPaint, (int) StaticLayout.getDesiredWidth(mText, mFontPaint),
                LINE_ALIGNMENTS[mLineAlign], 1F, 0F, false);
        Float x = 0F, y = 0F;

        if (mXAlign == X_ALIGN_LEFT) {
            x = mBorderWidth + mCornerRadius;
        } else if (mXAlign == X_ALIGN_RIGHT) {
            x = mWidth - layout.getWidth() - mBorderWidth - mCornerRadius;
        } else if (mXAlign == X_ALIGN_CENTER) {
            x = (mWidth - layout.getWidth()) * .5F;
        }
        if (mYAlign == Y_ALIGN_TOP) {
            y = mBorderWidth + mCornerRadius;
        } else if (mYAlign == Y_ALIGN_BOTTOM) {
            y = mHeight - layout.getHeight() - mBorderWidth - mCornerRadius;
        } else if (mYAlign == Y_ALIGN_MIDDLE) {
            y = (mHeight - layout.getHeight()) * .5F;
        }

        canvas.save();
        preDraw(canvas);
        canvas.translate(x, y);
        layout.draw(canvas);
        canvas.restore();
    }

    public static TextShape createFromXml(XmlPullParser parser)
            throws XmlPullParserException, IOException {
        if (isShapeTagType(parser, TYPE_NAME)) return null;
        TextShape textShape = new TextShape();
        textShape.copyAttributesFromXml(parser);
        return textShape;
    }
}
