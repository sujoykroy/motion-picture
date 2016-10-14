package bk2suz.motionpicture;

import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.widget.ImageView;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

import bk2suz.motionpicturelib.Document;
import bk2suz.motionpicturelib.TimeLineTask;

public class MainActivity extends AppCompatActivity {
    ScheduledExecutorService mExecutor = Executors.newSingleThreadScheduledExecutor();
    Document mDocument;
    ImageView mSingleBitmapImageView;
    TextView mSingleBitmapTimeTextView;
    TimeLineTask mTimeLineTask;
    Runnable mUpdateImageTask;

    ImageView mMultiDocImageView;
    Bitmap mMultiDocBitmap;
    Canvas  mMultiDocCanvas;
    ArrayList<Document> mMulitDocList = new ArrayList<>();
    ArrayList<TimeLineTask> mMultiDocTimeLineList = new ArrayList<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        mDocument = Document.loadFromResource(getResources(), R.xml.sample_anim2);
        mTimeLineTask = new TimeLineTask(mDocument);

        mSingleBitmapTimeTextView = (TextView) findViewById(R.id.txtSingleBitmapTime);
        mSingleBitmapImageView = (ImageView) findViewById(R.id.singleBitmapImageView);
        mDocument.setBitmapSize(300F, 300F);
        mSingleBitmapImageView.setImageBitmap(mDocument.getBitmap());


        mMulitDocList.add(Document.loadFromResource(getResources(), R.xml.sample_anim));
        mMulitDocList.add(Document.loadFromResource(getResources(), R.xml.sample_anim2));
        mMulitDocList.add(Document.loadFromResource(getResources(), R.xml.sample_anim3));
        mMulitDocList.add(Document.loadFromResource(getResources(), R.xml.sample_anim3));
        for(Document doc: mMulitDocList) {
            mMultiDocTimeLineList.add(new TimeLineTask(doc));
        }

        mMultiDocImageView =(ImageView) findViewById(R.id.multiDocImageView);

        mMultiDocBitmap = Bitmap.createBitmap(200, 200, Bitmap.Config.ARGB_8888);
        mMultiDocImageView.setImageBitmap(mMultiDocBitmap);

        mMultiDocCanvas = new Canvas(mMultiDocBitmap);
        mMulitDocList.get(0).setDrawPosition(150F, 100F);
        mMulitDocList.get(0).setDrawScale(.25F);
        mMulitDocList.get(1).setDrawPosition(50F, 50F);
        mMulitDocList.get(1).setDrawScale(.35F);
        mMulitDocList.get(2).setDrawPosition(30F, 130F);
        mMulitDocList.get(2).setDrawScale(.25F);

        mMulitDocList.get(3).setDrawPosition(50F, 80F);
        mMulitDocList.get(3).setDrawScale(.15F);
        mMulitDocList.get(3).setDrawClip(true);

        mUpdateImageTask = new Runnable() {
            @Override
            public void run() {
                mSingleBitmapImageView.setImageBitmap(mDocument.getBitmap());
                mSingleBitmapTimeTextView.setText(String.format("%.2f", mTimeLineTask.getPlayHead()));

                mMultiDocImageView.setImageBitmap(mMultiDocBitmap);
            }
        };

        mExecutor.scheduleAtFixedRate(new Runnable() {
            @Override
            public void run() {
                try {
                    mTimeLineTask.moveTimeNext();
                    for(TimeLineTask task: mMultiDocTimeLineList) {
                        task.moveTimeNext();
                    }

                    drawMultiDocImage();
                    mSingleBitmapImageView.post(mUpdateImageTask);
                } catch(Exception e) {
                    e.printStackTrace();
                }
            }
        }, 0, 100, TimeUnit.MILLISECONDS);
    }

    private void drawMultiDocImage() {
        mMultiDocBitmap.eraseColor(Color.TRANSPARENT);
        for(Document doc: mMulitDocList) {
            doc.draw(mMultiDocCanvas);
        }
    }
}
