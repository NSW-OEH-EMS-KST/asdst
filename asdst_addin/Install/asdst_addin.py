import arcpy
from arcpy import mapping
import pythonaddins
from os import environ, makedirs
from os.path import realpath, dirname, join, split
from json import load, dump

dashes = "-"*40 + "\n"


class AsdstExtension(object):

    def __init__(self):
        # print "AsdstExtension.__init__"

        _enable_tools()

        return

    def startup(self):
        # print "AsdstExtension.startup"

        _enable_tools()

        return

    def newDocument(self):
        # print "newDocument"

        _enable_tools()

        return

    def openDocument(self):
        # print "openDocument"

        _enable_tools()

        return

    def itemAdded(self, new_item):
        # print "itemAdded"

        _enable_tools()

        return

    def itemDeleted(self, deleted_item):
        # print "itemDeleted"

        _enable_tools()

        return


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


def geodata_exists(item):
    try:
        return arcpy.Exists(item)
    except:
        return False


def get_toolbox():

    script_path = dirname(realpath(__file__))
    toolbox = join(script_path, "asdst.pyt")

    if not geodata_exists(toolbox):
        raise ValueError("ASDST Toolbox not found : " + toolbox)

    return toolbox


def exists_return_3tuple(description, item):

    return [description, item, geodata_exists(item)]


class InfoButton(object):

    def onClick(self):

        pythonaddins.MessageBox(get_config_status(pretty=True), "ASDST Configuration")
        _enable_tools()

        return


class CalculateContextButton(object):

   def onClick(self):

        if asdst_data_is_valid():
            return pythonaddins.GPToolDialog(get_toolbox(), "ContextCalculationTool")
        else:
            return pythonaddins.MessageBox("Invalid configuration", "Context Calculation")


class CreateProjectButton(object):

    def onClick(self):

        if system_config_is_valid() and user_config_is_valid():
            return pythonaddins.GPToolDialog(get_toolbox(), "CreateProjectTool")
        else:
            return pythonaddins.MessageBox("Invalid configuration", "Create Project")


class BuildDataButton(object):

    def onClick(self):

        if system_config_is_valid() and user_config_is_valid() and map_config_is_valid():
            pythonaddins.GPToolDialog(get_toolbox(), "BuildDataTool")
        else:
            pythonaddins.MessageBox("Invalid configuration", "Build Data")

        return


class ConfigureButton(object):

    def onClick(self):

        return pythonaddins.GPToolDialog(get_toolbox(), "ConfigureTool")


def get_config_path_and_file():

    p = join(environ["USERPROFILE"], "AppData", "Local", "ASDST")
    try:
        makedirs(p)
    except (IOError, OSError):
        pass

    fn = join(p, "asdst_config.json")
    open(fn, 'a').close()

    # print locals()

    return p, fn


def get_default_user_config():

    appdata_path, config_file = get_config_path_and_file()
    source_fgdb = join(appdata_path, "asdst_source.gdb")
    template_mxd = join(appdata_path, "asdst_default.mxd")
    ahims_sites = ""
    config = locals()
    print config
    with open(config_file, 'w') as f:
        dump(config, f)

    return config


def get_system_config():

    script_path = dirname(realpath(__file__))

    toolbox = join(script_path, "asdst.pyt")

    template_project_gdb = join(script_path, "project.gdb")

    template_context_gdb = join(script_path, "context.gdb")

    empty_group_layer = join(script_path, "egl.lyr")
    empty_model_layer = join(script_path, "eml.lyr")
    empty_relia_layer = join(script_path, "erl.lyr")
    empty_accim_layer = join(script_path, "eai.lyr")
    empty_regio_layer = join(script_path, "eas.lyr")
    empty_prior_layer = join(script_path, "esp.lyr")
    empty_polyf_layer = join(script_path, "epf.lyr")
    empty_layers = {"group": empty_group_layer,
                    "model": empty_model_layer,
                    "relia": empty_relia_layer,
                    "accim": empty_accim_layer,
                    "regio": empty_regio_layer,
                    "prior": empty_prior_layer,
                    "polyf": empty_polyf_layer}

    appdata_path = get_config_path_and_file()[0]

    log_file = join(appdata_path, "asdst.log")

    return locals()


