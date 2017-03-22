import arcpy as ap
import os
import log
import json
import utils


class Configuration(object):
    @log.log
    def __init__(self):

        self.codes = dict(AFT="Stone artefact", ART="Rock art", BUR="Burial", ETM="Earth mound", GDG="Grinding groove",
                          HTH="Hearth or camp fire feature", SHL="Shell midden", STQ="Stone quarry", TRE="Scarred tree")

        self.codes_ex = dict(ACD="Aboriginal ceremony and dreaming", ARG="Aboriginal resource gathering",
                             AFT="Stone artefact", ART="Rock art", BUR="Burial", CFT="Conflict site",
                             CMR="Ceremonial ring", ETM="Earth mound", FSH="Fish trap", GDG="Grinding groove",
                             HAB="Habitation structure", HTH="Hearth or camp fire feature", OCQ="Ochre quarry",
                             PAD="Potential archaeological deposit", SHL="Shell midden", STA="Stone arrangement",
                             STQ="Stone quarry", TRE="Scarred tree", WTR="Water feature")

        # status stuff
        # self.errors = []
        # self.valid = False

        # important files
        self.script_path = os.path.dirname(os.path.realpath(__file__))

        self.appdata_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "ASDST")
        # try:
        if not os.path.exists(self.appdata_path):
            os.makedirs(self.appdata_path)
        # except Exception as e:
        #     self.errors.append("Could not create {}".format(self.appdata_path))

        self.config_file = os.path.join(self.appdata_path, "config.json")
        if not os.path.exists(self.config_file):
            # try:
            open(self.config_file, 'a').close()
            # except Exception as e:
            #     self.errors.append("Could not create {}".format(self.config_file))

        self.log_file = os.path.join(self.appdata_path, "asdst.log")
        # try:
        if not os.path.exists(self.log_file):
            open(self.log_file, 'a').close()
        # except Exception as e:
        #     self.errors.append("Could not create {}".format(self.log_file))

        self.toolbox = os.path.join(self.script_path, "asdst.pyt")

        # template fgdbs
        self.template_project_gdb = os.path.join(self.script_path, "project.gdb")
        self.template_context_gdb = os.path.join(self.script_path, "context.gdb")

        # empty model layers
        self.empty_group_layer = os.path.join(self.script_path, "egl.lyr")
        self.empty_model_layer = os.path.join(self.script_path, "eml.lyr")
        self.empty_relia_layer = os.path.join(self.script_path, "erl.lyr")
        self.empty_accim_layer = os.path.join(self.script_path, "eai.lyr")
        self.empty_regio_layer = os.path.join(self.script_path, "eas.lyr")
        self.empty_prior_layer = os.path.join(self.script_path, "esp.lyr")
        self.empty_polyf_layer = os.path.join(self.script_path, "epf.lyr")
        self.empty_layers = {"group": self.empty_group_layer,
                             "model": self.empty_model_layer,
                             "relia": self.empty_relia_layer,
                             "accim": self.empty_accim_layer,
                             "regio": self.empty_regio_layer,
                             "prior": self.empty_prior_layer,
                             "polyf": self.empty_polyf_layer}

        # configurable settings
        self.source_fgdb = os.path.join(self.appdata_path, "asdst_source.gdb")
        self.template_mxd = os.path.join(self.appdata_path, "asdst_default.mxd")
        self.ahims_sites = ""

        with open(self.config_file, 'r') as f:
            cfg = json.load(f)
            s = cfg.get("source_fgdb", "")
            t = cfg.get("template_mxd", "")
            a = cfg.get("ahims_sites", "")
        if s:
            self.source_fgdb = s
        if t:
            self.template_mxd = t
        if a:
            self.ahims_sites = a

        # self.validate()
        return

    @log.log
    def valid(self):
        status = self.get_status()

        return False not in [c for a, b, c in status[:-1]]  # Ahims is optional

    @log.log
    def get_status(self):

        # type: () -> [[str, str, str]]
        """ Validate the configuration

        :return:
        """
        result = [utils.exists_return_tuple("Python Toolbox", self.toolbox),
                  utils.exists_return_tuple("Log File", self.log_file),
                  utils.exists_return_tuple("Template Project FGDB", self.template_project_gdb),
                  utils.exists_return_tuple("Template Context FGDB", self.template_context_gdb),
                  utils.exists_return_tuple("Template GROUP Layer", self.empty_group_layer),
                  utils.exists_return_tuple("Template MODEL Layer", self.empty_model_layer),
                  utils.exists_return_tuple("Template RELIA Layer", self.empty_relia_layer),
                  utils.exists_return_tuple("Template ACCIM Layer", self.empty_accim_layer),
                  utils.exists_return_tuple("Template REGIO Layer", self.empty_regio_layer),
                  utils.exists_return_tuple("Template PRIOR Layer", self.empty_prior_layer),
                  utils.exists_return_tuple("Configuration File", self.config_file),
                  utils.exists_return_tuple("Source FGDB", self.source_fgdb),
                  utils.exists_return_tuple("Template MXD", self.template_mxd),
                  utils.exists_return_tuple("AHIMS Sites", self.ahims_sites)]

        log.debug("validate= {}".format(result))

        return result

    @log.log
    def get_config_status(self):
        true = u"\u2714"
        false = u"\u2716"
        fmt = u"{} {}"

        s = self.get_status()

        uni = [[unicode(desc), [false, true][value]] for desc, item, value in s]
        fmt_uni = [fmt.format(desc, value) for desc, value in uni]

        valid = False not in [value for desc, item, value in s[:-1]]  # AHIMS optional
        fmt_uni.append("THE CONFIGURATION IS " + ["INVALID", "VALID"][valid])

        return "\n".join(fmt_uni)

    @log.log
    def set_user_config(self, source_fgdb, template_mxd, ahims_sites):
        # type: (str, str, str) -> None
        """ Saves settings to JSON file

        :param source_fgdb:
        :param template_mxd:
        :param ahims_sites:
        :return:
        """

        cfg = {}

        self.source_fgdb = source_fgdb
        cfg["source_fgdb"] = source_fgdb

        self.template_mxd = template_mxd
        cfg["template_mxd"] = template_mxd

        self.ahims_sites = ahims_sites
        cfg["ahims_sites"] = ahims_sites

        with open(self.config_file, 'w') as f:
            json.dump(cfg, f)

        return

    @log.log
    def get_user_config(self):
        # type: () -> [str, str, str]
        """ Saves settings to JSON file

        Returns:
            3-tuple of strings

        Raises:

        """
        return [self.source_fgdb, self.template_mxd, self.ahims_sites]

    @log.log
    def layer_dictionary(self, local_workspace):
        # type: (str) -> dict[str: dict[str: str]]
        """ Build a dict of layers

        :param local_workspace:
        :return:
        """
        # if not local_workspace:
        #     print("local_workspace not set")
        #     return {}
        #
        # if not self.source_fgdb:
        #     print("self.source_fgdb not set")
        #     return {}

        source_ws = self.source_fgdb
        sfx_1750 = "_v7"
        sfx_curr = "_current"

        d = {k: {"name": v,
                 "1750_source": (os.path.join(source_ws, k.lower() + sfx_1750)),
                 "1750_local": (os.path.join(local_workspace, k.lower() + "_1750")),
                 "curr_local": (os.path.join(local_workspace, k.lower() + sfx_curr))}
             for k, v in self.codes.iteritems()}

        return d


