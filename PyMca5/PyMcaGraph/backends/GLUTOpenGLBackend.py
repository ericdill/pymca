# /*#########################################################################
#
# The PyMca X-Ray Fluorescence Toolkit
#
# Copyright (c) 2004-2014 European Synchrotron Radiation Facility
#
# This file is part of the PyMca X-ray Fluorescence Toolkit developed at
# the ESRF by the Software group.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/
__author__ = "T. Vincent - ESRF Data Analysis"
__contact__ = "thomas.vincent@esrf.fr"
__license__ = "MIT"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__doc__ = """
OpenGL/GLUT backend
"""


# import ######################################################################

from OpenGL.GLUT import *  # noqa
from .OpenGLBackend import OpenGLPlotCanvas


# GLUT ########################################################################

class GLUTOpenGLBackend(OpenGLPlotCanvas):
    _MOUSE_BTNS = {
        GLUT_LEFT_BUTTON: 'left',
        GLUT_RIGHT_BUTTON: 'right',
        GLUT_MIDDLE_BUTTON: 'middle'
    }

    def __init__(self, parent=None, **kw):
        glutInitWindowSize(800, 600)
        glutInitWindowPosition(0, 0)
        glutCreateWindow('GLUTOpenGLBackend')

        OpenGLPlotCanvas.__init__(self, parent, **kw)
        self.initializeGL()

        glutDisplayFunc(self.glutDisplay)
        glutReshapeFunc(self.resizeGL)
        glutMouseFunc(self.glutMouseClicked)
        glutMotionFunc(self.glutMouseMoved)
        glutPassiveMotionFunc(self.glutMouseMoved)

    def updateGL(self):
        glutPostRedisplay()

    def glutDisplay(self):
        self.paintGL()
        glutSwapBuffers()

    def glutMouseClicked(self, btn, state, xPixel, yPixel):
        if btn == 3:   # mouse wheel
            self.onMouseWheel(xPixel, yPixel, 15.)
        elif btn == 4:  # mouse wheel
            self.onMouseWheel(xPixel, yPixel, -15.)
        else:
            btn = self._MOUSE_BTNS[btn]
            if state == GLUT_DOWN:
                self.onMousePress(xPixel, yPixel, btn)
            else:
                self.onMouseRelease(xPixel, yPixel, btn)

    def glutMouseMoved(self, xPixel, yPixel):
        self.onMouseMove(xPixel, yPixel)


# main ########################################################################

if __name__ == "__main__":
    import sys
    import numpy as np
    from ..Plot import Plot

    glutInit(sys.argv)
    glutInitDisplayString("double rgba stencil")

    w = Plot(None, backend=GLUTOpenGLBackend)
    size = 4096
    data = np.arange(float(size)*size, dtype=np.dtype(np.float32))
    data.shape = size, size

    colormap = {'name': 'gray', 'normalization': 'linear',
                'autoscale': True, 'vmin': 0.0, 'vmax': 1.0,
                'colors': 256}
    w.addImage(data, legend="image 1",
               xScale=(25, 1.0), yScale=(-1000, 1.0),
               replot=False, colormap=colormap)

    sys.exit(glutMainLoop())
