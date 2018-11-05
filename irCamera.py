#!python3
import time, os, sys
import re
import irsdk

ir = irsdk.IRSDK()
ir.startup()
# LOCAL DEBUG
#ir.startup(test_file='Scripts\RaceData.bin')

def interactiveMenu():
    try:
        while True:
            if (sys.platform == "win32"):
                os.system('cls')
            else:
                os.system('clear')
            activeSession = ir['SessionNum']
            # Active Driver
            CamCarIdx = ir['CamCarIdx']
            activeDriver = ir['DriverInfo']['Drivers'][CamCarIdx]['UserName']
            activeNumber = ir['DriverInfo']['Drivers'][CamCarIdx]['CarNumberRaw']
            activeTeam   = ir['DriverInfo']['Drivers'][CamCarIdx]['TeamName']
            # Active Camera
            groupNum = ir['CamGroupNumber']
            activeCam = ir['CamGroupNumber']-1

            print("Active session\t: ",ir['SessionInfo']['Sessions'][activeSession]['SessionType'])

            print ("Active Driver\t: ", activeDriver)
            if (ir['DriverInfo']['Drivers'][CamCarIdx]['TeamID'] != 0):
                print ("Active Team\t: ", activeTeam)
            print ("Car Number\t: ", activeNumber)
            print ("Active Camera\t: ", ir['CameraInfo']['Groups'][activeCam]['GroupName'])
            print ("Camera Number\t: ", groupNum,"\n")
            print ("Do you want to change the position, team, active camera, the active driver, or quit the program?\n\n \
            A) Position \n \
            B) Team (WORK IN PROGRESS)\n \
            C) Camera \n \
            D) Drivers \n \
            R) Refresh \n \
            Q) Quit\n"),
            mainMenu = str.lower(input("\t> "))

            #Change active position
            if (mainMenu == "a"):
                changePosition(activeSession,groupNum)

            #Change active team (WORK IN PROGRESS)
            elif (mainMenu == "b"):
                changeTeam(activeSession,groupNum,activeCam)

            #Change active camera, driver remains the same
            elif (mainMenu == "c"):
                changeCamera(activeSession,activeCam,activeNumber)

            #Change active driver, camera remains the same
            elif (mainMenu == "d"):
                changeDriver(activeSession,groupNum)

            #Refreshing the program, to account for session and/or manual camera changes.
            elif (mainMenu == "r" or ):
                print('Refreshing. Returning to menu...\n\n')
                time.sleep(0.5)
            #Quit
            elif (mainMenu == "q"):
                print("Bye!\n")
                exit()
            #Anything other than A, B, C, D, Q? Reload menu.
            else:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("Ending Program\n")
        quit()
    pass

