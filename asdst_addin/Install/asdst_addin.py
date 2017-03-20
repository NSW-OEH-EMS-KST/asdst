from __future__ import print_function
import arcpy as ap
import arcpy.mapping as am
import pythonaddins as pa
import os
import sys
sys.path.append(os.path.dirname(__file__))
import log
import configure
import project


@log.log
def addin_message(msg, mb=0):
    return pa.MessageBox(msg, "ASDST Extension", mb)


PROTECTED = ["Areas of Interest", "Context", "Pre-1750", "Current", "ASDST"]


configuration = configure.get_configuration()
log.configure_logging(configuration.log_file, log.DEBUG, addin_message)


class InfoButton(object):
    """Implementation for asdst_extension_addin.cmd_label (Button)"""

    @log.log
    def onClick(self):
        msg = get_asdst_status()
        addin_message(msg)
        return


class StreamOrderButton(object):
    """Implementation for asdst_extension_addin.cmd_stream_order (Button)"""

    @log.log
    def onClick(self):
        # msg = get_asdst_status()
        # log.info(msg)
        return


class CalculateContextButton(object):
    """Implementation for asdst_extension_addin.cmd_new_project (Button)"""

    @log.log
    def onClick(self):
        # pa.GPToolDialog(ASDST_EXTENSION.config.toolbox, "ContextCalculationTool")
        return


class CreateProjectButton(object):
    """Implementation for asdst_extension_addin.cmd_new_project (Button)"""

    @log.log
    def onClick(self):

        pa.GPToolDialog(configuration.toolbox, "CreateProjectTool")

        return


class ConfigureButton(object):
    """Implementation for asdst_extension_addin.setup (Button)"""

    @log.log
    def onClick(self):
        pa.GPToolDialog(configuration.toolbox, "ConfigureTool")

        return


class AsdstExtension(object):
    """Implementation for asdst_extension_addin.extension (Extension)"""

    # For performance considerations, remove all unused methods in this class.

    @log.log
    def __init__(self):
        addin_message("__init__")
        # logging.debug("AsdstExtension.__init__")

        # global ASDST_EXTENSION
        # ASDST_EXTENSION = self

        # self.config = Config(self)
        # self.config.validate()

        # self.project = Project()
        # self.project.validate()
        #
        # self.__enable_tools()

        # except Exception as e:
        #     pass
        # logging.error(e)

        return

    @log.log
    def startup(self):
        addin_message("startup")
        addin_message(configuration.validate())
        # addin_message(configuration.valid)
        # addin_message(configuration.log_file)
        log.configure_logging(configuration.log_file, log.DEBUG, addin_message)

    @log.log
    def newDocument(self):
        addin_message("newDocument")
        project.validate()
        # self.__enable_tools()
        return

    @log.log
    def openDocument(self):
        addin_message("openDocument")
        project.validate()
        # self.__enable_tools()
        return


@log.log
def get_asdst_status():
    bar = '{0:-<60}'.format('')
    msg = u"Configuration Status:\n{0}\n{1}\n\nProject Status:\n{0}\n{2}"
    config_status = configuration.get_config_status()
    # config_status = self.config.config.status
    # ASDST_EXTENSION.project.validate()
    # project_status = ASDST_EXTENSION.project.status
    project_status = project.get_project_status()
    msg = msg.format(bar, config_status, project_status)
    return msg


        # @log.log
        # def itemAdded(self, new_item):
        #     self.__enable_tools()
        #     return

        # def itemDeleted(self, deleted_item):
        #     self.__enable_tools()
        #     return

        # @log.log
        # def __enable_tools(self):
        #
        #     if not self.config:
        #         raise ValueError("No Config")
        #     if not self.project:
        #         raise ValueError("No project")
        #
        #     CreateProjectButton.enabled = False
        #     CalculateContextButton.enabled = False
        #     StreamOrderButton.enabled = False
        #
        #     if self.config.errors:
        #         log.debug("config errors: {}".format(self.config.errors))
        #         return
        #
        #     log.debug("Listing layers in {}".format(self.project.mxd))
        #
        #     lyrs = am.ListLayers(self.project.mxd)
        #     if lyrs:  # require at least one layer for context
        #         log.debug("Enabling CreateProjectButton")
        #         CreateProjectButton.enabled = True
        #
        #     log.debug("Layers: {}".format(lyrs))
        #
        #     if not self.project.valid:
        #         log.debug("Invalid project, returning")
        #         return
        #     CalculateContextButton.enabled = not self.project.missing_layers
        #
        #         # StreamOrderButton... tODO
        #
        #     return


@log.log
def add_table(mxd, table, name=""):
    df = am.ListDataFrames(mxd)[0]
    tv = am.TableView(table)
    if name:
        tv.name = name
    am.AddTableView(df, tv)
    return


@log.log
def add_layers(mxd, layers, group_name, layer_type):
    # layers is a {name: datasource} dictionary

    if isinstance(mxd, basestring):
        mxd = am.MapDocument(mxd)

    df = am.ListDataFrames(mxd)[0]
    lyr_file = configuration.empty_layers.get(layer_type, None)
    glyr = None

    if group_name:  # try to find the group
        lyrs = am.ListLayers(mxd, group_name, df)
        glyr = lyrs[0] if lyrs else None
        if not glyr:  # not found, so create it
            glyr = am.Layer(configuration.empty_group_layer)
            glyr.name = group_name
            am.AddLayer(df, glyr)
        # this line is required, arc must add a deep copy or something?
        # anyway without this there is an exception raised
        glyr = am.ListLayers(mxd, group_name, df)[0]

    for k, v in layers.iteritems():
        if not lyr_file:
            lyr = am.Layer(v)
        else:
            lyr = am.Layer(lyr_file)
            p, n = os.path.split(v)
            lyr.replaceDataSource(p, "FILEGDB_WORKSPACE", n, validate=False)
        lyr.name = k
        if glyr:
            am.AddLayerToGroup(df, glyr, lyr)
            log.debug("...'{0}' layer added to group '{1}'".format(lyr.name,
                                                             glyr.name))
        else:
            am.AddLayer(df, lyr)
            log.debug("...'{0}' layer added".format(lyr.name))


def compact_fgdb(gdb):
    from glob import glob
    from os.path import getsize

    sz = 0
    mb = 1024 * 1024

    if gdb and ap.Exists(gdb):
        for f in glob(gdb + "\\*"):
            sz += getsize(f)
        sz /= mb

    return "Size of database '{0}' is ~ {1} MB".format(gdb, sz)


project = project.get_project(configuration, add_layers, add_table, compact_fgdb)

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


# @log.log
# def item_exists_nice(thing_to_check, thing_possible_base, thing_name=""):
#     # good = u"\t\u2714"
#     # bad = u"\t\u2716"
#     good = u"\u2714"
#     bad = u"\u2716"
#     # u = u"{0: <20}{1}"
#     u = u"{0} {1}"
#
#     x = unicode(thing_to_check.replace(thing_possible_base, "..."))
#
#     if not thing_to_check or not ap.Exists(thing_to_check):
#         if thing_name:
#             x = unicode(thing_name)
#         ret = u.format(x, bad)
#     else:
#         ret = u.format(x, good)
#
#     return ret
