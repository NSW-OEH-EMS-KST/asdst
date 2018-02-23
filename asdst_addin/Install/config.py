from os.path import realpath, dirname, join, split, exists
from os import environ, makedirs
from json import load, dump
from utils import geodata_exists, get_codes, get_codes_ex, get_toolbox, get_source_gdb
from arcpy import mapping
from functools import partial

DASHES = "-" * 40 + "\n"
CONFIG = {}
SYSTEM_CONFIG = {}


# # codes
# def get_codes():
#     return dict(AFT="Stone artefact", ART="Rock art", BUR="Burial", ETM="Earth mound", GDG="Grinding groove",
#                 HTH="Hearth or camp fire feature", SHL="Shell midden", STQ="Stone quarry", TRE="Scarred tree")
#
#
# # extended codes
# def get_codes_ex():
#     return dict(ACD="Aboriginal ceremony and dreaming", ARG="Aboriginal resource gathering",
#                 AFT="Stone artefact", ART="Rock art", BUR="Burial", CFT="Conflict site",
#                 CMR="Ceremonial ring", ETM="Earth mound", FSH="Fish trap", GDG="Grinding groove",
#                 HAB="Habitation structure", HTH="Hearth or camp fire feature", OCQ="Ochre quarry",
#                 PAD="Potential archaeological deposit", SHL="Shell midden", STA="Stone arrangement",
#                 STQ="Stone quarry", TRE="Scarred tree", WTR="Water feature")
#
#
def get_appdata_path():
    return join(environ["USERPROFILE"], "ASDST")


# def get_appdata_path():
#     return join(environ["USERPROFILE"], "ASDST")


def get_project_gdb(mxd=None):
    if not mxd:
        mxd = mapping.MapDocument("CURRENT")

    return mxd.filePath.replace(".mxd", ".gdb")


# def get_map_config():
#
#     mxd = mapping.MapDocument("CURRENT")
#
#     df = mapping.ListDataFrames(mxd)[0]
#
#     layers = mapping.ListLayers(mxd, None, df)
#     layers = [layer for layer in layers if not layer.isGroupLayer]
#
#     gdb = get_project_gdb(mxd)
#
#     return {"srs_code": df.spatialReference.factoryCode,
#             "non_group_layer_count": len(layers),
#             "gdb": gdb}


def exists_return_3tuple(name, value, items=None):
    # print "exists_return_3tuple({}, {}, items={})".format(name, value, items)

    if items is None:
        v = [name, value, geodata_exists(value)]
    else:
        v = [[name, value, geodata_exists(value)] for name, value in items.iteritems()]

    return v


def make_status_pretty(status_3tuple):
    true, false = u"\u2714", u"\u2716"

    unicoded = [[unicode(desc), [false, true][value]] for desc, item, value in status_3tuple]
    formatted_unicode = sorted([u"{} {}".format(desc, value) for desc, value in unicoded])

    return u"\n".join(formatted_unicode)


