package bk2suz.motionpicturelib;

import android.util.Log;

import java.util.Date;

/**
 * Created by sujoy on 13/10/16.
 */
public class TimeLineTask {
    private Document mDocument;
    private float mSpeed = 1F;
    private float mPlayHead = 0F;
    private long mLastUpdateTime = -1;
    private MultiShapeTimeLine mTimeline;
    private boolean mLoop = true;

    public TimeLineTask(Document document) {
        mDocument = document;
        mTimeline = document.getMainTimeLine();
    }

    public void setLoop(boolean loop) {
        mLoop = loop;
    }

    public void setPlayHead(float t) {
        if (mTimeline == null) return;
        if(mLoop && t>mTimeline.getDuration()) {
            t %= mTimeline.getDuration();
        }
        mPlayHead = t;
        mDocument.clearBitmap();
        mTimeline.moveTo(t);
    }

    public void moveBy(float increment) {
        setPlayHead(mPlayHead+increment);
    }

    public void moveTimeNext() {
        long currentTime = new Date().getTime();
        if (mLastUpdateTime>0) {
            setPlayHead(mPlayHead + (currentTime-mLastUpdateTime)*.001F);
        } else {
            setPlayHead(0);
        }
        mLastUpdateTime = currentTime;
    }
}
