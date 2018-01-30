from os.path import realpath, dirname
import sys
sys.path.append(dirname(realpath(__file__)))
import pythonaddins
from config import get_toolbox, get_config_status, get_asdst_data_status, asdst_data_is_valid, system_config_is_valid, user_config_is_valid, map_config_is_valid


# BUG
# https://community.esri.com/thread/199743-problems-with-event-handlers-not-firing-in-python-add-in-extensions
#
# from ArcGIS 10.5.1 Issues Addressed List: https://support.esri.com/en/download/7514
# BUG-000103736 Python add-in extensions are not turned on by default even if self.enabled is set to True.


class InfoButton(object):

    def __init__(self):
        self.enabled = False

        return

    def onClick(self):
        print "InfoButton.onClick"

        try:
            pythonaddins.MessageBox(get_config_status(pretty=True), "ASDST Configuration")

            _enable_tools()

        except Exception as e:
            print e

        return


class ManageLayersButton(object):

    def __init__(self):

        self.enabled = False

        return

    def onClick(self):
        print "ManageLayersButton.onClick"

        try:
            pythonaddins.GPToolDialog(get_toolbox(), "ManageLayersTool")

        except Exception as e:
            print e

        return


class ConfigureButton(object):

    def __init__(self):

        self.enabled = False

        return

    def onClick(self):
        print "ConfigureButton.onClick"

        try:
            pythonaddins.GPToolDialog(get_toolbox(), "ConfigureTool")

        except Exception as e:
            print e

        return


class CalculateContextButton(object):

    def __init__(self):

        self.enabled = False

        return

    def onClick(self):
        print "CalculateContextButton.onClick"

        try:
            # if asdst_data_is_valid():
            return pythonaddins.GPToolDialog(get_toolbox(), "ContextCalculationTool")
            # else:
            #     return pythonaddins.MessageBox("Invalid configuration", "Context Calculation")

        except Exception as e:
            print e

        return


class CreateProjectButton(object):

    def __init__(self):

        self.enabled = False

        return

    def onClick(self):
        print "CreateProjectButton.onClick"

        try:
            # if system_config_is_valid() and user_config_is_valid():
            return pythonaddins.GPToolDialog(get_toolbox(), "CreateProjectTool")
            # else:
            #     return pythonaddins.MessageBox("Invalid configuration", "Create Project")

        except Exception as e:
            print e

        return


class BuildDataButton(object):

    def __init__(self):

        self.enabled = False

        return

    def onClick(self):
        print "BuildDataButton.onClick"

        try:
            # if system_config_is_valid() and user_config_is_valid() and map_config_is_valid():
            pythonaddins.GPToolDialog(get_toolbox(), "BuildDataTool")
            # else:
            #     pythonaddins.MessageBox("Invalid configuration", "Build Data")

        except Exception as e:
            print e

        return


def _enable_tools():
    print "_enable_tools()"

    cmd_configure.enabled = True

    cmd_manage_layers.enabled = True

    cmd_create_project.enabled = system_config_is_valid() and user_config_is_valid()

    cmd_build_data.enabled = map_config_is_valid() and (not asdst_data_is_valid())

    cmd_calculate_context.enabled = asdst_data_is_valid()

    return


class AsdstExtension(object):

    def __init__(self):
        print "AsdstExtension.__init__"

        self.enabled = True  # no good until 10.5.1 when this bug was fixed

        return

    def startup(self):
        print "AsdstExtension.startup"

        cmd_info.enabled = True
        cmd_configure.enabled = True
        _enable_tools()

        return

    def newDocument(self):
        print "AsdstExtension.newDocument"

        _enable_tools()

        return

    def openDocument(self):
        print "AsdstExtension.openDocument"

        _enable_tools()

        return

    def itemAdded(self, new_item):
        print "AsdstExtension.itemAdded"

        _enable_tools()

        return

    def itemDeleted(self, deleted_item):
        print "AsdstExtension.itemDeleted"

        _enable_tools()

        return


