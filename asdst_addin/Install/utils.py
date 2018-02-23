from __future__ import print_function
import arcpy
from arcpy import mapping
from os import environ, makedirs
from os.path import split, join, realpath, dirname, exists
from json import load, dump
# from config import get_codes


# codes
def get_codes():
    return dict(AFT="Stone artefact", ART="Rock art", BUR="Burial", ETM="Earth mound", GDG="Grinding groove",
                HTH="Hearth or camp fire feature", SHL="Shell midden", STQ="Stone quarry", TRE="Scarred tree")


# extended codes
def get_codes_ex():
    return dict(ACD="Aboriginal ceremony and dreaming", ARG="Aboriginal resource gathering",
                AFT="Stone artefact", ART="Rock art", BUR="Burial", CFT="Conflict site",
                CMR="Ceremonial ring", ETM="Earth mound", FSH="Fish trap", GDG="Grinding groove",
                HAB="Habitation structure", HTH="Hearth or camp fire feature", OCQ="Ochre quarry",
                PAD="Potential archaeological deposit", SHL="Shell midden", STA="Stone arrangement",
                STQ="Stone quarry", TRE="Scarred tree", WTR="Water feature")


def get_appdata_path():
    return join(environ["USERPROFILE"], "ASDST")


def set_user_config(source_fgdb, template_mxd, ahims_sites):

    CONFIG = {"source_fgdb": source_fgdb, "template_mxd": template_mxd, "ahims_sites": ahims_sites}
    config_file = get_user_config_file()

    with open(config_file, 'w') as f:
        dump(CONFIG, f)

    m = "{}\nwritten to\n{}".format(CONFIG, config_file)
    print(m)

    return


def get_user_config_file():
    print("UserConfig.get_config_file()")

    p = join(get_appdata_path(), "system")
    fn = join(p, "user_config.json")

    if not exists(fn):
        print("User system_config file '{}' does not exist".format(fn))
        if not exists(p):
            makedirs(p)
            print("ASDST system path '{}' created".format(p))

        open(fn, 'a').close()  # any exception will be raised
        print("User system_config file '{}' created".format(fn))

        set_user_config("", "", "")

    print("\treturning {}".format(fn))

    return fn


def get_user_config():
    config_file = get_user_config_file()

    with open(config_file, 'r') as f:
        return load(f)


def get_source_gdb():

    return get_user_config()["source_fgdb"]


def get_layer_map(local_workspace):

    source_ws = get_source_gdb()

    if not source_ws:
        source_ws = "X:\\NOT_SET"

    if not local_workspace:
        local_workspace = "X:\\NOT_SET"

    d = {k: {"name": v,
             "1750_source": (join(source_ws, k.lower() + "_v7")),
             "1750_local": (join(local_workspace, k.lower() + "_1750")),
             "curr_local": (join(local_workspace, k.lower() + "_curr"))}
         for k, v in get_codes().iteritems()}

    # for k, v in d.iteritems():
    #     print(k, v)
    #     try:
    #         for x, y in y.iteritems():
    #             print(x, y)
    #     except:
    #         pass

    return d

# def read_asdst_system_config_from_file():
#     print("utils.read_asdst_system_config_from_file")
#
#     fn = join(environ["USERPROFILE"], "ASDST", "system", "system_config.json")
#
#     if not exists(fn):
#         print("User system_config file '{}' does not exist".format(fn))
#         return {}
#
#     with open(fn, 'r') as f:
#         cfg = load(f)
#
#     return cfg or {}


def get_toolbox():

    return join(dirname(realpath(__file__)), "asdst.pyt")


def get_template_layers():

    script_path = dirname(realpath(__file__))

    layers = {"empty_group_layer": "egl.lyr",
              "empty_model_layer": "eml.lyr",
              "empty_relia_layer": "erl.lyr",
              "empty_accim_layer": "eai.lyr",
              "empty_regio_layer": "eas.lyr",
              "empty_prior_layer": "esp.lyr",
              "empty_polyf_layer": "epf.lyr"}

    return {k: join(script_path, v) for k, v in layers.iteritems()}


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
            glyr.visible = False
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
        lyr.visible = False
        arcpy.mapping.AddLayerToGroup(df, glyr, lyr, add_position)
        if messages:
            messages.AddMessage("Added {} to {} under {}".format(lyr.name, df.name, glyr.name))
        arcpy.RefreshTOC()

    return


def add_layers_to_mxd(layers, group_name, layer_type, template_layers, messages=None, add_position="BOTTOM"):
    # layers is a {name: datasource} dictionary

    mxd = arcpy.mapping.MapDocument("CURRENT")
    df = arcpy.mapping.ListDataFrames(mxd)[0]

    lyr_file = template_layers.get(layer_type, None)
    glyr = None

    if group_name:  # try to find the group
        lyrs = arcpy.mapping.ListLayers(mxd, group_name, df)
        glyr = lyrs[0] if lyrs else None
        if not glyr:  # not found, so create it
            glyr = arcpy.mapping.Layer(template_layers["empty_group_layer"])
            glyr.name = group_name
            glyr.visible = False
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

