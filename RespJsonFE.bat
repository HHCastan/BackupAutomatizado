echo off
REM ----------------------------------------------------------------------------
REM (c) ALMACENES FLAMINGO
REM RESPJSONFE.BAT
REM AUTOR: hugo.castaneda@flamingo.com.com
REM FECHA: ABRIL 05 DE 2016
REM ----------------------------------------------------------------------------
REM UTILIDADE PARA LANZAR EL RESPALDO DE LOS PLANOS VTA AL CENTRAL
REM ----------------------------------------------------------------------------

M:
CD M:/RESPALDO
adx_spgm:python3 -X4690shell RespJsonFE.py
