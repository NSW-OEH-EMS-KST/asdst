import arcpy as ap
import arcpy.mapping as am
import pythonaddins as pa
import logging
from os import makedirs, environ
from os.path import dirname, realpath, join, exists, split
from json import load, dump
from ast import literal_eval

# Global for external module ref
asdst_extension = None


class Config(object):
    def __init__(self):
        try:
            self.long_name = "Aboriginal Site Decision Support Tools"
            self.short_name = "ASDST"
            self.version = "0.1"
            self.script_path = dirname(realpath(__file__))
            self.appdata_path = join(environ["USERPROFILE"], "AppData", "Local", "ASDST")
            self.config_file = join(self.appdata_path, "config.json")
            self.log_file = join(self.appdata_path, "asdst.log")
            self.toolbox = join(self.script_path, "asdst.pyt")
            self.errors = None
            self.valid = None
            self.status = ""
            # template fgdbs
            self.template_project_gdb = join(self.script_path, "project.gdb")
            self.template_context_gdb = join(self.script_path, "context.gdb")
            # empty model layers
            self.empty_group_layer = join(self.script_path, "egl.lyr")
            self.empty_model_layer = join(self.script_path, "eml.lyr")
            self.empty_relia_layer = join(self.script_path, "erl.lyr")
            self.empty_accim_layer = join(self.script_path, "eai.lyr")
            self.empty_regio_layer = join(self.script_path, "eas.lyr")
            self.empty_prior_layer = join(self.script_path, "esp.lyr")
            self.empty_layers = {"group": self.empty_group_layer,
                                 "model": self.empty_model_layer,
                                 "relia": self.empty_relia_layer,
                                 "accim": self.empty_accim_layer,
                                 "regio": self.empty_regio_layer,
                                 "prior": self.empty_prior_layer}
            # configurable settings
            self.source_fgdb = join(self.appdata_path, "asdst_source.gdb")
            self.template_mxd = join(self.appdata_path, "asdst_default.mxd")
            self.ahims_sites = None
            self.has_source_gdb = False
            self.has_template_mxd = False
        except Exception as e:
            asdst_extension.message(e)

    def layer_dictionary(self, local_workspace):
        # type: (str) -> dict[str: dict[str: str]]
        source_ws = self.source_fgdb
        sfx_1750 = "_v7"
        sfx_curr = "_current"
        return {k: {"name": v,
                    "1750_source": (join(source_ws, k.lower() + sfx_1750)),
                    "1750_local": (join(local_workspace, k.lower() + "_1750")),
                    "curr_local": (join(local_workspace, k.lower() + sfx_curr))}
                for k, v in asdst_extension.codes.iteritems()}

    def set_user_config(self, source_fgdb, template_mxd, ahims_sites):
        # type: (str, str, str) -> None
        """ Saves setting to JSON file

        Args:

        Returns:

        Raises:
          No raising or catching

        """
        # message("set_usr_config")

        errors = []
        cfg = {}

        if not ap.Exists(source_fgdb):
            errors.append("Source file geodatabase does not exist")
            cfg["source_fgdb"] = self.source_fgdb
        else:
            self.source_fgdb = source_fgdb
            cfg["source_fgdb"] = source_fgdb

        if not ap.Exists(template_mxd):
            errors.append("Template map does not exist")
            cfg["template_mxd"] = self.template_mxd
        else:
            self.template_mxd = template_mxd
            cfg["template_mxd"] = template_mxd

        if ahims_sites and not ap.Exists(ahims_sites):
            errors.append("AHIMS site data '{0}' does not exist")
            cfg["ahims_sites"] = self.ahims_sites
        else:
            self.ahims_sites = ahims_sites
            cfg["ahims_sites"] = ahims_sites

        cfg["errors"] = errors

        with open(self.config_file, 'w') as f:
            dump(cfg, f)

        return

    def get_user_config(self):
        # type: () -> [str, str, str]
        """ Saves settings to JSON file

        Args:
            None

        Returns:
            3-tuple of strings

        Raises:
            Nothing explicit

        """
        return self.source_fgdb, self.template_mxd, self.ahims_sites

    def validate(self):
        # type: () -> object
        asdst_extension.message("Config.validate")
        self.errors = []

        # check if the app data folder is there, if not create
        if not exists(self.appdata_path):
            try:
                makedirs(self.appdata_path)
            except Exception as e:
                self.errors.append(e)

        # check if the config file is there, if not create
        if not exists(self.config_file):
            try:
                open(self.config_file, 'a').close()
            except Exception as e:
                self.errors.append(e)

        cfg = {}
        try:
            with open(self.config_file, 'r') as f:
                cfg = load(f)
        except Exception as e:
            self.errors.append(e)

        self.source_fgdb = cfg.get("source_fgdb", "")
        self.template_mxd = cfg.get("template_mxd", "")
        self.ahims_sites = cfg.get("ahims_sites", "")

        self.has_source_gdb = False
        if not self.source_fgdb:
            self.errors.append("Source FGDB is not set")
        elif not ap.Exists(self.source_fgdb):
            self.errors.append(
                "Source FGDB '{0}' does not exist".format(self.source_fgdb))
        else:
            self.has_source_gdb = True

        self.has_template_mxd = False
        if not self.template_mxd:
            self.errors.append("Template map is not set")
        elif not ap.Exists(self.template_mxd):
            self.errors.append(
                "Template map '{0}' does not exist".format(self.template_mxd))
        else:
            self.has_template_mxd = True

        if self.ahims_sites and not ap.Exists(self.ahims_sites):
            self.errors.append(
                "AHIMS site data '{0}' does not exist".format(self.ahims_sites))

        v = "ASDST Version {0}".format(self.version)
        e = self.errors
        if not e:
            e = u"No start-up errors identified."

        ws = self.script_path
        r = [ws,
             nice_test(self.toolbox, ws),
             nice_test(self.template_project_gdb, ws),
             nice_test(self.template_context_gdb, ws),
             nice_test(self.empty_group_layer, ws),
             nice_test(self.empty_model_layer, ws),
             nice_test(self.empty_relia_layer, ws),
             nice_test(self.empty_accim_layer, ws),
             nice_test(self.config_file, ws),
             nice_test(self.source_fgdb, ws, "Source FGDB"),
             nice_test(self.template_mxd, ws, "Template MXD"),
             nice_test(self.ahims_sites, ws, "AHIMS Sites")]

        f = u"{0}\n{1}\n{2}\n{3}\n{4}\n{5}\n{6}\n{7}\n{8}\n{9}\n{10}\n{11}\nu{12}\n{13}"

        self.status = f.format(v, e, *r)

        asdst_extension.message("Config.validate END")
        return


