STRING FILENAME$,FECHA$,AUX$,LOGNAME$,ERRORSTRING$
INTEGER*4 I%,RETUADXS


!******************************************
!**Includes de librerias de definiciones **
!******************************************
%INCLUDE BASROUT.J86
%INCLUDE INT42HEX.R86
!******************************************

!************************
!** ADXSERVE subroutine *
!************************
SUB ADXSERVE (RET,FUNC,PARM1,PARM2) EXTERNAL
INTEGER*4 RET
INTEGER*2 FUNC,PARM1
STRING PARM2
END SUB
!*********************************************
!****************************************************************************
!*                           DETLOG                                         *
!****************************************************************************
!* Subprograma encargado de Determinar el Log de transacciones ha abrir     *
!****************************************************************************
FUNCTION DetLog$(Periodo)

String  Terminal,Slogname,Oslogname,Closepnt,DataTime,Bakup,reserved,Periodo,DetLog$

 Open "EAMCSCF1" Keyed Recl 36 As 75 NoWrite NoDel
 Read Form "C2,2C8,C4,C5,C1,C8";#75 Key Pack$("9998"); \
      Terminal,Slogname,Oslogname,Closepnt,DataTime,Bakup,reserved
 Close 75
 If Val(Periodo) = 1 Then Begin
 	DetLog$ = SlogName
 Endif Else Begin 
	DetLog$ = OslogName
 Endif
 FECHA$ = UNPACK$(DATATIME)
End FUNCTION
!*********************************************************************

FUNCTION NALMACEN$
STRING NALMACEN$,NRO.ALMACEN$
	OPEN "ALMACEN" AS 43
	READ #43; LINE NRO.ALMACEN$
	CLOSE 43
	NRO.ALMACEN$ = "0" + MID$(NRO.ALMACEN$,1,2)
	NALMACEN$ = NRO.ALMACEN$
END FUNCTION



!**************************************
!**        PROGRAMA PRINCIPAL        **
!** RESPALDO DEL LOG DE TRANSACIONES **
!**************************************

ON ERROR GOTO CONTROLERROR

CLEARS
CONSOLE
LOCATE 1,1
FILENAME$ = "adx_idt4:" + DetLog$("2") + ".dat"
FECHA$ = MID$(FECHA$,5,2) + MID$(FECHA$,3,2) + MID$(FECHA$,1,2)
LOGNAME$ = "C:\RESPALDO\LOGTRX\LG" + FECHA$ + "." + NALMACEN$
CALL ADXSERVE(RETUADXS,26,0,"Respaldo Log de Trxs: " + LOGNAME$)
WAIT;1
IF (RETUADXS < 0) THEN BEGIN
    PRINT "Error en llamada ADXSERVE: ";RETUADXS
ENDIF
PRINT "Respaldo Log de Trxs: " + LOGNAME$ 
I%=osshell("DEL C:\RESPALDO\LOGTRX\LG*.*" )
I%=osshell("COPY " + FILENAME$ + " " + LOGNAME$ )

!** Respaldo de Archivos de Saldos y Ordenes **
CALL ADXSERVE(RETUADXS,26,0,"Respaldo Saldos y Ordenes ... ")
WAIT;1
IF (RETUADXS < 0) THEN BEGIN
    PRINT "Error en llamada ADXSERVE: ";RETUADXS
ENDIF
PRINT "Respaldo Saldos y Ordenes ... "
I%=osshell("DEL C:\RESPALDO\UFSALDOS.ZOL")
I%=osshell("REN C:\RESPALDO\UFSALDOS.ZIP C:\RESPALDO\UFSALDOS.ZOL")
I%=osshell("DEL C:\RESPALDO\UFORDENS.ZOL")
I%=osshell("REN C:\RESPALDO\UFORDENS.ZIP C:\RESPALDO\UFORDENS.ZOL")
I%=osshell("ZIP C C:\RESPALDO\UFSALDOS.ZIP ADX_IDT1:UFSALDOS.DAT")
I%=osshell("ZIP C C:\RESPALDO\UFORDENS.ZIP ADX_IDT1:UFORDENS.DAT")
I%=osshell("DEL  C:\RESPALDO\OR*." + NALMACEN$ )
I%=osshell("DEL  C:\RESPALDO\SA*." + NALMACEN$ )
I%=osshell("COPY  C:\RESPALDO\UFORDENS.ZIP C:\RESPALDO\OR" + FECHA$ + "." + NALMACEN$ )
I%=osshell("COPY  C:\RESPALDO\UFSALDOS.ZIP C:\RESPALDO\SA" + FECHA$ + "." + NALMACEN$ )

CALL ADXSERVE(RETUADXS,26,0,"Proceso finalizado Satisfactoriamente!")
WAIT;1
IF (RETUADXS < 0) THEN BEGIN
    PRINT "Error en llamada ADXSERVE: ";RETUADXS
ENDIF
PRINT "Proceso finalizado Satisfactoriamente!"
STOP

CONTROLERROR:
	ERRORSTRING$ = ERR + "," + STR$(ERRN) + "," + STR$(ERRF%)
	CALL ADXSERVE(RETUADXS,26,0,"Error: " + ERRORSTRING$)
	WAIT;1
	IF (RETUADXS < 0) THEN BEGIN
	    PRINT "Error en llamada ADXSERVE: ";RETUADXS
	ENDIF
	PRINT ERRORSTRING$
	