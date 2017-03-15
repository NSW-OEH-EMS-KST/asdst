import log
import arcpy as ap


@log.log
def exists_tuple(description, item):
    try:
        v = ap.Exists(item)
    except:
        v = False
    return [description, item, v]
