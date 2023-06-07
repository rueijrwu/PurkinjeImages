import clr, os, winreg
aKey = winreg.OpenKey(winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER), r"Software\Zemax", 0, winreg.KEY_READ)
zemaxData = winreg.QueryValueEx(aKey, 'ZemaxRoot')
NetHelper = os.path.join(os.sep, zemaxData[0], r'ZOS-API\Libraries\ZOSAPI_NetHelper.dll')
winreg.CloseKey(aKey)
clr.AddReference(NetHelper)
import ZOSAPI_NetHelper
del aKey, zemaxData, NetHelper

ZOSAPI_NetHelper.ZOSAPI_Initializer.Initialize()
dir = ZOSAPI_NetHelper.ZOSAPI_Initializer.GetZemaxDirectory()
clr.AddReference(os.path.join(os.sep, dir, "ZOSAPI.dll"))
clr.AddReference(os.path.join(os.sep, dir, "ZOSAPI_Interfaces.dll"))
del dir
import ZOSAPI

from System import Enum, Int32, Double
import numpy as np
from matplotlib import pyplot as plt


class PurkinjeModel:
    TheConnection = None
    TheApplication = None
    TheSystem = None

    def __init__(self, filepath, rotationSurf):
        if PurkinjeModel.TheConnection is None:
            PurkinjeModel.OpenSystem()
        
        #self.TheApplication = PurkinjeModel.TheConnection.CreateNewApplication()
        self.TheSystem = PurkinjeModel.TheApplication.CreateNewSystem(ZOSAPI.SystemType.Sequential)
        if self.TheSystem is None:
            print("Unable to acquire Primary system")
            self.TheApplication.CloseApplication()
            self.TheApplication = None
            return

        self.isFileOpen = self.TheSystem.LoadFile(os.path.abspath(filepath), False)
        if not self.isFileOpen:
            return

        self.nSurfs = self.TheSystem.LDE.NumberOfSurfaces
        self.rotationSurf = self.TheSystem.LDE.GetSurfaceAt(rotationSurf)
        self.field = self.TheSystem.SystemData.Fields.GetField(1)

    def setMaxField(self, MAX_SOURCE_ANGLE, set_viggenetting=False):
        #MAX_FIELD = 100 * np.tan(np.deg2rad(MAX_SOURCE_ANGLE))
        self.field.Y = MAX_SOURCE_ANGLE
        if set_viggenetting:
            self.TheSystem.SystemData.Fields.SetVignetting() 
        self.max_source_angle = MAX_SOURCE_ANGLE

    def setSurfRadius(self, surf, thickness):
        if surf < 0:
            return
        if surf >= self.nSurfs:
            return
        surf = self.TheSystem.LDE.GetSurfaceAt(surf)
        surf.set_Radius(thickness)

    def setSurfThickness(self, surf, thickness):
        if surf < 0:
            return
        if surf >= self.nSurfs:
            return
        surf = self.TheSystem.LDE.GetSurfaceAt(surf)
        surf.set_Thickness(thickness)

    def setSurfConics(self, surf, conics):
        if surf < 0:
            return
        if surf >= self.nSurfs:
            return
        surf = self.TheSystem.LDE.GetSurfaceAt(surf)
        surf.set_Conic(conics)

    def getSurfRadius(self, surf):
        if surf < 0:
            return
        if surf >= self.nSurfs:
            return
        surf = self.TheSystem.LDE.GetSurfaceAt(surf)
        return surf.get_Radius()

    def getSurfThickness(self, surf):
        if surf < 0:
            return
        if surf >= self.nSurfs:
            return
        surf = self.TheSystem.LDE.GetSurfaceAt(surf)
        return surf.get_Thickness()

    def getSurfConics(self, surf):
        if surf < 0:
            return
        if surf >= self.nSurfs:
            return
        surf = self.TheSystem.LDE.GetSurfaceAt(surf)
        return surf.get_Conic()

    def setEyeRotationY(self, rotation, set_viggenetting=False):
        self.rotationSurf.GetCellAt(15).set_DoubleValue(rotation)
        if set_viggenetting:
            self.TheSystem.SystemData.Fields.SetVignetting() 
        self.eyeRotationY = rotation

    def getEyeRotationY(self):
        return self.eyeRotationY

    def setEyeRotationX(self, rotation, set_viggenetting=False):
        self.rotationSurf.GetCellAt(14).set_DoubleValue(rotation)
        if set_viggenetting:
            self.TheSystem.SystemData.Fields.SetVignetting() 
        self.eyeRotationX = rotation

    def getEyeRotationX(self):
        return self.eyeRotationX

    @staticmethod
    def OpenSystem():
        if PurkinjeModel.TheConnection is None:
            PurkinjeModel.TheConnection = ZOSAPI.ZOSAPI_Connection()
            PurkinjeModel.TheApplication = PurkinjeModel.TheConnection.CreateNewApplication()
            #PurkinjeModel.rayTracer = PurkinjeModel.zos.TheSystem.Tools.OpenBatchRayTrace()

    @staticmethod
    def CloseSystem():
        if PurkinjeModel.TheConnection is None:
            PurkinjeModel.TheApplication.CloseApplication()


    def trace(self, source_angle, surfaces=None, set_viggenetting=True):
        if not self.isFileOpen:
            return

        self.setMaxField(source_angle, set_viggenetting=set_viggenetting)
        
        if surfaces is None:
            surfaces = range(self.nSurfs)
        else:
            surfaces = np.array(surfaces, dtype=np.int32)

        rays = np.zeros([surfaces.size, 3, 6], dtype=np.double)

        MFE = self.TheSystem.MFE
        for sIdx, surf in enumerate(surfaces):
            for oIdx in range(1, 19):
                # set surface
                surfaceCell = MFE.GetOperandAt(oIdx).GetCellAt(2)
                surfaceCell.set_IntegerValue(int(surf))
            
            # calculate ray
            MFE.CalculateMeritFunction()

            # read data
            for oIdx in range(0, 18):
                val = MFE.GetOperandAt(oIdx+1).get_Value()
                if val >= 9.9999e9:
                    val = np.inf
                elif val <= -9.9999e9:
                    val = -np.inf
                rays[sIdx, int(oIdx / 6), oIdx % 6] = val
        return rays