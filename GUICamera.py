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
        changeCamera()  # Call the changeCamera function
    elif button == "Change Driver":
        changeDriver()
    elif button == "Change Position":
        changePosition()
    elif button == "Change Team":
        changeTeam()

def changeCamera(): # Change active camera, driver remains the same
    CamCarIdx = ir['CamCarIdx']
    activeNumber = ir['DriverInfo']['Drivers'][CamCarIdx]['CarNumberRaw']
    camera_list = []    # Array of TV cameras
    for i in range(0, len(ir['CameraInfo']['Groups'])):
        camera_list.append(ir['CameraInfo']['Groups'][i]['GroupName'])
    choice = app.getOptionBox("Change Camera") # Pulls choice from the "Change Camera" menu
    newCamera = camera_list.index(choice)+1
    #print("ir.cam_switch_num(",activeNumber,",",newCamera,",0)")   #Debug
    ir.cam_switch_num(activeNumber, newCamera, 1)
    app.setLabel("lbl-actCam", choice)  # Updates Active TV camera label

def changeDriver(): # Change active driver, camera remains the same
    groupNum = ir['CamGroupNumber']
    activeSession = ir['SessionNum']
    drivers_raw = ir['DriverInfo']['Drivers']
    drivers_list = {}
    for i in range(0, len(drivers_raw)):
        if (drivers_raw[i]['IsSpectator'] == 0):
            drivers_list[ "#"+drivers_raw[i]['CarNumber'] +": "+ drivers_raw[i]['UserName']] = drivers_raw[i]['CarNumber']  # Example: {'#1: foo':1, '#2: bar':2, '#3: foobar':3}
            #drivers_list[drivers_raw[i]['UserName']] = drivers_raw[i]['CarNumber']  # Example: {'foo':1, 'bar':2, 'foobar':3}
    choice = app.getOptionBox("Change Driver") # Pulls choice from the "Change Driver" menu
    for name, number in drivers_list.items():  # for name, number in drivers_list
        if name == choice:
            newDriver = number
    #print("ir.cam_switch_num(",newDriver,",",groupNum,", 0)")   #Debug
    ir.cam_switch_num(newDriver, groupNum, 1)
    time.sleep(0.1)
    CamCarIdx = ir['CamCarIdx']
    activeNumber = ir['DriverInfo']['Drivers'][CamCarIdx]['CarNumberRaw']
    set_position_label(activeSession)   # Sets Active position label, depending on session
    app.setLabel("lbl-actDrv", choice)  # Updates Active driver camera label

def changePosition(): # Change active position
    groupNum = ir['CamGroupNumber']
    activeSession = ir['SessionNum']
    choice  = app.getOptionBox("Change Position") # Pulls choice from the "Change Position" menu
    newCamera = int(groupNum)
    newPosition = int(choice)
    #print("ir.cam_switch_pos(",newPosition,",",newCamera,",0)")   #Debug
    ir.cam_switch_pos(newPosition,newCamera,0)
    time.sleep(0.1)
    CamCarIdx = ir['CamCarIdx']
    activeDriver = ir['DriverInfo']['Drivers'][CamCarIdx]['UserName']
    activeNumber = ir['DriverInfo']['Drivers'][CamCarIdx]['CarNumberRaw']
    app.setLabel("lbl-actDrv", "#"+str(activeNumber) +": "+activeDriver)    # Updates Active driver camera label
    app.setLabel("lbl-actPos", choice)                                      # Updates Position camera label
    if (ir['DriverInfo']['Drivers'][1]['TeamID'] != 0):	#If TeamID of the 1st place car is not 0, then this is a team race.
        activeTeam   = ir['DriverInfo']['Drivers'][CamCarIdx]['TeamName']
        app.setLabel("lbl-actTeam", "#"+str(activeNumber) +": "+activeTeam)         # Updates Team camera label

def changeTeam(): # Change active team (WORK IN PROGRESS)
    groupNum = ir['CamGroupNumber']
    activeSession = ir['SessionNum']
    activeCam = ir['CamGroupNumber']-1
    team_raw = ir['DriverInfo']['Drivers']
    team_list = {}
    for i in range(0, len(team_raw)):
        if (team_raw[i]['IsSpectator'] == 0):
            team_list["#"+team_raw[i]['CarNumber'] +": "+ team_raw[i]['TeamName']] = team_raw[i]['CarNumberRaw']
            #team_list[team_raw[i]['TeamName']] = team_raw[i]['CarNumberRaw']
    choice = app.getOptionBox("Change Team") # Pulls choice from the "Change Position" menu
    for name, number in team_list.items():  # for name, number in drivers_list
        if name == choice:
            changeTeam = number
    #print("ir.cam_switch_num(",changeTeam,",",groupNum,", 0)")  #Debug
    ir.cam_switch_num(changeTeam, groupNum, 1)
    time.sleep(0.1)
    CamCarIdx = ir['CamCarIdx']
    activeDriver = ir['DriverInfo']['Drivers'][CamCarIdx]['UserName']
    activeNumber = ir['DriverInfo']['Drivers'][CamCarIdx]['CarNumberRaw']
    set_position_label(activeSession)           # Sets Active position label, depending on session
    app.setLabel("lbl-actDrv", "#"+str(activeNumber) +": "+activeDriver)    # Updates Active driver camera label
    app.setLabel("lbl-actTeam", choice)         # Updates Team camera label

