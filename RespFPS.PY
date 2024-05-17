#######################################################################
#
# (C) COPYRIGHT Almacenes Flamingo S.A.
# Respalda archivos de la carpeta FPS en C:\FPS\BAK
# Ejecutar en controlador: python2 -X4690shell RespFPS.py
# Autor: hugo.castaneda@flamingo.com.co
# Fecha: Julio de 2017   

#######################################################################

import shutil
import os
import time
import ntpath
import glob

# Varibles de trabajo:
workDir		= 'C:/FPS/BACKUP/'	                    # Carpeta de trabajo
fecha		= time.strftime("%Y%m%d")				# Fecha actual
hora		= time.strftime("%H%M%S")				# Hora actual
sourceDir   = 'C:/FPS/'                             # Directorio FPS

logFileName	= sourceDir + 'backup.log'	            # Nombre del archivo para la huella del proceso

# Crea archivo huella de ejecuion:
logFile = open(logFileName, "w")

logFile.write("INICIANDO BACKUP EN :" + fecha + ' ' + hora + '\n')

# Respalda todos los archivo .DAT de C:/FPS:
fps_files = '*.DAT'
sourceDir = 'C:/FPS/'
fileList = glob.glob('C:/FPS/*.dat')

# Si no existe el directorio destino, lo crea
if os.path.exists(workDir):
	pass
else:
	os.makedirs(workDir, 0750)

# Agrega subcarpeta destino:
workDirOut = workDir + fecha + '/'

# Si no existe el directorio destino, lo crea
if os.path.exists(workDirOut):
	pass
else:
	os.makedirs(workDirOut, 0750)			

# Incia la respaldo
for fileX in fileList:
	if os.path.isfile(fileX):
		fileName = ntpath.basename(fileX)

		destino = workDirOut + fileName
		logFile.write('Copia: ' + fileX + ' ' + destino + '\n')
		# Captura posibles errores y continua con los otros archivos
		try:
			shutil.copyfile(fileX, destino)
			logFile.write('Copiado ' + fileX + ' a ' + destino + '\n')
		except (IOError, os.error) as why:
			logFile.write('Error: No se puede copiar  ' + fileX + ' ' + str(why) + '\n')
			os.system('copy ' + fileX + ' ' + destino)
			logFile.write('Archivo copiado por llamado al sistema. Ignorar error anterior\n')
	else:
		logFile.write('No existe archivo a enviar\n')
	

hora = time.strftime("%H%M%S")
logFile.write('FINAL COPIA EN: ' + fecha + ' ' + hora + '\n')

# Cierra el archivo log:
logFile.close
