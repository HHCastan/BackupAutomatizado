#######################################################################
#
# (C) COPYRIGHT Almacenes Flamingo S.A.
# Hace ping a todas las tiendas
# Ejecutar en controlador: python2 -X4690shell pingPOS.py
# Autor: hugo.castaneda@flamingo.com.co
# Fecha: Junio de 2021   

#######################################################################

import shutil
import os
import time
import ntpath
import glob
import flFuncts

# Varibles de trabajo:
workDir		= 'C:/'	                                # Carpeta de trabajo
fecha		= time.strftime("%Y%m%d")				# Fecha actual
hora		= time.strftime("%H%M%S")				# Hora actual
sourceDir   = 'C:/'                                 # Directorio de inicio

logFileName	= sourceDir + 'pingPOS.log'	            # Nombre del archivo para la huella del proceso

# Crea archivo huella de ejecuion:
logFile = open(logFileName, "w")

logFile.write("INICIANDO pingPOS EN :" + fecha + ' ' + hora + '\n')


resultado = flFuncts.ping('172.16.161.49')
print resultado

hora = time.strftime("%H%M%S")
logFile.write('FINAL COPIA EN: ' + fecha + ' ' + hora + '\n')

# Cierra el archivo log:
logFile.close
