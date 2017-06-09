from OpenGL.GL import *
from OpenGL.GL import shaders
class Polygon3DGLDrawer(object):
    VERTEXT_SHAPER_CODE = """
            precision highp float;
            attribute vec4 aPosition;
            attribute vec2 aTexCoords;
            varying vec2 vTexCoords;
            uniform mat4 uMVPMatrix;
            void main() {
               vTexCoords = aTexCoords;
               gl_Position = uMVPMatrix * aPosition;
            }
    """

    FRAGMENT_SHADER_CODE = """
            precision highp float;
            uniform vec4 uColor;
            uniform bool uHasTexture;
            uniform sampler2D uTexture;
            varying vec2 vTexCoords;
            void main() {
               if (uHasTexture == true) {
                   gl_FragColor = texture2D(uTexture, vTexCoords);
               } else {
                   gl_FragColor = uColor;
               }
            }
    """

    def __init__(self):
        self.vbo = glGenBuffers(1)

        #"""
        self.gl_program = glCreateProgram();
        self.vertex_shader = self.loadShader(GL_VERTEX_SHADER, self.VERTEXT_SHAPER_CODE)
        glAttachShader(self.gl_program, self.vertex_shader)
        self.fragment_shader = self.loadShader(GL_FRAGMENT_SHADER, self.FRAGMENT_SHADER_CODE)
        glAttachShader(self.gl_program, self.fragment_shader)
        #glValidateProgram(self.gl_program)
        #validation = glGetProgramiv( self.gl_program, GL_VALIDATE_STATUS )
        #print validation, glGetProgramInfoLog(self.gl_program)
        """
        self.gl_program = shaders.compileProgram(
             shaders.compileShader(self.VERTEXT_SHAPER_CODE, GL_VERTEX_SHADER)
            ,shaders.compileShader(self.FRAGMENT_SHADER_CODE,GL_FRAGMENT_SHADER))
        """
        glLinkProgram(self.gl_program)
        print(glGetProgramiv(self.gl_program, GL_LINK_STATUS) == 1)

        self.gl_position_handle = None
        self.gl_texCoords_handle = None
        self.gl_color_handle = None
        self.gl_has_texture_handle = None
        self.gl_texture_handle = None
        self.mvp_matrix_handle = None

    def cleanup(self):
        glDeleteBuffers(1, [self.vbo])
        glDeleteShader(self.vertex_shader)
        glDeleteShader(self.fragment_shader)
        glDeleteProgram(self.gl_program)

    @staticmethod
    def loadShader(shader_type, shader_code):
        shader = glCreateShader(shader_type)
        glShaderSource(shader, shader_code)
        glCompileShader(shader)
        return shader