def changePosition(activeSession,groupNum): #Change active position
	if ir['SessionInfo']['Sessions'][activeSession]['SessionType'] in ("Practice", "Lone Qualify", "Qualify") and ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'] == None:
		print ("There are currently no driver positions in this session. Try again later.\n\n")
		time.sleep(1)
	print("\nSelect New Position:")
	print ("Pos","\t","Class","\t","Num","\t", "Driver")
	for i in range(0, len(ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'])):
		position = ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'][i]['Position']
		classPos = ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'][i]['ClassPosition']
		#carID = ir['CarIdxPosition'][position]
		carID = ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'][i]['CarIdx']
		driverName = ir['DriverInfo']['Drivers'][carID]['UserName']
		carNum = ir['DriverInfo']['Drivers'][carID]['CarNumberRaw']
		TeamName = ir['DriverInfo']['Drivers'][carID]['TeamName']
		TeamID = ir['DriverInfo']['Drivers'][carID]['TeamID']
		if (TeamID == "0"):
			print (position, "\t", carNum, "\t" , driverName)
		else:
			print (position, "\t", classPos+1, "\t" , carNum, "\t" , TeamName)
	newPos = input("\tEnter Position Number > ")
	if (newPos == "") or (not re.match("(\d+)",newPos)): #little bit of regex to kill the script if anything other than 0-9 is entered
		print("\nReturning to Main Menu..\n")
		time.sleep(1)
	else:
		newCamera = int(groupNum)
		newPosition = int(newPos)
		ir.cam_switch_pos(newPosition,newCamera,0)
		print("ir.cam_switch_pos(",newPosition,",",newCamera,",0)")
		print('\nDone. Returning to menu...\n\n')
		time.sleep(1)
		del position, carID, driverName, newPos, newCamera, newPosition

def changeTeam(activeSession,groupNum,activeCam): #Change active team (WORK IN PROGRESS)
	if ir['SessionInfo']['Sessions'][activeSession]['SessionType'] in ("Practice", "Lone Qualify", "Qualify") and ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'] == None:
		print ("There are currently no driver positions in this session. Try again later.\n\n")
		time.sleep(1)
	TeamID = ir['DriverInfo']['Drivers'][1]['TeamID']			#Car 0 is always the Pace Car, so we look at Car 1.
	if (TeamID == 0):	#If TeamID of the 1st place car is 0, then this isn't a team race.
		print ("\nThis isn't a team race!\n\nReturning to Main Menu..\n")
		del TeamID
		time.sleep(1)
	else:
		print (ir['DriverInfo']['Drivers'][1]['UserName'], TeamID)
		print("\nSelect New Team:")
		print ("CarNum\t", "Team Name\t")
		for i in range(1, len(ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'])):
		#for i in range(1, len(ir['DriverInfo']['Drivers'])):
			carID = ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'][i]['CarIdx']
			posCarNum = ir['DriverInfo']['Drivers'][i]['CarNumberRaw']
			TeamID = ir['DriverInfo']['Drivers'][carID]['TeamID']
			TeamName = ir['DriverInfo']['Drivers'][i]['TeamName']
			PaceCar = ir['DriverInfo']['Drivers'][i]['CarIsPaceCar']
			print (posCarNum, "\t", TeamName)
		changeTeam = input("\tEnter Team Car Number > ")
		if (changeTeam == "") or (not re.match("(\d+)",changeTeam)): #little bit of regex to kill the script if anything other than 0-9 is entered
			print("\nReturning to Main Menu..\n")
			time.sleep(1)
		else:
			print("ir.cam_switch_num(",changeTeam,",",groupNum,", 0)")
			ir.cam_switch_num(changeTeam, groupNum, 1)
			print('\nDone. Returning to menu...\n\n')
			time.sleep(1)

def changeCamera(activeSession,activeCam,activeNumber): #Change active camera, driver remains the same
	if ir['SessionInfo']['Sessions'][activeSession]['SessionType'] in ("Practice", "Lone Qualify", "Qualify") and ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'] == None:
		print ("There are currently no driver positions in this session. Try again later.\n\n")
		time.sleep(1)
	print("\nSelect New Camera:")
	print ("Active Camera: ", ir['CameraInfo']['Groups'][activeCam]['GroupName'])
	print ("Group\t", "Name\t")
	for _grp in range(0, len(ir['CameraInfo']['Groups'])):
		changeGroup = ir['CameraInfo']['Groups'][_grp]['GroupNum']
		changeName	= ir['CameraInfo']['Groups'][_grp]['GroupName']
		print (changeGroup, "\t", changeName)
	changeCam = input("\tSelect New Camera > ")
	if (changeCam == "") or (not re.match("(\d+)",changeCam)): #little bit of regex to kill the script if anything other than 0-9 is entered
		print("\nReturning to Main Menu..\n")
		time.sleep(1)
	else:
		newCamera = int(changeCam)
		ir.cam_switch_num(activeNumber, newCamera, 1)
		print("ir.cam_switch_num(",activeNumber,",",changeCam,",0)")
		print('\nDone. Returning to menu...\n\n')
		time.sleep(1)

def changeDriver(activeSession,groupNum): #Change active driver, camera remains the same
	if ir['SessionInfo']['Sessions'][activeSession]['SessionType'] in ("Practice", "Lone Qualify", "Qualify") and ir['SessionInfo']['Sessions'][activeSession]['ResultsPositions'] == None:
		print ("There are currently no driver positions in this session. Try again later.\n\n")
		time.sleep(1)
	#Make an array out of ['DriverInfo']['Drivers'], then remove ['DriverInfo']['Drivers'][i]['IsSpectator'] = 1, and then parse that in a for loop.
	driversRaw = ir['DriverInfo']['Drivers']
	driversList = []
	for i in range(0, len(driversRaw)):
		if (driversRaw[i]['IsSpectator'] == 0):
			driversList.append (driversRaw[i])
	for i in range(0, len(driversList)):
		CarNum = driversList[i]['CarNumber']
		driverName = driversList[i]['UserName']
		TeamName = driversList[i]['TeamName']
		print (CarNum, "\t", driverName)
	newDriver = input("\tEnter Car Number > ")
	if (newDriver == "") or (not re.match("(\d+)",newDriver)): #little bit of regex to kill the script if anything other than 0-9 is entered
		print("\nReturning to Main Menu..\n")
		time.sleep(1)
	else:
		print("ir.cam_switch_num(",newDriver,",",groupNum,", 0)")
		ir.cam_switch_num(newDriver, groupNum, 1)
		print('\nDone. Returning to menu...\n\n')
		time.sleep(1)

interactiveMenu()
