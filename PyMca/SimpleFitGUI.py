#/*##########################################################################
# Copyright (C) 2004-2010 European Synchrotron Radiation Facility
#
# This file is part of the PyMCA X-ray Fluorescence Toolkit developed at
# the ESRF by the Beamline Instrumentation Software Support (BLISS) group.
#
# This toolkit is free software; you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option) 
# any later version.
#
# PyMCA is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# PyMCA; if not, write to the Free Software Foundation, Inc., 59 Temple Place,
# Suite 330, Boston, MA 02111-1307, USA.
#
# PyMCA follows the dual licensing model of Trolltech's Qt and Riverbank's PyQt
# and cannot be used as a free plugin for a non-free program. 
#
# Please contact the ESRF industrial unit (industry@esrf.fr) if this license 
# is a problem for you.
#############################################################################*/
import sys
import os
import SimpleFitModule
import SimpleFitConfigurationGUI
import Parameters
qt = Parameters.qt
if qt.qVersion() < '4.0.0':
    raise ImportError, "This module requires PyQt4"
try:
    #raise ImportError
    if 1:
        from QtBlissGraph import QtBlissGraph as GraphWindow
    else:
        from ScanWindow import ScanWindow as GraphWindow
except ImportError:
    from Plot1DMatplotlib import Plot1DMatplotlib as GraphWindow

DEBUG = 0

HorizontalSpacer = SimpleFitConfigurationGUI.HorizontalSpacer
VerticalSpacer = SimpleFitConfigurationGUI.VerticalSpacer

class TopWidget(qt.QWidget):
    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        self.mainLayout = qt.QGridLayout(self)
        self.mainLayout.setMargin(2)
        self.mainLayout.setSpacing(2)
        font = qt.QFont(self.font())
        font.setBold(True)

        #Function handling
        self.functionLabel = qt.QLabel(self)
        self.functionLabel.setFont(font)
        self.functionLabel.setText("Function:")
        self.addFunctionButton = qt.QPushButton(self)
        self.addFunctionButton.setText("ADD")

        #fit function
        self.fitFunctionLabel = qt.QLabel(self)
        self.fitFunctionLabel.setFont(font)
        self.fitFunctionLabel.setText("Fit:")
        self.fitFunctionCombo = qt.QComboBox(self)
        self.fitFunctionCombo.addItem(str("None"))
        self.fitFunctionCombo.setSizeAdjustPolicy(qt.QComboBox.AdjustToContents)
        self.fitFunctionCombo.setMinimumWidth(100)
        
        #background function
        self.backgroundLabel = qt.QLabel(self)
        self.backgroundLabel.setFont(font)
        self.backgroundLabel.setText("Background:")
        self.backgroundCombo  = qt.QComboBox(self)
        self.backgroundCombo.addItem(str("None"))
        self.backgroundCombo.setSizeAdjustPolicy(qt.QComboBox.AdjustToContents)
        self.backgroundCombo.setMinimumWidth(100)

        #arrange everything
        self.mainLayout.addWidget(self.functionLabel,     0, 0)
        self.mainLayout.addWidget(self.addFunctionButton,    0, 1)
        self.mainLayout.addWidget(HorizontalSpacer(self), 0, 2)
        self.mainLayout.addWidget(self.fitFunctionLabel,  0, 3)
        self.mainLayout.addWidget(self.fitFunctionCombo,  0, 4)
        self.mainLayout.addWidget(HorizontalSpacer(self), 0, 5)
        self.mainLayout.addWidget(self.backgroundLabel,   0, 6)
        self.mainLayout.addWidget(self.backgroundCombo,   0, 7)

        self.configureButton = qt.QPushButton(self)
        self.configureButton.setText("CONFIGURE")
        self.mainLayout.addWidget(self.configureButton,   0, 8)

    def setFunctions(self, functionList):
        currentFunction = str(self.fitFunctionCombo.currentText())
        currentBackground = str(self.backgroundCombo.currentText())
        self.fitFunctionCombo.clear()
        self.backgroundCombo.clear()
        self.fitFunctionCombo.addItem('None')
        self.backgroundCombo.addItem('None')
        for key in functionList:
            self.fitFunctionCombo.addItem(str(key))
            self.backgroundCombo.addItem(str(key))

        #restore previous values
        idx = self.fitFunctionCombo.findText(currentFunction)
        self.fitFunctionCombo.setCurrentIndex(idx)
        idx = self.backgroundCombo.findText(currentBackground)
        self.backgroundCombo.setCurrentIndex(idx)
        
