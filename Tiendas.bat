echo off
REM ----------------------------------------------------------------------------
REM (c) ALMACENES FLAMINGO
REM TIENDAS.BAT
REM AUTOR: hugo.castaneda@flamingo.com.com
REM FECHA: NOVIEMBRE DE 2021
REM ----------------------------------------------------------------------------
REM UTILIDAD PARA LANZAR ACTUALIZACIÓN DE TIENDAS.JSON
REM ----------------------------------------------------------------------------

f:
cd f:/respaldo
javaebin:java -jar /cdrive/f_drive/respaldo/tienda.jar
m:
copy f:\respaldo\Tiendas.JSON m:\respaldo\tiendas.JSON