class SystemConfig(object):

    def __init__(self):
        print "SystemConfig.__init__"

        self.script_path = dirname(realpath(__file__))

        j = partial(join, self.script_path)

        self.toolbox = get_toolbox()  # j("asdst.pyt")

        self.template_project_gdb = j("project.gdb")
        self.template_context_gdb = j("context.gdb")
        self.empty_group_layer = j("egl.lyr")
        self.empty_model_layer = j("eml.lyr")
        self.empty_relia_layer = j("erl.lyr")
        self.empty_accim_layer = j("eai.lyr")
        self.empty_regio_layer = j("eas.lyr")
        self.empty_prior_layer = j("esp.lyr")
        self.empty_polyf_layer = j("epf.lyr")

        self.valid = False
        self.validate()
        self.write_config(self.get_config())

        return

    def write_config(self, config):

        config_file = self.get_config_file()

        with open(config_file, 'w') as f:
            dump(config, f)

        print "{}\nwritten to\n{}".format(config, config_file)

        self.validate()

        return

    def get_config_file(self):
        print "SystemConfig.get_config_file()"

        p = join(get_appdata_path(), "system")
        fn = join(p, "system_config.json")

        if not exists(fn):
            print "User system_config file '{}' does not exist".format(fn)

            if not exists(p):
                makedirs(p)
                print "ASDST system path '{}' created".format(p)

            open(fn, 'a').close()  # any exception will be raised
            print "User system_config file '{}' created".format(fn)

            # self.write_config(self.get_config(ByFile=False))
            #
        print "\treturning {}".format(fn)

        return fn

    # def get_config_by_file(self):
    #
    #     config_file = self.get_config_file()
    #
    #     with open(config_file, 'r') as f:
    #         cfg = load(f)
    #
    #     if not cfg:
    #         cfg = self.get_config(ByFile=False)
    #         self.write_config(cfg)
    #
    #     return load(cfg)

    def get_config(self, ByFile=False):
        print "SystemConfig.get_config ByFile={}".format(ByFile)

        # if ByFile:
        #     v = self.get_config_by_file()
        # else:
        v = vars(self).copy()
        v.pop("valid")

        return v

    def get_status(self):
        print "SystemConfig.get_status"

        return exists_return_3tuple(None, None, self.get_config())

    def get_status_pretty(self):
        print "SystemConfig.get_status_pretty"

        s = make_status_pretty(self.get_status())

        return u"{}\nSYSTEM CONFIGURATION {}\n".format(s, [u"\u2716", u"\u2714"][self.valid])

    def validate(self):
        print "SystemConfig.validate"

        self.valid = False not in [b for name, value, b in self.get_status()]
        print "System config valid: ", self.valid

        return


class MapConfig(object):
    def __init__(self):
        print "MapConfig.__init__"

        self.mxd = mapping.MapDocument("CURRENT")
        self.valid = False
        self.dataframe_srs_code = -9999
        self.non_group_layers = 0
        self.project_gdb = ""

        self.validate()

        return

    def get_config(self):

        return vars(self).copy()

    def get_status(self):
        print "MapConfig.get_status"

        cfg = self.get_config()
        srs = cfg["dataframe_srs_code"]
        gdb = cfg["project_gdb"]

        nglc = len(cfg["non_group_layers"])

        s = [("dataframe_srs_code", srs, srs == 3308),
             ("project_gdb", gdb, geodata_exists(gdb)),
             ("non_grp_lyr_count", nglc, nglc > 0)]

        print s

        return s

    def get_status_pretty(self):
        print "MapConfig.get_status_pretty"

        s = make_status_pretty(self.get_status())

        return u"{}\nMXD CONFIGURATION {}\n".format(s, [u"\u2716", u"\u2714"][self.valid])

    def validate(self):
        print "MapConfig.validate"

        df = mapping.ListDataFrames(self.mxd)[0]
        self.dataframe_srs_code = df.spatialReference.factoryCode

        layers = mapping.ListLayers(self.mxd, None, df)
        layers = [layer for layer in layers if not layer.isGroupLayer]
        self.non_group_layers = layers

        self.project_gdb = get_project_gdb(self.mxd)

        self.valid = False not in [b for n, v, b in self.get_status()]

        print "Map config valid: ", self.valid

        return


class UserConfig(object):
    def __init__(self):
        print "UserConfig.__init__"

        self.asdst_gdb = None
        self.template_mxd = None
        self.ahims_sites = None
        self.valid = False

        self.validate()

        return

    def get_config_file(self):
        print "UserConfig.get_config_file()"

        p = join(get_appdata_path(), "system")
        fn = join(p, "user_config.json")

        if not exists(fn):
            print "User system_config file '{}' does not exist".format(fn)
            if not exists(p):
                makedirs(p)
                print "ASDST system path '{}' created".format(p)

            open(fn, 'a').close()  # any exception will be raised
            print "User system_config file '{}' created".format(fn)

            self.set_config("", "", "")

        print "\treturning {}".format(fn)

        return fn

    def get_config(self):

        config_file = self.get_config_file()

        with open(config_file, 'r') as f:
            return load(f)

    def get_status(self):
        print "UserConfig.get_status"

        return exists_return_3tuple(None, None, items=self.get_config())

    def get_status_pretty(self):
        print "UserConfig.get_status_pretty"

        s = make_status_pretty(self.get_status())

        return u"{}\nUSER CONFIGURATION {}\n".format(s, [u"\u2716", u"\u2714"][self.valid])

    def validate(self):
        print "UserConfig.validate"

        self.valid = False not in [b for n, v, b in self.get_status() if n != "ahims_sites"]

        print "User config valid: ", self.valid

        return

    def set_config(self, source_fgdb, template_mxd, ahims_sites, messages=None):

        CONFIG = {}

        CONFIG.update({"source_fgdb": source_fgdb, "template_mxd": template_mxd, "ahims_sites": ahims_sites})

        config_file = self.get_config_file()

        with open(config_file, 'w') as f:
            dump(CONFIG, f)

        m = "{}\nwritten to\n{}".format(CONFIG, config_file)
        print m
        if messages:
            messages.addMessage(m)

        self.validate()

        return


