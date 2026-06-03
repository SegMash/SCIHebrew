;;; Sierra Script 1.0 - (do not remove this comment)
;;; Decompiled by sluicebox
(script# 995)
(include sci.sh)
(use Main)
(use Interface)
(use Save)
(use System)

(local
	yesI
)

(class InvI of Obj
	(properties
		said 0
		description 0
		owner 0
		view 0
		loop 0
		cel 0
		script 0
	)

	(method (saidMe)
		(Said said)
	)

	(method (ownedBy id)
		(return (== owner id))
	)

	(method (moveTo id)
		(= owner id)
		(return self)
	)

	(method (showSelf)
		(ShowView (if description description else name) view loop cel)
	)

	(method (changeState newState)
		(if script
			(script changeState: newState)
		)
	)
)

(class Inv of Set
	(properties
		carrying {אתה נושא:}
		empty {אינך נושא דבר!}
	)

	(method (init)
		(= gInventory self)
	)

	(method (saidMe)
		(self firstTrue: #saidMe)
	)

	(method (ownedBy whom)
		(self firstTrue: #ownedBy whom)
	)

	(method (showSelf whom)
		(invD text: carrying doit: whom)
	)
)

(instance invD of Dialog
	(properties)

	(method (init param1 &tmp temp0 temp1 temp2 temp3 temp4 temp5 temp6 temp7 temp8 temp9)
		; Hebrew RTL: build columns growing LEFTWARD (temp0 holds the
		; current column's RIGHT edge in virtual coords). Each item is
		; right-aligned at placement time by shifting it left by its own
		; width, so the FIRST column ends up rightmost. After the loop we
		; shift everything so the leftmost item lands at nsLeft = 4.
		(= temp0 0)
		(= temp1 4)
		(= temp2 4)
		(= temp3 0)
		(for
			((= temp5 (gInventory first:)))
			temp5
			((= temp5 (gInventory next: temp5)))
			
			(= temp6 (NodeValue temp5))
			(if (temp6 ownedBy: param1)
				(++ temp3)
				(self
					add:
						((= temp4 (DText new:))
							value: temp6
							text: (temp6 name:)
							nsLeft: temp0
							nsTop: temp1
							state: 3
							font: gSmallFont
							setSize:
							yourself:
						)
				)
				; setSize set nsLeft=temp0, nsRight=temp0+width.
				; Shift left by width so nsRight = temp0 (right edge of column).
				(temp4 move: (- (temp4 nsLeft:) (temp4 nsRight:)) 0)
				(if (< temp2 (- (temp4 nsRight:) (temp4 nsLeft:)))
					(= temp2 (- (temp4 nsRight:) (temp4 nsLeft:)))
				)
				(if
					(>
						(+= temp1 (+ (- (temp4 nsBottom:) (temp4 nsTop:)) 1))
						140
					)
					; Column full -> next column extends LEFTWARD.
					(= temp1 4)
					(-= temp0 (+ temp2 10))
					(= temp2 4)
				)
			)
		)
		; Find leftmost nsLeft (= last/leftmost column's widest item),
		; then shift every item right so the leftmost lands on nsLeft = 4.
		(= temp9 0)
		(for
			((= temp7 (self first:)))
			temp7
			((= temp7 (self next: temp7)))
			(= temp8 (NodeValue temp7))
			(if (< (temp8 nsLeft:) temp9)
				(= temp9 (temp8 nsLeft:))
			)
		)
		(= temp9 (- 4 temp9))
		(if temp9
			(for
				((= temp7 (self first:)))
				temp7
				((= temp7 (self next: temp7)))
				(= temp8 (NodeValue temp7))
				(temp8 move: temp9 0)
			)
		)
		(if (not temp3)
			(self dispose:)
			(return 0)
		)
		(= window SysWindow)
		(self setSize:)
		(= yesI (DButton new:))
		(yesI
			text: {אישור}
			setSize:
			moveTo: (- nsRight (+ 4 (yesI nsRight:))) nsBottom
		)
		(yesI move: (- (yesI nsLeft:) (yesI nsRight:)) 0)
		(self add: yesI setSize: center:)
		(return temp3)
	)

	(method (doit param1 &tmp temp0)
		(if (not (self init: param1))
			(Print (gInventory empty:))
			(return)
		)
		(self open: 4 15)
		(= temp0 yesI)
		(repeat
			(if
				(or
					(not (= temp0 (super doit: temp0)))
					(== temp0 -1)
					(== temp0 yesI)
				)
				(break)
			)
			((temp0 value:) showSelf:)
		)
		(self dispose:)
	)

	(method (handleEvent event &tmp temp0 temp1)
		(= temp0 (event message:))
		(switch (= temp1 (event type:))
			(evKEYBOARD
				(switch temp0
					(KEY_UP
						(= temp0 KEY_SHIFTTAB)
					)
					(KEY_DOWN
						(= temp0 KEY_TAB)
					)
				)
			)
			($0040 ; direction
				(switch temp0
					(JOY_UP
						(= temp0 KEY_SHIFTTAB)
						(= temp1 evKEYBOARD)
					)
					(JOY_DOWN
						(= temp0 KEY_TAB)
						(= temp1 evKEYBOARD)
					)
				)
			)
		)
		(event type: temp1 message: temp0)
		(super handleEvent: event)
	)
)

