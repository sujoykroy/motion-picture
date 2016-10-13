package bk2suz.motionpicture;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.widget.ImageView;

import java.util.concurrent.Executor;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

import bk2suz.motionpicturelib.Document;
import bk2suz.motionpicturelib.TimeLineTask;

public class MainActivity extends AppCompatActivity {
    ScheduledExecutorService mExecutor = Executors.newSingleThreadScheduledExecutor();
    Document mDocument;
    ImageView mImageView;
    TimeLineTask mTimeLineTask;
    Runnable mUpdateImageTask;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        mDocument = Document.loadFromResource(getResources(), R.xml.sample_anim2);
        mTimeLineTask = new TimeLineTask(mDocument);

        mImageView = (ImageView) findViewById(R.id.imageView);
        //imageView.setImageBitmap(Effects.blur(this, doc.getBitmap(400F, 400F), 1));
        mImageView.setImageBitmap(mDocument.getBitmap(400F, 400F));

        mUpdateImageTask = new Runnable() {
            @Override
            public void run() {
                mImageView.setImageBitmap(mDocument.getBitmap(400F, 400F));
            }
        };

        mExecutor.scheduleAtFixedRate(new Runnable() {
            @Override
            public void run() {
                try {
                    mTimeLineTask.moveTimeNext();
                    mImageView.post(mUpdateImageTask);
                } catch(Exception e) {
                    e.printStackTrace();
                }
            }
        }, 0, 100, TimeUnit.MILLISECONDS);
    }
}
