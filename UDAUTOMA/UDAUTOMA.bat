echo off
REM ----------------------------------------------------------------------------
REM (c) ALMACENES FLAMINGO
REM UDAUTOMA.BAT
REM AUTOR: hugo.castaneda@flamingo.com.com
REM FECHA: ENERO 19 DE 2017
REM ----------------------------------------------------------------------------
REM UTILIDADES ATADAS AL CIERRE DE TEINDA
REM ----------------------------------------------------------------------------

REM ----------------------------------------------------------------------------
REM ACTUALIZA TIENDAS.JSON DESDE INFORMESPOS:
REM ------------------------
BATCH M:\RESPALDO\TIENDAS.BAT

REM ----------------------------------------------------------------------------
REM RESPALDO DIARIO DE JOURNALS AL CENTRAL:
REM ------------------------
BATCH M:\RESPALDO\RESPJOURNAL.BAT

REM ----------------------------------------------------------------------------
REM RESPALDO DIARIO DE ARCHIVOS SENCIBLES:
REM ----------------------------------------------------------------------------
BATCH M:\RESPALDO\BACKUP.BAT

REM ----------------------------------------------------------------------------
REM RESPALDO DIARIO DE ARCHIVOS PLANOS VTAx:
REM ----------------------------------------------------------------------------
BATCH M:\RESPALDO\RESPVTA.BAT  >> c:\lds\log\respvta.log

REM ----------------------------------------------------------------------------
REM RESPALDO DIARIO DE ARCHIVOS FPS:
REM ----------------------------------------------------------------------------
BATCH M:\RESPALDO\RESPFPS.BAT

REM ----------------------------------------------------------------------------
REM RESPALDO DIARIO DEL TLOG:
REM ----------------------------------------------------------------------------
BATCH M:\RESPALDO\RESPTLOG.BAT

REM ----------------------------------------------------------------------------
REM RESPALDO DIARIO DE SALDOS:
REM ----------------------------------------------------------------------------
BATCH M:\RESPALDO\RESPSALD.BAT

REM ----------------------------------------------------------------------------
REM RESPALDO DIARIO DE JSON FE:
REM ----------------------------------------------------------------------------
BATCH M:\RESPALDO\RESPJSONFE.BAT
