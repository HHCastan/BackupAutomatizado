!***************************************************************************
!** PROGRAMA BACKUP.BAS                                                   **
!** Almacenes Flamingo S.A.                                               **
!** Desarrollado por    : Ing. Hugo Castaneda                             **
!** Creacion: 17/11/2016                                                  **
!** Ultima Modificacion                                                   **
!***************************************************************************
!** Programa utilizado para lanzar la tarea de Backup                     **
!***************************************************************************
Integer*2 RETURN.SMALL

Function osshell(cmd.line$) External			                 ! routine to start
							                                     ! another program.
           integer*4    osshell				                     ! Upon completion of
           string       cmd.line$			                     ! program, control is
							                                     ! returned to calling
End Function						                             ! program.

!*********************************************
!**          PROGRAMA PRINCIPAL             **
!*********************************************

RETURN.SMALL = OSSHELL("M:respaldo/backup.bat")

	
