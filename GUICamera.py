import time
import irsdk
from appJar import gui

ir = irsdk.IRSDK()
try:
    ir.startup()
    # LOCAL DEBUG
    #ir.startup(test_file='Scripts\LoneQualData.bin')
    #ir.startup(test_file='Scripts\RaceData.bin')
    #if (ir.startup(test_file='Scripts\RaceData.bin')) == False:
    while not ir.startup(): # This can occur if the sim is not running or fully loaded
        print('iRacing is not running or not fully loaded, sleeping 30 seconds. . . ')
        time.sleep(30)
    else:
        activeSession = ir['SessionNum']
        # Active Driver
        CamCarIdx = ir['CamCarIdx']
        activeDriver = ir['DriverInfo']['Drivers'][CamCarIdx]['UserName']
        activeNumber = ir['DriverInfo']['Drivers'][CamCarIdx]['CarNumberRaw']
        activeTeam   = ir['DriverInfo']['Drivers'][CamCarIdx]['TeamName']
        # Active Camera
        groupNum = ir['CamGroupNumber']
        activeCam = ir['CamGroupNumber']-1
except KeyboardInterrupt:
    print('Ending Program\n')
    quit()

def button(button):
    if button == "Change Camera":
        CamCarIdx = ir['CamCarIdx']
        activeNumber = ir['DriverInfo']['Drivers'][CamCarIdx]['CarNumberRaw']
        camera_list = []    # Array of TV cameras
        for i in range(0, len(ir['CameraInfo']['Groups'])):
            camera_list.append(ir['CameraInfo']['Groups'][i]['GroupName'])
        changeCamera(activeNumber,camera_list)  # Call the changeCamera function
    elif button == "Change Driver":
        groupNum = ir['CamGroupNumber']
        drivers_raw = ir['DriverInfo']['Drivers']
        drivers_list = {}
        for i in range(0, len(drivers_raw)):
            if (drivers_raw[i]['IsSpectator'] == 0):
                drivers_list[drivers_raw[i]['UserName']] = drivers_raw[i]['CarNumber']
        changeDriver(groupNum,drivers_list)
    elif button == "Change Position":
        groupNum = ir['CamGroupNumber']
        activeSession = ir['SessionNum']
        position_list = []
        for i in range(0, len(ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'])):
            position_list.append(ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'][i]['Position'])
        changePosition(groupNum,activeSession,position_list)

def changeCamera(activeNumber,camera_list): #Change active camera, driver remains the same
    choice  = app.getOptionBox("Change Camera") # Pulls choice from the "Change Camera" menu
    newCamera = camera_list.index(choice)+1
    #print("ir.cam_switch_num(",activeNumber,",",newCamera,",0)")   #Debug
    ir.cam_switch_num(activeNumber, newCamera, 1)
    app.setLabel("lbl-actCam", choice)  # Updates Active TV camera label

def changeDriver(groupNum,drivers_list): #Change active driver, camera remains the same
    choice  = app.getOptionBox("Change Driver") # Pulls choice from the "Change Driver" menu
    for name, number in drivers_list.items():  # for name, number in drivers_list
        if name == choice:
            newDriver = number
    #print("ir.cam_switch_num(",newDriver,",",groupNum,", 0)")   #Debug
    ir.cam_switch_num(newDriver, groupNum, 1)
    time.sleep(0.1)
    activeSession = ir['SessionNum']
    CamCarIdx = ir['CamCarIdx']
    CarIdx = ir['DriverInfo']['Drivers'][CamCarIdx]['CarIdx']
    if (ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'] == None):
        app.setLabel("lbl-actPos", ["- No Positions At This Time -"])  # Updates Position camera label
    else:
        for i in range(0, len(ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'])):
            if(ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'][i]['CarIdx'] == CarIdx):
                position = ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'][i]['Position']
                app.setLabel("lbl-actPos", position)  # Updates Position camera label
    app.setLabel("lbl-actDrv", choice)  # Updates Active driver camera label

def changePosition(groupNum,activeSession,position_list): #Change active position
    choice  = app.getOptionBox("Change Position") # Pulls choice from the "Change Position" menu
    newCamera = int(groupNum)
    newPosition = int(choice)
    #print("ir.cam_switch_pos(",newPosition,",",newCamera,",0)")   #Debug
    ir.cam_switch_pos(newPosition,newCamera,0)
    time.sleep(0.1)
    CamCarIdx = ir['CamCarIdx']
    activeDriver = ir['DriverInfo']['Drivers'][CamCarIdx]['UserName']
    app.setLabel("lbl-actDrv", activeDriver)    # Updates Active driver camera label
    app.setLabel("lbl-actPos", choice)          # Updates Position camera label

def camera_driver_position_list():
    # Change Camera: Angle
    camera_list = []    # Array of TV cameras
    for i in range(0, len(ir['CameraInfo']['Groups'])):
        camera_list.append(ir['CameraInfo']['Groups'][i]['GroupName'])
    # Change Camera: Driver
    drivers_raw = ir['DriverInfo']['Drivers']
    drivers_list = []
    for i in range(0, len(drivers_raw)):
        if (drivers_raw[i]['IsSpectator'] == 0):
            drivers_list.append(drivers_raw[i]['UserName'])
    # Change Camera: Position
    activeSession = ir['SessionNum']
    position_list = []
    for i in range(0, len(ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'])):
        position_list.append(ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'][i]['Position'])
    return camera_list,drivers_list,position_list

camera_list,drivers_list,position_list = camera_driver_position_list() # Get the initial first-load variables

app = gui("Camera Director")    #Window name
app.setBg("white")              #Window color
app.setFont(18)                 #Font size

app.addLabel("lbl-actCamText", "Active TV Camera",0,0,0)  # Active TV camera
app.addLabel("lbl-actCam", ir['CameraInfo']['Groups'][activeCam]['GroupName'],0,1,0)  # Active TV camera

app.addLabel("lbl-actDrvText", "Active Driver",1,0,0)  # Active Driver
app.addLabel("lbl-actDrv", ir['DriverInfo']['Drivers'][CamCarIdx]['UserName'],1,1,0)  # Active Driver

app.addLabel("lbl-actPosText", "Position",2,0,0)  # Active Position
app.addLabel("lbl-actPos", ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'][CamCarIdx]['Position'],2,1,0)  # Active Position

app.addLabelOptionBox("Change Camera", camera_list,3,0,0) # Drop-down menu, array from 'camera_list'
app.addButton("Change Camera", button,3,1,0)

app.addLabelOptionBox("Change Driver", drivers_list,4,0,0) # Drop-down menu, array from 'drivers_list'
app.addButton("Change Driver", button,4,1,0)

app.addLabelOptionBox("Change Position", position_list,5,0,0) # Drop-down menu, array from 'position_list'
app.addButton("Change Position", button,5,1,0)

app.go()
