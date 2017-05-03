from __future__ import print_function
import arcpy as ap
import os
# import log
import utils
import json


class ConfigureTool(object):
    class ToolValidator(object):
        """Class for validating a tool's parameter values and controlling the behavior of the tool's dialog."""

        # @log.log
        def __init__(self, parameters):
            """Setup arcpy and the list of tool parameters."""

            self.params = parameters

            return

        # @log.log
        def initializeParameters(self):
            """Refine the properties of a tool's parameters.  This method is
            called when the tool is opened."""

            cfg = get_asdst_config()

            self.params[0].value = cfg.get("source_fgdb", "")  # cfg[0]
            self.params[1].value = cfg.get("template_mxd", "")  # cfg[1]
            self.params[2].value = cfg.get("ahims_sites", "")  # cfg[2]

            return

        # @log.log
        def updateParameters(self):
            """Modify the values and properties of parameters before internal
            validation is performed.  This method is called whenever a parameter
            has been changed."""

            return

        # @log.log
        def updateMessages(self):
            """Modify the messages created by internal validation for each tool
            parameter.  This method is called after internal validation."""

            if self.params[2].value:
                fields = ap.ListFields(self.params[2].value)
                fieldnames = {f.name for f in fields}
                codes = {k for k, v in get_codes().iteritems()}
                missing = codes - fieldnames
                if missing:
                    self.params[2].setErrorMessage(
                        "Feature class is missing required fields {}".format(", ", os.path.os.path.join(missing)))

            return

    # @log.log
    def __init__(self):

        self.label = u'Configure Extension'
        self.description = u'Configure parameters for the ASDST extension'
        self.canRunInBackground = True

        return

    # @log.log
    def getParameterInfo(self):

        cfg = get_asdst_config()

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

    # @log.log
    def isLicensed(self):

        return True

    # @log.log
    def updateParameters(self, parameters):

        validator = getattr(self, 'ToolValidator', None)
        if validator:
            return validator(parameters).updateParameters()

        return

    # @log.log
    def updateMessages(self, parameters):

        validator = getattr(self, 'ToolValidator', None)
        if validator:
            return validator(parameters).updateMessages()

        return

    # @log.log
    def execute(self, parameters, messages):

        set_user_config(parameters[0].valueAsText, parameters[1].valueAsText, parameters[2].valueAsText)

        utils.set_dataframe_spatial_reference(3308, messages)

        return


def get_config_file_and_path():
    return os.path.join(utils.get_appdata_path(), "config.json")


def get_default_settings():
    script_path = os.path.dirname(os.path.realpath(__file__))

    toolbox = os.path.join(script_path, "asdst_toolbox.pyt")
    template_project_gdb = os.path.join(script_path, "project.gdb")
    template_context_gdb = os.path.join(script_path, "context.gdb")

    # empty model layers
    empty_group_layer = os.path.join(script_path, "egl.lyr")
    empty_model_layer = os.path.join(script_path, "eml.lyr")
    empty_relia_layer = os.path.join(script_path, "erl.lyr")
    empty_accim_layer = os.path.join(script_path, "eai.lyr")
    empty_regio_layer = os.path.join(script_path, "eas.lyr")
    empty_prior_layer = os.path.join(script_path, "esp.lyr")
    empty_polyf_layer = os.path.join(script_path, "epf.lyr")
    empty_layers = {"group": empty_group_layer,
                    "model": empty_model_layer,
                    "relia": empty_relia_layer,
                    "accim": empty_accim_layer,
                    "regio": empty_regio_layer,
                    "prior": empty_prior_layer,
                    "polyf": empty_polyf_layer}

    appdata_path = utils.get_appdata_path()
    log_file = os.path.join(appdata_path, "asdst.log")

    # configurable settings
    source_fgdb = os.path.join(appdata_path, "asdst_source.gdb")
    template_mxd = os.path.join(appdata_path, "asdst_default.mxd")
    ahims_sites = ""

    return locals()


def make_default_config_file():
    config_path_and_file = get_config_file_and_path()

    if not os.path.exists(config_path_and_file):

        path, filename = os.path.split(config_path_and_file)

        if not os.path.exists(path):
            os.makedirs(path)

        open(config_path_and_file, 'a').close()  # shortcut to create file

        with open(config_path_and_file, 'w') as f:
            json.dump(get_default_settings(), f)

    return


