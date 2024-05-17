!***************************************************************************
!** PROGRAMA STARTAPP.BAS                                                 **
!** Almacenes Flamingo S.A.                                               **
!** Desarrollado por    : Ing. Hugo Castaneda                             **
!** Creacion: 07/07/2017                                                  **
!** Ultima Modificacion                                                   **
!***************************************************************************
!** Programa utilizado para lanzar la tarea de Background                 **
!***************************************************************************
Integer*2 RETURN.SMALL

STRING taskName$, taskParam$, taskMess$

FUNCTION ADXSTART (NAME$,PARM$,MESS$) EXTERNAL
   INTEGER*2 ADXSTART
   STRING NAME$,PARM$,MESS$
END FUNCTION


!*********************************************
!**          PROGRAMA PRINCIPAL             **
!*********************************************

taskName$  = "java2bin:java.386"
taskParam$ = "-Duser.dir=c:/paf -jar c:/paf/paf.jar"
taskMess$  = "POS Aplication Framework - PAF"



	
