(script# 88)
(include sci.sh)
(use Main)
(use System)


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
