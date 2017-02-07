from os.path import split, join
from os import system, getcwd
from shutil import copyfile
from time import sleep, strftime
from shutil import rmtree

# shutil.rmtree('/folder_name')
# Location of ESRIRegAddIn.exe
# esri = "C:/Program Files (x86)/Common Files/ArcGIS/bin/ESRIRegAddIn.exe"
cwd = getcwd()
mapdoc = r"C:\Data\asdst_test\test.mxd"
prof_dir = r"C:\Users\byed\AppData\Roaming\ESRI\Desktop10.4\ArcMap"
rmtree(prof_dir)

try:  # Close ArcMap if it is open
    system("TASKKILL /F /IM ArcMap.exe")
except:
    pass
sleep(1)

# Create ESRI Add-in file
system("C:\Python27\ArcGIS10.4\python.exe " + join(cwd, "makeaddin.py"))
sleep(1)
# Silently install Add-in file.
# The name of the file is based on folder it's located in.
# system('"{0}" {1} /s'.format(esri, split(cwd)[-1] + ".esriaddin"))

fn1 = split(cwd)[-1] + ".esriaddin"
fn2 = r"C:\Users\byed\Documents\ArcGIS\AddIns\Desktop10.4\asdst_addin.esriaddin"
copyfile(fn1, fn2)
sleep(1)

# Open test map document.
system(mapdoc)