def get_asdst_config(messages=None):
    if messages:
        say = messages.AddMessage
    else:
        say = print

    say("Reading ASDST configuration")

    config_file = get_config_file_and_path()

    if not os.path.exists(config_file):
        say("No config file. Creating default file with defaults.")
        make_default_config_file()

    with open(config_file, 'r') as f:
        cfg = json.load(f)

    say("ASDST configuration is:\n{}".format(cfg))

    return cfg


# def get_asdst_config():
#
#     with open(get_config_file_and_path(), 'r') as f:
#
#         return json.load(f)


# @log.log
def get_asdst_config_status():
    # type: () -> [[str, str, str]]
    """ Validate the configuration

    :return:
    """
    config = get_asdst_config()

    result = [utils.exists_return_tuple(k, v) for k, v in config.iteritems()]

    # result = [exists_return_tuple("Python Toolbox", self.toolbox),
    #           exists_return_tuple("Log File", self.log_file),
    #           exists_return_tuple("Template Project FGDB", self.template_project_gdb),
    #           exists_return_tuple("Template Context FGDB", self.template_context_gdb),
    #           exists_return_tuple("Template GROUP Layer", self.empty_group_layer),
    #           exists_return_tuple("Template MODEL Layer", self.empty_model_layer),
    #           exists_return_tuple("Template RELIA Layer", self.empty_relia_layer),
    #           exists_return_tuple("Template ACCIM Layer", self.empty_accim_layer),
    #           exists_return_tuple("Template REGIO Layer", self.empty_regio_layer),
    #           exists_return_tuple("Template PRIOR Layer", self.empty_prior_layer),
    #           exists_return_tuple("Configuration File", self.config_file),
    #           exists_return_tuple("Source FGDB", self.source_fgdb),
    #           exists_return_tuple("Template MXD", self.template_mxd),
    #           exists_return_tuple("AHIMS Sites", self.ahims_sites)]

    # log.debug("validate= {}".format(result))

    return result


# @log.log
def get_asdst_config_status_pretty():
    true = u"\u2714"
    false = u"\u2716"
    fmt = u"{} {}"

    s = get_asdst_config_status()

    uni = [[unicode(desc), [false, true][value]] for desc, item, value in s]
    fmt_uni = [fmt.format(desc, value) for desc, value in uni]

    valid = False not in [value for desc, item, value in s[:-1]]  # AHIMS optional
    fmt_uni.append("THE CONFIGURATION IS " + ["INVALID", "VALID"][valid])

    return "\n".join(fmt_uni)


# @log.log
def get_user_config():
    # type: () -> [str, str, str]
    """ Gets settings from JSON file

    Returns:
        3-tuple of strings

    """
    cfg = get_asdst_config()

    return [cfg["source_fgdb"], cfg["template_mxd"], cfg["ahims_sites"]]


# @log.log
def set_user_config(source_fgdb, template_mxd, ahims_sites):
    # type: (str, str, str) -> None
    """ Saves settings to JSON file

    :param source_fgdb:
    :param template_mxd:
    :param ahims_sites:
    :return:
    """

    cfg = get_asdst_config()

    cfg["source_fgdb"] = source_fgdb
    cfg["template_mxd"] = template_mxd
    cfg["ahims_sites"] = ahims_sites

    with open(get_config_file_and_path(), 'w') as f:

        json.dump(cfg, f)

    return


# @log.log
def get_layer_dictionary(local_workspace):
    # type: (str) -> dict[str: dict[str: str]]
    """ Build a dict of layers

    :param local_workspace:
    :return:
    """
    cfg = get_asdst_config()

    source_ws = cfg["source_fgdb"]

    sfx_1750 = "_v7"
    sfx_curr = "_current"

    d = {k: {"name": v,
             "1750_source": (os.path.join(source_ws, k.lower() + sfx_1750)),
             "1750_local": (os.path.join(local_workspace, k.lower() + "_1750")),
             "curr_local": (os.path.join(local_workspace, k.lower() + sfx_curr))}
         for k, v in get_codes().iteritems()}

    return d


# @log.log
def config_is_valid():

    status = get_asdst_config_status()

    return False not in [c for a, b, c in status[:-1]]  # Ahims is optional


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
