import arcpy as ap
from arcpy import env as env
import arcpy.mapping as am
import os
import log
import ast
import utils


class Project(object):
    def __init__(self, configuration, add_layers, add_table, compact_fgdb):
        self.configuration = configuration
        self.add_layers = add_layers
        self.add_table = add_table
        self.compact_fgdb = compact_fgdb
        self.title = None
        self.gdb = None
        self.mxd = am.MapDocument("CURRENT")
        self.df = None
        self.valid = None
        # self.missing_layers = True
        self.validate()

    @log.log
    def refresh(self):

        self.valid = False
        self.mxd = am.MapDocument("CURRENT")

        if not self.mxd:  # at startup?
            return

        self.df = am.ListDataFrames(self.mxd)[0]
        self.gdb = None
        gdb = self.mxd.filePath.replace(".mxd", ".gdb")
        if ap.Exists(gdb):  # standard case, same name as mxd
            self.valid = True
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
                        self.valid = True

        # self.status = self.get_project_status()
        # self.missing_layers = (u"\t\u2716" in self.status)

        # status = []
        #
        # lyrs = am.ListLayers(self.mxd)
        # if not lyrs:
        #     status.append("Map document has no layers")
        #
        # ws = self.gdb if self.gdb else None
        # if not ws:
        #     status.append("No ASDST Project Workspace")
        # else:
        #     f = u"{0}\n{1}\n{2}\n{3}\n{4}\n{5}\n{6}\n{7}\n{8}\n{9}\n{10}\n{11}\n" \
        #         u"{12}\n{13}\n{14}\n{15}\n{16}\n{17}\n{18}"
        #     r = [ws]
        #     for k, v in self.configuration.layer_dictionary(ws).iteritems():
        #         r.append(utils.exists_tuple(v["1750_local"]))
        #         r.append(utils.exists_tuple(v["curr_local"]))
        #
        #     return f.format(*r)
        self.validate()

        return

    @log.log
    def validate(self):
        # self.refresh()

        result = []
        for k, v in self.configuration.layer_dictionary(self.gdb or "NONE").iteritems():
            result.append(utils.exists_tuple("", v["1750_local"]))
            result.append(utils.exists_tuple("", v["curr_local"]))

        x = [c for a, b, c in result]
        self.valid = not (False in x)
        return result

    @log.log
    def get_project_status(self):
        true = u"\u2714"
        false = u"\u2716"
        fmt = u"{} {}"

        s = self.validate()
        s = [[unicode(item), [false, true][value]] for desc, item, value in s]
        s = [fmt.format(item, value) for item, value in s]
        s.append("THE PROJECT IS " + ["INVALID", "VALID"][self.valid])

        return "\n".join(s)


