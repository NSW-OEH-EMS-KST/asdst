from os.path import split, join
from os import system, getcwd
from shutil import copyfile

# Location of ESRIRegAddIn.exe
# esri = "C:/Program Files (x86)/Common Files/ArcGIS/bin/ESRIRegAddIn.exe"
cwd = getcwd()
mapdoc = r"c:\users\byed\projects\asdst\test\q.mxd"

# Close ArcMap if it is open
try:
    system("TASKKILL /F /IM ArcMap.exe")
except:
    pass

# Create ESRI Add-in file
system("C:\Python27\ArcGIS10.1\python.exe " + join(cwd, "makeaddin.py"))

# Silently install Add-in file.
# The name of the file is based on folder it's located in.
# system('"{0}" {1} /s'.format(esri, split(cwd)[-1] + ".esriaddin"))

fn1 = split(cwd)[-1] + ".esriaddin"
fn2 = "C:\\Users\\byed\\Documents\\ArcGIS\\AddIns\\Desktop10.1\\asdst_addin.esriaddin"
copyfile(fn1, fn2)

# Open test map document.
system(mapdoc)
