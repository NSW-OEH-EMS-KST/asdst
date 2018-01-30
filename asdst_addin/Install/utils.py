from __future__ import print_function
import arcpy
from arcpy import mapping
# from config import get_system_config
from os.path import split


def geodata_exists(item):
    try:
        return arcpy.Exists(item)
    except:
        return False


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


def get_dataframe_spatial_reference(mxd=None):

    if not mxd:
        mxd = mapping.MapDocument("CURRENT")

    df = mapping.ListDataFrames(mxd)[0]

    return df.spatialReference


def set_dataframe_spatial_reference(code, messages):

    mxd = arcpy.mapping.MapDocument("CURRENT")
    df = arcpy.mapping.ListDataFrames(mxd)[0]
    sr = arcpy.SpatialReference(code)
    df.spatialReference = sr

    msg = "Dataframe Spatial Reference has been set to '{}'".format(sr.name)
    if messages:
        messages.addMessage(msg)

    return


def get_layer_datasources(mxd=None):

    if not mxd:
        mxd = mapping.MapDocument("CURRENT")
    elif isinstance(mxd, basestring):
        mxd = mapping.MapDocument(mxd)

    return {layer.name: layer.dataSource for layer in mapping.ListLayers(mxd) if hasattr(layer, "dataSource")}


def add_group_layers(layer_names, group_name, configuration, messages=None, add_position="BOTTOM"):

    mxd = arcpy.mapping.MapDocument("CURRENT")
    df = arcpy.mapping.ListDataFrames(mxd)[0]

    if group_name:  # try to find the parentgroup
        lyrs = arcpy.mapping.ListLayers(mxd, group_name, df)
        glyr = lyrs[0] if lyrs else None
        if not glyr:  # not found, so create it
            glyr = arcpy.mapping.Layer(configuration["empty_group_layer"])
            glyr.name = group_name
            arcpy.mapping.AddLayer(df, glyr, add_position)
            if messages:
                messages.AddMessage("Added {} to {}".format(glyr.name, df.name))
            arcpy.RefreshTOC()

        # this line is required, arc must add a deep copy or something?
        # anyway without this there is an exception raised
        glyr = arcpy.mapping.ListLayers(mxd, group_name, df)[0]

    lyrs = arcpy.mapping.ListLayers(mxd, None, df)
    lyr_names = [l.name for l in lyrs]

    for layer_name in layer_names:
        if layer_name in lyr_names:
            continue
        lyr = arcpy.mapping.Layer(configuration["empty_group_layer"])
        lyr.name = layer_name
        arcpy.mapping.AddLayerToGroup(df, glyr, lyr, add_position)
        if messages:
            messages.AddMessage("Added {} to {} under {}".format(lyr.name, df.name, glyr.name))
        arcpy.RefreshTOC()

    return


def add_layers_to_mxd(layers, group_name, layer_type, configuration, messages=None, add_position="BOTTOM"):
    # layers is a {name: datasource} dictionary

    mxd = arcpy.mapping.MapDocument("CURRENT")
    df = arcpy.mapping.ListDataFrames(mxd)[0]

    lyr_file = configuration["empty_layers"].get(layer_type, None)
    glyr = None

    if group_name:  # try to find the group
        lyrs = arcpy.mapping.ListLayers(mxd, group_name, df)
        glyr = lyrs[0] if lyrs else None
        if not glyr:  # not found, so create it
            glyr = arcpy.mapping.Layer(configuration["empty_group_layer"])
            glyr.name = group_name
            arcpy.mapping.AddLayer(df, glyr, add_position)
            if messages:
                messages.AddMessage("Added {} to {}".format(glyr.name, df))
            arcpy.RefreshTOC()

        # this line is required, arc must add a deep copy or something?
        # anyway without this there is an exception raised
        glyr = arcpy.mapping.ListLayers(mxd, group_name, df)[0]

    for k, v in layers.iteritems():

        if not lyr_file:
            lyr = arcpy.mapping.Layer(v)
        else:
            lyr = arcpy.mapping.Layer(lyr_file)
            p, n = split(v)
            lyr.replaceDataSource(p, "FILEGDB_WORKSPACE", n, validate=True)

        lyr.name = k

        if glyr:
            arcpy.mapping.AddLayerToGroup(df, glyr, lyr, add_position)
            if messages:
                msg = "'{}' layer added to group '{}'".format(lyr.name, glyr.name)  #, mxd.filePath)
                messages.AddMessage(msg)
        else:
            arcpy.mapping.AddLayer(df, lyr, add_position)
            if messages:
                msg = "'{}' layer added to {}".format(lyr.name, mxd.filePath)
                messages.AddMessage(msg)

    arcpy.RefreshTOC()
    # mxd.save()

    return


def add_table_to_mxd(table, name="", messages=None):

    mxd = arcpy.mapping.MapDocument("CURRENT")
    df = arcpy.mapping.ListDataFrames(mxd)[0]
    tv = arcpy.mapping.TableView(table)
    if name:
        tv.name = name

    arcpy.mapping.AddTableView(df, tv)
    if messages:
        msg = "'{}' table added to {}".format(name or tv.name, mxd.filePath)
        messages.addMessage(msg)

    arcpy.RefreshTOC()
    mxd.save()

    return

