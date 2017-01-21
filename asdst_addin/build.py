from os.path import split, join
from os import system, getcwd
from shutil import copyfile

# Location of ESRIRegAddIn.exe
# esri = "C:/Program Files (x86)/Common Files/ArcGIS/bin/ESRIRegAddIn.exe"
cwd = getcwd()
mapdoc = r"C:\Data\asdst_test\test.mxd"

# Close ArcMap if it is open
try:
    system("TASKKILL /F /IM ArcMap.exe")
except:
    pass

# Create ESRI Add-in file
system("C:\Python27\ArcGIS10.4\python.exe " + join(cwd, "makeaddin.py"))

# Silently install Add-in file.
# The name of the file is based on folder it's located in.
# system('"{0}" {1} /s'.format(esri, split(cwd)[-1] + ".esriaddin"))

fn1 = split(cwd)[-1] + ".esriaddin"
fn2 = r"C:\Users\aspire\Documents\ArcGIS\AddIns\Desktop10.4\asdst_addin.esriaddin"
copyfile(fn1, fn2)

# Open test map document.
system(mapdoc)