def get_project(configuration, add_layers, add_table, compact_fgdb):
    return Project(configuration, add_layers, add_table, compact_fgdb)


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

    def __init__(self):
        self.enabled = False
        self.label = u'Create Project'
        self.description = "Create a new ASDST Project"
        self.canRunInBackground = True
        self.raw_title = ""
        self.directory = ""
        self.geometry = None
        self.sane_title = ""
        self.base = ""
        self.gdb = ""
        self.area = ""
        self.loss = ""
        self.mxd_file = ""
        self.mxd = None
        self.success = ""
        self.layer_dict = None
        self.layer_dict2 = {}

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

        # Project_Area
        param_4 = ap.Parameter()
        param_4.name = u'Project_Area'
        param_4.displayName = u'Project Area'
        param_4.parameterType = 'Required'
        param_4.direction = 'Input'
        param_4.datatype = u'GPFeatureRecordsetlayer'
        # fs = ap.FeatureSet()
        # fc = ap.CreateFeatureclass_management("in_memory", "fc", "POLYGON")
        # fs.load(fc)
        # try:
        #     fc = ap.CreateFeatureclass_management("in_memory", "fc", "POLYGON")
        #     # efs = ap.MakeFeatureLayer_management(ASDST_EXTENSION.config.empty_featureset_layer, "efs")
        #     # efs.replaceDataSource(fc)  # p, "FILEGDB_WORKSPACE", n, validate=False)
        #     # efs = am.Layer(ASDST_EXTENSION.config.empty_featureset_layer)
        #     # # param_4.value = u'in_memory\\{714ADB01-ECAF-44AD-9CE1-0DE3ECF49BBB}'
        #     param_4.value = fc
        # except:
        #     pass

        return [param_1, param_2, param_3, param_4]

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
        import asdst_addin
        # Aliases
        add_message = messages.addMessage
        add_error = messages.addErrorMessage

        # Get user inputs
        self.raw_title = parameters[0].valueAsText  # title
        self.description = parameters[1].valueAsText  # title
        self.directory = parameters[2].valueAsText  # parent directory
        self.geometry = parameters[3]  # geometry (feature set)
        self.sane_title = self.raw_title.lower().replace(" ", "_")
        self.base = os.path.join(self.directory, self.sane_title)
        self.mxd_file = self.base + ".mxd"
        self.gdb = self.base + ".gdb"
        self.area = os.path.join(self.gdb, "project_area")
        self.loss = os.path.join(self.gdb, "project_loss")
        self.success = "ASDST project '{0}' launched in new window"
        self.success = self.success.format(self.raw_title)
        self.layer_dict = self.configuration.layer_dictionary(self.gdb)

        # Make the required file os.system
        ok_msg = "Project {0} created: {1}"
        err_msg = "Error creating {0}: {1}"
        try:
            ap.Copy_management(self.configuration.template_project_gdb, self.gdb)
            add_message(ok_msg.format("geodatabase", self.gdb))
        except Exception as e:
            add_error(err_msg.format(self.gdb, e.message))
            raise ap.ExecuteError
        try:
            ap.Copy_management(self.configuration.template_mxd, self.mxd_file)
            add_message(ok_msg.format("map document", self.mxd_file))
            self.mxd = ap.mapping.MapDocument(self.mxd_file)
        except Exception as e:
            add_error(err_msg.format(self.mxd, e.message))
            raise ap.ExecuteError

        # Fix default MXD tags
        add_message("Fixing tags...")
        try:
            self.mxd.title = self.raw_title
            tag = {"ASDST": "DO NOT EDIT THIS TAG",
                   "Version": 7,
                   "Title": self.sane_title,
                   "mxd": self.mxd_file,
                   "gdb": self.gdb}
            tag = str(tag).replace(",", ";")
            self.mxd.tags = ",".join([self.mxd.tags, tag])
        except Exception as e:
            add_error(e)

        # Import project areas into project workspace i.e. save the geometry to be used
        add_message("Importing areas...")
        msg = "...area imported: {0} ({1} - {2})"
        # save the new geometry
        try:
            # might be a feature set
            self.geometry.save(self.area)
            msg = msg.format(self.area, "Feature set created by user", "Temporary")
            add_message(msg)
        except:
            try:
                # or might be a layer
                ap.CopyFeatures_management(self.geometry, self.area)
                msg = msg.format(self.area, "Feature layer", self.geometry)
                add_message(msg)
            except Exception as e:
                # or fuck knows what it is
                add_error("Error copying project area feature {0}".format(e.message))
                raise ap.ExecuteError

        # Build data
        add_message("Building data...")

        add_message("...clipping model reliability layer...")
        src = os.path.join(self.configuration.source_fgdb, "drvd_rel")
        add_message("... ...{0}".format(os.path.split(src)[1]))
        lcl = os.path.join(self.gdb, "drvd_rel")
        ap.Clip_management(src, "#", lcl, self.area, "#", "ClippingGeometry")
        self.layer_dict2["reliability"] = lcl

        add_message("...clipping survey priority layer...")
        src = os.path.join(self.configuration.source_fgdb, "drvd_srv")
        add_message("... ...{0}".format(os.path.split(src)[1]))
        lcl = os.path.join(self.gdb, "drvd_srv")
        ap.Clip_management(src, "#", lcl, self.area, "#", "ClippingGeometry")
        self.layer_dict2["priority"] = lcl

        add_message("...clipping regionalisation layers...")
        for i in range(1, 5):
            n = "aslu_lvl{0}".format(i)
            src = os.path.join(self.configuration.source_fgdb, n)
            add_message("... ...{0}".format(n))
            lcl = os.path.join(self.gdb, n)
            ap.Clip_analysis(src, self.area, lcl)
            self.layer_dict2[n] = lcl

        add_message("...clipping 1750 layers...")
        for k, v in self.layer_dict.iteritems():
            lyr = v["name"]
            add_message("... ...{0}".format(lyr))
            src, lcl = v["1750_source"], v["1750_local"]
            ap.Clip_management(src, "#", lcl, self.area, "#", "ClippingGeometry")
            ap.BuildRasterAttributeTable_management(lcl, "Overwrite")
            try:  # wrap this: it fails if the raster contains only 0's (SHL)
                ap.CalculateStatistics_management(lcl)
            except:
                pass

        add_message("...calculating current layers...")
        src = os.path.join(self.configuration.source_fgdb, "cu_param3")
        lup = os.path.join(self.gdb, "cu_param3")
        ap.Clip_management(src, "#", lup, self.area, "#", "ClippingGeometry")
        loss_rasters = {}
        env.workspace = self.gdb
        for k, v in self.layer_dict.iteritems():
            add_message("... ...{0}".format(v["name"]))
            ras_par = ap.sa.Lookup(lup, k)  # lcl_lup_ras, k)
            ras_1750 = ap.Raster(v["1750_local"])
            ras_curr = ap.sa.Int((ras_par / 100.0) * ras_1750)
            lcl = v["curr_local"]
            ras_curr.save(lcl)
            ras_loss = ap.sa.Minus(ras_1750, ras_curr)
            ras_loss.save(os.path.join(self.gdb, "loss_{0}".format(k.lower())))
            loss_rasters[v["name"]] = ras_loss.catalogPath
            ap.BuildRasterAttributeTable_management(lcl, "Overwrite")
            try:  # wrap this: it fails if the raster contains only 0's (SHL)
                ap.CalculateStatistics_management(lcl)
            except:
                pass
            del ras_curr, ras_1750, ras_loss, ras_par

        add_message("...calculating accumulated impact...")
        t_ras = None
        for k, ras in loss_rasters.iteritems():
            add_message("... ...{0}".format(k))
            t_ras = ap.Raster(ras)
            if t_ras is not None:
                t_ras += t_ras
        acc_ds = os.path.join(self.gdb, "acc_impact_unscaled")
        t_ras.save(acc_ds)
        ap.BuildRasterAttributeTable_management(t_ras, "Overwrite")
        try:
            ap.CalculateStatistics_management(t_ras)
        except:
            pass
        minv = int(ap.GetRasterProperties_management(t_ras, "MINIMUM").getOutput(0))
        maxv = int(ap.GetRasterProperties_management(t_ras, "MAXIMUM").getOutput(0))
        # Rescaled grid = [(grid - Min value from grid) * (Max scale value - Min scale value) / (Max value from grid - Min value from grid)] + Min scale value
        t_ras_2 = (t_ras - minv) * (1000 - 0) / (maxv - minv)
        acc_ds = os.path.join(self.gdb, "acc_impact_scaled")
        t_ras_2.save(acc_ds)
        del t_ras, t_ras_2
        self.layer_dict2["impact"] = acc_ds

        add_message("...calculating loss...")

        ic = ap.da.InsertCursor(self.loss, "*")
        n = 0
        for k, v in self.layer_dict.iteritems():
            add_message("... ...{0}".format(v["name"]))
            n += 1
            sum_1750 = ap.RasterToNumPyArray(v["1750_local"], nodata_to_value=0).sum()
            sum_curr = ap.RasterToNumPyArray(v["curr_local"], nodata_to_value=0).sum()
            sum_change = (sum_curr - sum_1750)
            if sum_curr == 0 and sum_1750 == 0:
                loss = 0
            elif sum_change == sum_1750:
                loss = 100
            else:
                loss = int((sum_1750 - sum_curr) * 100.0 / sum_1750)
            vals = (n, k, v["name"], sum_1750, sum_curr, sum_change, loss)
            ic.insertRow(vals)
        del ic

        # Compact the FGDB workspace
        add_message(self.compact_fgdb(self.gdb))

        # Add data to map
        add_message("Adding data layers to map...")

        self.add_table(self.mxd, self.loss)

        lyrs = {"Model Reliability": self.layer_dict2["reliability"]}
        self.add_layers(self.mxd, lyrs, "Derived", "relia")

        lyrs = {"Survey Priority": self.layer_dict2["priority"]}
        self.add_layers(self.mxd, lyrs, "Derived", "prior")

        lyrs = {"Accumulated Impact": self.layer_dict2["impact"]}
        self.add_layers(self.mxd, lyrs, "Derived", "accim")

        lyrs = {"Regionalisation Level {0}".format(i): self.layer_dict2["aslu_lvl{0}".format(i)] for i in
                range(1, 5)}
        self.add_layers(self.mxd, lyrs, "Regionalisation", "regio")

        lyrs = {v["name"]: v["1750_local"] for k, v in self.layer_dict.iteritems()}
        self.add_layers(self.mxd, lyrs, "Pre-1750", "model")

        lyrs = {v["name"]: v["curr_local"] for k, v in self.layer_dict.iteritems()}
        self.add_layers(self.mxd, lyrs, "Current", "model")

        # Save and report status
        self.mxd.save()
        add_message(self.success)

        # Launch new MXD
        os.system(self.mxd_file)



def main():
    pass

if __name__ == '__main__':
    main()
