;;; Sierra Script 1.0 - (do not remove this comment)
;;; Decompiled by sluicebox
(script# 994)
(include sci.sh)
(use Main)
(use LoadMany)
(use Interface)
(use Sound)
(use Save)
(use Motion)
(use Inventory)
(use User)
(use System)
(use Menu)

(public
	EgoDeadNew 28
)

(procedure (PromptForDiskChange saveDisk &tmp ret [saveDevice 40] [curDevice 40] [str 40])
	(= ret 1)
	(DeviceInfo diGET_DEVICE gCurSaveDir @saveDevice)
	(DeviceInfo diGET_CURRENT_DEVICE @curDevice)
	(if (and (DeviceInfo diPATHS_EQUAL @saveDevice @curDevice) (DeviceInfo diIS_FLOPPY @curDevice))
		(Format @str 994 6 (if saveDisk {שמור משחק} else {משחק}) @curDevice) ; "Please insert your %s disk in drive %s."
		(DeviceInfo 4) ; CloseDevice
		(if
			(==
				(= ret
					(if saveDisk
						(Print
							@str
							#font
							0
							#button
							{אישור}
							1
							#button
							{ביטול}
							0
							#button
							{שנה תיקייה}
							2
						)
					else
						(Print @str #font 0 #button {אישור} 1)
					)
				)
				2
			)
			(= ret (GetDirectory gCurSaveDir))
		)
	)
	(return ret)
)

(procedure (EgoDeadNew)
	(HandsOff)
	(backSound fade:)
	(gameSound fade:)
	(SciAudio stop:)
	(Wait 100)
	(gSounds eachElementDo: #stop)
	(switch (Random 0 2)
		(0
			(SciAudio play: {death.mp3} 0)
		)
		(1
			(SciAudio play: {death2.mp3} 0)
		)
		(2
			(SciAudio play: {death3.mp3} 0)
		)
	)
		
	;(backSound
	;	number:
	;		(switch (Random 0 2)
	;			(0 49)
	;			(1 28)
	;			(2 3)
	;		)
	;	loop: 1
	;	priority: 15
	;	init:
	;	play:
	;)
	(gGame setCursor: gNormalCursor 1)
	(repeat
		(switch
			(Print
				&rest
				#width
				250
				#button
				{לשחזר}
				1
				#button
				{ לאתחל }
				2
				#button
				{ לצאת }
				3
				
			)
			(1
				(gGame restore:)
			)
			(2
				(gGame restart:)
			)
			(3
				(= gQuit 1)
				(break)
			)
		)
	)
)

(instance gameSound of Sound
	(properties
		number 1
		priority 5
	)
)

(instance backSound of Sound
	(properties
		number 1
	)
)




(instance cast of EventHandler
	(properties)
)

(instance features of EventHandler
	(properties)
)

(instance sFeatures of EventHandler
	(properties)

	(method (delete theElement)
		(super delete: theElement)
		(if
			(and
				global54
				(theElement isKindOf: Collect)
				(not (OneOf theElement gRegions gLocales))
			)
			(theElement release: dispose:)
		)
	)
)

(instance sounds of EventHandler
	(properties)
)

(instance regions of EventHandler
	(properties)
)

(instance locales of EventHandler
	(properties)
)

(instance addToPics of EventHandler
	(properties)

	(method (doit)
		(AddToPic elements)
	)
)

(instance controls of Controls
	(properties)
)

(instance timers of Set
	(properties)
)

(class Game of Obj
	(properties
		script 0
		parseLang 1
		printLang 1
		subtitleLang 0
	)

	(method (play)
		(= gGame self)
		(= gCurSaveDir (GetSaveDir))
		(if (not (GameIsRestarting))
			(GetCWD gCurSaveDir)
		)
		(self setCursor: gWaitCursor 1)
		(self init:)
		(self setCursor: gNormalCursor (HaveMouse))
		(while (not gQuit)
			(self doit:)
			(= gAniInterval (Wait gSpeed))
		)
	)

	(method (replay)
		(if gLastEvent
			(gLastEvent dispose:)
		)
		(gSortedFeatures release:)
		(if gModelessDialog
			(gModelessDialog dispose:)
		)
		(gCast eachElementDo: #perform RU)
		(gGame setCursor: gWaitCursor 1)
		(DrawPic (gCurRoom curPic:) 100 1 global61)
		(if (!= global57 -1)
			(DrawPic global57 100 0 global61)
		)
		(if (gCurRoom controls:)
			((gCurRoom controls:) draw:)
		)
		(gAddToPics doit:)
		(gGame setCursor: gNormalCursor (HaveMouse))
		(SL doit:)
		(DoSound sndRESUME)
		(Sound pause: 0)
		(while (not gQuit)
			(self doit:)
			(= gAniInterval (Wait gSpeed))
		)
	)

	(method (init &tmp foo)
		(= foo Motion)
		(= foo Sound)
		(= foo Save)
		((= gCast cast) add:)
		((= gFeatures features) add:)
		((= gSortedFeatures sFeatures) add:)
		((= gSounds sounds) add:)
		((= gRegions regions) add:)
		((= gLocales locales) add:)
		((= gAddToPics addToPics) add:)
		((= gTimers timers) add:)
		(= gCurSaveDir (GetSaveDir))
		(Inv init:)
		(User init:)
	)

	(method (doit)
		(gSounds eachElementDo: #check)
		(gTimers eachElementDo: #doit)
		(if gModelessDialog
			(gModelessDialog check:)
		)
		(Animate (gCast elements:) 1)
		(if (and (== ((ScriptID 0 23) number:) 98) (not (IsFlag 51)))
			((ScriptID 0 23) stop:)
			(SciAudio stop:)
			(SciAudio play: {treasures.mp3} 0)
			(SetFlag 51)
		)
		(if global58
			(= global58 0)
			(gCast eachElementDo: #motionCue)
		)
		(if script
			(script doit:)
		)
		(gRegions eachElementDo: #doit)
		(if (== gNewRoomNum gCurRoomNum)
			(User doit:)
		)
		(if (!= gNewRoomNum gCurRoomNum)
			(self newRoom: gNewRoomNum)
		)
		(gTimers eachElementDo: #delete)
		(GameIsRestarting 0)
	)

	(method (showSelf)
		(gRegions showSelf:)
	)

	(method (newRoom newRoomNumber &tmp [temp0 4] temp4 temp5)
		(gAddToPics dispose:)
		(gFeatures eachElementDo: #dispose release:)
		(gCast eachElementDo: #dispose eachElementDo: #delete)
		(gTimers eachElementDo: #delete)
		(gRegions eachElementDo: #perform DNKR release:)
		(gLocales eachElementDo: #dispose release:)
		(Animate 0)
		(= gPrevRoomNum gCurRoomNum)
		(= gCurRoomNum newRoomNumber)
		(= gNewRoomNum newRoomNumber)
		(FlushResources newRoomNumber)
		(= temp4 (self setCursor: gWaitCursor 1))
		(self startRoomMain: gCurRoomNum checkAni: setCursor: temp4 (HaveMouse))
		(SetSynonyms gRegions)
		(while ((= temp5 (Event new: evMOUSE)) type:)
			(temp5 dispose:)
		)
		(temp5 dispose:)
	)

	(method (checkAni &tmp theExtra)
		(Animate (gCast elements:) 0)
		(Wait 0)
		(Animate (gCast elements:) 0)
		(while (> (Wait 0) gAniThreshold)
			(breakif (== (= theExtra (gCast firstTrue: #isExtra)) 0))
			(theExtra addToPic:)
			(Animate (gCast elements:) 0)
			(gCast eachElementDo: #delete)
		)
	)
	
	(method (startRoomMain roomNum)
		(LoadMany
			0
			985
			982
			972
			988
			980
			978
			977
			975
			974
			971
			970
			969
			973
			966
			965
			964
			962
			956
			976
			959
			955
			949
			991
			986
			983
			611
			600
			608
			779
			784
			782
			781
			780
			615
			898
			899
		)
		(if gDebugOn
			(= gDebugOn 0)
			(SetDebug)
		)
		(if
			(and
				(u> (MemoryInfo 1) (+ 20 (MemoryInfo 0))) ; FreeHeap, LargestPtr
				global118
				(Print 0 3 #button {Debug} 1) ; "Memory fragmented."
			)
			(SetDebug)
		)
		(self startRoom: roomNum)
		(if (and (== gPrevRoomNum 0) (not (IsFlag 40)))
			(MenuBar draw:)
			(SL enable:)
		)
		(gCurRoom picAngle: 50)
		(if (and (IsFlag 2) (not (>= 79 gCurRoomNum 49)))
			(gCurRoom setRegions: 600) ; rgGoat
		else
			(if global119
				(proc0_13)
			)
			(if
				(and
					(OneOf
						gCurRoomNum
						3
						4
						5
						6
						7
						8
						9
						12
						14
						15
						16
						17
						18
						19
						20
						23
						24
						26
						30
						31
						32
						33
						34
						36
						37
						38
						42
						45
						47
						56
						57
						59
						60
						61
						62
						70
						71
						72
						82
					)
					(>= global101 1)
				)
				(gCurRoom setLocales: 611)
			)
		)
		(if (OneOf gCurRoomNum 24 31 38)
			(cond
				((gEgo has: 20) ; Beans
					(gCurRoom setRegions: 606) ; beanRg
				)
				((== global131 gCurRoomNum)
					(gCurRoom setRegions: 607) ; stalkRg
				)
			)
		)
		(if (OneOf gCurRoomNum 56 57 58 59 60 61 62 72 82)
			(gCurRoom setRegions: 610) ; rgClouds
		)
		(if global124
			(gCurRoom setRegions: 616) ; rgHalo
		)
		(gameSound loop: 0)
		(cond
			(
				(and
					(gEgo has: 14) ; Magic_Mirror
					(gEgo has: 1) ; Chest
					(gEgo has: 16) ; Magic_Shield
					(not (IsFlag 51))
					(or (< gCurRoomNum 70) (== gCurRoomNum 83))
					(!= gCurRoomNum 53)
				)
				(PlayBackSound 98)
			)
			((OneOf gCurRoomNum 50 66 67 68 69 73 74 75 76 77 78)
				((ScriptID 0 23) stop:) ; backSound
				(SciAudio stop:)
				(SciAudio play: {cave.mp3} -1)
				;(PlayBackSound 31)
			)
			((OneOf gCurRoomNum 63)
				(PlayBackSound 73)
			)
			(
				(OneOf
					gCurRoomNum
					3
					9
					10
					11
					12
					13
					15
					16
					19
					21
					22
					24
					27
					28
					29
					30
					31
					35
					36
					38
					40
					44
					45
					46
					48
					95
				)
				(PlayBackSound 2)
			)
			((OneOf gCurRoomNum 1 2 25 26 39 41 42 83)
				(PlayBackSound 52)
			)
			((OneOf gCurRoomNum 7 32 33 34 47)
				(PlayBackSound 12)
			)
			((OneOf gCurRoomNum 4 5 6 8 17 18 20 23 37 43)
				(PlayBackSound 68)
			)
		)
		(self dispose:)
	)

	(method (startRoom roomNum)
		(if gDebugOn
			(SetDebug)
		)
		(gRegions addToFront: (= gCurRoom (ScriptID roomNum)))
		(gCurRoom init:)
		(if global55
			(gCurRoom setRegions: 975)
		)
	)

	(method (handleEvent event)
		(or
			(and
				(not (and global54 (== (event type:) evSAID)))
				(or
					(gRegions handleEvent: event)
					(gLocales handleEvent: event)
				)
			)
			(and script (script handleEvent: event))
		)
		(event claimed:)
	)

	(method (changeScore delta)
		(+= gScore delta)
		(SL doit:)
	)

	(method (restart)
		(if gModelessDialog
			(gModelessDialog dispose:)
		)
		(RestartGame)
	)

	(method (save &tmp [temp0 20] temp20 temp21 temp22 temp23)
		(= temp23 parseLang)
		(= parseLang 1)
		(Load rsFONT gSmallFont)
		(Load rsCURSOR gWaitCursor)
		(= temp21 (self setCursor: gNormalCursor))
		(= temp22 (Sound pause: 1))
		(if (PromptForDiskChange 1)
			(if gModelessDialog
				(gModelessDialog dispose:)
			)
			(if (!= (= temp20 (Save doit: @temp0)) -1)
				(= parseLang temp23)
				(= temp21 (self setCursor: gWaitCursor 1))
				(if (not (SaveGame name temp20 @temp0 gVersion))
					(Print 994 0 #font 0 #button {אישור} 1) ; "Your save game disk is full. You must either use another disk or save over an existing saved game."
				)
				(self setCursor: temp21 (HaveMouse))
			)
			(PromptForDiskChange 0)
		)
		(Sound pause: temp22)
		(= parseLang temp23)
	)

	(method (restore &tmp [temp0 20] temp20 temp21 temp22 temp23)
		(= temp23 parseLang)
		(= parseLang 1)
		(Load rsFONT gSmallFont)
		(Load rsCURSOR gWaitCursor)
		(= temp21 (self setCursor: gNormalCursor))
		(= temp22 (Sound pause: 1))
		(if (PromptForDiskChange 1)
			(if gModelessDialog
				(gModelessDialog dispose:)
			)
			(if (!= (= temp20 (Restore doit: &rest)) -1)
				(self setCursor: gWaitCursor 1)
				(if (CheckSaveGame name temp20 gVersion)
					(RestoreGame name temp20 gVersion)
				else
					(Print 994 1 #font 0 #button {אישור} 1) ; "That game was saved under a different interpreter. It cannot be restored."
					(self setCursor: temp21 (HaveMouse))
					(= parseLang temp23)
				)
			else
				(= parseLang temp23)
			)
			(PromptForDiskChange 0)
		)
		(Sound pause: temp22)
	)

	(method (setSpeed newSpeed &tmp oldSpeed)
		(= oldSpeed gSpeed)
		(= gSpeed newSpeed)
		(return oldSpeed)
	)

	(method (setCursor form &tmp oldCur)
		(= oldCur gTheCursor)
		(= gTheCursor form)
		(SetCursor form &rest)
		(return oldCur)
	)

	(method (showMem)
		(Printf
			{זיכרון זמין: %u בתים\nהצבעה הגדול ביותר: %u בתים\nחלק זמין: %u קילובייט\nהחלק הגדול ביותר: %u בתים}
			(MemoryInfo 1) ; FreeHeap
			(MemoryInfo 0) ; LargestPtr
			(>> (MemoryInfo miFREEHUNK) $0006)
			(MemoryInfo miLARGESTHUNK)
		)
	)

	(method (wordFail word &tmp [str 100])
		(Printf 994 2 word) ; "I don't understand "%s"."
		(return 0)
	)

	(method (syntaxFail)
		(Print 994 3) ; "That doesn't appear to be a proper sentence."
	)

	(method (semanticFail)
		(Print 994 4) ; "That sentence doesn't make sense."
	)

	(method (pragmaFail)
		(Print 994 5) ; "You've left me responseless."
	)

	(method (notify))

	(method (setScript newScript)
		(if script
			(script dispose:)
		)
		(if newScript
			(newScript init: self &rest)
		)
	)

	(method (cue)
		(if script
			(script cue:)
		)
	)
)

(class Rgn of Obj
	(properties
		script 0
		number 0
		timer 0
		keep 0
		initialized 0
	)

	(method (init)
		(if (not initialized)
			(= initialized 1)
			(if (not (gRegions contains: self))
				(gRegions addToEnd: self)
			)
			(super init:)
		)
	)

	(method (doit)
		(if script
			(script doit:)
		)
	)

	(method (handleEvent event)
		(if script
			(script handleEvent: event)
		)
		(event claimed:)
	)

	(method (dispose)
		(gRegions delete: self)
		(if (IsObject script)
			(script dispose:)
		)
		(if (IsObject timer)
			(timer dispose:)
		)
		(gSounds eachElementDo: #clean self)
		(DisposeScript number)
	)

	(method (setScript newScript)
		(if (IsObject script)
			(script dispose:)
		)
		(if newScript
			(newScript init: self &rest)
		)
	)

	(method (cue)
		(if script
			(script cue:)
		)
	)

	(method (newRoom))

	(method (notify))
)

(class Rm of Rgn
	(properties
		picture 0
		style -1
		horizon 0
		controls 0
		north 0
		east 0
		south 0
		west 0
		curPic 0
		picAngle 0
		vanishingX 160
		vanishingY -30000
	)

	(method (init &tmp how)
		(= number gCurRoomNum)
		(= controls controls)
		(= gPerspective picAngle)
		(if picture
			(self drawPic: picture)
		)
		(switch ((User alterEgo:) edgeHit:)
			(EDGE_TOP
				((User alterEgo:) y: 188)
			)
			(EDGE_LEFT
				((User alterEgo:) x: (- 319 ((User alterEgo:) xStep:)))
			)
			(EDGE_BOTTOM
				((User alterEgo:) y: (+ horizon ((User alterEgo:) yStep:)))
			)
			(EDGE_RIGHT
				((User alterEgo:) x: 1)
			)
		)
		((User alterEgo:) edgeHit: EDGE_NONE)
	)

	(method (doit &tmp nRoom)
		(if script
			(script doit:)
		)
		(if
			(= nRoom
				(switch ((User alterEgo:) edgeHit:)
					(EDGE_TOP north)
					(EDGE_RIGHT east)
					(EDGE_BOTTOM south)
					(EDGE_LEFT west)
				)
			)
			(self newRoom: nRoom)
		)
	)

	(method (dispose)
		(if controls
			(controls dispose:)
		)
		(super dispose:)
	)

	(method (handleEvent event)
		(or
			(super handleEvent: event)
			(and controls (controls handleEvent: event))
		)
		(event claimed:)
	)

	(method (setRegions region &tmp i n regID)
		(for ((= i 0)) (< i argc) ((++ i))
			(= n [region i])
			(= regID (ScriptID n))
			(regID number: n)
			(gRegions add: regID)
			(if (not (regID initialized:))
				(regID init:)
			)
		)
	)

	(method (setLocales locale &tmp i n locID)
		(for ((= i 0)) (< i argc) ((++ i))
			(= n [locale i])
			((= locID (ScriptID n)) number: n)
			(gLocales add: locID)
			(locID init:)
		)
	)

	(method (setFeatures feature &tmp temp0 [temp1 2])
		(for ((= temp0 0)) (< temp0 argc) ((++ temp0))
			(gFeatures add: [feature temp0])
		)
	)

	(method (newRoom newRoomNumber)
		(gRegions delete: self eachElementDo: #newRoom newRoomNumber addToFront: self)
		(= gNewRoomNum newRoomNumber)
		(super newRoom: newRoomNumber)
	)

	(method (drawPic pic theStyle)
		(if gAddToPics
			(gAddToPics dispose:)
		)
		(= curPic pic)
		(= global57 -1)
		(DrawPic
			pic
			(cond
				((== argc 2) theStyle)
				((!= style -1) style)
				(else gShowStyle)
			)
			1
			global61
		)
	)

	(method (overlay pic theStyle)
		(= global57 pic)
		(DrawPic
			pic
			(cond
				((== argc 2) theStyle)
				((!= style -1) style)
				(else gShowStyle)
			)
			0
			global61
		)
	)
)

(class Locale of Obj
	(properties
		number 0
	)

	(method (handleEvent event)
		(event claimed:)
	)

	(method (dispose)
		(gLocales delete: self)
		(DisposeScript number)
	)
)

(class SL of Obj
	(properties
		state 0
		code 0
	)

	(method (doit &tmp [theLine 41])
		(if code
			(code doit: @theLine)
			(DrawStatus (if state @theLine else 0))
		)
	)

	(method (enable)
		(= state 1)
		(self doit:)
	)

	(method (disable)
		(= state 0)
		(self doit:)
	)
)

(instance RU of Code
	(properties)

	(method (doit param1 &tmp temp0)
		(if (param1 underBits:)
			(= temp0 (& (= temp0 (| (= temp0 (param1 signal:)) $0001)) $fffb))
			(param1 underBits: 0 signal: temp0)
		)
	)
)

(instance DNKR of Code
	(properties)

	(method (doit param1)
		(if (not (param1 keep:))
			(param1 dispose:)
		)
	)
)

(class SciAudio of Obj
	(properties
		command   0
		fileName  0
		loopCount 0
	)
	
	(method (play aFileName aLoopCount)
		(= fileName aFileName)
		(= loopCount (if (>= argc 2) aLoopCount else 0))
		(= command 1)
		(self writeIt:)
	)
	
	(method (stop)
		(= command 2)
		(self writeIt:)
	)
	
	(method (writeIt &tmp h)
		(= h (FileIO 0 {sciAudio\5ccmd} 1))
		(if h
			(FileIO 6 h {})
			(FileIO 1 h)
		)
	)
)

