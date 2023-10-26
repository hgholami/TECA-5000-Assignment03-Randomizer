import maya.cmds as cmds
from random import randint
from random import uniform as randF
from enum import IntEnum
from itertools import product as iterProd

class IND(IntEnum):
    x=0
    y=1
    z=2
    min=0
    max=1
    h=0
    w=1
    d=2

# Global constants
WND_NAME = "advMulti"
WND_TITLE = "Houman's Randomizer"
WND_SIZE_W = 400
UI_SEPARATOR_H = 10
UI_RL_W_OBJSET = [int(WND_SIZE_W*0.35), int(WND_SIZE_W*0.6)]
UI_RL_W_MAINBTN = [int(WND_SIZE_W/3), int(WND_SIZE_W/3), int(WND_SIZE_W/3)]
UI_RL_W_MODESET = [int(WND_SIZE_W*0.35), int(WND_SIZE_W*0.1), int(WND_SIZE_W*0.4), int(WND_SIZE_W*0.2)]
UI_RL_W_XYZ_INPT = [int(WND_SIZE_W*0.35), int(WND_SIZE_W*0.2), int(WND_SIZE_W*0.2), int(WND_SIZE_W*0.2)]
UI_RL_COL_COUNT = 2
UI_DEF_OBJ_NAME = "MyObject"
UI_DEF_GRP_NAME = "MyGroup"
UI_OPT_MENU_CREATE = "optMenuCreate"
UI_OPT_MENU_DUPE = "optMenuDupe"
UI_BTN_REFRESH = "btnRefresh"
UI_NAME_OBJECT_COUNT = "objCount"
UI_NAME_SCALE_COL = "scaleCol"
UI_NAME_ROT_COL = "rotCol"
UI_NAME_RAD_ROW = "radRow"
UI_NAME_HWD_ROW = "hwdRow"
UI_NAME_HEIGHT = "heightField"
UI_NAME_WIDTH = "widthField"
UI_NAME_DEPTH = "depthField"
UI_BTN_GENERATE = "btnGenerate"
UI_BTN_GENCLOSE = "btnGenerateAndClose"
UI_BTN_CANCEL = "btnCancel"
UI_CREATE_MENU_ITEMS = [
    "Cube",
    "Sphere",
    "Cone",
    "Cylinder"
]

# Global variables
objName = UI_DEF_OBJ_NAME
isGrouped = False
groupList = []
groupName = UI_DEF_GRP_NAME
isCreateMode = True
targetObj = UI_CREATE_MENU_ITEMS[0]
objCount = 15
distSpaceMinMax = [[-10,-10,-10], [10, 10, 10]]
hwdAmount = [1, 1, 1]
radAmount = 1.0
scaleMinMax = [[1, 1, 1], [1, 1, 1]]
rotMinMax = [[0, 0, 0], [0, 0, 0]]
genPoints=[]

# Functions
def SetObjName(name:str):
    global objName
    nameStripped = name.strip()
    if nameStripped == "":
        objName = UI_DEF_OBJ_NAME
        return
    objName = nameStripped
    # print(f"Set Object Name to \"{objName}\"")
    
def ToggleGroup(input:bool):
    # print("The objects %s be grouped" %("will" if input else "will not"))
    global isGrouped
    isGrouped = input
    cmds.text("LabelGrpName", e=True, en=isGrouped)
    cmds.textFieldGrp("TextGrpName", e=True, en=isGrouped)

def SetGroupName(name:str):
    global groupName
    nameStripped = name.strip()
    if nameStripped == "":
        groupName = UI_DEF_GRP_NAME
        return
    groupName = nameStripped
    # print(f"Set Group Name to \"{groupName}\"")

def SetRadAndHWDEnable(enRad:bool = False, enHWD:bool = True,
                       enWidth:bool = True, enHDepth:bool = True):
    if cmds.layout(UI_NAME_RAD_ROW, q=True, ex=True):
        cmds.layout(UI_NAME_RAD_ROW, e=True, en=enRad)
    if cmds.layout(UI_NAME_HWD_ROW, q=True, ex=True):
        cmds.layout(UI_NAME_HWD_ROW, e=True, en=enHWD)
        cmds.floatField(UI_NAME_WIDTH, e=True, en=enWidth)
        cmds.floatField(UI_NAME_DEPTH, e=True, en=enHDepth)

