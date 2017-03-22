import arcpy as ap
import arcpy.mapping as am
import os
import log
import ast
import utils
import configure


class Project(object):
    @log.log
    def __init__(self):

        self.title = None
        self.gdb = None
        self.mxd = am.MapDocument("CURRENT")
        self.df = None
        self.df = am.ListDataFrames(self.mxd)[0]
        self.gdb = None

        gdb = self.mxd.filePath.replace(".mxd", ".gdb")
        if ap.Exists(gdb):  # standard case, same name as mxd
            self.gdb = gdb
        else:  # mxd saved to a new name, go to tags
            tags = self.mxd.tags
            if tags:
                tag_list = tags.os.path.split(",")
                tag = [t for t in tag_list if (("ASDST" in t) and ("gdb" in t))]
                if tag:
                    tag = tag[0]
                    tag = tag.replace(";", ",")
                    tag = ast.literal_eval(tag)
                    gdb = tag.get("gdb", None)

                    if gdb and os.path.exists(gdb):
                        self.gdb = gdb

        return

    @log.log
    def valid(self):
        status = self.get_status()

        return False not in [c for a, b, c in status]

    @log.log
    def valid_gdb_and_srs(self):

        return utils.geodata_exists(self.gdb) and utils.get_dataframe_spatial_reference().factoryCode == 3308

    @log.log
    def get_status(self):

        result = []
        for k, v in configure.Configuration().layer_dictionary(self.gdb or "NONE").iteritems():
            result.append(utils.exists_return_tuple("description", v["1750_local"]))
            result.append(utils.exists_return_tuple("description", v["curr_local"]))

        result.append(["", "Dataframe spatial reference is GDA_1994_NSW_Lambert", self.df.spatialReference.name == "GDA_1994_NSW_Lambert"])

        return result

    @log.log
    def get_project_status(self):
        true = u"\u2714"
        false = u"\u2716"
        fmt = u"{} {}"

        s = self.get_status()

        uni = [[unicode(item), [false, true][value]] for desc, item, value in s]
        fmt_uni = [fmt.format(item, value) for item, value in uni]

        valid = False not in [value for desc, item, value in s]
        fmt_uni.append("THE PROJECT IS " + ["INVALID", "VALID"][valid])

        return "\n".join(fmt_uni)


class CreateProjectTool(object):

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

        config = configure.Configuration()

        messages.addMessage("Creating project geodatabase '{}'".format(gdb))
        ap.Copy_management(config.template_project_gdb, gdb)

        messages.addMessage("Creating project map document '{}'".format(mxd_file))
        ap.Copy_management(config.template_mxd, mxd_file)

        # Fix default MXD tags
        messages.addMessage("Fixing mxd tags")
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