class Project(object):
    def __init__(self):
        # self.addin = addin
        self.title = None
        self.gdb = None
        self.mxd = None
        self.df = None
        self.valid = None
        self.status = None
        self.missing_layers = True

    def update(self):
        asdst_extension.message("Project.update")
        self.valid = False
        self.mxd = am.MapDocument("CURRENT")
        self.df = am.ListDataFrames(self.mxd)[0]
        self.gdb = None
        gdb = self.mxd.filePath.replace(".mxd", ".gdb")
        if ap.Exists(gdb):  # standard case, same name as mxd
            self.valid = True
            self.gdb = gdb
        else:  # mxd saved to a new name, go to tags
            # tag = {"asdst_extension": "DO NOT EDIT THIS TAG",
            #        "Version": 7,
            #        "Title": self.sane_title,
            #        "mxd": self.mxd,
            #        "gdb": self.gdb}
            # tag = str(tag).replace(",", ";")
            tags = self.mxd.tags
            if tags:
                tag_list = tags.split(",")
                tag = [t for t in tag_list if (("ASDST" in t) and ("gdb" in t))]
                if tag:
                    tag = tag[0]
                    tag = tag.replace(";", ",")
                    tag = literal_eval(tag)
                    gdb = tag.get("gdb", None)

                    if gdb and exists(gdb):
                        self.gdb = gdb
                        self.valid = True

        self.status = self.__get_layer_status()
        self.missing_layers = (u"\t\u2716" in self.status)

        asdst_extension.message("Project.update END")

    def __get_layer_status(self):
        # asdst_extension.message("Project.__get_layer_status")

        ws = self.gdb if self.gdb else None
        if not ws:
            return "No ASDST Project Workspace"

        f = u"{0}\n{1}\n{2}\n{3}\n{4}\n{5}\n{6}\n{7}\n{8}\n{9}\n{10}\n{11}\n" \
            u"{12}\n{13}\n{14}\n{15}\n{16}\n{17}\n{18}"
        r = [ws]
        for k, v in asdst_extension.config.layer_dictionary(ws).iteritems():
            r.append(nice_test(v["1750_local"], ws))
            r.append(nice_test(v["curr_local"], ws))

        # asdst_extension.message("status returning")
        return f.format(*r)

    def layer_dictionary(self):
        return asdst_extension.config.layer_dictionary(self.gdb)

    def add_layers(self, layers, group_name, layer_type):
        asdst_extension.add_layers(self.mxd, layers, group_name, layer_type)

    def add_table(self, mxd, table, name=""):
        asdst_extension.add_table(self.mxd, mxd, table, name)

    def compact_fgdb(self):
        asdst_extension.compact_fgdb(self.gdb)


