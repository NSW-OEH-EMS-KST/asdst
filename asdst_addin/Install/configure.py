import arcpy as ap
from asdst_addin import the_extension, log


class ConfigureTool(object):

    class ToolValidator(object):
        """Class for validating a tool's parameter values and controlling
        the behavior of the tool's dialog."""

        def __init__(self, parameters):
            """Setup arcpy and the list of tool parameters."""
            self.params = parameters

        def initializeParameters(self):
            """Refine the properties of a tool's parameters.  This method is
            called when the tool is opened."""

            try:
                cfg = the_extension.config.get_user_config()
                self.params[0].value = cfg[0]
                self.params[1].value = cfg[1]
                self.params[2].value = cfg[2]
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
                codes = {k for k, v in the_extension.codes.iteritems()}
                miss = codes - fieldnames
                if miss:
                    s = ", ".join(miss)
                self.params[2].setErrorMessage("Feature class does not contain all required fields {0}".format(s))

            return

    def __init__(self):
        self.label = u'Configure Toolbox'
        self.description = u'Set up parameters for the ASDST toolbox'
        self.canRunInBackground = False

    def getParameterInfo(self):
        # Source_Database
        param_1 = ap.Parameter()
        param_1.name = u'Source_Database'
        param_1.displayName = u'Source Database'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'Workspace'
        try:
            param_1.value = the_extension.config.source_fgdb
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
            param_2.value = the_extension.config.template_mxd  # u'C:\\AppData\\Local\\ASDST\\template.mxd'
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
            param_3.value = the_extension.config.ahims_sites
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
        the_extension.config.set_user_config(parameters[0].valueAsText,
                                             parameters[1].valueAsText,
                                             parameters[2].valueAsText)

    # def main():
    #     """ Main entry
    #
    #     Args:
    #
    #     Returns:
    #
    #     Raises:
    #       No raising or catching
    #
    #     """
    #     asdst.config.set_user_config(parameters[0].valueAsText,
    #                                  parameters[1].valueAsText,
    #                                  parameters[2].valueAsText)
    #
    # if __name__ == '__main__':
    #     main()

