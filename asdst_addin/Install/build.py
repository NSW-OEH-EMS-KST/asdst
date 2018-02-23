import arcpy
from arcpy import env
from arcpy import mapping
import os
from utils import compact_fgdb, add_layers_to_mxd, add_table_to_mxd, geodata_exists, get_template_layers, get_source_gdb, get_layer_map
from os.path import realpath, dirname, join


class BuildDataTool(object):

    def __init__(self):

        self.label = u'Build ASDST Data'
        self.description = u'Build ASDST data for project'
        self.canRunInBackground = True

        self.empty_polyfeature_layer = join(dirname(realpath(__file__)), "epf.lyr")
        self.mxd = mapping.MapDocument("CURRENT")
        self.project_gdb = self.mxd.filePath.replace(".mxd", ".gdb")

        self.empty_polyfeature_layer_exists = geodata_exists(self.empty_polyfeature_layer)
        self.project_gdb_exists = geodata_exists(self.project_gdb)

        return

    def getParameterInfo(self):

        # Project_Area
        param0 = arcpy.Parameter()
        param0.name = 'Project_Area'
        param0.displayName = 'Project Area'
        param0.parameterType = 'Required'
        param0.direction = 'Input'
        param0.datatype = 'GPFeatureRecordSetLayer'

        param0.value = self.empty_polyfeature_layer

        return [param0]

    # def isLicensed(self):
    #
    #     return True
    #
    # def updateParameters(self, parameters):
    #
    #     return

    def updateMessages(self, parameters):

        if not self.empty_polyfeature_layer_exists:
            parameters[0].setWarningMessage("Input drawing layer could not be created.\n"
                                            "Empty polygon feature layer {} does not exist".format(self.empty_polyfeature_layer_exists))
        return

    def execute(self, parameters, messages):

        # Aliases
        add_message = messages.addMessage
        add_error = messages.addErrorMessage

        # Get user input
        geometry = parameters[0].value  # geometry (feature set)

        # Import project area into project workspace i.e. save the geometry to be used
        add_message("Importing area")

        if not self.project_gdb_exists:  # standard case, same name as mxd
            add_error("Project geodatabase '{}' does not exist".format(self.project_gdb))
            raise arcpy.ExecuteError

        area = os.path.join(self.project_gdb, "project_area")
        try:
            # might be a feature set
            geometry.save(area)
            add_message("\tTemporary feature set imported to {}".format(area))
        except:
            try:
                # or might be a layer
                arcpy.CopyFeatures_management(geometry, area)
                add_message("\tFeature layer imported to {}".format(area))
            except Exception as e:
                # or who knows what it is!
                add_error("Error copying project area feature {0}".format(e.message))
                raise arcpy.ExecuteError

        # Build data
        source_fgdb = get_source_gdb()
        add_message("Building data into {} from {}".format(self.project_gdb, source_fgdb))
        layer_map = get_layer_map(self.project_gdb)

        layer_map2 = {}

        add_message("\tClipping model reliability layer")

        n = "drvd_rel"
        src = os.path.join(source_fgdb, n)
        lcl = os.path.join(self.project_gdb, n)
        add_message("\t\t{} \t{} --> {}".format(n, src, lcl))
        arcpy.Clip_management(src, "#", lcl, area, "#", "ClippingGeometry")
        layer_map2["reliability"] = lcl
        arcpy.BuildRasterAttributeTable_management(lcl, "Overwrite")
        try:  # wrap this: it fails if the raster contains only 0's (SHL)
            arcpy.CalculateStatistics_management(lcl)
        except:
            pass

        add_message("\tClipping survey priority layer")

        n = "drvd_srv"
        lcl = os.path.join(self.project_gdb, n)
        src = os.path.join(source_fgdb, n)
        add_message("\t\t{} \t{} --> {}".format(n, src, lcl))
        arcpy.Clip_management(src, "#", lcl, area, "#", "ClippingGeometry")
        layer_map2["priority"] = lcl
        arcpy.BuildRasterAttributeTable_management(lcl, "Overwrite")
        try:  # wrap this: it fails if the raster contains only 0's (SHL)
            arcpy.CalculateStatistics_management(lcl)
        except:
            pass

        add_message("\tClipping regionalisation layers")

        for i in range(1, 5):
            n = "aslu_lvl{0}".format(i)
            src = os.path.join(source_fgdb, n)
            lcl = os.path.join(self.project_gdb, n)
            add_message("\t\t{}\t{} --> {}".format(n, src, lcl))
            arcpy.Clip_analysis(src, area, lcl)
            layer_map2[n] = lcl

        add_message("\tClipping 1750 layers")

        for k, v in layer_map.iteritems():
            lyr = v["name"]
            src, lcl = v["1750_source"], v["1750_local"]
            add_message("\t\t{}\t{} --> {}".format(lyr, src, lcl))
            arcpy.Clip_management(src, "#", lcl, area, "#", "ClippingGeometry")
            arcpy.BuildRasterAttributeTable_management(lcl, "Overwrite")
            try:  # wrap this: it fails if the raster contains only 0's (SHL)
                arcpy.CalculateStatistics_management(lcl)
            except:
                pass

        src = os.path.join(source_fgdb, "cu_param3")
        add_message("\tCalculating current layers using '{}'".format(src))

        try:
            lup = os.path.join(self.project_gdb, "cu_param3")
            arcpy.Clip_management(src, "#", lup, area, "#", "ClippingGeometry")
            arcpy.CalculateStatistics_management(lup)
            loss_rasters = {}
            env.workspace = self.project_gdb

            for k, v in layer_map.iteritems():
                n = v["name"]
                lcl = v["curr_local"]
                add_message("\t\t{}\t{}".format(n, lcl))
                arcpy.gp.Lookup_sa(src, k, lup)
                ras_par = arcpy.Raster(lup)
                ras_1750 = arcpy.Raster(v["1750_local"])
                ras_curr = arcpy.sa.Int((ras_par / 100.0) * ras_1750)
                ras_curr.save(lcl)
                ras_loss = arcpy.sa.Minus(ras_1750, ras_curr)
                ras_loss.save(os.path.join(self.project_gdb, "loss_{}".format(k.lower())))
                loss_rasters[n] = ras_loss.catalogPath
                arcpy.BuildRasterAttributeTable_management(lcl, "Overwrite")
                try:  # wrap this: it fails if the raster contains only 0's (SHL)
                    arcpy.CalculateStatistics_management(lcl)
                except:
                    pass
                del ras_curr, ras_1750, ras_loss, ras_par

        except Exception as e:
            add_error(str(e))
            exit()

        add_message("\tCalculating accumulated impact")
        t_ras = None
        for k, ras in loss_rasters.iteritems():
            add_message("\t\t{0}".format(k))
            t_ras = arcpy.Raster(ras)
            if t_ras is not None:
                t_ras += t_ras
        acc_ds = os.path.join(self.project_gdb, "acc_impact_unscaled")
        t_ras.save(acc_ds)
        arcpy.BuildRasterAttributeTable_management(t_ras, "Overwrite")
        try:
            arcpy.CalculateStatistics_management(t_ras)
        except:
            pass
        minv = int(arcpy.GetRasterProperties_management(t_ras, "MINIMUM").getOutput(0))
        maxv = int(arcpy.GetRasterProperties_management(t_ras, "MAXIMUM").getOutput(0))
        # Rescaled grid = [(grid - Min value from grid) * (Max scale value - Min scale value) / (Max value from grid - Min value from grid)] + Min scale value
        t_ras_2 = (t_ras - minv) * (1000 - 0) / (maxv - minv)
        acc_ds = os.path.join(self.project_gdb, "acc_impact_scaled")
        t_ras_2.save(acc_ds)
        del t_ras, t_ras_2
        layer_map2["impact"] = acc_ds

        add_message("\tCalculating loss")
        loss = os.path.join(self.project_gdb, "project_loss")
        ic = arcpy.da.InsertCursor(loss, "*")
        n = 0
        for k, v in layer_map.iteritems():
            add_message("\t\t{0}".format(v["name"]))
            n += 1
            sum_1750 = arcpy.RasterToNumPyArray(v["1750_local"], nodata_to_value=0).sum()
            sum_curr = arcpy.RasterToNumPyArray(v["curr_local"], nodata_to_value=0).sum()
            sum_change = (sum_curr - sum_1750)
            if sum_curr == 0 and sum_1750 == 0:
                loss_val = 0
            elif sum_change == sum_1750:
                loss_val = 100
            else:
                loss_val = int((sum_1750 - sum_curr) * 100.0 / sum_1750)
            vals = (n, k, v["name"], sum_1750, sum_curr, sum_change, loss_val)
            ic.insertRow(vals)
        del ic

        # Compact the FGDB workspace
        add_message(compact_fgdb(self.project_gdb))

        # Add data to map
        add_message("Adding data layers to map...")
        add_table_to_mxd(loss, messages=messages)

        template_layers = get_template_layers()

        lyrs = {"Model Reliability": layer_map2["reliability"]}
        add_layers_to_mxd(lyrs, "Derived", "relia", template_layers, messages=messages)

        lyrs = {"Survey Priority": layer_map2["priority"]}
        add_layers_to_mxd(lyrs, "Derived", "prior", template_layers, messages=messages)

        lyrs = {"Accumulated Impact": layer_map2["impact"]}
        add_layers_to_mxd(lyrs, "Derived", "accim", template_layers, messages=messages)

        lyrs = {"Regionalisation Level {0}".format(i): layer_map2["aslu_lvl{0}".format(i)] for i in range(1, 5)}
        add_layers_to_mxd(lyrs, "Regionalisation", "regio", template_layers, messages=messages)

        lyrs = {v["name"]: v["1750_local"] for k, v in layer_map.iteritems()}
        add_layers_to_mxd(lyrs, "Pre-1750", "model", template_layers, messages=messages)

        lyrs = {v["name"]: v["curr_local"] for k, v in layer_map.iteritems()}
        add_layers_to_mxd(lyrs, "Current", "model", template_layers, messages=messages)

        # Save and report status
        # mxd.save()
        add_message("ASDST data built OK")

        return