PROTECTED = ["Areas of Interest", "Context", "Pre-1750", "Current", "ASDST"]


class InfoButton(object):
    """Implementation for asdst_extension_addin.cmd_label (Button)"""

    def __init__(self):
        self.enabled = True

    def onClick(self):
        try:
            # show the version, any error info and ASDST layer status
            bar = '{0:-<60}'.format('')
            m = u"{0}\n{1}\n{2}"
            asdst_extension.config.validate()
            a = asdst_extension.config.status
            asdst_extension.project.update()
            b = asdst_extension.project.status
            m = m.format(bar, a, bar, b)
            asdst_extension.message(m)
        except Exception as e:
            pa.MessageBox(e, "InfoButton.onClick")


class CalculateContextButton(object):
    """Implementation for asdst_extension_addin.cmd_new_project (Button)"""

    def __init__(self):
        self.enabled = False

    def onClick(self):
        try:  # launch the calculate context tool
            pa.GPToolDialog(asdst_extension.config.toolbox, "ContextCalculationTool")
            pass
        except Exception as e:
            pa.MessageBox(e, "CalculateContextButton.onClick")


class CreateProjectButton(object):
    """Implementation for asdst_extension_addin.cmd_new_project (Button)"""

    def __init__(self):
        self.enabled = False

    def onClick(self):
        try:  # launch the new project tool
            pa.GPToolDialog(asdst_extension.config.toolbox, "CreateProjectTool")
            pass
        except Exception as e:
            pa.MessageBox(e, "CreateProjectButton.onClick")


class ConfigureButton(object):
    """Implementation for asdst_extension_addin.setup (Button)"""

    def __init__(self):
        self.enabled = True

    def onClick(self):
        try:  # launch the configuration tool
            pa.GPToolDialog(asdst_extension.config.toolbox, "ConfigureTool")
            asdst_extension.project.update()
            # pass
        except Exception as e:
            pa.MessageBox(e, "ConfigureButton.onClick")


