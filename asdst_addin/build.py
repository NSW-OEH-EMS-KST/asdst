from os.path import split, join, exists
from os import system, getcwd
from shutil import copyfile
from time import sleep, strftime
from shutil import rmtree
from tempfile import mkstemp
from shutil import move
from os import remove, close

# Location of ESRIRegAddIn.exe
# esri = "C:/Program Files (x86)/Common Files/ArcGIS/bin/ESRIRegAddIn.exe"

try:  # Close ArcMap if it is open
    system("TASKKILL /F /IM ArcMap.exe")
except:
    pass
sleep(1)

# print "deleting profile"
# prof_dir = "C:\\Users\\byed\\AppData\\Roaming\\ESRI"
# try:  # remove the profile !!
#     rmtree(prof_dir)
#     print "Removed {}".format(prof_dir)
# except:
#     pass

# print "deleting cache"
# cache_dir = r"C:\Users\byed\AppData\Local\ESRI\Desktop10.1\AssemblyCache\{A1CEE72A-50AA-317E-DB3E-FBAA3EBF2523}"
# try:  # remove the profile !!
#     rmtree(cache_dir)
#     print "Removed {}".format(cache_dir)
# except:
#     pass


def replace(file_path, pattern, subst):
    fh, abs_path = mkstemp()  # Create temp file
    with open(abs_path, 'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                if pattern in line:
                    new_file.write(subst + '\n')
                else:
                    new_file.write(line)
    close(fh)
    remove(file_path)  # Remove original file
    move(abs_path, file_path)  # Move new file

# update the system_config file with new date + time
cfg_file = r"C:\Data\asdst\asdst_addin\config.xml"
replace(cfg_file, "    <Date>", "    <Date>" + strftime("%Y-%m-%d %H:%M"))

# Create ESRI Add-in file
cwd = getcwd()
print "Building addin"
system("C:\Python27\ArcGIS10.4\python.exe " + join(cwd, "makeaddin.py"))
print "Addin built"
sleep(1)

# Silently install Add-in file.
# The name of the file is based on folder it's located in.
# system('"{0}" {1} /s'.format(esri, split(cwd)[-1] + ".esriaddin"))
print "Replacing files"
fn1 = split(cwd)[-1] + ".esriaddin"
udir = "C:\\Users\\byed\\"
if not exists(udir):
    udir = "C:\\Users\\aspire\\"
fn2 = join(udir, "Documents\\ArcGIS\\AddIns\\Desktop10.4\\asdst_addin.esriaddin")

copyfile(fn1, fn2)
print fn1, " files replaced with ", fn2
sleep(1)

# # Open test map document.
print "Re-opening ArcMap"
# mapdoc = r"C:\Data\asdst_test\test_1.mxd"
arcmap = 'c:\\"Program Files (x86)"\\ArcGIS\\Desktop10.4\\bin\\arcmap.exe'
system(arcmap)
# sleep(20)
# print "and closing again!!!"
# try:  # Close ArcMap if it is open
#     system("TASKKILL /F /IM ArcMap.exe")
# except:
#     pass
# sleep(2)
# print "and reopening again !!!@@#@@"
# system(mapdoc)