def get_map_config(mxd=None):

    if not mxd:
        mxd = mapping.MapDocument("CURRENT")
    elif isinstance(mxd, basestring):
        mxd = mapping.MapDocument(mxd)

    df = arcpy.mapping.ListDataFrames(mxd)[0]

    layers = arcpy.mapping.ListLayers(mxd, None, df)
    layers = [layer for layer in layers if not layer.isGroupLayer]

    gdb = get_project_gdb(mxd)

    return {"srs_code": df.spatialReference.factoryCode,
            "non_group_layer_count": len(layers),
            "gdb": gdb}


def get_layer_datasources(mxd=None):

    if not mxd:
        mxd = mapping.MapDocument("CURRENT")
    elif isinstance(mxd, basestring):
        mxd = mapping.MapDocument(mxd)

    return {layer.name: layer.dataSource for layer in mapping.ListLayers(mxd) if hasattr(layer, "dataSource")}


def get_user_config():

    config_file = get_config_path_and_file()[1]
    try:
        with open(config_file, 'r') as f:
            usr_cfg = load(f)
    except (IOError, OSError, ValueError):
        usr_cfg = get_default_user_config()

    return usr_cfg


def get_config():

    cfg = get_system_config()
    cfg.update(get_user_config())

    return cfg


def make_status_pretty(status_3tuple):

    true, false = u"\u2714", u"\u2716"

    unicoded = [[unicode(desc), [false, true][value]] for desc, item, value in status_3tuple]
    formatted_unicode = sorted([u"{} {}".format(desc, value) for desc, value in unicoded])

    return "\n".join(formatted_unicode)


def get_config_status(pretty=False):

    system_config_status = get_system_config_status(pretty)

    user_config_status = get_user_config_status(pretty)

    map_config_status = get_map_config_status(pretty)

    data_config_status = get_asdst_data_status(pretty)

    return u"{}\n{}\n{}\n{}".format(system_config_status, user_config_status, map_config_status, data_config_status)


def get_system_config_status(pretty=False):

    config = get_system_config()
    config.pop("empty_layers")

    config_status = [exists_return_3tuple(k, v) for k, v in config.iteritems()]

    if not pretty:
        return config_status

    valid = system_config_is_valid(config_status)

    config_status = make_status_pretty(config_status)

    config_status = u"{}\nSYSTEM CONFIGURATION {}\n".format(config_status, [u"\u2716", u"\u2714"][valid])  # dashes) + config_status + "\n"

    return config_status


def get_map_config_status(pretty=False):

    config = get_map_config()

    srs_ok = config["srs_code"] == 3308
    layers_ok = config["non_group_layer_count"] > 0
    gdb_ok = arcpy.Exists(config["gdb"])

    config_status = [("srs_code", config["srs_code"], srs_ok),
                     ("ng_layer_count", config["non_group_layer_count"], layers_ok),
                     ("gdb", config["gdb"], gdb_ok)]

    if not pretty:
        return config_status

    valid = srs_ok and layers_ok and gdb_ok

    config_status = make_status_pretty(config_status)

    config_status = u"{}\nMXD CONFIGURATION {}\n".format(config_status, [u"\u2716", u"\u2714"][valid])  # dashes) + config_status + "\n"

    return config_status


def get_user_config_status(pretty=False):

    config = get_user_config()

    config_status = [exists_return_3tuple(k, v) for k, v in config.iteritems()]

    if not pretty:
        return config_status

    valid = user_config_is_valid(config_status)

    config_status = make_status_pretty(config_status)

    config_status = u"{}\nUSER CONFIGURATION {}\n".format(config_status, [u"\u2716", u"\u2714"][valid])  # dashes) + config_status + "\n"

    return config_status