class ConfigureTool(object):
    class ToolValidator(object):
        """Class for validating a tool's parameter values and controlling the behavior of the tool's dialog."""

        @log.log
        def __init__(self, parameters):
            """Setup arcpy and the list of tool parameters."""
            self.params = parameters

        @log.log
        def initializeParameters(self):
            """Refine the properties of a tool's parameters.  This method is
            called when the tool is opened."""
            # if not CONFIG:
            #     return
            cfg = Configuration()

            self.params[0].value = cfg.source_fgdb  # cfg[0]
            self.params[1].value = cfg.template_mxd  # cfg[1]
            self.params[2].value = cfg.ahims_sites  # cfg[2]

            return

        @log.log
        def updateParameters(self):
            """Modify the values and properties of parameters before internal
            validation is performed.  This method is called whenever a parameter
            has been changed."""

            return

        @log.log
        def updateMessages(self):
            """Modify the messages created by internal validation for each tool
            parameter.  This method is called after internal validation."""
            if self.params[2].value:
                fields = ap.ListFields(self.params[2].value)
                fieldnames = {f.name for f in fields}
                codes = {k for k, v in Configuration().codes.iteritems()}
                missing = codes - fieldnames
                if missing:
                    self.params[2].setErrorMessage(
                        "Feature class is missing required fields {}".format(", ", os.path.os.path.join(missing)))

            return

    @log.log
    def __init__(self):
        self.label = u'Configure'
        self.description = u'Configure parameters for the ASDST'
        self.canRunInBackground = False

    @log.log
    def getParameterInfo(self):
        cfg = Configuration()
        # if not CONFIG:
        #     return

        # Source_Database
        param_1 = ap.Parameter()
        param_1.name = u'Source_Database'
        param_1.displayName = u'Source Database'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'Workspace'
        try:
            param_1.value = cfg.source_fgdb
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
            param_2.value = cfg.template_mxd
        except:
            pass

        # AHIMS_Sites
        param_3 = ap.Parameter()
        param_3.name = u'AHIMS_Sites'
        param_3.displayName = u'AHIMS Sites'
        param_3.parameterType = 'Optional'
        param_3.direction = 'Input'
        param_3.datatype = u'Feature Class'
        param_3.value = cfg.ahims_sites

        return [param_1, param_2, param_3]

    @log.log
    def isLicensed(self):
        return True

    @log.log
    def updateParameters(self, parameters):
        validator = getattr(self, 'ToolValidator', None)
        if validator:
            return validator(parameters).updateParameters()
        return

    @log.log
    def updateMessages(self, parameters):
        validator = getattr(self, 'ToolValidator', None)
        if validator:
            return validator(parameters).updateMessages()
        return

    @log.log
    def execute(self, parameters, messages):
        cfg = Configuration()

        cfg.set_user_config(parameters[0].valueAsText,
                            parameters[1].valueAsText,
                            parameters[2].valueAsText)

        utils.set_dataframe_spatial_reference(3308, messages)

        return


def main():
    return


if __name__ == '__main__':
    main()
