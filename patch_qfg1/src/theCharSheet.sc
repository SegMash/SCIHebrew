;;; Sierra Script 1.0 - (do not remove this comment)
;;; Decompiled by sluicebox
(script# 204)
(include sci.sh)
(use Main)
(use System)

(public
	theCharSheet 0
)


(procedure (localproc_0 &tmp temp0)
	(for ((= temp0 0)) (< temp0 25) ((++ temp0))
		(= [gOldStats temp0] [gEgoStats temp0])
	)
)

(procedure (localproc_1 param1 param2 &tmp temp0)
	(= temp0 (if (< global211 16) 0 else 1))
	(Display &rest 100 param1 param2 dsALIGN alLEFT dsFONT 300 dsCOLOR temp0)
)

(procedure (localproc_2 param1 param2 param3)
	(Display &rest 100 param1 param2 dsALIGN alRIGHT dsFONT 300 dsCOLOR param3 dsBACKGROUND 15)
)

(procedure (localproc_5 param1 param2 &tmp temp0)
	(= temp0 (if (< global211 16) 0 else 1))
	(Display &rest 100 param1 param2 dsALIGN alLEFT dsFONT 300 dsCOLOR temp0 dsWIDTH 100)
)

(procedure (localproc_3 param1)
	(return
		(if (== [gEgoStats param1] [gOldStats param1]) global274 else global275)
	)
)

(procedure (localproc_4 param1 param2 param3 param4 &tmp temp0 [temp1 6])
	(= temp0
		(if param4
			(localproc_3 param3)
		else
			global274
		)
	)
	(localproc_2
		param1
		param2
		temp0
		(Format @temp1 204 0 [gEgoStats param3]) ; "%d"
		106
		22
	)
)

(class CharSheet of Obj
	(properties
		nsTop 0
		nsLeft 0
		nsBottom 189
		nsRight 320
		theWindow 0
		useWindow 0
		showBars 0
	)

	(method (dispose)
		(localproc_0)
		(if theWindow
			(DisposeWindow theWindow)
		)
		(super dispose:)
		(DisposeScript 204)
	)

	(method (doit &tmp temp0 temp1)
		(= temp1 evNULL)
		(while (not temp1)
			(GlobalToLocal (= temp0 (Event new:)))
			(= temp1 (temp0 type:))
			(temp0 dispose:)
		)
		(self dispose:)
	)

	(method (init &tmp temp0)
		(super init: &rest)
		(Load rsVIEW 802)
		(if useWindow
			(= theWindow (NewWindow nsTop nsLeft nsBottom nsRight {} 0 15 0 15))
		)
		(= temp0 26)
		(if (!= gHeroType 0) ; Fighter
			(+= temp0 3)
		)
		(DrawCel 802 2 0 10 23 -1)
		(DrawCel 802 0 gHeroType temp0 32 -1)
		(if (== gHeroType 1) ; Magic User
			(DrawCel 802 1 0 40 52 -1)
		)
		(localproc_1 288 8 204 1) ; "Name :"
		;(localproc_1 83 35 204 2) ; "Strength"
		(localproc_5 80 35 204 2) ; "Strength"
		(localproc_5 80 47 204 3) ; "Intelligence"
		(localproc_5 80 59 204 4) ; "Agility"
		(localproc_5 80 71 204 5) ; "Vitality"
		(localproc_5 80 83 204 6) ; "Luck"
		(if showBars
			(localproc_5 50 112 204 7) ; "Puzzle Points"
			(localproc_5 50 124 204 8) ; "Experience"
		)
		(localproc_5 50 148 204 9) ; "Health Points"
		(localproc_5 50 160 204 10) ; "Stamina Points"
		(localproc_5 50 172 204 11) ; "Magic Points"
		(localproc_5 210 28 204 12) ; "Weapon Use"
		(localproc_5 210 40 204 13) ; "Parry"
		(localproc_5 210 52 204 14) ; "Dodge"
		(localproc_5 210 64 204 15) ; "Stealth"
		(localproc_5 210 76 204 16) ; "Pick Locks"
		(localproc_5 210 88 204 17) ; "Throwing"
		(localproc_5 210 100 204 18) ; "Climbing"
		(localproc_5 210 112 204 19) ; "Magic"
		(self update:)
	)

	(method (update &tmp temp0 [temp1 20])
		(if showBars
			(Display @global401 dsWIDTH 225 dsCOORD 58 8 dsALIGN alLEFT dsFONT 300 dsCOLOR global274)
		)
		(localproc_4 83 35 0 showBars)
		(localproc_4 83 47 1 showBars)
		(localproc_4 83 59 2 showBars)
		(localproc_4 83 71 3 showBars)
		(localproc_4 83 83 4 showBars)
		(if showBars
			(= temp0 (if (== gScore global335) global274 else global275))
			(= global335 gScore)
			(localproc_2 10 112 temp0 (Format @temp1 204 0 gScore) 106 50) ; "%d"
			(localproc_2
				10
				124
				(localproc_3 13)
				(Format @temp1 204 0 [gEgoStats 13]) ; "%d", experience
				106
				50
			)
		)
		(= temp0
			(if showBars
				(localproc_3 14)
			else
				global274
			)
		)
		(localproc_2
			10
			148
			temp0
			(Format ; "%d / %d"
				@temp1
				204
				20
				(/ (+ [gEgoStats 14] 1) 2) ; health
				(/ (+ (MaxHealth) 1) 2)
			)
			106
			50
		)
		(= temp0
			(if showBars
				(localproc_3 15)
			else
				global274
			)
		)
		(localproc_2
			10
			160
			temp0
			(Format ; "%d / %d"
				@temp1
				204
				20
				(/ (+ [gEgoStats 15] 3) 4) ; stamina
				(/ (+ (MaxStamina) 3) 4)
			)
			106
			50
		)
		(= temp0
			(if showBars
				(localproc_3 16)
			else
				global274
			)
		)
		(localproc_2
			10
			172
			temp0
			(Format @temp1 204 20 [gEgoStats 16] (MaxMana)) ; "%d / %d", mana
			106
			50
		)
		(localproc_4 200 28 5 showBars)
		(localproc_4 200 40 6 showBars)
		(localproc_4 200 52 7 showBars)
		(localproc_4 200 64 8 showBars)
		(localproc_4 200 76 9 showBars)
		(localproc_4 200 88 10 showBars)
		(localproc_4 200 100 11 showBars)
		(localproc_4 200 112 12 showBars)
	)
)

(instance theCharSheet of CharSheet
	(properties)
)

