# from __future__ import print_function
import arcpy
import pythonaddins
import os
import sys
# sys.path.append(os.path.dirname(__file__))
# import log
# import configure
# import project
# import utils

# PROTECTED_GROUPS = ["Areas of Interest", "Context", "Pre-1750", "Current", "ASDST"]
# STARTED = None


# @log.log
# def addin_message(msg, mb=0):
#     return pythonaddins.MessageBox(msg, "ASDST Extension", mb)


# @log.log
# def get_asdst_status():
#
#     bar = '{0:-<60}'.format('')
#     msg = u"Configuration Status:\n{0}\n{1}\n\nProject Status:\n{0}\n{2}"
#
#     config_status = configure.Configuration().get_config_status()
#     project_status = project.Project().get_project_status()
#
#     return msg.format(bar, config_status, project_status)


class InfoButton(object):
    """Implementation for asdst_extension_addin.cmd_label (Button)"""

    # @log.log
    def onClick(self):

        print "onClick " + "InfoButton"
        # pythonaddins.MessageBox("onClick", "InfoButton", 0)
        # msg = configure.get_asdst_config_status_pretty()
        # addin_message(msg)

        # return


# class StreamOrderButton(object):
#     """Implementation for asdst_extension_addin.cmd_stream_order (Button)"""
#
#     # @log.log
#     def onClick(self):
#
#         # pythonaddins.GPToolDialog(configure.Configuration().toolbox, "ContextCalculationTool")
#
#         return


# class CalculateContextButton(object):
#     """Implementation for asdst_extension_addin.cmd_calculate_context (Button)"""
#
#     # @log.log
#     def onClick(self):
#
#         # cfg = configure.Configuration()
#         # prj = project.Project()
#         #
#         # if cfg.valid() and prj.valid():
#         #     pythonaddins.GPToolDialog(configure.Configuration().toolbox, "ContextCalculationTool")
#         # else:
#         #     addin_message("Configuration and/or project are invalid")
#
#         return


# class CreateProjectButton(object):
#     """Implementation for asdst_extension_addin.cmd_new_project (Button)"""
#
#     # @log.log
#     def onClick(self):
#
#         # cfg = configure.Configuration()
#         #
#         # if cfg.valid():
#         #     pythonaddins.GPToolDialog(configure.Configuration().toolbox, "CreateProjectTool")
#         # else:
#         #     addin_message("Configuration is invalid")
#
#         return


# class BuildDataButton(object):
#     """Implementation for asdst_extension_addin.cmd_new_project (Button)"""
#
#     # @log.log
#     def onClick(self):
#
#         # cfg = configure.Configuration()
#         # prj = project.Project()
#         #
#         # if cfg.valid() and prj.valid_gdb_and_srs():
#         #     pythonaddins.GPToolDialog(configure.Configuration().toolbox, "BuildDataTool")
#         # else:
#         #     addin_message("Configuration and/or project are invalid")
#
#         return


class ConfigureButton(object):
    """Implementation for asdst_extension_addin.setup (Button)"""

    # @log.log
    def onClick(self):

        print "onClick " + "ConfigureButton"

        # pythonaddins.MessageBox("onClick", "ConfigureButton", 0)
        # pythonaddins.GPToolDialog(configure.Configuration().toolbox, "ConfigureTool")

        # return


class AsdstExtension(object):
    """Implementation for asdst_extension_addin.extension (Extension)"""

    # For performance considerations, remove all unused methods in this class.

    # @log.log
    def __init__(self):

        print "__init__ " + "AsdstExtension"

        # log.configure_logging()
        # pythonaddins.MessageBox("__init__", "AsdstExtension", 0)
        # addin_message("__init__")
        # log.configure_logging(configure.Configuration().log_file, addin_message)
        self.enabled = True

        # logging.debug("AsdstExtension.__init__")

        # global ASDST_EXTENSION
        # ASDST_EXTENSION = self

        # self.config = Config(self)
        # self.config.validate()

        # self.project = Project()
        # self.project.validate()
        #
        # self._enable_tools()

        # except Exception as e:
        #     pass
        # logging.error(e)

        # return

    # @log.log
    def startup(self):

        print "startup " + "AsdstExtension"
        # pythonaddins.MessageBox("startup", "AsdstExtension", 0)
        # addin_message("startup")
        # config = configure.Configuration()
        # log.configure_logging(configure.Configuration().log_file, addin_message)
        # self._enable_tools()
        # addin_message(configuration.validate())
        # # addin_message(configuration.valid)
        # # addin_message(configuration.log_file)
        # log.configure_logging(configuration.log_file, log.DEBUG, addin_message)

        # return

    # # @log.log
    # def newDocument(self):
    #     # if not current_project:
    #     #     return
    #
    #     # current_project.refresh()
    #     self._enable_tools()
    #
    #     return
    #
    # # @log.log
    # def openDocument(self):
    #     # if not current_project:
    #     #     return
    #
    #     # current_project.refresh()
    #     self._enable_tools()
    #
    #     return

    # # @log.log
    # def itemAdded(self, new_item):
    #     # if not current_project:
    #     #     return
    #
    #     # current_project.refresh()
    #     self._enable_tools()
    #
    #     return
    #
    # # @log.log
    # def itemDeleted(self, deleted_item):
    #     # if not current_project:
    #     #     return
    #
    #     # current_project.refresh()
    #     self._enable_tools()
    #
    #     return

    # # @log.log
    # def _enable_tools(self):
    #
    #     # addin_message("_enable_tools")
    #     # if not configuration:
    #     #     raise ValueError("No Config")
    #     # if not current_project:
    #     #     raise ValueError("No project")
    #
    #     # CreateProjectButton.enabled = configuration.valid
    #     # CalculateContextButton.enabled = False
    #     # StreamOrderButton.enabled = False
    #
    #     # if not configuration.valid:
    #     #     log.debug("configuration.valid = FALSE")
    #     #     return
    #
    #     # # log.debug("Listing layers in {}".format(current_project.mxd))
    #     # mxd = arcpy.mapping.MapDocument("CURRENT")
    #     # lyrs = arcpy.mapping.ListLayers(mxd)
    #     # # addin_message(lyrs)
    #     # # addin_message(lyrs is not None)
    #     #
    #     # config = configure.Configuration()
    #     # CreateProjectButton.enabled = (lyrs or False) and config.valid
    #     # if lyrs:  # require at least one layer for context
    #     #     log.debug("Enabling CreateProjectButton")
    #     #     CreateProjectButton.enabled = True
    #
    #     # log.debug("Layers: {}".format(lyrs))
    #
    #     # if not current_project.valid:
    #     #     log.debug("current_project.valid = FALSE")
    #     #     return
    #
    #     # CalculateContextButton.enabled = not self.project.missing_layers
    #
    #         # StreamOrderButton...
    #
    #     return


# def is_within_project_area(area):
#     prj_lyr = am.ListLayers(am.MapDocument("CURRENT"), "Project Area")
#     if not prj_lyr:
#         raise Exception("No layer called 'Project Area'")
#
#     mlyr = join("in_memory", "tmp")
#     ap.MakeFeatureLayer_management(area, mlyr)
#     ap.SelectLayerByLocation_management(mlyr, 'WITHIN', prj_lyr)
#
#     count = int(ap.GetCount_management(mlyr).getOutput(0))
#
#     return count > 0
