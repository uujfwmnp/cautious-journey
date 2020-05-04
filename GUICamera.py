import time
import irsdk
from appJar import gui

ir = irsdk.IRSDK()
try:
    ir.startup()
    # LOCAL DEBUG
    #ir.startup(test_file='Scripts\RaceData.bin')
    while not ir.startup(): # This can occur if the sim is not running or fully loaded
        print('iRacing is not running or not fully loaded, sleeping 30 seconds. . . ')
        time.sleep(30)
    else:   # Setup initial variables and lists
        # Active Session
        activeSession = ir['SessionNum']
        # Active Driver
        CamCarIdx = ir['CamCarIdx']
        activeDriver = ir['DriverInfo']['Drivers'][CamCarIdx]['UserName']
        activeNumber = ir['DriverInfo']['Drivers'][CamCarIdx]['CarNumberRaw']
        activeTeam   = ir['DriverInfo']['Drivers'][CamCarIdx]['TeamName']
        # Active Camera
        groupNum = ir['CamGroupNumber']
        activeCam = ir['CamGroupNumber']-1
        # Change Camera: Angle
        camera_list = []    # Array of TV cameras
        for i in range(0, len(ir['CameraInfo']['Groups'])):
            camera_list.append("Cam: "+ir['CameraInfo']['Groups'][i]['GroupName'])
        # Change Camera: Driver / Team
        drivers_raw = ir['DriverInfo']['Drivers']
        if (ir['WeekendInfo']['TeamRacing'] == 1): # If TeamRacing is 1, then this is a team race.
            team_race = True
        else:
            team_race = False
        drivers_list = {}
        team_list = {}
        for i in range(0, len(drivers_raw)):
            if (team_race == True and drivers_raw[i]['IsSpectator'] == 0):
                drivers_list["#"+drivers_raw[i]['CarNumber'] +": "+ drivers_raw[i]['UserName']] = drivers_raw[i]['CarNumberRaw']
                team_list["#"+drivers_raw[i]['CarNumber'] +": "+ drivers_raw[i]['TeamName']] = drivers_raw[i]['CarNumberRaw']
            elif (drivers_raw[i]['IsSpectator'] == 0):
                drivers_list["#"+drivers_raw[i]['CarNumber'] +": "+ drivers_raw[i]['UserName']] = drivers_raw[i]['CarNumberRaw']
                team_list = None
        # Change Camera: Position
        position_list = []
        while ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'] == None:
            position_list.append("None")
        else:
            for i in range(0, len(ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'])):
                position_list.append(ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'][i]['Position'])

except KeyboardInterrupt:
    print('Ending Program\n')
    quit()

def button(button):
    if button.startswith('Cam:'):
        changeCamera(button,camera_list)  # Call the changeCamera function
    elif button.startswith('#'):
       changeDriver(button,groupNum,activeSession)
    else:
        changePosition(groupNum,activeSession)

def changeCamera(button,camera_list): # Change active camera, driver remains the same
    choice = button # Pulls choice from the "Change Camera" menu
    CamCarIdx = ir['CamCarIdx']         # Need to reset this variable to get the new team name and car number
    activeNumber = ir['DriverInfo']['Drivers'][CamCarIdx]['CarNumberRaw']
    newCamera = camera_list.index(choice)+1
    print("ir.cam_switch_num(",activeNumber,",",newCamera,",0)")   #Debug
    ir.cam_switch_num(activeNumber, newCamera, 1)
    app.setLabel("lbl-actCam", choice)  # Updates Active TV camera label

def changeDriver(button,groupNum,activeSession): # Change active driver, camera remains the same
    global team_list
    global driver_list
    global drivers_raw
    print(button)
    choice = button # Pulls choice from the "Change Driver" menu
    if (team_race == True):
        for name, number in team_list.items():  # for name, number in team_list
            if name == choice:
                changeTeam = number
        print("ir.cam_switch_num(",changeTeam,",",groupNum,", 0)")  #Debug
        ir.cam_switch_num(changeTeam, groupNum, 1)
        app.setLabel("lbl-actTeam", choice)         # Updates Team camera label
    else:
        for name, number in drivers_list.items():  # for name, number in drivers_list
            if name == choice:
                newDriver = number
        #print("ir.cam_switch_num(",newDriver,",",groupNum,", 0)")   #Debug
        ir.cam_switch_num(newDriver, groupNum, 1)
    time.sleep(1)
    CamCarIdx = ir['CamCarIdx']         # Need to reset this variable to get the new team name and car number
    activeDriver = drivers_raw[CamCarIdx]['UserName']
    activeNumber = drivers_raw[CamCarIdx]['CarNumberRaw']
    set_position_label(CamCarIdx,activeSession)           # Sets Active position label, depending on session
    app.setLabel("lbl-actDrv", "#"+str(activeNumber) +": "+activeDriver)    # Updates Active driver camera label

def changePosition(groupNum,activeSession): # Change active position
    global drivers_raw
    choice  = app.getOptionBox("Change Position") # Pulls choice from the "Change Position" menu
    newCamera = int(groupNum)
    newPosition = int(choice)
    print("ir.cam_switch_pos(",newPosition,",",newCamera,",0)")   #Debug
    ir.cam_switch_pos(newPosition,newCamera,0)
    time.sleep(0.1)
    CamCarIdx = ir['CamCarIdx']         # Need to reset this variable to get the new driver name and car number
    activeDriver = drivers_raw[CamCarIdx]['UserName']
    activeNumber = drivers_raw[CamCarIdx]['CarNumberRaw']
    app.setLabel("lbl-actDrv", "#"+str(activeNumber) +": "+activeDriver)    # Updates Active driver camera label
    app.setLabel("lbl-actPos", choice)                                      # Updates Position camera label
    if (team_race == True):	#If TeamID of the 1st place car is not 0, then this is a team race.
        activeTeam   = drivers_raw[CamCarIdx]['TeamName']
        app.setLabel("lbl-actTeam", "#"+str(activeNumber) +": "+activeTeam)         # Updates Team camera label

def set_position_label(CamCarIdx,activeSession):
    global drivers_raw
    global position_list
    CarIdx = drivers_raw[CamCarIdx]['CarIdx']
    if (position_list != "None"):
        for i in range(0, len(ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'])):
            if(ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'][i]['CarIdx'] == CarIdx):
                position = ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'][i]['Position']
        app.setLabel("lbl-actPos", position)  # Updates Position camera label

app = gui("Camera Director")    #Window name
app.setStretch("both")
app.setSticky("nesw")
app.setFont(10)

# Change Team/Driver
app.addLabel("lbl-changeDriverText", "Change Driver",0,0,3)
app.setLabelBg("lbl-changeDriverText", "green")
row = 1
column = 0
if (team_race == True):
    for name, number in team_list.items():
        app.addButton(name, button,row,column)  #print(str(row)+" "+str(column))
        if(column == 2):    # This is actually the 3rd column in the GUI
            row += 1
            column = 0
        else:
            column += 1
else:
    for name, number in drivers_list.items():  # for name, number in drivers_list
        app.addButton(name, button,row,column)  #print(str(row)+" "+str(column))
        if(column == 2):    # This is actually the 3rd column in the GUI
            row += 1
            column = 0
        else:
            column += 1

# Change TV camera
app.addLabel("lbl-changeCamText", "Change TV Camera",20,0,3)
app.setLabelBg("lbl-changeCamText", "green")
row = 21
column = 0
for camera in camera_list:
    app.addButton(camera, button,row,column)    #print(str(row)+" "+str(column))
    if(column == 2):    # This is actually the 3rd column in the GUI
        row += 1
        column = 0
    else:
        column += 1

app.addLabel("lbl-actCamText", "Active TV Camera",0,3,0)  # Active TV camera
app.setLabelBg("lbl-actCamText", "red")
app.addLabel("lbl-actCam", ir['CameraInfo']['Groups'][activeCam]['GroupName'],1,3,0)  # Active TV camera
app.addLabel("lbl-actDrvText", "Active Driver",2,3,0)  # Active Driver
app.setLabelBg("lbl-actDrvText", "red")
app.addLabel("lbl-actDrv", "#"+str(activeNumber) +": "+activeDriver,3,3,0)  # Active Driver

app.addLabel("lbl-actPosText", "Active Position",4,3,0)  # Active Position
app.setLabelBg("lbl-actPosText", "red")

if (position_list == "None"):
    app.addLabel("lbl-actPos", ["- No Positions At This Time -"],5,3,0)  # Active Position
else:
    app.addLabel("lbl-actPos", ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'][CamCarIdx]['Position'],5,3,0)  # Active Position

if (team_race == True):	#If TeamID of the 1st place car is not 0, then this is a team race.
    app.addLabel("lbl-actTeamText", "Active Team",6,3,0)  # Active Team
    app.setLabelBg("lbl-actTeamText", "red")
    app.addLabel("lbl-actTeam", "#"+str(activeNumber) +": "+activeTeam,7,3,0)  # Active Team

if (position_list != "None"):
    app.addLabelOptionBox("Change Position", position_list,8,3,0) # Drop-down menu, array from 'position_list'
    app.addButton("Change Position", button,9,3,0)
app.go()