def set_position_label(activeSession):
    CamCarIdx = ir['CamCarIdx']
    CarIdx = ir['DriverInfo']['Drivers'][CamCarIdx]['CarIdx']
    if (ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'] == None):
        app.setLabel("lbl-actPos", ["- No Positions At This Time -"])  # Updates Position camera label
    else:
        for i in range(0, len(ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'])):
            if(ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'][i]['CarIdx'] == CarIdx):
                position = ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'][i]['Position']
        app.setLabel("lbl-actPos", position)  # Updates Position camera label

def first_load_list():
    # Change Camera: Angle
    camera_list = []    # Array of TV cameras
    for i in range(0, len(ir['CameraInfo']['Groups'])):
        camera_list.append(ir['CameraInfo']['Groups'][i]['GroupName'])
    # Change Camera: Driver
    drivers_raw = ir['DriverInfo']['Drivers']
    drivers_list = []
    gui_menu_list = []  #
    for i in range(0, len(drivers_raw)):
        if (drivers_raw[1]['TeamID'] != 0 and drivers_raw[i]['IsSpectator'] == 0):
            drivers_list.append(drivers_raw[i]['UserName'])
            gui_menu_list.append("#"+drivers_raw[i]['CarNumber'] +": "+ drivers_raw[i]['TeamName'])   # Example: {'foo':1, 'bar':2, 'foobar':3}
        elif (drivers_raw[i]['IsSpectator'] == 0):
            gui_menu_list.append("#"+drivers_raw[i]['CarNumber'] +": "+ drivers_raw[i]['UserName'])   # Example: {'foo':1, 'bar':2, 'foobar':3}
    # Change Camera: Position
    activeSession = ir['SessionNum']
    position_list = []
    if (ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'] == None):
        position_list.append("- No Positions At This Time -")
    else:
        for i in range(0, len(ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'])):
            position_list.append(ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'][i]['Position'])
    # Change Camera: Team
    team_list = []
    if (ir['DriverInfo']['Drivers'][1]['TeamID'] != 0):	#If TeamID of the 1st place car is not 0, then this is a team race.
        for i in range(1, len(ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'])):
            team_list.append(ir['DriverInfo']['Drivers'][i]['TeamName'])
    return camera_list,drivers_list,gui_menu_list,position_list,team_list

camera_list,drivers_list,gui_menu_list,position_list,team_list = first_load_list() # Get the initial first-load variables

app = gui("Camera Director")    #Window name
app.setBg("white")              #Window color
app.setFont(18)                 #Font size

app.addLabel("lbl-actCamText", "Active TV Camera",0,0,0)  # Active TV camera
app.addLabel("lbl-actCam", ir['CameraInfo']['Groups'][activeCam]['GroupName'],0,1,0)  # Active TV camera

app.addLabel("lbl-actDrvText", "Active Driver",1,0,0)  # Active Driver
app.addLabel("lbl-actDrv", "#"+str(activeNumber) +": "+ir['DriverInfo']['Drivers'][CamCarIdx]['UserName'],1,1,0)  # Active Driver

app.addLabel("lbl-actPosText", "Position",2,0,0)  # Active Position
if (ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'] == None):
    app.addLabel("lbl-actPos", ["- No Positions At This Time -"],2,1,0)  # Active Position
else:
    app.addLabel("lbl-actPos", ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'][CamCarIdx]['Position'],2,1,0)  # Active Position

if (ir['DriverInfo']['Drivers'][1]['TeamID'] != 0):	#If TeamID of the 1st place car is not 0, then this is a team race.
    app.addLabel("lbl-actTeamText", "Team",3,0,0)  # Active Team
    app.addLabel("lbl-actTeam", "#"+str(activeNumber) +": "+activeTeam,3,1,0)  # Active Team

app.addLabelOptionBox("Change Camera", camera_list,4,0,0) # Drop-down menu, array from 'camera_list'
app.addButton("Change Camera", button,4,1,0)

if (ir['DriverInfo']['Drivers'][1]['TeamID'] != 0):	#If TeamID of the 1st place car is not 0, then this is a team race.
    app.addLabelOptionBox("Change Team", gui_menu_list,5,0,0) # Drop-down menu, array from 'position_list'
#    app.addLabelOptionBox("Change Team", team_list,5,0,0) # Drop-down menu, array from 'position_list'
    app.addButton("Change Team", button,5,1,0)
else:
    app.addLabelOptionBox("Change Team", gui_menu_list,5,0,0) # Drop-down menu, array from 'position_list'
#    app.addLabelOptionBox("Change Driver", drivers_list,5,0,0) # Drop-down menu, array from 'drivers_list'
    app.addButton("Change Driver", button,5,1,0)

app.addLabelOptionBox("Change Position", position_list,6,0,0) # Drop-down menu, array from 'position_list'
app.addButton("Change Position", button,6,1,0)

app.go()