def SetTargetObj(input:str):
    global targetObj
    targetObj = input
    # print(targetObj)
    if targetObj == UI_CREATE_MENU_ITEMS[0]: # Cube
        SetRadAndHWDEnable(False, True, True, True)
    elif targetObj == UI_CREATE_MENU_ITEMS[1]: # Sphere
        SetRadAndHWDEnable(True, False, True, True)
    elif targetObj == UI_CREATE_MENU_ITEMS[2]: # Cone
        SetRadAndHWDEnable(True, True, False, False)
    elif targetObj == UI_CREATE_MENU_ITEMS[3]: # Cylinder
        SetRadAndHWDEnable(True, True, False, False)

def ToggleCreateMode(input:bool):
    global isCreateMode
    isCreateMode = input
    cmds.optionMenu(UI_OPT_MENU_CREATE, e=True, en=isCreateMode)
    cmds.optionMenu(UI_OPT_MENU_DUPE, e=True, en=not isCreateMode)
    cmds.button(UI_BTN_REFRESH, e=True, en=not isCreateMode)
    
    cmds.layout(UI_NAME_SCALE_COL, e=True, vis=not isCreateMode)
    cmds.layout(UI_NAME_ROT_COL, e=True, vis=not isCreateMode)
    cmds.layout(UI_NAME_RAD_ROW, e=True, vis=isCreateMode)
    cmds.layout(UI_NAME_HWD_ROW, e=True, vis=isCreateMode)
    UpdateDupeList()
    SetTargetObj(cmds.optionMenu(UI_OPT_MENU_CREATE if isCreateMode else UI_OPT_MENU_DUPE,
                 q=True, v=True))
    cmds.text(UI_NAME_OBJECT_COUNT, e=True, 
              l=("%s Count:" %("Object" if isCreateMode else "Duplicate")))
    SetBtnEnable()
    # print("Create Mode: " + str(isCreateMode))
    # print("Object to Create/Dupe is: " + str(targetObj))

def UpdateDupeList():
    dupeList = cmds.ls(tr=True, v=True)
    # print(dupeList)
    menuItems = cmds.optionMenu(UI_OPT_MENU_DUPE, q=True, itemListLong=True)
    if menuItems:
        cmds.deleteUI(menuItems)
    for item in dupeList:
        cmds.menuItem(l=item, p=UI_OPT_MENU_DUPE)
    SetTargetObj(cmds.optionMenu(UI_OPT_MENU_CREATE if isCreateMode else UI_OPT_MENU_DUPE,
                 q=True, v=True))
    SetBtnEnable()
        

def SetObjCount(count:int):
    global objCount
    objCount = count
    # print("Set objCount to " + str(objCount))

def IsSpaceEnough() -> bool:
    global spotCount
    spotCount = 0
    for x, y, z in iterProd(range(distSpaceMinMax[IND.min][IND.x], distSpaceMinMax[IND.max][IND.x] + 1),
                            range(distSpaceMinMax[IND.min][IND.y], distSpaceMinMax[IND.max][IND.y] + 1), 
                            range(distSpaceMinMax[IND.min][IND.z], distSpaceMinMax[IND.max][IND.z] + 1)):
        spotCount += 1
    return spotCount >= objCount
        

