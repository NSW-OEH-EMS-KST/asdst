from __future__ import print_function
import log
import arcpy
from arcpy import mapping
# import pythonaddins
import os
# from asdst_addin import get_system_config


def get_dataframe_spatial_reference(mxd=None):

    if not mxd:
        mxd = mapping.MapDocument("CURRENT")

    df = mapping.ListDataFrames(mxd)[0]

    return df.spatialReference


# def get_project_gdb(mxd=None):
#
#     if not mxd:
#         mxd = mapping.MapDocument("CURRENT")
#
#     return mxd.filePath.replace(".mxd", ".gdb")
#
#
# def get_appdata_path():
#
#     return os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "ASDST")
#

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


def set_dataframe_spatial_reference(code, messages):

    mxd = arcpy.mapping.MapDocument("CURRENT")
    df = arcpy.mapping.ListDataFrames(mxd)[0]
    sr = arcpy.SpatialReference(code)
    df.spatialReference = sr

    msg = "Dataframe Spatial Reference has been set to '{}'".format(sr.name)
    if messages:
        messages.addMessage(msg)

    return

#
# def get_dataframe_spatial_reference():
#
#     mxd = arcpy.mapping.MapDocument("CURRENT")
#     df = arcpy.mapping.ListDataFrames(mxd)[0]
#     sr = df.spatialReference
#     df.spatialReference = sr
#
#     return sr


def valid_gdb_and_srs():

    mxd = mapping.MapDocument("CURRENT")

    gdb = get_project_gdb(mxd)

    gdb_ok = geodata_exists(gdb)

    srs_3308 = get_dataframe_spatial_reference(mxd).factoryCode == 3308

    valid = gdb_ok and srs_3308

    return valid


def get_layer_datasources(mxd=None):

    if not mxd:
        mxd = mapping.MapDocument("CURRENT")
    elif isinstance(mxd, basestring):
        mxd = mapping.MapDocument(mxd)

    return {layer.name: layer.dataSource for layer in mapping.ListLayers(mxd) if hasattr(layer, "dataSource")}


# def get_map_config(mxd=None):
#
#     if not mxd:
#         mxd = mapping.MapDocument("CURRENT")
#     elif isinstance(mxd, basestring):
#         mxd = mapping.MapDocument(mxd)
#
#     df = arcpy.mapping.ListDataFrames(mxd)[0]
#
#     layers = arcpy.mapping.ListLayers(mxd, None, df)
#     layers = [layer for layer in layers if not layer.isGroupLayer]
#
#     gdb = get_project_gdb(mxd)
#
#     return {"srs_code": df.spatialReference.factoryCode,
#             "non_group_layer_count": len(layers),
#             "gdb": gdb}


# def add_layers_to_mxd(mxd, layers, group_name, layer_type, messages=None):
#     # layers is a {name: datasource} dictionary
#
#     if isinstance(mxd, basestring):
#         mxd = arcpy.mapping.MapDocument(mxd)
#
#     df = arcpy.mapping.ListDataFrames(mxd)[0]
#     configuration = get_system_config()
#     lyr_file = configuration["empty_layers"].get(layer_type, None)
#     glyr = None
#
#     if group_name:  # try to find the group
#         lyrs = arcpy.mapping.ListLayers(mxd, group_name, df)
#         glyr = lyrs[0] if lyrs else None
#         if not glyr:  # not found, so create it
#             log.debug("Creating group layer '{}".format(group_name))
#             glyr = arcpy.mapping.Layer(configuration["empty_group_layer"])
#             glyr.name = group_name
#             arcpy.mapping.AddLayer(df, glyr)
#             log.debug("New group layer added")
#         # this line is required, arc must add a deep copy or something?
#         # anyway without this there is an exception raised
#         glyr = arcpy.mapping.ListLayers(mxd, group_name, df)[0]
#
#     for k, v in layers.iteritems():
#
#         if not lyr_file:
#             lyr = arcpy.mapping.Layer(v)
#         else:
#             lyr = arcpy.mapping.Layer(lyr_file)
#             p, n = os.path.split(v)
#             lyr.replaceDataSource(p, "FILEGDB_WORKSPACE", n, validate=True)
#
#         lyr.name = k
#
#         if glyr:
#             arcpy.mapping.AddLayerToGroup(df, glyr, lyr)
#             msg = "'{0}' layer added to group '{1}'".format(lyr.name, glyr.name)
#             log.debug(msg)
#             if messages:
#                 messages.addMessage(msg)
#         else:
#             arcpy.mapping.AddLayer(df, lyr)
#             msg = "'{0}' layer added".format(lyr.name)
#             log.debug(msg)
#             if messages:
#                 messages.addMessage(msg)
#
#     return