class StatusWidget(qt.QWidget):
    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        self.mainLayout = qt.QHBoxLayout(self)
        self.mainLayout.setMargin(2)
        self.mainLayout.setSpacing(2)
        
        self.statusLabel = qt.QLabel(self)
        self.statusLabel.setText(str("Status:"))
        self.statusLine = qt.QLineEdit(self)
        self.statusLine.setText(str("Ready"))
        self.statusLine.setReadOnly(1)

        self.chi2Label = qt.QLabel(self)
        self.chi2Label.setText(str("Reduced Chi Square:"))

        self.chi2Line = qt.QLineEdit(self)
        self.chi2Line.setText(str(""))
        self.chi2Line.setReadOnly(1)
        
        self.mainLayout.addWidget(self.statusLabel)
        self.mainLayout.addWidget(self.statusLine)
        self.mainLayout.addWidget(self.chi2Label)
        self.mainLayout.addWidget(self.chi2Line)

class SimpleFitGUI(qt.QWidget):
    def __init__(self, parent=None, fit=None, graph=None):
        qt.QWidget.__init__(self, parent)
        self.setWindowTitle("SimpleFitGUI")
        if fit is None:
            self.fitModule = SimpleFitModule.SimpleFit()
        else:
            self.fitModule = fit
        if graph is None:
            self.__useTab = True
            self.graph = GraphWindow()
        else:
            self.__useTab = False
            self.graph = graph
        self._configurationDialog = None
        self.mainLayout = qt.QVBoxLayout(self)
        self.mainLayout.setMargin(2)
        self.mainLayout.setSpacing(2)
        self.topWidget  = TopWidget(self)
        config = self.fitModule.getConfiguration()
        self.topWidget.setFunctions(config['fit']['functions'])
        config = None

        if self.__useTab:
            self.mainTab = qt.QTabWidget(self)
            self.mainLayout.addWidget(self.mainTab)
            self.parametersTable = Parameters.Parameters()
            self.mainTab.addTab(self.graph, 'GRAPH')
            self.mainTab.addTab(self.parametersTable, 'FIT')
        else:
            self.parametersTable = Parameters.Parameters(self)

        self.statusWidget  = StatusWidget(self)

        #build the actions widget
        self.fitActions = qt.QWidget(self)
        self.fitActions.mainLayout = qt.QHBoxLayout(self.fitActions)
        self.fitActions.mainLayout.setMargin(2)
        self.fitActions.mainLayout.setSpacing(2)
        self.fitActions.estimateButton = qt.QPushButton(self.fitActions)
        self.fitActions.estimateButton.setText("Estimate")
        self.fitActions.startFitButton = qt.QPushButton(self.fitActions)
        self.fitActions.startFitButton.setText("Start Fit")
        self.fitActions.dismissButton = qt.QPushButton(self.fitActions)
        self.fitActions.dismissButton.setText("Dismiss")
        self.fitActions.mainLayout.addWidget(self.fitActions.estimateButton)
        self.fitActions.mainLayout.addWidget(self.fitActions.startFitButton)
        self.fitActions.mainLayout.addWidget(self.fitActions.dismissButton)
        self.mainLayout.addWidget(self.topWidget)
        if self.__useTab:
            self.mainLayout.addWidget(self.mainTab)
        else:
            self.mainLayout.addWidget(self.parametersTable)
        self.mainLayout.addWidget(self.statusWidget)
        self.mainLayout.addWidget(self.fitActions)

        #connect top widget
        self.connect(self.topWidget.addFunctionButton,
                    qt.SIGNAL("clicked()"),self.importFunctions)
        
        self.connect(self.topWidget.fitFunctionCombo,
                     qt.SIGNAL("currentIndexChanged(int)"),
                     self.fitFunctionComboSlot)

        self.connect(self.topWidget.backgroundCombo,
                     qt.SIGNAL("currentIndexChanged(int)"),
                     self.backgroundComboSlot)

        self.connect(self.topWidget.configureButton,
                     qt.SIGNAL("clicked()"),
                     self.configureButtonSlot)

        #connect actions
        self.connect(self.fitActions.estimateButton,
                    qt.SIGNAL("clicked()"),self.estimate)
        self.connect(self.fitActions.startFitButton,
                                qt.SIGNAL("clicked()"),self.startFit)
        self.connect(self.fitActions.dismissButton,
                                qt.SIGNAL("clicked()"),self.dismiss)        

    def importFunctions(self, functionsfile=None):
        if functionsfile is None:
            fn = qt.QFileDialog.getOpenFileName()
            if fn.isEmpty():
                functionsfile = ""
            else:
                functionsfile= str(fn)
            if not len(functionsfile):
                return
        if DEBUG:
            self.fitModule.importFunctions(functionsfile)
        else:
            try:
                self.fitModule.importFunctions(functionsfile)
            except:
                qt.QMessageBox.critical(self, "ERROR",
                                        "Function not imported")

        config = self.fitModule.getConfiguration()
        self.topWidget.setFunctions(config['fit']['functions'])

    def fitFunctionComboSlot(self, idx):
        if idx <= 0:
            fname = "None"
        else:
            fname = str(self.topWidget.fitFunctionCombo.itemText(idx))
        self.fitModule.setFitFunction(fname)

    def backgroundComboSlot(self, idx):
        if idx <= 0:
            fname = "None"
        else:
            fname = str(self.topWidget.backgroundCombo.itemText(idx))
        self.setBackgroundFunction(fname)

    def configureButtonSlot(self):
        if self._configurationDialog is None:
            self._configurationDialog =\
                SimpleFitConfigurationGUI.SimpleFitConfigurationGUI()
        self._configurationDialog.setSimpleFitInstance(self.fitModule)
        if not self._configurationDialog.exec_():
            if DEBUG:
                print "NOT UPDATING CONFIGURATION"
            oldConfig = self.fitModule.getConfiguration()
            self._configurationDialog.setConfiguration(oldConfig)
            return
        newConfig = self._configurationDialog.getConfiguration()
        self.fitModule.setConfiguration(newConfig)
        newConfig = self.fitModule.getConfiguration()
        #self.topWidget.setFunctions(newConfig['fit']['functions'])
        fname = self.fitModule.getFitFunction()
        if fname in [None, "None", "NONE"]:
            idx = 0
        else:
            idx = newConfig['fit']['functions'].index(fname) + 1
        self.topWidget.fitFunctionCombo.setCurrentIndex(idx)
        fname = self.fitModule.getBackgroundFunction()
        if fname in [None, "None", "NONE"]:
            idx = 0
        else:
            idx = newConfig['fit']['functions'].index(fname) + 1
        idx = self.topWidget.backgroundCombo.findText(fname)
        self.topWidget.backgroundCombo.setCurrentIndex(idx)
        print "TABLE TO BE CLEANED"
        #self.estimate()
        
    def setFitFunction(self, fname):
        current = self.fitModule.getFitFunction()
        if current != fname:
            self.fitModule.setFitFunction(fname)
            idx = self.topWidget.fitFunctionCombo.findText(fname)
            self.topWidget.fitFunctionCombo.setCurrentIndex(idx)

    def setBackgroundFunction(self, fname):
        current = self.fitModule.getBackgroundFunction()
        if current != fname:
            self.fitModule.setBackgroundFunction(fname)
            idx = self.topWidget.backgroundCombo.findText(fname)
            self.topWidget.backgroundCombo.setCurrentIndex(idx)

    def setData(self, *var, **kw):
        returnValue = self.fitModule.setData(*var, **kw)
        if self.__useTab:
            if hasattr(self.graph, "addCurve"):
                self.graph.addCurve(self.fitModule._x,
                                    self.fitModule._y,
                                    legend='Data',
                                    replace=True)
            elif hasattr(self.graph, "newCurve"):
                self.graph.clearCurves()
                self.graph.newCurve('Data',
                                    self.fitModule._x,
                                    self.fitModule._y)
                self.graph.replot()
        return returnValue

    def estimate(self):
        self.setStatus("Estimate started")
        self.statusWidget.chi2Line.setText("")
        if DEBUG:
            self.fitModule.estimate()
            self.setStatus()
            self.parametersTable.fillTableFromFit(self.fitModule.paramlist)
        else:
            try:
                self.fitModule.estimate()
                self.setStatus()
                self.parametersTable.fillTableFromFit(self.fitModule.paramlist)
            except:
                text = "%s:%s" % (sys.exc_info()[0], sys.exc_info()[1])
                msg = qt.QMessageBox(self)
                msg.setIcon(qt.QMessageBox.Critical)
                msg.setText(text)
                msg.exec_()
                self.setStatus("Ready (after estimate error)")
            

    def setStatus(self, text=None):
        if text is None:
            text = "%s" % self.fitModule.getStatus()

        self.statusWidget.statusLine.setText(text)

    def startFit(self):
        #get parameters from table
        self.fitModule.paramlist = self.parametersTable.fillFitFromTable()
        if DEBUG:
            values, chisq, sigma, niter, lastdeltachi = self.fitModule.startFit()
            self.setStatus()
        else:
            try:
                values,chisq,sigma,niter,lastdeltachi = self.fitModule.startFit()
                self.setStatus()
            except:
                text = "%s:%s" % (sys.exc_info()[0], sys.exc_info()[1])
                msg = qt.QMessageBox(self)
                msg.setIcon(qt.QMessageBox.Critical)
                msg.setText(text)
                msg.exec_()
                self.setStatus("Ready (after fit error)")
                return
            
        self.parametersTable.fillTableFromFit(self.fitModule.paramlist)
        self.statusWidget.chi2Line.setText("%f" % chisq)
        ddict = {}
        ddict['event'] = "FitFinished"
        ddict['x']    = self.fitModule._x
        ddict['y']    = self.fitModule._y
        ddict['yfit'] = self.evaluateDefinedFunction()
        self.emit(qt.SIGNAL('SimpleFitSignal'), ddict)
        self.updateGraph()

    def updateGraph(self):
        #this is to be overwritten and for test purposes
        if self.graph is None:
            return
        ddict = {}
        ddict['event'] = "FitFinished"
        ddict['x']    = self.fitModule._x
        ddict['y']    = self.fitModule._y
        ddict['yfit'] = self.evaluateDefinedFunction()
        ddict['background'] = self.fitModule._evaluateBackground()
        if hasattr(self.graph, "addCurve"):
            self.graph.addCurve(ddict['x'], ddict['y'], 'Data') 
            self.graph.addCurve(ddict['x'], ddict['yfit'], 'Fit')
            self.graph.addCurve(ddict['x'], ddict['background'], 'Background') 
        elif hasattr(self.graph, "newCurve"):
            self.graph.newCurve('Data', ddict['x'], ddict['y']) 
            self.graph.newCurve('Fit', ddict['x'], ddict['yfit']) 
            self.graph.newCurve('Background', ddict['x'], ddict['background']) 
            self.graph.replot()
        self.graph.show()

    def dismiss(self):
        self.close()

    def evaluateDefinedFunction(self, x=None):
        return self.fitModule.evaluateDefinedFunction()