def GenObjs():
    if not IsSpaceEnough():
        cmds.warning("Not enough space for %i objects in %i available spots" %(objCount, spotCount))
        return
    global groupList
    groupList = []
    for i in range (objCount):
        if targetObj == UI_CREATE_MENU_ITEMS[0]:
            cmds.polyCube(n=objName, h=hwdAmount[IND.h], w=hwdAmount[IND.w], d=hwdAmount[IND.d])
        elif targetObj == UI_CREATE_MENU_ITEMS[1]:
            cmds.polySphere(n=objName, r=radAmount)
        elif targetObj == UI_CREATE_MENU_ITEMS[2]:
            cmds.polyCone(n=objName, h=hwdAmount[IND.h], r=radAmount)
        elif targetObj == UI_CREATE_MENU_ITEMS[3]:
            cmds.polyCylinder(n=objName, h=hwdAmount[IND.h], r=radAmount)
        else:
            cmds.warning("GenObj - \"" + str(targetObj) + "\" is not a supported object type!")
            return
        trX = randint(distSpaceMinMax[IND.min][IND.x], distSpaceMinMax[IND.max][IND.x])
        trY = randint(distSpaceMinMax[IND.min][IND.y], distSpaceMinMax[IND.max][IND.y])
        trZ = randint(distSpaceMinMax[IND.min][IND.z], distSpaceMinMax[IND.max][IND.z])
        GeneratedPoint=str(trX)+","+str(trY)+","+str(trZ)
        # print(str(trX)+","+str(trY)+","+str(trZ))
        while GeneratedPoint in genPoints:
            trX = randint(distSpaceMinMax[IND.min][IND.x], distSpaceMinMax[IND.max][IND.x])
            trY = randint(distSpaceMinMax[IND.min][IND.y], distSpaceMinMax[IND.max][IND.y])
            trZ = randint(distSpaceMinMax[IND.min][IND.z], distSpaceMinMax[IND.max][IND.z])
            GeneratedPoint=str(trX)+","+str(trY)+","+str(trZ)
        genPoints.append(GeneratedPoint)
        groupList.extend(cmds.ls(sl=True))
        # print(genPoints)
        cmds.move(trX,trY,trZ)
    # print(groupList)

def DupeObjs():
    if not IsSpaceEnough():
        cmds.warning("Not enough space for %i objects in %i available spots" %(objCount, spotCount))
        return
    global groupList
    groupList = []
    for i in range (objCount):
        dupedObj = cmds.duplicate(targetObj, n=(objName if objName is not UI_DEF_OBJ_NAME else targetObj), un=True)
        trX = randint(distSpaceMinMax[IND.min][IND.x], distSpaceMinMax[IND.max][IND.x])
        trY = randint(distSpaceMinMax[IND.min][IND.y], distSpaceMinMax[IND.max][IND.y])
        trZ = randint(distSpaceMinMax[IND.min][IND.z], distSpaceMinMax[IND.max][IND.z])
        rotX = randint(rotMinMax[IND.min][IND.x], rotMinMax[IND.max][IND.x])
        rotY = randint(rotMinMax[IND.min][IND.y], rotMinMax[IND.max][IND.y])
        rotZ = randint(rotMinMax[IND.min][IND.z], rotMinMax[IND.max][IND.z])
        scX = randF(scaleMinMax[IND.min][IND.x], scaleMinMax[IND.max][IND.x])
        scY = randF(scaleMinMax[IND.min][IND.y], scaleMinMax[IND.max][IND.y])
        scZ = randF(scaleMinMax[IND.min][IND.z], scaleMinMax[IND.max][IND.z])
        GeneratedPoint=str(trX)+","+str(trY)+","+str(trZ)
        # print(str(trX)+","+str(trY)+","+str(trZ))
        while GeneratedPoint in genPoints:
            trX = randint(distSpaceMinMax[IND.min][IND.x], distSpaceMinMax[IND.max][IND.x])
            trY = randint(distSpaceMinMax[IND.min][IND.y], distSpaceMinMax[IND.max][IND.y])
            trZ = randint(distSpaceMinMax[IND.min][IND.z], distSpaceMinMax[IND.max][IND.z])
            GeneratedPoint=str(trX)+","+str(trY)+","+str(trZ)
        genPoints.append(GeneratedPoint)
        cmds.select(targetObj)
        groupList.extend(dupedObj)
        cmds.move(trX,trY,trZ)
        cmds.rotate(rotX,rotY,rotZ)
        cmds.scale(scX, scY, scZ)
    # print(groupList)

def Generate(self):
    if isCreateMode:
        GenObjs()
    else:
        DupeObjs()
    if isGrouped:
        # print(groupList)
        cmds.group(groupList, n=groupName)
    UpdateDupeList()
    global genPoints
    genPoints=[]

def GenerateAndClose(self):
    Generate(self)
    DeleteWindow()

def Cancel(self):
    DeleteWindow()

def SetBtnEnable():
    try:
        cmds.button(UI_BTN_GENERATE, e=True, en=bool(targetObj is not None))
        cmds.button(UI_BTN_GENCLOSE, e=True, en=bool(targetObj is not None))
    except (RuntimeError):
        pass