class AsdstDataConfig(object):
    def __init__(self, source_gdb):
        print "AsdstDataConfig.__init__"

        self.mxd = None
        self.project_gdb = ""
        self.source_gdb = source_gdb
        self.valid = False

        self.validate()

        return

    def get_status(self):
        print "AsdstDataConfig.get_status"

        if not self.source_gdb:
            self.source_gdb = get_source_gdb()

        lmap = self.get_layer_map(self.project_gdb)
        lmap["AOI"] = join(self.project_gdb, "aoi")

        print "LMAP", "\n", lmap

        lmap2 = {}
        for n, d in lmap.iteritems():
            print n, d
            if n != "AOI":
                lmap2[n + "_1750_local"] = d["1750_local"]
                lmap2[n + "_curr_local"] = d["curr_local"]
            else:
                lmap2[n] = lmap[n]

        print lmap2
        layer_status = exists_return_3tuple(None, None, items=lmap2)

        # hack, in a rush
        # ['ART',
        #  {'1750_local': u'C:\\Data\\GIS\\Temp\\y.gdb\\art_1750', 'curr_local': u'C:\\Data\\GIS\\Temp\\y.gdb\\art_curr', 'name': 'Rock art', '1750_source': u'C:\\Users\\byed\\ASDST\\system\\asdst_source.gdb\\art_v7'},
        #  False]

        # layer_status = [d for n, d, b in layer_status]  # list of dicts
        # layer_status_d = {}
        # for d in layer_status:
        #     d.pop("1750_source")
        #     layer_status_d.update(d)
        #
        # # layer_status = {k: v[""] for k, v, b in layer_status}
        # layer_status = exists_return_3tuple(None, None, items=d)

        print layer_status

        return layer_status  # exists_return_3tuple(None, None, items=self.get_config())

    def get_status_pretty(self):
        print "AsdstDataConfig.get_status_pretty"

        s = make_status_pretty(self.get_status())

        return u"{}\nASDST DATA CONFIGURATION {}\n".format(s, [u"\u2716", u"\u2714"][self.valid])

    def validate(self):
        print "AsdstDataConfig.validate"

        self.mxd = mapping.MapDocument("CURRENT")
        self.project_gdb = get_project_gdb(self.mxd)
        self.valid = False not in [b for n, v, b in self.get_status()]

        print "Map config valid: ", self.valid

        return

    def get_layer_map(self, local_workspace):

        source_ws = self.source_gdb

        if not source_ws:
            source_ws = get_source_gdb()

        if not local_workspace:
            local_workspace = "X:\\NOT_SET"

        d = {k: {"name": v,
                 "1750_source": (join(source_ws, k.lower() + "_v7")),
                 "1750_local": (join(local_workspace, k.lower() + "_1750")),
                 "curr_local": (join(local_workspace, k.lower() + "_curr"))}
             for k, v in get_codes().iteritems()}

        return d

# def get_user_config(messages=None):
#
#     global CONFIG
#
#     if CONFIG:
#         return CONFIG
#
#     config_file = get_config_file()
#
#     # try:
#     with open(config_file, 'r') as f:
#         CONFIG = load(f)

