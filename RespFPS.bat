echo off
REM ----------------------------------------------------------------------------
REM (c) ALMACENES FLAMINGO
REM RESPFPS.BAT
REM AUTOR: hugo.castaneda@flamingo.com.com
REM FECHA: ENERO 05 DE 2020
REM ----------------------------------------------------------------------------
REM UTILIDADE PARA LANZAR EL RESPALDO DE C:/FPS
REM ----------------------------------------------------------------------------


M:
CD M:/RESPALDO


REM Respalda los archivos de FPS:
adx_spgm:python2 -X4690shell RespFPS.py