def DeleteWindow():
    try:
        cmds.deleteUI(WND_NAME, wnd=True)
    except (RuntimeError):
        cmds.warning(("Cannot delete specified UI: ") + WND_NAME)

def CreateWindow():
    # SubscribeToEvents()
    if(cmds.window(WND_NAME, ex=True)):
        DeleteWindow()

    #Declare window control
    global wnd
    wnd = cmds.window(WND_NAME, t=WND_TITLE, s=False, w=WND_SIZE_W, h=540)
    # The root layout
    mainCL = cmds.columnLayout()
    
    # Object Settings
    # Object Name
    # Group Name - Toggle
    cmds.separator(h=UI_SEPARATOR_H)
    cmds.text(l="Object Settings:", fn="boldLabelFont")
    
    cmds.rowLayout(nc=2, cw2=UI_RL_W_OBJSET, 
                   cal=[(1, 'right'), (2, 'left')],
                   cat=[(1, 'right', 0), (2, 'left', 10)])
    cmds.text(l="Object Name:")
    cmds.textFieldGrp(ann=f"Defaults to \"{UI_DEF_OBJ_NAME}\" if blank", cc=SetObjName)
    cmds.setParent(mainCL)
    
    cmds.separator(h=UI_SEPARATOR_H)
    
    tempRL = cmds.rowColumnLayout(nr=2)
    cmds.rowLayout(nc=2, cw2=UI_RL_W_OBJSET, 
                   cal=[(1, 'right'), (2, 'left')],
                   cat=[(1, 'right', 0), (2, 'left', 10)])
    cmds.text(l="Group Objects:")
    cmds.checkBoxGrp(cc=ToggleGroup)
    cmds.setParent(tempRL)
    cmds.rowLayout(nc=2, cw2=UI_RL_W_OBJSET, 
                   cal=[(1, 'right'), (2, 'left')],
                   cat=[(1, 'right', 0), (2, 'left', 10)])
    cmds.text("LabelGrpName", l="Group Name:", en=False)
    cmds.textFieldGrp("TextGrpName", ann=f"Defaults to \"{UI_DEF_GRP_NAME}\" if blank",
                      en=False, cc=SetGroupName)
    cmds.setParent(mainCL)
    
    # Mode Settings
    # Create Mode - Toggle
    # Duplicate Mode - Toggle
    cmds.separator(w=WND_SIZE_W, h=UI_SEPARATOR_H)
    cmds.text(l="Mode Settings:", fn="boldLabelFont")
    
    tempRL = cmds.rowLayout(nc=4, cw4=UI_RL_W_MODESET, 
                   cal=[(1, 'right'), (2, 'left'), (3, 'left'), (4, 'left')],
                   cat=[(1, 'right', 0), (2, 'left', 10), (3, 'left', 0), (4, 'left', -50)])
    cmds.columnLayout(cal='right', cat=('right', 14))
    cmds.text("Create Mode:")
    cmds.separator(h=8, st="none")
    cmds.text("Duplicate Mode:")
    cmds.setParent(tempRL)
    cmds.columnLayout()
    radModeGrp = cmds.radioButtonGrp(sl=1, cc1=ToggleCreateMode)
    cmds.separator(h=5, st="none")
    cmds.radioButtonGrp(scl=radModeGrp)
    cmds.setParent(tempRL)
    cmds.columnLayout()
    cmds.optionMenu(UI_OPT_MENU_CREATE, cc=SetTargetObj)
    for item in UI_CREATE_MENU_ITEMS:
        cmds.menuItem(l=item)
    cmds.optionMenu(UI_OPT_MENU_DUPE, w=88, en=False, cc=SetTargetObj)
    UpdateDupeList()
    cmds.setParent(tempRL)
    cmds.columnLayout(cal='left', cat=('left', 0))
    cmds.text(l="")
    cmds.button(UI_BTN_REFRESH, l="↺ Refresh", c="UpdateDupeList()", en=False,
                ann="Refreshes the list of available objects in Duplication Mode")
    cmds.setParent(mainCL)
    
    # Generation Settings
    # Object Count
    cmds.separator(w=WND_SIZE_W, h=UI_SEPARATOR_H)
    cmds.text(l="Generator Settings:", fn="boldLabelFont")
    
    cmds.rowLayout(nc=2, cw2=UI_RL_W_OBJSET, 
                   cal=[(1, 'right'), (2, 'left')],
                   cat=[(1, 'right', 0), (2, 'left', 10)])
    cmds.text(UI_NAME_OBJECT_COUNT, l="Object Count:")
    cmds.intSliderGrp(f=True, v=objCount, min=1, max=1000,
                                  cc=SetObjCount)
    cmds.setParent(mainCL)
    
    cmds.separator(h=5, st="none")
    
    cmds.rowLayout(UI_NAME_HWD_ROW, nc=4, cw4=UI_RL_W_XYZ_INPT, 
                   cal=[(1, 'right'), (2, 'left'), (2, 'center'), (3, 'center')],
                   cat=[(1, 'right', 0), (2, 'left', 10), (3, 'both', 0), (4, 'both', 0)])
    cmds.text(l="Height/Width/Depth")
    cmds.floatField(UI_NAME_HEIGHT, ann="Height", v=hwdAmount[IND.h], min=-100, max=100,
                    cc="hwdAmount[IND.h] = cmds.floatField(UI_NAME_HEIGHT, q=True, v=True)")
    cmds.floatField(UI_NAME_WIDTH, ann="Width", v=hwdAmount[IND.w], min=-100, max=100,
                    cc="hwdAmount[IND.w] = cmds.floatField(UI_NAME_WIDTH, q=True, v=True)")
    cmds.floatField(UI_NAME_DEPTH, ann="Depth", v=hwdAmount[IND.d], min=-100, max=100,
                    cc="hwdAmount[IND.d] = cmds.floatField(UI_NAME_DEPTH, q=True, v=True)")
    cmds.setParent(mainCL)
    
    cmds.rowLayout(UI_NAME_RAD_ROW, nc=2, cw2=UI_RL_W_OBJSET, 
                   cal=[(1, 'right'), (2, 'left')],
                   cat=[(1, 'right', 0), (2, 'left', 10)],
                   en=False)
    cmds.text(l="Radius:")
    cmds.floatSliderGrp("radFloatSlider", field=True, min=0.1, max=360, v=radAmount, ann="Degrees",
                        cc="radAmount = cmds.floatSliderGrp('radFloatSlider', q=True, v=True)")
    cmds.setParent(mainCL)

    # Randomizer Settings
    # Distribution Space
    # Scale
    # Rotation
    # Height/Width/Depth
    # Radius
    cmds.separator(w=WND_SIZE_W, h=UI_SEPARATOR_H)
    cmds.text(l="Randomizer Settings:", fn="boldLabelFont")
    cmds.separator(h=5, st="none")

    cmds.rowLayout(nc=2, cw2=UI_RL_W_OBJSET, 
                   cal=[(1, 'right'), (2, 'left')],
                   cat=[(1, 'right', 0), (2, 'left', 10)])
    cmds.text(l="Distribution Space:")
    cmds.text(l="Min")
    cmds.setParent(mainCL)
    cmds.rowLayout(nc=4, cw4=UI_RL_W_XYZ_INPT, 
                   cal=[(1, 'right'), (2, 'center'), (2, 'center'), (3, 'center')],
                   cat=[(1, 'right', 0), (2, 'left', 10), (3, 'both', 0), (4, 'both', 0)])
    cmds.text(l="")
    cmds.intField("distMinX", ann="Axis: x", v=distSpaceMinMax[IND.min][IND.x], min=-100, max=100,
                  cc="distSpaceMinMax[IND.min][IND.x] = cmds.intField('distMinX', q=True, v=True)")
    cmds.intField("distMinY", ann="Axis: y", v=distSpaceMinMax[IND.min][IND.y], min=-100, max=100,
                  cc="distSpaceMinMax[IND.min][IND.y] = cmds.intField('distMinY', q=True, v=True)")
    cmds.intField("distMinZ", ann="Axis: z", v=distSpaceMinMax[IND.min][IND.z], min=-100, max=100,
                  cc="distSpaceMinMax[IND.min][IND.z] = cmds.intField('distMinZ', q=True, v=True)")
    cmds.setParent(mainCL)
    cmds.rowLayout(nc=2, cw2=UI_RL_W_OBJSET, 
                   cal=[(1, 'right'), (2, 'left')],
                   cat=[(1, 'right', 0), (2, 'left', 10)])
    cmds.text(l="")
    cmds.text(l="Max")
    cmds.setParent(mainCL)
    cmds.rowLayout(nc=4, cw4=UI_RL_W_XYZ_INPT, 
                   cal=[(1, 'right'), (2, 'center'), (2, 'center'), (3, 'center')],
                   cat=[(1, 'right', 0), (2, 'left', 10), (3, 'both', 0), (4, 'both', 0)])
    cmds.text(l="")
    cmds.intField("distMaxX", ann="Axis: x", v=distSpaceMinMax[IND.max][IND.x], min=-100, max=100,
                  cc="distSpaceMinMax[IND.max][IND.x] = cmds.intField('distMaxX', q=True, v=True)")
    cmds.intField("distMaxY", ann="Axis: y", v=distSpaceMinMax[IND.max][IND.y], min=-100, max=100,
                  cc="distSpaceMinMax[IND.max][IND.y] = cmds.intField('distMaxY', q=True, v=True)")
    cmds.intField("distMaxZ", ann="Axis: z", v=distSpaceMinMax[IND.max][IND.z], min=-100, max=100,
                  cc="distSpaceMinMax[IND.max][IND.z] = cmds.intField('distMaxZ', q=True, v=True)")
    
    cmds.setParent(mainCL)
    cmds.separator(h=5, st="none")
    
    tempCL = cmds.columnLayout(UI_NAME_SCALE_COL, vis=False)
    cmds.rowLayout(nc=2, cw2=UI_RL_W_OBJSET, 
                   cal=[(1, 'right'), (2, 'left')],
                   cat=[(1, 'right', 0), (2, 'left', 10)])
    cmds.text(l="Scale:")
    cmds.text(l="Min")
    cmds.setParent(tempCL)
    cmds.rowLayout(nc=4, cw4=UI_RL_W_XYZ_INPT, 
                   cal=[(1, 'right'), (2, 'center'), (2, 'center'), (3, 'center')],
                   cat=[(1, 'right', 0), (2, 'left', 10), (3, 'both', 0), (4, 'both', 0)])
    cmds.text(l="")
    cmds.floatField("scaleMinX", ann="Axis: x", v=scaleMinMax[IND.min][IND.x], min=0, max=100,
                  cc="scaleMinMax[IND.min][IND.x] = cmds.floatField('scaleMinX', q=True, v=True)")
    cmds.floatField("scaleMinY", ann="Axis: y", v=scaleMinMax[IND.min][IND.y], min=0, max=100,
                  cc="scaleMinMax[IND.min][IND.y] = cmds.floatField('scaleMinY', q=True, v=True)")
    cmds.floatField("scaleMinZ", ann="Axis: z", v=scaleMinMax[IND.min][IND.z], min=0, max=100,
                  cc="scaleMinMax[IND.min][IND.z] = cmds.floatField('scaleMinZ', q=True, v=True)")
    cmds.setParent(tempCL)
    cmds.rowLayout(nc=2, cw2=UI_RL_W_OBJSET, 
                   cal=[(1, 'right'), (2, 'left')],
                   cat=[(1, 'right', 0), (2, 'left', 10)])
    cmds.text(l="")
    cmds.text(l="Max")
    cmds.setParent(tempCL)
    cmds.rowLayout(nc=4, cw4=UI_RL_W_XYZ_INPT, 
                   cal=[(1, 'right'), (2, 'center'), (2, 'center'), (3, 'center')],
                   cat=[(1, 'right', 0), (2, 'left', 10), (3, 'both', 0), (4, 'both', 0)])
    cmds.text(l="")
    cmds.floatField("scaleMaxX", ann="Axis: x", v=scaleMinMax[IND.max][IND.x], min=0, max=100,
                  cc="scaleMinMax[IND.max][IND.x] = cmds.floatField('scaleMaxX', q=True, v=True)")
    cmds.floatField("scaleMaxY", ann="Axis: y", v=scaleMinMax[IND.max][IND.y], min=0, max=100,
                  cc="scaleMinMax[IND.max][IND.y] = cmds.floatField('scaleMaxY', q=True, v=True)")
    cmds.floatField("scaleMaxZ", ann="Axis: z", v=scaleMinMax[IND.max][IND.z], min=0, max=100,
                  cc="scaleMinMax[IND.max][IND.z] = cmds.floatField('scaleMaxZ', q=True, v=True)")
    
    cmds.setParent(mainCL)
    cmds.separator(h=5, st="none")
    
    tempCL = cmds.columnLayout(UI_NAME_ROT_COL, vis=False)
    cmds.rowLayout(nc=2, cw2=UI_RL_W_OBJSET, 
                   cal=[(1, 'right'), (2, 'left')],
                   cat=[(1, 'right', 0), (2, 'left', 10)])
    cmds.text(l="Rotation:")
    cmds.text(l="Min")
    cmds.setParent(tempCL)
    cmds.rowLayout(nc=4, cw4=UI_RL_W_XYZ_INPT, 
                   cal=[(1, 'right'), (2, 'center'), (2, 'center'), (3, 'center')],
                   cat=[(1, 'right', 0), (2, 'left', 10), (3, 'both', 0), (4, 'both', 0)])
    cmds.text(l="")
    cmds.intField("rotMinX", ann="Axis: x", v=rotMinMax[IND.min][IND.x], min=0, max=360,
                  cc="rotMinMax[IND.min][IND.x] = cmds.intField('rotMinX', q=True, v=True)")
    cmds.intField("rotMinY", ann="Axis: y", v=rotMinMax[IND.min][IND.y], min=0, max=360,
                  cc="rotMinMax[IND.min][IND.y] = cmds.intField('rotMinY', q=True, v=True)")
    cmds.intField("rotMinZ", ann="Axis: z", v=rotMinMax[IND.min][IND.z], min=0, max=360,
                  cc="rotMinMax[IND.min][IND.z] = cmds.intField('rotMinZ', q=True, v=True)")
    cmds.setParent(tempCL)
    cmds.rowLayout(nc=2, cw2=UI_RL_W_OBJSET, 
                   cal=[(1, 'right'), (2, 'left')],
                   cat=[(1, 'right', 0), (2, 'left', 10)])
    cmds.text(l="")
    cmds.text(l="Max")
    cmds.setParent(tempCL)
    cmds.rowLayout(nc=4, cw4=UI_RL_W_XYZ_INPT, 
                   cal=[(1, 'right'), (2, 'center'), (2, 'center'), (3, 'center')],
                   cat=[(1, 'right', 0), (2, 'left', 10), (3, 'both', 0), (4, 'both', 0)])
    cmds.text(l="")
    cmds.intField("rotMaxX", ann="Axis: x", v=rotMinMax[IND.max][IND.x], min=0, max=360,
                  cc="rotMinMax[IND.max][IND.x] = cmds.intField('rotMaxX', q=True, v=True)")
    cmds.intField("rotMaxY", ann="Axis: y", v=rotMinMax[IND.max][IND.y], min=0, max=360,
                  cc="rotMinMax[IND.max][IND.y] = cmds.intField('rotMaxY', q=True, v=True)")
    cmds.intField("rotMaxZ", ann="Axis: z", v=rotMinMax[IND.max][IND.z], min=0, max=360,
                  cc="rotMinMax[IND.max][IND.z] = cmds.intField('rotMaxZ', q=True, v=True)")
    
    cmds.setParent(mainCL)
    
    # Main Buttons
    # Generate - Generates based on above info
    # Generate & Close - Generates then closes window
    # Cancel - Closes window without generating
    cmds.separator(w=WND_SIZE_W, h=UI_SEPARATOR_H*2)
    cmds.rowLayout(w=WND_SIZE_W, nc=3, cw3=UI_RL_W_MAINBTN,
                   cal=[(1, 'right'), (2, 'center'), (3, 'left')],
                   cat=[(1, 'right', 0), (2, 'both', 10), (3, 'left', 0)])
    cmds.button(UI_BTN_GENERATE, l="Generate", c=Generate)
    cmds.button(UI_BTN_GENCLOSE, l="Generate && Close", c=GenerateAndClose)
    cmds.button(UI_BTN_CANCEL, l="Cancel", c=Cancel)
    cmds.setParent(mainCL)
    
    cmds.separator(w=WND_SIZE_W, h=UI_SEPARATOR_H, st="none")
    cmds.showWindow()
    
# Run Program
CreateWindow()