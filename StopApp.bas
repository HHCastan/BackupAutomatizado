!***************************************************************************
!** PROGRAMA STOPAPP.BAS                                                  **
!** Almacenes Flamingo S.A.                                               **
!** Desarrollado por    : Ing. Hugo Castaneda                             **
!** Creacion: 07/07/2017                                                  **
!** Ultima Modificacion                                                   **
!***************************************************************************
!** Programa utilizado para detener la tarea de Background                **
!***************************************************************************
!** Compilar:                                                             **
!**          BASIC STOPAPP                                                **
!**          LINK86 STOPAPP                                               **
!**          POSTLINK STOPAPP.286                                         **
!***************************************************************************

Integer*4 RET

STRING taskName$, taskParam$, param2$

SUB ADXSERVE (RET,FUNC,PARM1,PARM2) EXTERNAL
   INTEGER*4 RET
   INTEGER*2 FUNC,PARM1
   STRING PARM2
END SUB

!*********************************************
!**          PROGRAMA PRINCIPAL             **
!*********************************************

taskName$  = "java2bin:java.386       "
taskParam$ = "-Duser.dir=c:/paf -jar c:/paf/paf.jar"
param2$  = taskName$ + taskParam$


CALL ADXSERVE(RET, 19, 2, param2$)
	
PRINT RET