def add_layers_to_mxd(layers, group_name, layer_type, messages=None):
    # layers is a {name: datasource} dictionary

    mxd = arcpy.mapping.MapDocument("CURRENT")
    df = arcpy.mapping.ListDataFrames(mxd)[0]
    configuration = get_system_config()
    lyr_file = configuration["empty_layers"].get(layer_type, None)
    glyr = None

    if group_name:  # try to find the group
        lyrs = arcpy.mapping.ListLayers(mxd, group_name, df)
        glyr = lyrs[0] if lyrs else None
        if not glyr:  # not found, so create it
            # self.info("Creating group layer '{}".format(group_name))
            glyr = arcpy.mapping.Layer(configuration["empty_group_layer"])
            glyr.name = group_name
            arcpy.mapping.AddLayer(df, glyr)
            # self.info("New group layer added")
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
            arcpy.mapping.AddLayerToGroup(df, glyr, lyr, "AUTO_ARRANGE")
            if messages:
                msg = "'{}' layer added to group '{}' in {}".format(lyr.name, glyr.name, mxd.filePath)
                messages.addMessage(msg)
        else:
            arcpy.mapping.AddLayer(df, lyr, "AUTO_ARRANGE")
            if messages:
                msg = "'{}' layer added to {}".format(lyr.name, mxd.filePath)
                messages.addMessage(msg)

    arcpy.RefreshTOC()
    mxd.save()

    return

# def add_table_to_mxd(mxd, table, name="", messages=None):
#
#     if isinstance(mxd, basestring):
#         mxd = arcpy.mapping.MapDocument(mxd)
#
#     df = arcpy.mapping.ListDataFrames(mxd)[0]
#     tv = arcpy.mapping.TableView(table)
#     if name:
#         tv.name = name
#
#     arcpy.mapping.AddTableView(df, tv)
#     msg = "Table '{}' added".format(name or tv.name)
#     log.debug(msg)
#     if messages:
#         messages.addMessage(msg)
#
#     return

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


# def get_user_config():
#
#     config_file = get_config_path_and_file()[1]
#     try:
#         with open(config_file, 'r') as f:
#             usr_cfg = load(f)
#     except (IOError, OSError, ValueError):
#         usr_cfg = get_default_user_config()
#
#     return usr_cfg


# def get_config():
#
#     cfg = get_system_config()
#     cfg.update(get_user_config())
#
#     return cfg


# def get_asdst_data_status(pretty=False):
#
#     mxd = arcpy.mapping.MapDocument("CURRENT")
#     gdb = utils.get_project_gdb(mxd)
#
#     layer_status = []
#     for k, v in get_layer_map(gdb).iteritems():
#
#         layer_status.append(utils.exists_return_3tuple("{} 1750".format(k), v["1750_local"]))
#
#         layer_status.append(utils.exists_return_3tuple("{} Current".format(k), v["curr_local"]))
#
#     if not pretty:
#         return layer_status
#
#     valid = asdst_data_is_valid(layer_status)
#
#     layer_status = make_status_pretty(layer_status)
#
#     layer_status = u"{}\nDATA CONFIGURATION {}\n".format(layer_status, [u"\u2716", u"\u2714"][valid])  # dashes) + config_status + "\n"
#
#     return layer_status

# def get_toolbox():
#
#     script_path = dirname(realpath(__file__))
#     toolbox = join(script_path, "asdst.pyt")
#
#     if not utils.geodata_exists(toolbox):
#         raise ValueError("ASDST Toolbox not found : " + toolbox)
#
#     return toolbox
#
#
# # def exists_return_3tuple(description, item):
# #
# #     return [description, item, geodata_exists(item)]
# #
# #
# def get_config_path_and_file():
#
#     p = join(environ["USERPROFILE"], "AppData", "Local", "ASDST")
#     try:
#         makedirs(p)
#     except (IOError, OSError):
#         pass
#
#     fn = join(p, "asdst_config.json")
#     open(fn, 'a').close()
#
#     # print locals()
#
#     return p, fn
#
#
# def get_default_user_config():
#
#     appdata_path, config_file = get_config_path_and_file()
#     source_fgdb = join(appdata_path, "asdst_source.gdb")
#     template_mxd = join(appdata_path, "asdst_default.mxd")
#     ahims_sites = ""
#     config = locals()
#     print config
#     with open(config_file, 'w') as f:
#         dump(config, f)
#
#     return config
#
#
# def get_system_config():
#
#     script_path = dirname(realpath(__file__))
#
#     toolbox = join(script_path, "asdst.pyt")
#
#     template_project_gdb = join(script_path, "project.gdb")
#
#     template_context_gdb = join(script_path, "context.gdb")
#
#     empty_group_layer = join(script_path, "egl.lyr")
#     empty_model_layer = join(script_path, "eml.lyr")
#     empty_relia_layer = join(script_path, "erl.lyr")
#     empty_accim_layer = join(script_path, "eai.lyr")
#     empty_regio_layer = join(script_path, "eas.lyr")
#     empty_prior_layer = join(script_path, "esp.lyr")
#     empty_polyf_layer = join(script_path, "epf.lyr")
#     empty_layers = {"group": empty_group_layer,
#                     "model": empty_model_layer,
#                     "relia": empty_relia_layer,
#                     "accim": empty_accim_layer,
#                     "regio": empty_regio_layer,
#                     "prior": empty_prior_layer,
#                     "polyf": empty_polyf_layer}
#
#     appdata_path = get_config_path_and_file()[0]
#
#     log_file = join(appdata_path, "asdst.log")
#
#     return locals()
