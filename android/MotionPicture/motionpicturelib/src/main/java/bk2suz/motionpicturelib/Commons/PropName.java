package bk2suz.motionpicturelib.Commons;

/**
 * Created by sujoy on 11/10/16.
 */
public enum PropName {
    NONE(""),
    X("x"),
    Y("y"),
    STAGE_X("stage_x"),
    STAGE_Y("stage_y"),
    SCALE_X("scale_x"),
    SCALE_Y("scale_y"),
    ANCHOR_X("anchor_x"),
    ANCHOR_Y("anchor_y"),
    ANCHOR_AT("anchor_at"),
    POST_SCALE_X("post_scale_x"),
    POST_SCALE_Y("post_scale_y"),
    BORDER_WIDTH("border_width"),
    BORDER_COLOR("border_color"),
    FILL_COLOR("fill_color"),
    WIDTH("width"),
    HEIGHT("height"),
    ANGLE("angle"),
    TRANSLATION("translation"),
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
    END_FORM("end_form"),
    TYPE("type"),
    REL_ABS_ANCHOR_AT("rel_abs_anchor_at"),
    CAMERA_ROTATE_X("camera_rotate_x"),
    CAMERA_ROTATE_Y("camera_rotate_y"),
    CAMERA_ROTATE_Z("camera_rotate_z");

    private String mXmlName;

    PropName(String xmlName) {
        this.mXmlName = xmlName;
    }

    public static PropName getByXmlName(String xmlName) {
        if(xmlName == null) return NONE;
        for(PropName p: PropName.values()) {
            if (p.mXmlName.equals(xmlName)) return p;
        }
        return NONE;
    }
}