class AsdstExtension(object):
    """Implementation for asdst_extension_addin.extension (Extension)"""
    # For performance considerations, remove all unused methods in this class.

    def __init__(self):
        global asdst_extension
        asdst_extension = self

        try:
            # pass
            # pa.MessageBox("AsdstExtension.__init__ START", "AsdstExtension.__init__ START")

            self.config = Config()

            logging.basicConfig(filename=r"c:\Data\asdst.log", filemode="w", level=logging.DEBUG)
            logging.debug("AsdstExtension.__init__: " + str(locals()))

            self.project = Project()

            self.codes = {'AFT': "Stone artefact", 'ART': "Rock art", 'BUR': "Burial",
                          'ETM': "Earth mound", 'GDG': "Grinding groove",
                          'HTH': "Hearth or camp fire feature", 'SHL': "Shell midden",
                          'STQ': "Stone quarry", 'TRE': "Scarred tree"}

            self.codes_ex = {'ACD': "Aboriginal ceremony and dreaming",
                             'ARG': "Aboriginal resource gathering",
                             'AFT': "Stone artefact", 'ART': "Rock art",
                             'BUR': "Burial", 'CFT': "Conflict site",
                             'CMR': "Ceremonial ring", 'ETM': "Earth mound",
                             'FSH': "Fish trap", 'GDG': "Grinding groove",
                             'HAB': "Habitation structure",
                             'HTH': "Hearth or camp fire feature",
                             'OCQ': "Ochre quarry",
                             'PAD': "Potential archaeological deposit",
                             'SHL': "Shell midden", 'STA': "Stone arrangement",
                             'STQ': "Stone quarry", 'TRE': "Scarred tree",
                             'WTR': "Water feature"}

        except Exception as e:
            logging.debug("AsdstExtension.__init__:\nERR {}\nLOCALS {}".format(e, str(locals())))

        # pa.MessageBox("AsdstExtension.__init__ END", "AsdstExtension.__init__ END")

    def message(self, msg, mb=0):
        return pa.MessageBox(msg, "ASDST Extension", mb)

    def log_debug(self, msg):
        logging.debug(str(msg))

    def startup(self):
        try:
            self.message("Extension.startup")
        except:
            pass
        try:
            # check config
            # self.config.validate()
            pass
        except Exception as e:
            # pass
            pa.MessageBox(e, "asdst_extension.startup")

    def newDocument(self):
        try:
            # pass
            self.project.update()
            self.__enable_tools()
        except Exception as e:
            pa.MessageBox(e, "asdst_extension.newDocument")
            # pass

    def openDocument(self):
        try:
            pa.MessageBox("open", "asdst_extension.openDocument")
            # pass
            self.project.update()
            self.__enable_tools()
        except Exception as e:
            pass
            pa.MessageBox(e, "asdst_extension.openDocument")

    def itemAdded(self, new_item):
        try:
            # pass
            self.__enable_tools()
        except Exception as e:
            # pass
            pa.MessageBox(e, "asdst_extension.openDocument")

    def itemDeleted(self, deleted_item):
        try:
            # pass
            self.__enable_tools()
        except Exception as e:
            pa.MessageBox(e, "asdst_extension.openDocument")

    def __enable_tools(self):
        # message("asdst_extensionExtension.enable_tools")

        commands = [CreateProjectButton, CalculateContextButton, ConfigureButton]

        for cmd in commands:
            cmd.enabled = False

        if self.config.errors:
            self.message(self.config.errors)
            return

        lyrs = am.ListLayers(self.project.mxd)

        if lyrs:  # require at least one layer for context
            CreateProjectButton.enabled = True

        if not self.project.valid:
            return

        # msg = check_layers(lyrs)
        msg = self.project.status

        # if "MISSING" not in msg:
        CalculateContextButton.enabled = not self.project.missing_layers
        # pass
        # message("asdst_extensionExtension.enable_tools END")

    def add_table(self, mxd, table, name=""):
        # message("Adding {0}".format(table))

        # ap.AddMessage("mxd = {0}".format(mxd))
        df = am.ListDataFrames(mxd)[0]
        tv = am.TableView(table)
        if name:
            tv.name = name
        am.AddTableView(df, tv)
        ap.AddMessage("...table '{0}' added".format(tv.name))
        # pass

    def add_layers(self, mxd, layers, group_name, layer_type):
        # layers is a {name: datasource} dictionary

        if isinstance(mxd, basestring):
            mxd = am.MapDocument(mxd)

        df = am.ListDataFrames(mxd)[0]
        lyr_file = self.config.empty_layers.get(layer_type, None)
        glyr = None

        if group_name:  # try to find the group
            lyrs = am.ListLayers(mxd, group_name, df)
            glyr = lyrs[0] if lyrs else None
            if not glyr:  # not found, so create it
                glyr = am.Layer(self.config.empty_group_layer)
                glyr.name = group_name
                am.AddLayer(df, glyr)
            # this line is required, arc must add a deep copy or something?
            # anyway without this there is an exception raised
            glyr = am.ListLayers(mxd, group_name, df)[0]

        for k, v in layers.iteritems():
            if not lyr_file:
                lyr = am.Layer(v)
            else:
                lyr = am.Layer(lyr_file)
                p, n = split(v)
                lyr.replaceDataSource(p, "FILEGDB_WORKSPACE", n, validate=False)
            lyr.name = k
            if glyr:
                am.AddLayerToGroup(df, glyr, lyr)
                ap.AddMessage(
                    "...'{0}' layer added to group '{1}'".format(lyr.name,
                                                                 glyr.name))
            else:
                am.AddLayer(df, lyr)
                ap.AddMessage("...'{0}' layer added".format(lyr.name))
        # pass

    def compact_fgdb(self, gdb):
        from glob import glob
        from os.path import getsize
        sz = 0
        mb = 1024 * 1024

        if gdb and ap.Exists(gdb):
            for f in glob(gdb + "\\*"):
                sz += getsize(f)
            sz /= mb
            ap.AddMessage("Size of database '{0}' is ~ {1} MB".format(gdb, sz))
        # pass


def is_within_project_area(area):
    prj_lyr = am.ListLayers(am.MapDocument("CURRENT"), "Project Area")
    if not prj_lyr:
        raise Exception("No layer called 'Project Area'")

    mlyr = join("in_memory", "tmp")
    ap.MakeFeatureLayer_management(area, mlyr)
    ap.SelectLayerByLocation_management(mlyr, 'WITHIN', prj_lyr)

    count = int(ap.GetCount_management(mlyr).getOutput(0))

    return count > 0


def nice_test(thing_to_check, thing_possible_base, thing_name=""):
    good = u"\t\u2714"
    bad = u"\t\u2716"
    u = u"{0: <20}{1}"

    try:
        x2 = unicode(thing_to_check.replace(thing_possible_base, "..."))
    except:
        x2 = u"Something went wrong"

    if not thing_to_check or not ap.Exists(thing_to_check):
        if thing_name:
            x2 = unicode(thing_name)
        return u.format(x2, bad)

    return u.format(x2, good)