def set_user_config(source_fgdb, template_mxd, ahims_sites):

    config = get_user_config()
    config.update({"source_fgdb": source_fgdb, "template_mxd": template_mxd, "ahims_sites": ahims_sites})

    with open(config["config_file"], 'w') as f:
        dump(config, f)

    return


def get_layer_map(local_workspace):

    cfg = get_user_config()

    source_ws = cfg["source_fgdb"]

    d = {k: {"name": v,
             "1750_source": (join(source_ws, k.lower() + "_v7")),
             "1750_local": (join(local_workspace, k.lower() + "_1750")),
             "curr_local": (join(local_workspace, k.lower() + "_curr"))}
         for k, v in get_codes().iteritems()}

    return d


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


def system_config_is_valid(system_config_status=None):

    if not system_config_status:
        system_config_status = get_system_config_status()

    valid = False not in [value for desc, item, value in system_config_status]

    return valid


def user_config_is_valid(user_config_status=None):

    if not user_config_status:
        user_config_status = get_user_config_status()

    valid = False not in [value for desc, item, value in user_config_status if desc != "ahims_sites"]  # AHIMS is optional

    return valid


def map_config_is_valid(map_config_status=None):

    if not map_config_status:
        map_config_status = get_map_config_status()

    valid = False not in [value for desc, item, value in map_config_status]

    return valid


# def layer_config_is_valid(layer_status=None):
#
#     if not layer_status:
#         layer_status = get_layer_status()
#
#     valid = False not in [value for desc, item, value in layer_status]
#
#     return valid


# def get_missing_layer_datasources():
#
#     template_layer_sources = get_layer_datasources(get_system_config()["template_mxd"])
#
#     current_layer_sources = get_layer_datasources()
#
#     missing_sources = [x for x in template_layer_sources if x not in current_layer_sources]
#
#     missing_sources
#
#     return missing_sources


def get_dataframe_spatial_reference(mxd=None):

    if not mxd:
        mxd = mapping.MapDocument("CURRENT")

    df = mapping.ListDataFrames(mxd)[0]

    return df.spatialReference


def get_project_gdb(mxd=None):

    if not mxd:
        mxd = mapping.MapDocument("CURRENT")

    return mxd.filePath.replace(".mxd", ".gdb")


def valid_gdb_and_srs():

    mxd = mapping.MapDocument("CURRENT")

    gdb = get_project_gdb(mxd)

    gdb_ok = geodata_exists(gdb)

    srs_3308 = get_dataframe_spatial_reference(mxd).factoryCode == 3308

    valid = gdb_ok and srs_3308

    return valid


def get_asdst_data_status(pretty=False):

    mxd = arcpy.mapping.MapDocument("CURRENT")
    gdb = get_project_gdb(mxd)

    layer_status = []
    for k, v in get_layer_map(gdb).iteritems():

        layer_status.append(exists_return_3tuple("{} 1750".format(k), v["1750_local"]))

        layer_status.append(exists_return_3tuple("{} Current".format(k), v["curr_local"]))

    if not pretty:
        return layer_status

    valid = asdst_data_is_valid(layer_status)

    layer_status = make_status_pretty(layer_status)

    layer_status = u"{}\nDATA CONFIGURATION {}\n".format(layer_status, [u"\u2716", u"\u2714"][valid])  # dashes) + config_status + "\n"

    return layer_status


def asdst_data_is_valid(asdst_data_status=None):

    if not asdst_data_status:
        asdst_data_status = get_asdst_data_status()

    return False not in [c for a, b, c in asdst_data_status]


def _enable_tools():

    CreateProjectButton.enabled = system_config_is_valid() and user_config_is_valid()

    BuildDataButton.enabled = map_config_is_valid()

    CalculateContextButton.enabled = asdst_data_is_valid()

    return
