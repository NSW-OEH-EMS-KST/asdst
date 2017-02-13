import arcpy as ap
from os import makedirs, environ
from os.path import dirname, realpath, join, exists  # , split
from json import load, dump
from asdst_addin import asdst_extension  #, log, nice_test


# class Config(object):
#     def __init__(self):
#         self.long_name = "Aboriginal Site Decision Support Tools"
#         self.short_name = "ASDST"
#         self.version = "0.1"
#         self.script_path = dirname(realpath(__file__))
#         self.appdata_path = join(environ["USERPROFILE"], "AppData", "Local", "ASDST")
#         self.config_file = join(self.appdata_path, "config.json")
#         self.toolbox = join(self.script_path, "ASDST.pyt")
#         self.errors = None
#         self.valid = None
#         self.status = ""
#         # template fgdbs
#         self.template_project_gdb = join(self.script_path, "project.gdb")
#         self.template_context_gdb = join(self.script_path, "context.gdb")
#         # empty model layers
#         self.empty_group_layer = join(self.script_path, "egl.lyr")
#         self.empty_model_layer = join(self.script_path, "eml.lyr")
#         self.empty_relia_layer = join(self.script_path, "erl.lyr")
#         self.empty_accim_layer = join(self.script_path, "eai.lyr")
#         self.empty_regio_layer = join(self.script_path, "eas.lyr")
#         self.empty_prior_layer = join(self.script_path, "esp.lyr")
#         self.empty_layers = {"group": self.empty_group_layer,
#                              "model": self.empty_model_layer,
#                              "relia": self.empty_relia_layer,
#                              "accim": self.empty_accim_layer,
#                              "regio": self.empty_regio_layer,
#                              "prior": self.empty_prior_layer}
#         # configurable settings
#         self.source_fgdb = join(self.appdata_path, "asdst_source.gdb")
#         self.template_mxd = join(self.appdata_path, "asdst_default.mxd")
#         self.log_file = join(self.appdata_path, "asdst.log")
#         self.ahims_sites = None
#         self.has_source_gdb = False
#         self.has_template_mxd = False
#         # logging
#         # global log
#         # log = logging
#         log.basicConfig(filename=self.log_file, filemode="w", level=log.DEBUG)
#         log.debug("Config.__init__: " + str(locals()))
#
#     def layer_dictionary(self, local_workspace):
#         # type: (str) -> dict[str: dict[str: str]]
#         source_ws = self.source_fgdb
#         sfx_1750 = "_v7"
#         sfx_curr = "_current"
#         return {k: {"name": v,
#                     "1750_source": (join(source_ws, k.lower() + sfx_1750)),
#                     "1750_local": (join(local_workspace, k.lower() + "_1750")),
#                     "curr_local": (join(local_workspace, k.lower() + sfx_curr))}
#                 for k, v in asdst_extension.codes.iteritems()}
#
#     def set_user_config(self, source_fgdb, template_mxd, ahims_sites):
#         # type: (str, str, str) -> None
#         """ Saves setting to JSON file
#
#         Args:
#
#         Returns:
#
#         Raises:
#           No raising or catching
#
#         """
#         # message("set_usr_config")
#
#         errors = []
#         cfg = {}
#
#         if not ap.Exists(source_fgdb):
#             errors.append("Source file geodatabase does not exist")
#             cfg["source_fgdb"] = self.source_fgdb
#         else:
#             self.source_fgdb = source_fgdb
#             cfg["source_fgdb"] = source_fgdb
#
#         if not ap.Exists(template_mxd):
#             errors.append("Template map does not exist")
#             cfg["template_mxd"] = self.template_mxd
#         else:
#             self.template_mxd = template_mxd
#             cfg["template_mxd"] = template_mxd
#
#         if ahims_sites and not ap.Exists(ahims_sites):
#             errors.append("AHIMS site data '{0}' does not exist")
#             cfg["ahims_sites"] = self.ahims_sites
#         else:
#             self.ahims_sites = ahims_sites
#             cfg["ahims_sites"] = ahims_sites
#
#         cfg["errors"] = errors
#
#         with open(self.config_file, 'w') as f:
#             dump(cfg, f)
#
#         return
#
#     def get_user_config(self):
#         # type: () -> [str, str, str]
#         """ Saves settings to JSON file
#
#         Returns:
#             3-tuple of strings
#
#         Raises:
#             Nothing explicit
#
#         """
#         return self.source_fgdb, self.template_mxd, self.ahims_sites
#
#     def validate(self):
#         # type: () -> object
#         # asdst.message("Config.validate")
#         self.errors = []
#
#         # check if the app data folder is there, if not create
#         if not exists(self.appdata_path):
#             try:
#                 makedirs(self.appdata_path)
#             except Exception as e:
#                 self.errors.append(e)
#
#         # check if the config file is there, if not create
#         if not exists(self.config_file):
#             try:
#                 open(self.config_file, 'a').close()
#             except Exception as e:
#                 self.errors.append(e)
#
#         cfg = {}
#         try:
#             with open(self.config_file, 'r') as f:
#                 cfg = load(f)
#         except Exception as e:
#             self.errors.append(e)
#
#         self.source_fgdb = cfg.get("source_fgdb", "")
#         self.template_mxd = cfg.get("template_mxd", "")
#         self.ahims_sites = cfg.get("ahims_sites", "")
#
#         self.has_source_gdb = False
#         if not self.source_fgdb:
#             self.errors.append("Source FGDB is not set")
#         elif not ap.Exists(self.source_fgdb):
#             self.errors.append(
#                 "Source FGDB '{0}' does not exist".format(self.source_fgdb))
#         else:
#             self.has_source_gdb = True
#
#         self.has_template_mxd = False
#         if not self.template_mxd:
#             self.errors.append("Template map is not set")
#         elif not ap.Exists(self.template_mxd):
#             self.errors.append(
#                 "Template map '{0}' does not exist".format(self.template_mxd))
#         else:
#             self.has_template_mxd = True
#
#         if self.ahims_sites and not ap.Exists(self.ahims_sites):
#             self.errors.append(
#                 "AHIMS site data '{0}' does not exist".format(self.ahims_sites))
#
#         v = "ASDST Version {0}".format(self.version)
#         e = self.errors
#         if not e:
#             e = u"No start-up errors identified."
#
#         ws = self.script_path
#         r = [ws,
#              nice_test(self.toolbox, ws),
#              nice_test(self.template_project_gdb, ws),
#              nice_test(self.template_context_gdb, ws),
#              nice_test(self.empty_group_layer, ws),
#              nice_test(self.empty_model_layer, ws),
#              nice_test(self.empty_relia_layer, ws),
#              nice_test(self.empty_accim_layer, ws),
#              nice_test(self.config_file, ws),
#              nice_test(self.source_fgdb, ws, "Source FGDB"),
#              nice_test(self.template_mxd, ws, "Template MXD"),
#              nice_test(self.ahims_sites, ws, "AHIMS Sites")]
#
#         f = u"{0}\n{1}\n{2}\n{3}\n{4}\n{5}\n{6}\n{7}\n{8}\n{9}\n{10}\n{11}\nu{12}\n{13}"
#
#         self.status = f.format(v, e, *r)
#
#         # asdst.message("Config.validate END")
#         return
#


