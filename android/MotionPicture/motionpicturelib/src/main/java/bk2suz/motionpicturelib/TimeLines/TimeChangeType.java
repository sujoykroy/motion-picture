package bk2suz.motionpicturelib.TimeLines;

/**
 * Created by sujoy on 11/10/16.
 */
public class TimeChangeType {
    public static final String TAG_NAME = "time_change_type";

    public TimeSliceValue getValueAt(TimeSliceValue startValue, TimeSliceValue endValue, Float t, Float duration) {
        TimeSliceValue timeSliceValue = endValue.copy();
        timeSliceValue.subtract(startValue);
        timeSliceValue.multiply(t/duration);
        timeSliceValue.add(startValue);
        //return startValue + (endValue-startValue)*t/duration;
        return timeSliceValue;
    }
}