# except Exception as e:
#     print e
#     if messages:
#         messages.addMessage(e)
#     usr_cfg = get_default_user_config()
# if not usr_cfg:
#     usr_cfg = get_default_user_config()
#     if messages:
#         messages.addMessage("Default user system_config retrieved: {}".format(usr_cfg))
#     set_user_config(usr_cfg["source_fgdb"], usr_cfg["template_mxd"], usr_cfg["ahims_sites"])
#     if messages:
#         messages.addMessage("Default user system_config saved: {}".format(usr_cfg))

# CONFIG = usr_cfg

#     return CONFIG
#
#

# def exists_return_3tuple(description, item):
#
#     return [description, item, geodata_exists(item)]


# def make_status_pretty(status_3tuple):
#
#     true, false = u"\u2714", u"\u2716"
#
#     unicoded = [[unicode(desc), [false, true][value]] for desc, item, value in status_3tuple]
#     formatted_unicode = sorted([u"{} {}".format(desc, value) for desc, value in unicoded])
#
#     return "\n".join(formatted_unicode)


# def get_config_status(pretty=False):
#
#     system_config_status = get_system_config_status(pretty=pretty)
#
#     user_config_status = get_user_config_status(pretty=pretty)
#
#     map_config_status = get_map_config_status(pretty=pretty)
#
#     data_config_status = get_asdst_data_status(pretty=pretty)
#
#     return u"Cache\n{}\n\n{}\n{}\n{}\n{}".format(get_script_path(), system_config_status, user_config_status, map_config_status, data_config_status)


# def get_system_config_status(sys_cfg=None, pretty=False):
#     print "get_system_config_status  sys_cfg={}".format(sys_cfg)
#
#     if not sys_cfg:
#         sys_cfg = get_system_config()
#         sys_cfg = sys_cfg.copy()
#         sys_cfg.pop("empty_layers")
#
#     config_status = [exists_return_3tuple(k, v) for k, v in sys_cfg.iteritems()]
#     print "config_status: {}".format(config_status)
#
#     if not pretty:
#         return config_status
#
#     valid = system_config_is_valid(config_status)
#
#     config_status = make_status_pretty(config_status)
#
#     config_status = u"{}\nSYSTEM CONFIGURATION {}\n".format(config_status, [u"\u2716", u"\u2714"][valid])  # DASHES) + config_status + "\n"
#
#     return config_status


# def get_map_config_status(pretty=False):
#
#     config = get_map_config()
#
#     srs_ok = config["srs_code"] == 3308
#     layers_ok = config["non_group_layer_count"] > 0
#     gdb_ok = geodata_exists(config["gdb"])
#
#     config_status = [("srs_code", config["srs_code"], srs_ok),
#                      ("ng_layer_count", config["non_group_layer_count"], layers_ok),
#                      ("gdb", config["gdb"], gdb_ok)]
#
#     if not pretty:
#         return config_status
#
#     valid = srs_ok and layers_ok and gdb_ok
#
#     config_status = make_status_pretty(config_status)
#
#     config_status = u"{}\nMXD CONFIGURATION {}\n".format(config_status, [u"\u2716", u"\u2714"][valid])  # DASHES) + config_status + "\n"
#
#     return config_status


# def get_user_config_status(pretty=False):
#
#     config = get_user_config()
#
#     config_status = [exists_return_3tuple(k, v) for k, v in config.iteritems()]
#
#     if not pretty:
#         return config_status
#
#     valid = user_config_is_valid(config_status)
#
#     config_status = make_status_pretty(config_status)
#
#     config_status = u"{}\nUSER CONFIGURATION {}\n".format(config_status, [u"\u2716", u"\u2714"][valid])  # DASHES) + config_status + "\n"
#
#     return config_status
#
#
# def set_user_config(source_fgdb, template_mxd, ahims_sites, messages=None):
#
#     global CONFIG
#
#     CONFIG.update({"source_fgdb": source_fgdb, "template_mxd": template_mxd, "ahims_sites": ahims_sites})
#
#     config_file = get_config_file()
#
#     with open(config_file, 'w') as f:
#         dump(CONFIG, f)
#
#     m = "{}\nwritten to\n{}".format(CONFIG, config_file)
#     print m
#     if messages:
#         messages.addMessage(m)
#
#     return