def test():
    import numpy
    #import DefaultFitFunctions as SpecfitFunctions
    import SpecfitFunctions
    a=SpecfitFunctions.SpecfitFunctions()
    x = numpy.arange(1000).astype(numpy.float)
    p1 = numpy.array([1500,100.,50.0])
    p2 = numpy.array([1500,700.,50.0])
    y = a.gauss(p1, x)
    y = y + a.gauss(p2,x) + x * 5.
    if 0:
        fit = SimpleFitModule.SimpleFit()
        fit.importFunctions(SpecfitFunctions)
        fit.setFitFunction('Gaussians')
        #fit.setBackgroundFunction('Gaussians')
        #fit.setBackgroundFunction('Constant')
        fit.setData(x, y)
        w = SimpleFitGUI(fit=fit)
        w.show()
    else:
        fit=None
        w = SimpleFitGUI(fit=fit)
        w.setData(x, y, xmin=x[0], xmax=x[-1])
        w.show()
        import SimpleFitUserEstimatedFunctions
        fname = SimpleFitUserEstimatedFunctions.__file__
        w.importFunctions(fname)
        w.setFitFunction('User Estimated Gaussians')
    return w

if __name__=="__main__":
    DEBUG = 0
    app = qt.QApplication([])
    w = test()
    app.exec_()
