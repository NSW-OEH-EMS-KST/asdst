import arcpy
from os.path import realpath, dirname, join
# from asdst_addin import get_system_config
from utils import get_user_config


class CreateProjectTool(object):

    def __init__(self):

        self.label = u'Create Project'
        self.description = u'Create a new ASDST project'
        self.canRunInBackground = True

        return

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

    def execute(self, parameters, messages):

        # Get user inputs
        raw_title = parameters[0].valueAsText  # title
        description = parameters[1].valueAsText  # description
        directory = parameters[2].valueAsText  # parent directory

        sane_title = raw_title.lower().replace(" ", "_")
        base = join(directory, sane_title)

        gdb = base + ".gdb"

        # sys_cfg =
        t_gdb = join(dirname(realpath(__file__)), "project.gdb")   # get_system_config()["template_project_gdb"]

        messages.addMessage("Creating project geodatabase '{}' using '{}'".format(gdb, t_gdb))

        arcpy.Copy_management(t_gdb, gdb)

        mxd_file = base + ".mxd"
        t_mxd = get_user_config()["template_mxd"]

        messages.addMessage("Creating project map document '{}' using '{}'".format(mxd_file, t_mxd))

        arcpy.Copy_management(t_mxd, mxd_file)

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

