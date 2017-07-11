from __future__ import print_function
import log
import arcpy
import arcpy.mapping
# import pythonaddins
import os
from asdst_addin import get_system_config

def get_appdata_path():

    return os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "ASDST")


def geodata_exists(item):
    try:
        return arcpy.Exists(item)
    except:
        return False


def exists_return_3tuple(description, item):

    return [description, item, geodata_exists(item)]


def compact_fgdb(gdb):

    from glob import glob
    from os.path import getsize

    sz = 0
    mb = 1024 * 1024

    if gdb and arcpy.Exists(gdb):
        for f in glob(gdb + "\\*"):
            sz += getsize(f)
        sz /= mb

    return "Size of database '{0}' is ~ {1} MB".format(gdb, sz)


def set_dataframe_spatial_reference(code, messages):

    mxd = arcpy.mapping.MapDocument("CURRENT")
    df = arcpy.mapping.ListDataFrames(mxd)[0]
    sr = arcpy.SpatialReference(code)
    df.spatialReference = sr

    msg = "Dataframe Spatial Reference has been set to '{}'".format(sr.name)
    if messages:
        messages.addMessage(msg)

    return


def get_dataframe_spatial_reference():

    mxd = arcpy.mapping.MapDocument("CURRENT")
    df = arcpy.mapping.ListDataFrames(mxd)[0]
    sr = df.spatialReference
    df.spatialReference = sr

    return sr


def add_layers_to_mxd(mxd, layers, group_name, layer_type, messages=None):
    # layers is a {name: datasource} dictionary

    if isinstance(mxd, basestring):
        mxd = arcpy.mapping.MapDocument(mxd)

    df = arcpy.mapping.ListDataFrames(mxd)[0]
    configuration = get_system_config()
    lyr_file = configuration["empty_layers"].get(layer_type, None)
    glyr = None

    if group_name:  # try to find the group
        lyrs = arcpy.mapping.ListLayers(mxd, group_name, df)
        glyr = lyrs[0] if lyrs else None
        if not glyr:  # not found, so create it
            log.debug("Creating group layer '{}".format(group_name))
            glyr = arcpy.mapping.Layer(configuration["empty_group_layer"])
            glyr.name = group_name
            arcpy.mapping.AddLayer(df, glyr)
            log.debug("New group layer added")
        # this line is required, arc must add a deep copy or something?
        # anyway without this there is an exception raised
        glyr = arcpy.mapping.ListLayers(mxd, group_name, df)[0]

    for k, v in layers.iteritems():

        if not lyr_file:
            lyr = arcpy.mapping.Layer(v)
        else:
            lyr = arcpy.mapping.Layer(lyr_file)
            p, n = os.path.split(v)
            lyr.replaceDataSource(p, "FILEGDB_WORKSPACE", n, validate=True)

        lyr.name = k

        if glyr:
            arcpy.mapping.AddLayerToGroup(df, glyr, lyr)
            msg = "'{0}' layer added to group '{1}'".format(lyr.name, glyr.name)
            log.debug(msg)
            if messages:
                messages.addMessage(msg)
        else:
            arcpy.mapping.AddLayer(df, lyr)
            msg = "'{0}' layer added".format(lyr.name)
            log.debug(msg)
            if messages:
                messages.addMessage(msg)

    return


def add_table_to_mxd(mxd, table, name="", messages=None):

    if isinstance(mxd, basestring):
        mxd = arcpy.mapping.MapDocument(mxd)

    df = arcpy.mapping.ListDataFrames(mxd)[0]
    tv = arcpy.mapping.TableView(table)
    if name:
        tv.name = name

    arcpy.mapping.AddTableView(df, tv)
    msg = "Table '{}' added".format(name or tv.name)
    log.debug(msg)
    if messages:
        messages.addMessage(msg)

    return

