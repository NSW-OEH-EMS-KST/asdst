from __future__ import print_function
import arcpy as ap
import os
from utils import set_dataframe_spatial_reference
from asdst_addin import get_user_config, set_user_config, get_codes
from log import log


class ConfigureTool(object):

    @log
    def __init__(self):

        self.label = u'Configure Extension'
        self.description = u'Configure parameters for the ASDST extension'
        self.canRunInBackground = True

        return

    @log
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
    # def updateParameters(self, parameters):
    #
    #     return

    @log
    def updateMessages(self, parameters):

        if parameters[2].value:
            fields = ap.ListFields(parameters[2].value)
            fieldnames = {f.name for f in fields}
            codes = {k for k, v in get_codes().iteritems()}
            missing = codes - fieldnames
            if missing:
                parameters[2].setErrorMessage(
                    "Feature class is missing required fields {}".format(", ", os.path.os.path.join(missing)))

    @log
    def execute(self, parameters, messages):

        set_user_config(parameters[0].valueAsText, parameters[1].valueAsText, parameters[2].valueAsText)

        set_dataframe_spatial_reference(3308, messages)

        return
