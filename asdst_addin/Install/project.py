import arcpy
from arcpy import mapping
from os import system
from os.path import join
from config import get_config


class CreateProjectTool(object):

    # @log
    def __init__(self):

        self.label = u'Create Project'
        self.description = u'Create a new ASDST project'
        self.canRunInBackground = True

        return

    # @log
    def getParameterInfo(self):

        # Name
        param_1 = arcpy.Parameter()
        param_1.name = u'Name'
        param_1.displayName = u'Name'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'String'

        # Description
        param_2 = arcpy.Parameter()
        param_2.name = u'Description'
        param_2.displayName = u'Description'
        param_2.parameterType = 'Required'
        param_2.direction = 'Input'
        param_2.datatype = u'String'

        # Parent_Directory
        param_3 = arcpy.Parameter()
        param_3.name = u'Parent_Directory'
        param_3.displayName = u'Parent Directory'
        param_3.parameterType = 'Required'
        param_3.direction = 'Input'
        param_3.datatype = u'Workspace'

        return [param_1, param_2, param_3]

    # def isLicensed(self):
    #
    #     return True
    #
    # def updateParameters(self, parameters):
    #
    #     return
    #
    # def updateMessages(self, parameters):
    #
    #     return

    # @log
    def execute(self, parameters, messages):

        # Get user inputs
        raw_title = parameters[0].valueAsText  # title
        description = parameters[1].valueAsText  # description
        directory = parameters[2].valueAsText  # parent directory

        sane_title = raw_title.lower().replace(" ", "_")
        base = join(directory, sane_title)

        config = get_config()

        gdb = base + ".gdb"

        messages.addMessage("Creating project geodatabase '{}'".format(gdb))

        arcpy.Copy_management(config["template_project_gdb"], gdb)

        mxd_file = base + ".mxd"

        messages.addMessage("Creating project map document '{}'".format(mxd_file))

        arcpy.Copy_management(config["template_mxd"], mxd_file)

        # # Fix default MXD tags  REMOVED THIS JUST TAKES TOO LONG ON OEH SYSTEM
        # messages.addMessage("Updating tags")
        # mxd = mapping.MapDocument(mxd_file)
        # mxd.title = raw_title
        # tag = {"ASDST": "DO NOT EDIT THIS TAG",
        #        "Version": 1,
        #        "Title": sane_title,
        #        "mxd": mxd_file,
        #        "gdb": gdb,
        #        "Description": description}
        # tag = str(tag).replace(",", ";")
        # mxd.tags = ",".join([mxd.tags, tag])

        # # Save and report status
        # mxd.save()

        messages.addMessage("New ASDST project '{} ({})' has been created: {}".format(raw_title, description, mxd_file))

        return

        # messages.addMessage("New ASDST project '{0}' is launching in a separate ArcMap window".format(raw_title))
        #
        # # Launch new MXD
        # system(mxd_file)
