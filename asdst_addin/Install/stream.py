import arcpy as ap
# import arcpy.mapping as am
import os
import log
# import ast
import utils
# import configure


class StreamOrderTool(object):

    class ToolValidator(object):
        """Class for validating a tool's parameter values and controlling
        the behavior of the tool's dialog."""

        def __init__(self, parameters):
            """Setup arcpy and the list of tool parameters."""
            self.params = parameters

        def initializeParameters(self):
            """Refine the properties of a tool's parameters.  This method is
            called when the tool is opened."""
            return

        def updateParameters(self):
            """Modify the values and properties of parameters before internal
            validation is performed.  This method is called whenever a parameter
            has been changed."""
            return

        def updateMessages(self):
            """Modify the messages created by internal validation for each tool
            parameter.  This method is called after internal validation."""
            return

    @log.log
    def __init__(self):

        self.label = u'Stream'
        self.description = u'Build stream data'
        self.canRunInBackground = True

        return

    @log.log
    def getParameterInfo(self):

        # Name
        param_1 = ap.Parameter()
        param_1.name = u'Name'
        param_1.displayName = u'Name'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'String'

        # Description
        param_2 = ap.Parameter()
        param_2.name = u'Description'
        param_2.displayName = u'Description'
        param_2.parameterType = 'Required'
        param_2.direction = 'Input'
        param_2.datatype = u'String'

        # Parent_Directory
        param_3 = ap.Parameter()
        param_3.name = u'Parent_Directory'
        param_3.displayName = u'Parent Directory'
        param_3.parameterType = 'Required'
        param_3.direction = 'Input'
        param_3.datatype = u'Workspace'

        return [param_1, param_2, param_3]

    @log.log
    def isLicensed(self):
        return True

    @log.log
    def updateParameters(self, parameters):
        validator = getattr(self, 'ToolValidator', None)
        if validator:
            return validator(parameters).updateParameters()

    @log.log
    def updateMessages(self, parameters):
        validator = getattr(self, 'ToolValidator', None)
        if validator:
            return validator(parameters).updateMessages()

    @log.log
    def execute(self, parameters, messages):

        # Get user inputs
        raw_title = parameters[0].valueAsText  # title
        description = parameters[1].valueAsText  # description
        directory = parameters[2].valueAsText  # parent directory

        sane_title = raw_title.lower().replace(" ", "_")
        base = os.path.join(directory, sane_title)
        mxd_file = base + ".mxd"
        gdb = base + ".gdb"

        config = utils.get_asdst_config()

        messages.addMessage("Creating project geodatabase '{}'".format(gdb))
        ap.Copy_management(config["template_project_gdb"], gdb)

        messages.addMessage("Creating project map document '{}'".format(mxd_file))
        ap.Copy_management(config["template_mxd"], mxd_file)

        # Fix default MXD tags
        messages.addMessage("Updating tags")
        mxd = ap.mapping.MapDocument(mxd_file)
        mxd.title = raw_title
        tag = {"ASDST": "DO NOT EDIT THIS TAG",
               "Version": 7,
               "Title": sane_title,
               "mxd": mxd_file,
               "gdb": gdb,
               "Description": description}
        tag = str(tag).replace(",", ";")
        mxd.tags = ",".join([mxd.tags, tag])

        # Save and report status
        mxd.save()
        messages.addMessage("New ASDST project '{0}' is launching in a new ArcMap window".format(raw_title))

        # Launch new MXD
        os.system(mxd_file)


def main():
    return

if __name__ == '__main__':
    main()
