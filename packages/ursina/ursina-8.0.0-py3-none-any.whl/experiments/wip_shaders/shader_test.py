from direct.showbase.ShowBase import ShowBase
# from ShaderCombiner import ShaderCombiner
from direct.gui.DirectSlider import DirectSlider
from panda3d.core import GeomPatches, GeomVertexFormat, GeomVertexWriter, GeomVertexData, Geom, GeomNode


from os.path import join
from panda3d.core import Shader

from os import makedirs
from os.path import isdir


class ShaderCombiner:

    __tmp_path = "shader_dump"

    @classmethod
    def setTempPath(self, p):
        self.__tmp_path = p

    @classmethod
    def ensureTempPath(self):
        if isdir(self.__tmp_path):
            return
        try:
            makedirs(self.__tmp_path)
        except Exception as msg:
            print ("Could not create shader dir at", self.__tmp_path, ":", msg)

    @classmethod
    def getShaderFileContents(self, filename):
        with open(filename) as f:
            return f.read()

    @classmethod
    def writeShaderFileContents(self, filename, content, append=False):
        with open(filename, 'a' if append else 'w') as f:
            f.write(content)

    @classmethod
    def parseShaderContent(self, content):
        content = content.replace("\r", "")
        return content

    @classmethod
    def createGlslShader(self, files, has_geometry, name, glslversion=130, externals=None, defines=None, has_tesselation=False):

        dbg = "Creating shader '" + str(name) + "' with glslversion " + str(glslversion)
        if has_geometry:
            dbg += " (geometry)"
        if has_tesselation:
            dbg += " (tesselated)"
        print(dbg)


        self.ensureTempPath()

        if type(files) == str:
            files = [files]

        if type(files) != list:
            files = list(files)

        files = [] + files

        header = "//GLSL\n"
        header += "#version " + str(glslversion) + "\n"


        if defines is not None:
            for dname, dvalue in defines.items():
                header += "#define " + dname + " " + str(dvalue) + "\n"

        content_vshader = header
        content_fshader = header
        content_gshader = header
        content_tessControl = header
        content_tessEval    = header


        content_vshader += "#define _VERTEX_\n\n#define VARIABLE out\n\n"

        if has_geometry:
            content_fshader += "#extension GL_ARB_fragment_layer_viewport : enable\n"

        content_fshader += "#define _FRAGMENT_\n\n#define VARIABLE in\n\n"

        if has_geometry:
            content_gshader += "#extension GL_EXT_geometry_shader4 : enable\n"
            content_gshader += "#extension GL_ARB_fragment_layer_viewport : enable\n"
            content_gshader += "#define _GEOMETRY_\n\n"

        if has_tesselation:
            content_tessControl += "#define _TESSCONTROL_\n"
            content_tessEval    += "#define _TESSEVAL_\n"




        combined_content = ""

        for f in files:
            c = self.getShaderFileContents(f)
            combined_content += self.parseShaderContent(c) + "\n\n"

        if externals is not None:
            for eid, source in externals.items():
                repl = '#EXTERNAL("' + eid + '")'
                content = self.getShaderFileContents(source)
                combined_content = combined_content.replace(repl, content)

        content_vshader += combined_content
        content_fshader += combined_content
        content_gshader += combined_content
        content_tessControl += combined_content
        content_tessEval    += combined_content

        f_vertex = join(self.__tmp_path, name + "_vertex.glsl")
        f_fragment = join(self.__tmp_path, name + "_fragment.glsl")
        f_geometry = join(self.__tmp_path, name + "_geometry.glsl")

        f_tessControl = join(self.__tmp_path, name + "_tesselationControl.glsl")
        f_tessEval    = join(self.__tmp_path, name + "_tesselationEvaluation.glsl")


        self.writeShaderFileContents(f_vertex, content_vshader)
        self.writeShaderFileContents(f_fragment, content_fshader)

        if has_geometry:
            self.writeShaderFileContents(f_geometry, content_gshader)

        if has_tesselation:
            self.writeShaderFileContents(f_tessControl, content_tessControl)
            self.writeShaderFileContents(f_tessEval, content_tessEval)

        args = [f_vertex, f_fragment]

        if has_geometry:
            args.append(f_geometry)

        if has_tesselation:
            if not has_geometry:
                args.append("")
            args.append(f_tessControl)
            args.append(f_tessEval)


        shader = Shader.load(Shader.SLGLSL, *args)
        return shader

class MyApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        # Camera stuff
        base.disableMouse()
        base.camera.setPos(0, -3, 0)
        base.camera.lookAt(0, 0, 0)

        # Toggle wireframe so we can see the vertices
        base.toggleWireframe()

        # For reloading the shaders
        self.accept("r", self.loadShader)

        # Create the patch
        form = GeomVertexFormat.getV3()
        vdata = GeomVertexData("vertices", form, Geom.UHStatic)

        vertexWriter = GeomVertexWriter(vdata, "vertex")
        vertexWriter.addData3f(0, 0, 0)
        vertexWriter.addData3f(1, 0, 0)
        vertexWriter.addData3f(1, 0, 1)
        vertexWriter.addData3f(0, 0, 1)

        patches = GeomPatches(3, Geom.UHStatic)
        patches.addVertex(0)
        patches.addVertex(1)
        patches.addVertex(3)
        patches.closePrimitive()

        patches.addConsecutiveVertices(1, 3)
        patches.closePrimitive()

        gm = Geom(vdata)
        gm.addPrimitive(patches)

        gn = GeomNode("model")
        gn.addGeom(gm)
        self.tesselatedQuad = render.attachNewNode(gn)
        self.tesselatedQuad.setPos(-0.5, 0, -0.5)

        # Load tesselation shader
        self.loadShader()

        # Set initial tesselation factors
        self.tesselatedQuad.setShaderInput("TessLevelInner", 5.0)
        self.tesselatedQuad.setShaderInput("TessLevelOuter", 5.0)

        # Sliders to modify the tesselation factors
        self.tessInnerSlider = DirectSlider(range=(1, 20), value=8.0, pageSize=1.0, pos=(
            0, 0, 0.8), scale=(1.1, 1, 0.4), command=self.setInnerTess)
        self.tessOuterSlider = DirectSlider(range=(1, 20), value=8.0, pageSize=1.0, pos=(
            0, 0, 0.7), scale=(1.1, 1, 0.4), command=self.setOuterTess)

    def setInnerTess(self):
        self.tesselatedQuad.setShaderInput(
            "TessLevelInner", float(self.tessInnerSlider['value']))

    def setOuterTess(self):
        self.tesselatedQuad.setShaderInput(
            "TessLevelOuter", float(self.tessOuterSlider['value']))

    def loadShader(self):
    # #     # This simply loads the tesselation shaders
    # #     sha = ShaderCombiner.createGlslShader(
    # #         ["shader.glsl"], False, "shader", glslversion=400, externals=None, defines=None, has_tesselation=True)
        from tesselation_test import tesselation_shader
    #     self.tesselatedQuad.setShader(tesselation_shader._shader)


app = MyApp()
app.run()
