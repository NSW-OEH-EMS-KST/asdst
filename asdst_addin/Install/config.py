from os.path import realpath, dirname, join, split, exists
from os import environ, makedirs
from json import load, dump
from utils import geodata_exists, get_dataframe_spatial_reference
from arcpy import mapping
import arcpy as ap


DASHES = "-"*40 + "\n"


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


def get_project_gdb(mxd=None):

    if not mxd:
        mxd = mapping.MapDocument("CURRENT")

    return mxd.filePath.replace(".mxd", ".gdb")


def get_map_config():

    mxd = mapping.MapDocument("CURRENT")

    df = mapping.ListDataFrames(mxd)[0]

    layers = mapping.ListLayers(mxd, None, df)
    layers = [layer for layer in layers if not layer.isGroupLayer]

    gdb = get_project_gdb(mxd)

    return {"srs_code": df.spatialReference.factoryCode,
            "non_group_layer_count": len(layers),
            "gdb": gdb}


def get_user_config(messages=None):

    config_file = get_config_path_and_file()[1]

    try:
        with open(config_file, 'r') as f:
            usr_cfg = load(f)

    except Exception as e:
        print e
        if messages:
            messages.addMessage(e)
        usr_cfg = get_default_user_config(messages)

    return usr_cfg


def get_appdata_path():

    # return join(environ["USERPROFILE"], "AppData", "Local", "ASDST")
    return join(environ["USERPROFILE"], "ASDST")


def exists_return_3tuple(description, item):

    return [description, item, geodata_exists(item)]


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

    config_status = u"{}\nSYSTEM CONFIGURATION {}\n".format(config_status, [u"\u2716", u"\u2714"][valid])  # DASHES) + config_status + "\n"

    return config_status


def get_map_config_status(pretty=False):

    config = get_map_config()

    srs_ok = config["srs_code"] == 3308
    layers_ok = config["non_group_layer_count"] > 0
    gdb_ok = geodata_exists(config["gdb"])

    config_status = [("srs_code", config["srs_code"], srs_ok),
                     ("ng_layer_count", config["non_group_layer_count"], layers_ok),
                     ("gdb", config["gdb"], gdb_ok)]

    if not pretty:
        return config_status

    valid = srs_ok and layers_ok and gdb_ok

    config_status = make_status_pretty(config_status)

    config_status = u"{}\nMXD CONFIGURATION {}\n".format(config_status, [u"\u2716", u"\u2714"][valid])  # DASHES) + config_status + "\n"

    return config_status


def get_user_config_status(pretty=False):

    config = get_user_config()

    config_status = [exists_return_3tuple(k, v) for k, v in config.iteritems()]

    if not pretty:
        return config_status

    valid = user_config_is_valid(config_status)

    config_status = make_status_pretty(config_status)

    config_status = u"{}\nUSER CONFIGURATION {}\n".format(config_status, [u"\u2716", u"\u2714"][valid])  # DASHES) + config_status + "\n"

    return config_status


def set_user_config(source_fgdb, template_mxd, ahims_sites, messages=None):

    config = get_user_config(messages=messages)
    config.update({"source_fgdb": source_fgdb, "template_mxd": template_mxd, "ahims_sites": ahims_sites})

    with open(config["config_file"], 'w') as f:
        dump(config, f)

    m = "{}\nwritten to\n{}".format(config, config["config_file"])
    print m
    if messages:
        messages.addMessage(m)

    x = get_user_config(messages)
    if messages:
        messages.addMessage(x)

    return


def system_config_is_valid(system_config_status=None):

    if not system_config_status:
        system_config_status = get_system_config_status()

    valid = False not in [value for desc, item, value in system_config_status]

    print "System config valid: ", valid

    return valid


def user_config_is_valid(user_config_status=None):

    if not user_config_status:
        user_config_status = get_user_config_status()

    valid = False not in [value for desc, item, value in user_config_status if desc != "ahims_sites"]  # AHIMS is optional

    print "User config valid: ", valid

    return valid


def map_config_is_valid(map_config_status=None):

    if not map_config_status:
        map_config_status = get_map_config_status()

    valid = False not in [value for desc, item, value in map_config_status]

    print "Map config valid: ", valid

    return valid


def asdst_data_is_valid(asdst_data_status=None):

    if not asdst_data_status:
        asdst_data_status = get_asdst_data_status()

    valid = False not in [c for a, b, c in asdst_data_status]

    print "ASDST data valid: ", valid

    return valid


def get_toolbox():

    script_path = dirname(realpath(__file__))

    toolbox = join(script_path, "asdst.pyt")

    if not geodata_exists(toolbox):
        raise ValueError("ASDST Toolbox not found : " + toolbox)

    return toolbox