class ConfigureTool(object):

    class ToolValidator(object):
        """Class for validating a tool's parameter values and controlling the behavior of the tool's dialog."""

        def __init__(self, parameters):
            """Setup arcpy and the list of tool parameters."""
            self.params = parameters

        def initializeParameters(self):
            """Refine the properties of a tool's parameters.  This method is
            called when the tool is opened."""

            try:
                cfg = asdst_extension.config.get_user_config()
                self.params[0].value = cfg[0]
                self.params[1].value = cfg[1]
                self.params[2].value = cfg[2]
                pass
            except:
                pass

            return

        def updateParameters(self):
            """Modify the values and properties of parameters before internal
            validation is performed.  This method is called whenever a parameter
            has been changed."""

            return

        def updateMessages(self):
            """Modify the messages created by internal validation for each tool
            parameter.  This method is called after internal validation."""
            if self.params[2].value:
                fields = ap.ListFields(self.params[2].value)
                fieldnames = {f.name for f in fields}
                codes = {k for k, v in asdst_extension.codes.iteritems()}
                miss = codes - fieldnames
                if miss:
                    self.params[2].setErrorMessage("Feature class does is missing required fields {}".format(", ".join(miss)))

            return

    def __init__(self):
        self.label = u'Configure'
        self.description = u'Configure parameters for the ASDST'
        self.canRunInBackground = False

    def getParameterInfo(self):
        pass
        # Source_Database
        param_1 = ap.Parameter()
        param_1.name = u'Source_Database'
        param_1.displayName = u'Source Database'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'Workspace'
        try:
            param_1.value = asdst_extension.config.source_fgdb
        except:
            pass

        # Template_Map
        param_2 = ap.Parameter()
        param_2.name = u'Template_Map'
        param_2.displayName = u'Template Map'
        param_2.parameterType = 'Required'
        param_2.direction = 'Input'
        param_2.datatype = u'ArcMap Document'
        try:
            param_2.value = asdst_extension.config.template_mxd  # u'C:\\AppData\\Local\\ASDST\\template.mxd'
        except:
            pass

        # AHIMS_Sites
        param_3 = ap.Parameter()
        param_3.name = u'AHIMS_Sites'
        param_3.displayName = u'AHIMS Sites'
        param_3.parameterType = 'Optional'
        param_3.direction = 'Input'
        param_3.datatype = u'Feature Class'
        try:
            param_3.value = asdst_extension.config.ahims_sites
        except:
            pass

        return [param_1, param_2, param_3]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        validator = getattr(self, 'ToolValidator', None)
        if validator:
            return validator(parameters).updateParameters()

    def updateMessages(self, parameters):
        validator = getattr(self, 'ToolValidator', None)
        if validator:
            return validator(parameters).updateMessages()

    def execute(self, parameters, messages):
        asdst_extension.config.set_user_config(parameters[0].valueAsText,
                                             parameters[1].valueAsText,
                                             parameters[2].valueAsText)

        # pass

# def main():
#         """ Main entry
#
#         Args:
#
#         Returns:
#
#         Raises:
#           No raising or catching
#
#         """
#         asdst_extension.config.set_user_config(parameters[0].valueAsText,
#                                      parameters[1].valueAsText,
#                                      parameters[2].valueAsText)
#
#     if __name__ == '__main__':
#         main()

