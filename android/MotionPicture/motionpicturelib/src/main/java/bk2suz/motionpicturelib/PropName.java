package bk2suz.motionpicturelib;

import java.util.HashMap;

/**
 * Created by sujoy on 11/10/16.
 */
public enum PropName {
    NONE(""),
    NULL(null),
    X("x"),
    Y("y"),
    STAGE_X("stage_x"),
    STAGE_Y("stage_y"),
    SCALE_X("scale_x"),
    SCALE_Y("scale_y"),
    ANCHOR_X("anchor_x"),
    ANCHOR_Y("anchor_y"),
    POST_SCALE_X("post_scale_x"),
    POST_SCALE_Y("post_scale_y"),
    BORDER_WIDTH("border_width"),
    BORDER_COLOR("border_color"),
    FILL_COLOR("fill_color"),
    WIDTH("width"),
    HEIGHT("width"),
    ANGLE("angle"),
    PRE_MATRIX("pre_matrix"),
    MIRRO_ANGLE("mirror_angle"),
    SWEEP_ANGLE("sweep_angle"),
    THICKNESS("thickness"),
    X_ALIGN("x_align"),
    Y_ALIGN("y_align"),
    FONT("font"),
    FONT_COLOR("font_color"),
    LINE_ALIGN("line_align"),
    TEXT("TEXT"),
    POSE("pose"),
    START_POSE("start_pose"),
    END_POSE("end_pose"),
    TIMELINE("timeline"),
    CORNER_RADIUS("corner_radius"),
    INTERNAL("internal"),
    FORM("form"),
    START_FORM("start_form"),
    END_FORM("end_form");

    private String mXmlName;

    PropName(String xmlName) {
        this.mXmlName = xmlName;
    }

    public static PropName getByXmlName(String xmlName) {
        for(PropName p: PropName.values()) {
            if (p.mXmlName.equals(xmlName)) return p;
        }
        return NULL;
    }
}