def get_config_path_and_file():

    p = join(environ["USERPROFILE"], "ASDST")
    if not exists(p):
        try:
            makedirs(p)
        except (IOError, OSError) as e:
            print e

    fn = join(p, "system", "asdst_config.json")
    open(fn, 'a').close()

    return p, fn


def get_default_user_config(messages=None):

    appdata_path, config_file = get_config_path_and_file()
    source_fgdb = join(appdata_path, "system", "asdst_source.gdb")
    template_mxd = join(appdata_path, "templates", "asdst_default.mxd")
    ahims_sites = ""

    config = locals()
    m = "default config: ", config
    print m
    if messages:
        messages.addMessage(m)

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

    return locals()


def get_layer_map(local_workspace):

    cfg = get_user_config()

    source_ws = cfg["source_fgdb"]

    d = {k: {"name": v,
             "1750_source": (join(source_ws, k.lower() + "_v7")),
             "1750_local": (join(local_workspace, k.lower() + "_1750")),
             "curr_local": (join(local_workspace, k.lower() + "_curr"))}
         for k, v in get_codes().iteritems()}

    return d


def get_asdst_data_status(pretty=False):

    mxd = mapping.MapDocument("CURRENT")
    gdb = get_project_gdb(mxd)

    layer_status = []
    for k, v in get_layer_map(gdb).iteritems():

        layer_status.append(exists_return_3tuple("{} 1750".format(k), v["1750_local"]))

        layer_status.append(exists_return_3tuple("{} Current".format(k), v["curr_local"]))

    if not pretty:
        return layer_status

    valid = asdst_data_is_valid(layer_status)

    layer_status = make_status_pretty(layer_status)

    layer_status = u"{}\nDATA CONFIGURATION {}\n".format(layer_status, [u"\u2716", u"\u2714"][valid])  # DASHES) + config_status + "\n"

    return layer_status


def get_config():

    cfg = get_system_config()
    cfg.update(get_user_config())

    return cfg


def update_config():

    cfg = get_system_config()
    cfg.update(get_user_config())

    return cfg


def valid_gdb_and_srs():

    mxd = mapping.MapDocument("CURRENT")

    gdb = get_project_gdb(mxd)

    gdb_ok = geodata_exists(gdb)

    srs_3308 = get_dataframe_spatial_reference(mxd).factoryCode == 3308

    valid = gdb_ok and srs_3308

    return valid


class ConfigureTool(object):

    def __init__(self):

        self.label = u'Configure ASDST Extension'
        self.description = u'Configure parameters for the ASDST extension'
        self.canRunInBackground = False

        return

    def getParameterInfo(self):

        cfg = get_user_config()

        # Source_Database
        param_1 = ap.Parameter()
        param_1.name = u'Source_Database'
        param_1.displayName = u'Source Database'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'Workspace'
        param_1.value = cfg.get("source_fgdb", "")

        # Template_Map
        param_2 = ap.Parameter()
        param_2.name = u'Template_Map'
        param_2.displayName = u'Template Map'
        param_2.parameterType = 'Required'
        param_2.direction = 'Input'
        param_2.datatype = u'ArcMap Document'
        param_2.value = cfg.get("template_mxd", "")

        # AHIMS_Sites
        param_3 = ap.Parameter()
        param_3.name = u'AHIMS_Sites'
        param_3.displayName = u'AHIMS Sites'
        param_3.parameterType = 'Optional'
        param_3.direction = 'Input'
        param_3.datatype = u'Feature Class'
        param_3.value = cfg.get("ahims_sites", "")

        return [param_1, param_2, param_3]

    # def isLicensed(self):
    #
    #     return True
    #
    # def initializeParameters(self):
    #
    #     cfg = get_user_config()
    #
    #     self.params[0] = cfg.get("source_fgdb", "")
    #     self.params[1] = cfg.get("template_mxd", "")
    #     self.params[2] = cfg.get("ahims_sites", "")
    #
    #     return

    def updateParameters(self, parameters):

        if parameters[0].altered or parameters[1].altered or parameters[2].altered:
            set_user_config(parameters[0].valueAsText, parameters[1].valueAsText, parameters[2].valueAsText)

        # set_user_config(parameters[0].valueAsText, parameters[1].valueAsText, parameters[2].valueAsText)

        return

    def updateMessages(self, parameters):

        if parameters[2].value:
            fields = ap.ListFields(parameters[2].value)
            fieldnames = {f.name for f in fields}
            codes = {k for k, v in get_codes().iteritems()}
            missing = codes - fieldnames
            if missing:
                parameters[2].setErrorMessage("Feature class is missing required fields {}".format(", ", join(missing)))

        return

    def execute(self, parameters, messages):

        set_user_config(parameters[0].valueAsText, parameters[1].valueAsText, parameters[2].valueAsText, messages=messages)

        return