# def system_config_is_valid(system_config=None, system_config_status=None):
#     print "system_config_is_valid  system_config_status={}".format(system_config_status)
#
#     if not system_config:
#         system_config = get_system_config()
#
#     if not system_config_status:
#         system_config_status = get_system_config_status(system_config)
#
#     valid = False not in [value for desc, item, value in system_config_status]
#
#     print "System system_config valid: ", valid
#
#     return valid


# def user_config_is_valid(user_config_status=None):
#
#     if not user_config_status:
#         user_config_status = get_user_config_status()
#
#     valid = False not in [value for desc, item, value in user_config_status if desc != "ahims_sites"]  # AHIMS is optional
#
#     print "User system_config valid: ", valid
#
#     return valid
#
#
# def map_config_is_valid(map_config_status=None):
#
#     if not map_config_status:
#         map_config_status = get_map_config_status()
#
#     valid = False not in [value for desc, item, value in map_config_status]
#
#     print "Map system_config valid: ", valid
#
#     return valid


# def asdst_data_is_valid(asdst_data_status=None):
#
#     if not asdst_data_status:
#         asdst_data_status = get_asdst_data_status()
#
#     valid = False not in [c for a, b, c in asdst_data_status]
#
#     print "ASDST data valid: ", valid
#
#     return valid
#
#
# def get_script_path():
#
#     return dirname(realpath(__file__))


# def get_toolbox():
#
#     script_path = get_script_path()
#
#     toolbox = join(script_path, "asdst.pyt")
#
#     if not geodata_exists(toolbox):
#         raise ValueError("ASDST Toolbox not found : " + toolbox)
#
#     return toolbox
#
#
# def get_config_file():
#     print "get_config_file()"
#
#     p = join(get_appdata_path(), "system")
#     fn = join(p, "user_config.json")
#
#     if not exists(fn):
#         print "User system_config file '{}' does not exist".format(fn)
#         if not exists(p):
#             makedirs(p)
#             print "ASDST system path '{}' created".format(p)
#
#         open(fn, 'a').close()  # any exception will be raised
#         print "User system_config file '{}' created".format(fn)
#
#         set_user_config("", "", "")
#
#     print "\treturning {}".format(fn)
#
#     return fn


# def get_default_user_config():
#     print "get_default_user_config()"
#
#     appdata_path = get_appdata_path()
#     source_fgdb = join(appdata_path, "system", "asdst_source.gdb")
#     template_mxd = join(appdata_path, "templates", "asdst_default.mxd")
#     ahims_sites = ""
#
#     system_config = locals()
#     print "default system_config: {}".format(system_config)
#
#     config_file = get_config_file()
#     with open(config_file, 'w') as f:
#         dump(system_config, f)
#
#     return system_config


# def get_system_config():
#     print "get_system_config()"
#
#     global SYSTEM_CONFIG
#
#     if SYSTEM_CONFIG:
#         return SYSTEM_CONFIG
#
#     script_path = get_script_path()
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
#
#     empty_layers = {"group": empty_group_layer,
#                     "model": empty_model_layer,
#                     "relia": empty_relia_layer,
#                     "accim": empty_accim_layer,
#                     "regio": empty_regio_layer,
#                     "prior": empty_prior_layer,
#                     "polyf": empty_polyf_layer}
#
#     SYSTEM_CONFIG = locals()
#
#     return SYSTEM_CONFIG


# def get_layer_map(local_workspace):
#
#     cfg = get_user_config()
#
#     source_ws = cfg["source_fgdb"]
#
#     d = {k: {"name": v,
#              "1750_source": (join(source_ws, k.lower() + "_v7")),
#              "1750_local": (join(local_workspace, k.lower() + "_1750")),
#              "curr_local": (join(local_workspace, k.lower() + "_curr"))}
#          for k, v in get_codes().iteritems()}
#
#     return d


