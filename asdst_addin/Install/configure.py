from os.path import realpath, dirname, join, split, exists
import arcpy as ap
from config import get_codes
from utils import get_user_config, set_user_config


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
    def initializeParameters(self):

        cfg = get_user_config()

        self.params[0] = cfg.get("source_fgdb", "")
        self.params[1] = cfg.get("template_mxd", "")
        self.params[2] = cfg.get("ahims_sites", "")

        return

    def updateParameters(self, parameters):

        # if parameters[0].altered or parameters[1].altered or parameters[2].altered:
        #     set_user_config(parameters[0].valueAsText, parameters[1].valueAsText, parameters[2].valueAsText)

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

        # send_event("user_config_updated")

        return


