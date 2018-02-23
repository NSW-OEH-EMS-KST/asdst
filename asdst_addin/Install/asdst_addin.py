from os.path import realpath, dirname
import sys
sys.path.append(dirname(realpath(__file__)))
import pythonaddins
from state import ProjectStateMachine
from utils import get_toolbox

from config import SystemConfig, AsdstDataConfig

# BUG
# https://community.esri.com/thread/199743-problems-with-event-handlers-not-firing-in-python-add-in-extensions
#
# from ArcGIS 10.5.1 Issues Addressed List: https://support.esri.com/en/download/7514
# BUG-000103736 Python add-in extensions are not turned on by default even if self.enabled is set to True.


# # for the use of tools (performance)
# SYSTEM_CONFIG = SystemConfig()
# TOOLBOX = get_toolbox()
# print TOOLBOX
# USER_CONFIG = {}
# MAP_CONFIG = None
# ASDST_DATA_CONFIG = None
# STATE_MACHINE = None

# def get_global_sm():
#     global STATE_MACHINE
#     if not STATE_MACHINE:
#     STATE_MACHINE
#
# STATE = None

#
# def get_project_mxd():
#     try:
#         return extension.state.user_config.project_mxd
#     except:
#         return ProjectStateMachine(None).user_config.project_mxd
#     # return extension.state.map_config.project_mxd

# def get_project_gdb():
#     try:
#         return STATE.map_config.project_mxd
#     except:
#         return "No Project GDB available"
    # return extension.state.map_config.project_mxd

#
# def get_template_mxd():
#     try:
#         return extension.state.user_config.template_mxd
#     except:
#         return ProjectStateMachine(None).user_config.template_mxd
#     # return extension.state.user_config.template_mxd
#
#
# def get_template_project_gdb():
#     return extension.state.system_config.template_project_gdb
#
#
# def get_ahims_points():
#     return extension.state.user_config.ahims_pts


# def send_event(event):
#     try:
#         STATE.on_event(event)
#     except Exception as e:
#         print "Error sending event '{}': {}".format(event, e)


# def get_user_config():
#     try:
#         return STATE.user_config.get_config()
#     except:
#         return {}
#
#
# def set_user_config(source_fgdb, template_mxd, ahims_sites, messages=None):
#
#     return STATE.user_config.set_config(source_fgdb, template_mxd, ahims_sites, messages=messages)


# def get_system_config(ByFile=False):
#
#     if ByFile:
#         return SystemConfig(get_source_gdb()).get_config_by_file()
#
#     global SYSTEM_CONFIG
#
#     if not SYSTEM_CONFIG:
#         SYSTEM_CONFIG = STATE.state.system_config.get_config()
#
#     return SYSTEM_CONFIG


# def get_asdst_data_config():
#     return extension.state.asdst_data_config.get_config()


# def get_layer_map(gdb):
#
#     return STATE.asdst_data_config.get_layer_map(gdb)
#     # return asdst_addin.extension.state.asdst_data_config.get_layer_map(gdb)


class InfoButton(object):

    def __init__(self):
        self.enabled = False

        return

    def onClick(self):
        print "InfoButton.onClick"

        pythonaddins.MessageBox(extension.state.get_state_report(), "ASDST Configuration")

        return


# class ManageLayersButton(object):
#
#     def __init__(self):
#
#         self.enabled = False
#
#         return
#
#     def onClick(self):
#         print "ManageLayersButton.onClick"
#
#         pythonaddins.GPToolDialog(TOOLBOX, "ManageLayersTool")
#
#         return


class ConfigureButton(object):

    def __init__(self):

        self.enabled = False

        return

    def onClick(self):
        print "ConfigureButton.onClick"

        pythonaddins.GPToolDialog(extension.toolbox, "ConfigureTool")

        extension.state.on_event("user_config_updated")

        return


class CalculateContextButton(object):

    def __init__(self):

        self.enabled = False

        return

    def onClick(self):
        print "CalculateContextButton.onClick"

        pythonaddins.GPToolDialog(extension.toolbox, "ContextCalculationTool")

        return


class CreateProjectButton(object):

    def __init__(self):

        self.enabled = False

        return

    def onClick(self):
        print "CreateProjectButton.onClick"

        pythonaddins.GPToolDialog(extension.toolbox, "CreateProjectTool")

        return


class BuildDataButton(object):

    def __init__(self):

        self.enabled = False

        return

    def onClick(self):
        print "BuildDataButton.onClick"

        pythonaddins.GPToolDialog(extension.toolbox, "BuildDataTool")

        extension.state.on_event("asdst_data_built")

        return


class AsdstExtension(object):

    def __init__(self):
        print "AsdstExtension.__init__"

        self.enabled = True  # no good until after version 10.5.1 when this bug was fixed

        self.state = ProjectStateMachine(self)
        self.toolbox = get_toolbox()
        print self.toolbox
        # global STATE
        # STATE = ProjectStateMachine(self)
        #
        # global TOOLBOX  #, SYSTEM_CONFIG
        # # SYSTEM_CONFIG = STATE.system_config.get_config()
        # TOOLBOX = get_toolbox()

        return

    def startup(self):
        print "AsdstExtension.startup"

        extension.state.on_event("startup")

        return

    def newDocument(self):
        print "AsdstExtension.newDocument"

        extension.state.on_event("newDocument")

        return

    def openDocument(self):
        print "AsdstExtension.openDocument"

        extension.state.on_event("openDocument")

        return

    def itemAdded(self, new_item):
        print "AsdstExtension.itemAdded"

        extension.state.on_event("itemAdded")

        return

    def itemDeleted(self, deleted_item):
        print "AsdstExtension.itemDeleted"

        extension.state.on_event("itemDeleted")

        return

    def enable_tools(self):
        print "AsdstExtension.enable_tools()"

        cmd_info.enabled = True
        cmd_configure.enabled = True
        cmd_create_project.enabled = True
        cmd_build_data.enabled = True
        cmd_calculate_context.enabled = True

        state = str(extension.state.state)
        print "state: {}".format(state)

        if state == "InvalidMap":
            cmd_build_data.enabled = False
            cmd_calculate_context.enabled = False

        if state == "InvalidAsdstData":
            cmd_calculate_context.enabled = False

        #
        # #
        # # sys_config = get_system_config()
        # #
        # # system_config_valid = system_config_is_valid(sys_config)
        # # user_config_valid = user_config_is_valid()
        # #
        # cmd_create_project.enabled = self.state.system_config.valid and self.state.user_config.valid
        # #
        # # asdst_data_valid = asdst_data_is_valid()
        # # map_config_valid = map_config_is_valid()
        # #
        # cmd_build_data.enabled = self.state.map_config.valid and not self.state.asdst_data_config.valid
        # #
        # cmd_calculate_context.enabled = self.state.asdst_data_config.valid

        return