# def get_asdst_data_status(pretty=False):
#
#     mxd = mapping.MapDocument("CURRENT")
#     gdb = get_project_gdb(mxd)
#
#     layer_status = []
#     for k, v in get_layer_map(gdb).iteritems():
#
#         layer_status.append(exists_return_3tuple("{} 1750".format(k), v["1750_local"]))
#
#         layer_status.append(exists_return_3tuple("{} Current".format(k), v["curr_local"]))
#
#     if not pretty:
#         return layer_status
#
#     valid = asdst_data_is_valid(layer_status)
#
#     layer_status = make_status_pretty(layer_status)
#
#     layer_status = u"{}\nDATA CONFIGURATION {}\n".format(layer_status, [u"\u2716", u"\u2714"][valid])  # DASHES) + config_status + "\n"
#
#     return layer_status
#
#
# def get_config():
#
#     cfg = get_system_config()
#     cfg.update(get_user_config())
#
#     return cfg
#
#
# def update_config():
#
#     cfg = get_system_config()
#     cfg.update(get_user_config())
#
#     return cfg


# def valid_gdb_and_srs():
#
#     mxd = mapping.MapDocument("CURRENT")
#
#     gdb = get_project_gdb(mxd)
#
#     gdb_ok = geodata_exists(gdb)
#
#     srs_3308 = get_dataframe_spatial_reference(mxd).factoryCode == 3308
#
#     valid = gdb_ok and srs_3308
#
#     return valid


# class ConfigureTool(object):
#
#     def __init__(self):
#
#         self.label = u'Configure ASDST Extension'
#         self.description = u'Configure parameters for the ASDST extension'
#         self.canRunInBackground = False
#
#         return
#
#     def getParameterInfo(self):
#
#         cfg = get_user_config()
#
#         # Source_Database
#         param_1 = ap.Parameter()
#         param_1.name = u'Source_Database'
#         param_1.displayName = u'Source Database'
#         param_1.parameterType = 'Required'
#         param_1.direction = 'Input'
#         param_1.datatype = u'Workspace'
#         param_1.value = cfg.get("source_fgdb", "")
#
#         # Template_Map
#         param_2 = ap.Parameter()
#         param_2.name = u'Template_Map'
#         param_2.displayName = u'Template Map'
#         param_2.parameterType = 'Required'
#         param_2.direction = 'Input'
#         param_2.datatype = u'ArcMap Document'
#         param_2.value = cfg.get("template_mxd", "")
#
#         # AHIMS_Sites
#         param_3 = ap.Parameter()
#         param_3.name = u'AHIMS_Sites'
#         param_3.displayName = u'AHIMS Sites'
#         param_3.parameterType = 'Optional'
#         param_3.direction = 'Input'
#         param_3.datatype = u'Feature Class'
#         param_3.value = cfg.get("ahims_sites", "")
#
#         return [param_1, param_2, param_3]
#
#     # def isLicensed(self):
#     #
#     #     return True
#     #
#     def initializeParameters(self):
#
#         cfg = get_user_config()
#
#         self.params[0] = cfg.get("source_fgdb", "")
#         self.params[1] = cfg.get("template_mxd", "")
#         self.params[2] = cfg.get("ahims_sites", "")
#
#         return
#
#     def updateParameters(self, parameters):
#
#         # if parameters[0].altered or parameters[1].altered or parameters[2].altered:
#         #     set_user_config(parameters[0].valueAsText, parameters[1].valueAsText, parameters[2].valueAsText)
#
#         # set_user_config(parameters[0].valueAsText, parameters[1].valueAsText, parameters[2].valueAsText)
#
#         return
#
#     def updateMessages(self, parameters):
#
#         if parameters[2].value:
#             fields = ap.ListFields(parameters[2].value)
#             fieldnames = {f.name for f in fields}
#             codes = {k for k, v in get_codes().iteritems()}
#             missing = codes - fieldnames
#             if missing:
#                 parameters[2].setErrorMessage("Feature class is missing required fields {}".format(", ", join(missing)))
#
#         return
#
#     def execute(self, parameters, messages):
#
#         set_user_config(parameters[0].valueAsText, parameters[1].valueAsText, parameters[2].valueAsText, messages=messages)
#
#         # send_event("user_config_updated")
#
#         return
#
#
