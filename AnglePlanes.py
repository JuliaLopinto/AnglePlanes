import vtk, qt, ctk, slicer
import numpy
from math import *

class AnglePlanes:
    def __init__(self, parent):
        parent.title = "Calculate angle between planes"
        parent.categories = ["AnglePlanes"]
        parent.dependencies = []
        parent.contributors = ["Julia Lopinto"]
        parent.helpText = """
        This Module is used to calculate the angle between two planes by using the normals.
        This is an alpha version of the module.
        It can't be used for the moment.
        """

        parent.acknowledgementText = """
        The tool is developped by Julia Lopinto (intern at the University of Michigan, School of Dentistry)
        """

        self.parent = parent


class AnglePlanesWidget:
    def __init__(self, parent = None):
      if not parent:
        self.parent = slicer.qMRMLWidget()
        self.parent.setLayout(qt.QVBoxLayout())
        self.parent.setMRMLScene(slicer.mrmlScene)
      else:
        self.parent = parent
      self.layout = self.parent.layout()
      if not parent:
        self.setup()
        self.parent.show()

    def setup(self):

        self.n_vector = numpy.matrix([[0], [0], [1], [1]])

        self.interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
        #Definition of the 2 planes
        self.redslice = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeRed')
        matRed = self.redslice.GetSliceToRAS()

        matRed.SetElement(0,3,0)
        matRed.SetElement(1,3,0)
        matRed.SetElement(2,3,0)
        print matRed

        self.greenslice = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeGreen')
        matGreen = self.greenslice.GetSliceToRAS()

        matGreen.SetElement(0,3,0)
        matGreen.SetElement(1,3,0)
        matGreen.SetElement(2,3,0)

        print matGreen

        self.laplaceCollapsibleButton = ctk.ctkCollapsibleButton()
        self.laplaceCollapsibleButton.text = "Planes"
        self.layout.addWidget(self.laplaceCollapsibleButton)
        sampleFormLayout = qt.QFormLayout(self.laplaceCollapsibleButton)


        self.computeBox = qt.QPushButton("Compute Box around the model")
        sampleFormLayout.addWidget(self.computeBox)
        self.computeBox.connect('clicked()', self.onComputeBox)

        # Collapsible button


        self.firstOption = qt.QGroupBox("Move current planes")
        self.firstOption.setCheckable(True)
        self.firstOption.setChecked(False)
        self.firstOption.connect('clicked(bool)', self.firstOptionClicked)

        self.textFirstOption = qt.QLabel("Move the current planes.")

        self.checkPlaneRed = qt.QCheckBox("Red Plane")
        self.checkPlaneRed.connect('clicked(bool)', self.checkPlaneRedClicked)

        self.checkPlaneYellow = qt.QCheckBox("Yellow Plane")
        self.checkPlaneYellow.connect('clicked(bool)', self.checkPlaneYellowClicked)

        self.checkPlaneGreen = qt.QCheckBox("Green Plane")
        self.checkPlaneGreen.connect('clicked(bool)', self.checkPlaneGreenClicked)

        vbox = qt.QVBoxLayout()
        vbox.addWidget(self.textFirstOption)
        vbox.addWidget(self.checkPlaneRed)
        vbox.addWidget(self.checkPlaneYellow)
        vbox.addWidget(self.checkPlaneGreen)
        vbox.addStretch(1)
        self.firstOption.setLayout(vbox)
        sampleFormLayout.addWidget(self.firstOption)



        self.secondOption = qt.QGroupBox("Place Landmarks to define planes")
        self.secondOption.setCheckable(True)
        self.secondOption.setChecked(False)
        # self.secondOption.connect('clicked(bool)', self.secondOptionClicked)

        self.textFirstOption = qt.QLabel("Define a plane using 3 landmarks.")


        self.addLandMark = qt.QPushButton("Add LandMarks")
        self.addLandMark.connect('clicked()', self.addLandMarkClicked)
        # self.addLandMark.setDisabled(True)

        self.placePlaneButton = qt.QPushButton("Define and Place Planes")
        # self.addLandMark.connect('clicked()', self.addLandMarkClicked)

        vbox1 = qt.QVBoxLayout()
        vbox1.addWidget(self.textFirstOption)
        vbox1.addWidget(self.addLandMark)
        vbox1.addWidget(self.placePlaneButton)
        vbox1.addStretch(1)
        self.secondOption.setLayout(vbox1)
        sampleFormLayout.addWidget(self.secondOption)


        self.laplaceCollapsibleButton2 = ctk.ctkCollapsibleButton()
        self.laplaceCollapsibleButton2.text = "Results"
        self.layout.addWidget(self.laplaceCollapsibleButton2)
        sampleFormLayout2 = qt.QFormLayout(self.laplaceCollapsibleButton2)


        label_RL = qt.QLabel("R-L View")
        self.getAngle_RL = qt.QLabel()
        # ligne1 = qt.QLabel()

        label_SI = qt.QLabel("S-I View")
        self.getAngle_SI = qt.QLabel()
        # ligne2 = qt.QLabel()

        label_AP = qt.QLabel("A-P View")
        self.getAngle_AP = qt.QLabel()
        # ligne3= qt.QLabel()

        tableResult = qt.QTableWidget(2, 3)
        tableResult.setColumnCount(2)
        # tableResult.setMaximumWidth(460)
        tableResult.setHorizontalHeaderLabels([' View ', 'Values'])
        # tableResult.horizontalHeader().setResizeMode(qt.QHeaderView::Stretch)
        tableResult.setColumnWidth(0, 80)
        tableResult.setColumnWidth(1, 80)

        tableResult.setRowCount(1)
        tableResult.setCellWidget(0, 0, label_RL)
        tableResult.setCellWidget(0, 1, self.getAngle_RL)

        tableResult.setRowCount(2)
        tableResult.setCellWidget(1, 0, label_SI)
        tableResult.setCellWidget(1, 1, self.getAngle_SI)

        tableResult.setRowCount(3)
        tableResult.setCellWidget(2, 0, label_AP)
        tableResult.setCellWidget(2, 1, self.getAngle_AP)

        # Add vertical spacer
        self.layout.addStretch(1)

        sampleFormLayout2.addWidget(tableResult)

        self.getAngleClicked()

        self.redslice.AddObserver(self.redslice.SliceToRASFlag, self.modify)
        self.greenslice.AddObserver(self.greenslice.SliceToRASFlag, self.modify)


    def onComputeBox(self):
        self.onReload("EasyClip")
        #--------------------------- Box around the model --------------------------#
        node = slicer.util.getNode(self.elements.GetName())
        polydata = node.GetPolyData()
        bound = polydata.GetBounds()
        print "bound", bound

        dimX = bound[1]-bound[0]
        dimY = bound[3]-bound[2]
        dimZ = bound[5]-bound[4]

        print "dimension X :", dimX
        print "dimension Y :", dimY
        print "dimension Z :", dimZ

        dimX = dimX + 10
        dimY = dimY + 20
        dimZ = dimZ + 20

        center = polydata.GetCenter()
        print "Center polydata :", center

        # Creation of an Image
        self.image = sitk.Image(int(dimX), int(dimY), int(dimZ), sitk.sitkInt16)

        dir = (-1.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, 1.0)
        self.image.SetDirection(dir)

        spacing = (1,1,1)
        self.image.SetSpacing(spacing)

        tab = [-center[0]+dimX/2,-center[1]+dimY/2,center[2]-dimZ/2]
        print tab
        self.image.SetOrigin(tab)


        writer = sitk.ImageFileWriter()
        tempPath = slicer.app.temporaryPath
        filename = "Box.nrrd"
        filenameFull=os.path.join(tempPath,filename)
        print filenameFull
        writer.SetFileName(str(filenameFull))
        writer.Execute(self.image)


        slicer.util.loadVolume(filenameFull)

        #------------------------ Slice Intersection Visibility ----------------------#
        numDisplayNode = slicer.mrmlScene.GetNumberOfNodesByClass("vtkMRMLModelDisplayNode")
        for i in range (3,numDisplayNode):
            self.slice = slicer.mrmlScene.GetNthNodeByClass(i,"vtkMRMLModelDisplayNode" )
            self.slice.SetSliceIntersectionVisibility(1)

    def firstOptionClicked(self):
        print "First Option chosen"

    def checkPlaneRedClicked(self):
        if self.checkPlaneRed.isChecked():
            self.redslice.SetWidgetVisible(True)
            self.redslice.SetSliceVisible(1)
        else:
            self.redslice.SetWidgetVisible(False)

    def checkPlaneYellowClicked(self):
        if self.checkPlaneYellow.isChecked():
            "print Yellow Plane"
        else:
            "disable yellow plane"

    def checkPlaneGreenClicked(self):
        if self.checkPlaneGreen.isChecked():
            self.greenslice.SetWidgetVisible(True)
            self.greenslice.SetSliceVisible(1)
        else:
            self.greenslice.SetWidgetVisible(False)

    def getAngleClicked(self):

        # Normal vector to the Red slice:
        n_vector = numpy.matrix([[0],[0],[1],[1]])

        # point on the Red slice:
        A = numpy.matrix([[0], [0], [0], [1]])

        #---------------------- RED SLICE -----------------------#

        matRed = self.redslice.GetSliceToRAS()

        # Matrix with the elements of SliceToRAS
        m_Red = numpy.matrix([[matRed.GetElement(0,0), matRed.GetElement(0,1), matRed.GetElement(0,2), matRed.GetElement(0,3)],
                              [matRed.GetElement(1,0), matRed.GetElement(1,1), matRed.GetElement(1,2), matRed.GetElement(1,3)],
                              [matRed.GetElement(2,0), matRed.GetElement(2,1), matRed.GetElement(2,2), matRed.GetElement(2,3)],
                              [matRed.GetElement(3,0), matRed.GetElement(3,1), matRed.GetElement(3,2), matRed.GetElement(3,3)]])
        print m_Red

        #---------------------- GREEN SLICE ----------------------#
        GreenNode = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeGreen')
        matGreen = GreenNode.GetSliceToRAS()


        # Matrix with the elements of SliceToRAS
        m_Green = numpy.matrix([[matGreen.GetElement(0,0), matGreen.GetElement(0,1), matGreen.GetElement(0,2), matGreen.GetElement(0,3)],
                                [matGreen.GetElement(1,0), matGreen.GetElement(1,1), matGreen.GetElement(1,2), matGreen.GetElement(1,3)],
                                [matGreen.GetElement(2,0), matGreen.GetElement(2,1), matGreen.GetElement(2,2), matGreen.GetElement(2,3)],
                                [matGreen.GetElement(3,0), matGreen.GetElement(3,1), matGreen.GetElement(3,2), matGreen.GetElement(3,3)]])
        print m_Green


        n_NewRedPlan = m_Red * n_vector
        print "n : \n", n_NewRedPlan
        A_NewRedPlan = m_Red * A
        print "A : \n", A_NewRedPlan
        n_NewGreenPlan = m_Green * n_vector
        print "n : \n", n_NewGreenPlan
        A_NewGreenPlan = m_Green * A
        print "A : \n", A_NewGreenPlan

        n_NewRedPlan1 = n_NewRedPlan
        n_NewGreenPlan1 = n_NewGreenPlan

        n_NewRedPlan1[0] = n_NewRedPlan[0] - A_NewRedPlan[0]
        n_NewRedPlan1[1] = n_NewRedPlan[1] - A_NewRedPlan[1]
        n_NewRedPlan1[2] = n_NewRedPlan[2] - A_NewRedPlan[2]
        print n_NewRedPlan1

        n_NewGreenPlan1[0] = n_NewGreenPlan[0] - A_NewGreenPlan[0]
        n_NewGreenPlan1[1] = n_NewGreenPlan[1] - A_NewGreenPlan[1]
        n_NewGreenPlan1[2] = n_NewGreenPlan[2] - A_NewGreenPlan[2]
        print n_NewGreenPlan1


        norm_red = sqrt(n_NewRedPlan1[0]*n_NewRedPlan1[0]+n_NewRedPlan1[1]*n_NewRedPlan1[1]+n_NewRedPlan1[2]*n_NewRedPlan1[2])
        print "norme : \n", norm_red
        norm_green =sqrt(n_NewGreenPlan1[0]*n_NewGreenPlan1[0]+n_NewGreenPlan1[1]*n_NewGreenPlan1[1]+n_NewGreenPlan1[2]*n_NewGreenPlan1[2])
        print "norme : \n", norm_green


        scalar_product = (n_NewRedPlan1[0]*n_NewGreenPlan1[0]+n_NewRedPlan1[1]*n_NewGreenPlan1[1]+n_NewRedPlan1[2]*n_NewGreenPlan1[2])
        print "scalar product : \n", scalar_product

        angle = acos(scalar_product/(norm_red*norm_green))
        print "radian angle : ", angle

        self.angle_degre = angle*180/pi
        # self.label1.setText(self.angle_degre)


        norm_red_RL = sqrt(n_NewRedPlan1[1]*n_NewRedPlan1[1]+n_NewRedPlan1[2]*n_NewRedPlan1[2])
        print "norme : \n", norm_red_RL
        norm_green_RL =sqrt(n_NewGreenPlan1[1]*n_NewGreenPlan1[1]+n_NewGreenPlan1[2]*n_NewGreenPlan1[2])
        print "norme : \n", norm_green_RL

        if norm_red_RL ==0 or norm_green_RL ==0 :
            self.angle_degre_RL = 0
        else:
            scalar_product_RL = (n_NewRedPlan1[1]*n_NewGreenPlan1[1]+n_NewRedPlan1[2]*n_NewGreenPlan1[2])
            print "scalar product : \n", scalar_product_RL

            angleRL = acos(scalar_product_RL/(norm_red_RL*norm_green_RL))
            print "radian angle : ", angleRL

            self.angle_degre_RL = angleRL*180/pi
            self.angle_degre_RL = round(self.angle_degre_RL,2)
            print self.angle_degre_RL

        self.getAngle_RL.setText(self.angle_degre_RL)


        norm_red_SI = sqrt(n_NewRedPlan1[0]*n_NewRedPlan1[0]+n_NewRedPlan1[1]*n_NewRedPlan1[1])
        print "norme_red_SI : \n", norm_red_SI
        norm_green_SI =sqrt(n_NewGreenPlan1[0]*n_NewGreenPlan1[0]+n_NewGreenPlan1[1]*n_NewGreenPlan1[1])
        print "norme_green_SI : \n", norm_green_SI

        if norm_red_SI ==0 or norm_green_SI ==0 :
            self.angle_degre_SI = 0
        else:
            scalar_product_SI = (n_NewRedPlan1[0]*n_NewGreenPlan1[0]+n_NewRedPlan1[1]*n_NewGreenPlan1[1])
            print "scalar product_SI : \n", scalar_product_SI

            angleSI = acos(scalar_product_SI/(norm_red_SI*norm_green_SI))
            print "radian angle : ", angleSI

            self.angle_degre_SI = angleSI*180/pi
            self.angle_degre_SI = round(self.angle_degre_SI,2)
            print self.angle_degre_SI

        self.getAngle_SI.setText(self.angle_degre_SI)

        norm_red_AP = sqrt(n_NewRedPlan1[0]*n_NewRedPlan1[0]+n_NewRedPlan1[2]*n_NewRedPlan1[2])
        print "norme_red_SI : \n", norm_red_AP
        norm_green_AP =sqrt(n_NewGreenPlan1[0]*n_NewGreenPlan1[0]+n_NewGreenPlan1[2]*n_NewGreenPlan1[2])
        print "norme_green_SI : \n", norm_green_AP

        if norm_red_AP ==0 or norm_green_AP ==0 :
            self.angle_degre_AP = 0
        else:
            scalar_product_AP = (n_NewRedPlan1[0]*n_NewGreenPlan1[0]+n_NewRedPlan1[2]*n_NewGreenPlan1[2])
            print "scalar product_SI : \n", scalar_product_AP

            angleAP = acos(scalar_product_AP/(norm_red_SI*norm_green_AP))
            print "radian angle : ", angleAP

            self.angle_degre_AP = angleAP*180/pi
            self.angle_degre_AP = round(self.angle_degre_AP,2)
            print self.angle_degre_AP

        self.getAngle_AP.setText(self.angle_degre_AP)

    def modify(self, obj, event):
        self.getAngleClicked()

    def addLandMarkClicked(self):
        print "Add 3 landmarks"
        # Place landmarks in the 3D scene
        landmarks = slicer.mrmlScene.GetNodeByID("vtkMRMLSelectionNodeSingleton")
        landmarks.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsFiducialNode")

        interactionLandmarks = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
        interactionLandmarks.SetCurrentInteractionMode(1)

        # Limit the number of 3 landmarks to define a plane
        # Keep the coordinates of the landmarks
        listCoord = list()
        fidNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode1')
        coord = numpy.zeros(3)
        fidNode.GetNthFiducialPosition(0, coord)
        listCoord.insert(0,coord)
        # fidNode.GetNthFiducialPosition(1, coord)
        # listCoord.insert(0,coord)
        # fidNode.GetNthFiducialPosition(2, coord)
        # listCoord.insert(0,coord)

        print coord
        print listCoord
        # slicer.mrmlScene.AddNode(fidNode)
        # fidNode.SetAndObserveDisplayNodeID(displayNode.GetID())