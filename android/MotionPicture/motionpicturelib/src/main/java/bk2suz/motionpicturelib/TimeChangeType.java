package bk2suz.motionpicturelib;

/**
 * Created by sujoy on 11/10/16.
 */
public class TimeChangeType {
    public static final String TAG_NAME = "time_change_type";

    public Float getValueAt(Float startValue, Float endValue, Float t, Float duration) {
        return startValue + (endValue-startValue)*t/duration;
    }
}
