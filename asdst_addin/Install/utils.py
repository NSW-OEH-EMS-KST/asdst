from __future__ import print_function
import log
import arcpy as ap
import arcpy.mapping as am
import pythonaddins as pa
import os


def get_appdata_path():
    return os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "ASDST")


@log.log
def geodata_exists(item):
    try:
        return ap.Exists(item)
    except:
        return False


@log.log
def exists_return_tuple(description, item):
    return [description, item, geodata_exists(item)]


@log.log
def add_table_to_mxd(mxd, table, name="", messages=None):
    df = am.ListDataFrames(mxd)[0]
    tv = am.TableView(table)
    if name:
        tv.name = name

    am.AddTableView(df, tv)
    msg = "Table '{}' added".format(name or tv.name)
    log.debug(msg)
    if messages:
        messages.AddMessage(msg)

    return


@log.log
def add_layers_to_mxd(mxd, layers, group_name, layer_type, messages=None):
    # layers is a {name: datasource} dictionary

    if isinstance(mxd, basestring):
        mxd = am.MapDocument(mxd)

    df = am.ListDataFrames(mxd)[0]
    configuration = get_asdst_config()
    lyr_file = configuration["empty_layers"].get(layer_type, None)
    glyr = None

    if group_name:  # try to find the group
        lyrs = am.ListLayers(mxd, group_name, df)
        glyr = lyrs[0] if lyrs else None
        if not glyr:  # not found, so create it
            log.debug("Creating group layer '{}".format(group_name))
            glyr = am.Layer(configuration["empty_group_layer"])
            glyr.name = group_name
            am.AddLayer(df, glyr)
            log.debug("New group layer added")
        # this line is required, arc must add a deep copy or something?
        # anyway without this there is an exception raised
        glyr = am.ListLayers(mxd, group_name, df)[0]

    for k, v in layers.iteritems():

        if not lyr_file:
            lyr = am.Layer(v)
        else:
            lyr = am.Layer(lyr_file)
            p, n = os.path.split(v)
            lyr.replaceDataSource(p, "FILEGDB_WORKSPACE", n, validate=True)

        lyr.name = k

        if glyr:
            am.AddLayerToGroup(df, glyr, lyr)
            msg = "'{0}' layer added to group '{1}'".format(lyr.name, glyr.name)
            log.debug(msg)
            if messages:
                messages.AddMessage(msg)
        else:
            am.AddLayer(df, lyr)
            msg = "'{0}' layer added".format(lyr.name)
            log.debug(msg)
            if messages:
                messages.AddMessage(msg)

    return


@log.log
def compact_fgdb(gdb):
    from glob import glob
    from os.path import getsize

    sz = 0
    mb = 1024 * 1024

    if gdb and ap.Exists(gdb):
        for f in glob(gdb + "\\*"):
            sz += getsize(f)
        sz /= mb

    return "Size of database '{0}' is ~ {1} MB".format(gdb, sz)


def set_dataframe_spatial_reference(code, messages):
    mxd = am.MapDocument("CURRENT")
    df = am.ListDataFrames(mxd)[0]
    sr = ap.SpatialReference(code)
    df.spatialReference = sr

    msg = "Dataframe Spatial Reference has been set to '{}'".format(sr.name)
    if messages:
        messages.AddMessage(msg)
    else:
        pa.MessageBox(msg, "ASDST Extension")

    return


def get_dataframe_spatial_reference():
    mxd = am.MapDocument("CURRENT")
    df = am.ListDataFrames(mxd)[0]
    sr = df.spatialReference
    df.spatialReference = sr

    return sr



