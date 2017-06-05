package bk2suz.motionpicturelib.TimeLines;

/**
 * Created by sujoy on 5/6/17.
 */
public class TimeSliceValue {
    private boolean mIsArray = false;
    private float[] mValues;


    public Object getData() {
        if(mIsArray) {
            return mValues;
        } else {
            return mValues[0];
        }
    }

    public float[] getFloatArray() {
        return mValues;
    }

    public TimeSliceValue copy() {
        TimeSliceValue timeSliceValue = new TimeSliceValue();
        timeSliceValue.mValues = mValues.clone();
        timeSliceValue.mIsArray = mIsArray;
        return timeSliceValue;
    }

    public void subtract(TimeSliceValue other) {
        if(!mIsArray) {
            mValues[0] -= other.mValues[0];
        } else {
            for (int i = 0; i < mValues.length; i++) {
                mValues[i] -= other.mValues[i];
            }
        }
    }

    public void add(TimeSliceValue other) {
        if(!mIsArray) {
            mValues[0] += other.mValues[0];
        } else {
            for (int i = 0; i < mValues.length; i++) {
                mValues[i] += other.mValues[i];
            }
        }
    }

    public void add(float factor) {
        if(!mIsArray) {
            mValues[0] += factor;
        } else {
            for (int i = 0; i < mValues.length; i++) {
                mValues[i] += factor;
            }
        }
    }

    public void multiply(float factor) {
        if(!mIsArray) {
            mValues[0] *= factor;
        } else {
            for (int i = 0; i < mValues.length; i++) {
                mValues[i] *= factor;
            }
        }
    }

    public static TimeSliceValue createFromText(String text) {
        TimeSliceValue timeSliceValue = new TimeSliceValue();

        if(text.startsWith("[") && text.endsWith("]")) {
            timeSliceValue.mIsArray = true;
            text = text.substring(1, text.length()-1);
        } else {
            timeSliceValue.mIsArray = false;
        }
        String[] strArray = text.split(",");
        timeSliceValue.mValues = new float[strArray.length];
        for(int i=0; i<strArray.length; i++) {
            try {
                timeSliceValue.mValues[i] = Float.parseFloat(strArray[i]);
            } catch (NumberFormatException e) {
                timeSliceValue.mValues[i] = 0;
            }
        }
        return timeSliceValue;
    }
}
