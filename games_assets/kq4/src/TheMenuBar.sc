;;; Sierra Script 1.0 - (do not remove this comment)
(script# 997)
(include sci.sh)
(use Main)
(use Class_255_0)
(use Gauge)
(use Sound)
(use InvI)
(use User)


(class TheMenuBar of Class_255_0
	(properties
		state $0000
	)
	
	(method (init)
		(AddMenu { _} {אודות KQ4`^a:עזרה`#1})
		(AddMenu
			{ קובץ_}
			{שמור`#5:שחזר`#7:-!:אתחל`#9:צא`^q}
		)
		(AddMenu {פעולה_} 
			 {השהה`^p:חפצים`^i:הקלד שוב`#3}
		)
		(AddMenu
			{ מהירות_}
			{מהירות`^s:-!:מהיר יותר`+:רגיל`=:איטי יותר`-}
		)
		(AddMenu { קול_} {עוצמה`^v:-!:כיבוי=1`#2})
		(SetMenu
			1283
			110
			(if (DoSound sndSET_SOUND) {כבה} else {הפעל})
		)
		(SetMenu 513 109 ',[/game]')
		(SetMenu 514 109 'restore[/game]')
		(SetMenu 516 109 'restart[/game]')
		(SetMenu 517 109 'quit[/game]')
		(SetMenu 769 109 'pause[/game]')
		(SetMenu 770 109 'inventory')
	)
	
	(method (handleEvent pEvent &tmp temp0 temp1 [temp2 4] temp6 [temp7 288])
		(switch (= temp0 (super handleEvent: pEvent))
			(257
				(= temp6 (Sound pause: 1))
				(proc255_0
					(Format @temp7 997 0 gVersion)
					80
					{A Ken Williams Production}
					33
					gSmallFont
					30
					1
					67
					20
					10
					70
					260
				)
				(Sound pause: temp6)
			)
			(258
				(= temp6 (Sound pause: 1))
				(proc255_0 997 1 33 gSmallFont)
				(Sound pause: temp6)
			)
			(513
				(if (not (HaveMem 1028))
					(proc255_0 997 2)
				else
					(gGame save:)
				)
			)
			(514
				(if (not (HaveMem 1028))
					(proc255_0 997 3)
				else
					(gGame restore:)
				)
			)
			(516
				(= temp6 (Sound pause: 1))
				(if
					(proc255_0
						997
						4
						82
						100
						0
						0
						33
						0
						81
						{ Restart_}
						1
						81
						{המשך}
						0
					)
					(gGame restart:)
				)
				(Sound pause: temp6)
			)
			(517
				(= temp6 (Sound pause: 1))
				(= gQuit
					(proc255_0
						997
						5
						82
						100
						0
						0
						33
						0
						81
						{____יציאה____}
						1
						81
						{ Continue_}
						0
					)
				)
				(Sound pause: temp6)
			)
			(769
				(= temp6 (Sound pause: 1))
				(proc255_0 997 6 33 0 30 1 81 { Continue_} 0)
				(Sound pause: temp6)
			)
			(770
				(if (not (HaveMem 2348))
					(proc255_0 997 7)
				else
					(= temp6 (Sound pause: 1))
					(Inv showSelf: gEgo)
					(Sound pause: temp6)
				)
			)
			(771
				(pEvent claimed: 0 type: 4 message: (User echo?))
			)
			(1025
				(if (not (HaveMem 1850))
					(proc255_0 997 8)
				else
					(= temp1
						((Gauge new:)
							description:
								{השתמשי בעכבר או במקשי החיצים ימינה ושמאלה כדי לשנות את מהירות הדמויות.}
							text: {מהירות אנימציה}
							minimum: 0
							normal: 10
							maximum: 15
							higher: {מהר יותר}
							lower: {לאט יותר}
							doit: (- 16 gSpeed)
						)
					)
					(gGame setSpeed: (- 16 temp1))
					(DisposeScript 987)
				)
			)
			(1027
				(if (> gSpeed 1) (gGame setSpeed: (-- gSpeed)))
			)
			(1028 (gGame setSpeed: 6))
			(1029
				(gGame setSpeed: (++ gSpeed))
			)
			(1281
				(if (not (HaveMem 1850))
					(proc255_0 997 9)
				else
					(= temp6 (DoSound sndPAUSE 1))
					(= temp1
						((Gauge new:)
							description:
								{השתמשי בעכבר או במקשי החיצים ימינה ושמאלה כדי לשנות את עוצמת השמע.}
							text: {עוצמת שמע}
							minimum: 0
							normal: 12
							maximum: 15
							higher: {חזק יותר}
							lower: {חלש יותר}
							doit: (DoSound sndVOLUME)
						)
					)
					(DoSound sndPAUSE temp6)
					(DoSound sndVOLUME temp1)
					(DisposeScript 987)
				)
			)
			(1283
				(if (= temp1 (DoSound sndSET_SOUND))
					(SetMenu 1283 110 {הפעל})
				else
					(SetMenu 1283 110 {כבה})
				)
				(DoSound sndSET_SOUND (not temp1))
			)
			(else 
				(if global202 (global202 doit: temp0))
			)
		)
	)
)
