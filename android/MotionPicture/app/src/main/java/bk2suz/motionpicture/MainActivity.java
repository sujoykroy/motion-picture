package bk2suz.motionpicture;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.widget.ImageView;

import bk2suz.motionpicturelib.Document;
import bk2suz.motionpicturelib.Effects;

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Document doc = Document.loadFromResource(getResources(), R.xml.sample_anim);
        ImageView imageView = (ImageView) findViewById(R.id.imageView);
        //imageView.setImageBitmap(Effects.blur(this, doc.getBitmap(400F, 400F), 1));
        imageView.setImageBitmap(doc.getBitmap(400F, 400F));
    }
}
