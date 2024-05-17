!***************************************************************************
!** PROGRAMA UDAUTOMA.BAS                                                 **
!** Linea Informatica S.A.                                                **
!** Desarrollado por    : Ing. Walter Acevedo Franco.                     **
!** Modificacion 17/08/2001, 04:00PM, por requerimiento de                **
!** ALMACENES FLAMINGO S.A.                                               **
!** Ultima Modificacion HHC: 19/01/2017, para incluir llamado a .bat      **
!***************************************************************************
!** Programa utilizado para lanzar las tareas de Backgroud encargadas de  **
!** realizar el respaldo y La generacion de los archivos planos para los  **
!** reportes fiscales. Este programa realiza una espera de 1 minuto       **
!** para darle tiempo al proceso del cierre de que actualice el archivo   **
!** EAMCSCF1, del cual se obtiene el nombre del log a procesar y a        **
!** respaldar.                                                            **
!***************************************************************************


INTEGER*2 RETURN.SMALL

FUNCTION ADXSTART (NAME$,PARM$,MESS$) EXTERNAL
      INTEGER*2 ADXSTART
      STRING NAME$,PARM$,MESS$
END FUNCTION

FUNCTION OSSHELL(cmd.line$) EXTERNAL			                 ! routine to start
							                                     ! another program.
           INTEGER*4    OSSHELL				                     ! Upon completion of
           STRING       cmd.line$			                     ! program, control is
							                                     ! returned to calling
END FUNCTION						                             ! program.

!*********************************************
!**          PROGRAMA PRINCIPAL             **
!*********************************************

WAIT;60000
RETURN.SMALL = ADXSTART ("ADX_UPGM:RESPALDO.286"," ","Respaldo Informacion")
RETURN.SMALL = ADXSTART ("ADX_UPGM:UDSAINFO.286"," ","Generacion de Archivos de Ventas")
WAIT;600000
RETURN.SMALL = OSSHELL("ADX_UPGM:UDAUTOMA.BAT")
