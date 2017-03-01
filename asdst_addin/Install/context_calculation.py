import arcpy as ap
from os.path import split, join
from asdst_addin import ASDST_EXTENSION, LOG


class ContextCalculationTool(object):

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
        self.label = u'Context Calculation'
        self.description = u'This tool performs a context calculation.\r\n\r\n Three layers are required: \r\n1. Context\r\n2. Assessment\r\n3. Conservation'
        self.canRunInBackground = False
        self.raw_title = ""
        self.description = ""
        self.parent_dir = ""
        self.geom_context = None
        self.geom_assessment = None
        self.geom_conservation = None
        self.sane_title = ""
        self.gdb_path = ""
        self.gdb_name = ""
        self.gdb = ""
        self.context = ""
        # self.table_full = ""
        self.table_summ = ""
        self.table_ahims = ""
        self.assessment = ""
        self.conservation = ""
        self.areas = {}
        self.success = ""
        self.layer_dict = {}
        # pass

    def getParameterInfo(self):
        # pass
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

        # Context_Feature
        param_3 = ap.Parameter()
        param_3.name = u'Context_Feature'
        param_3.displayName = u'Context Feature'
        param_3.parameterType = 'Required'
        param_3.direction = 'Input'
        param_3.datatype = u'Feature Set'
        # param_3.value = u'in_memory\\{D6FEE351-0F89-4D68-AAF4-1A6B805A2A7E}'

        # Assessment_Feature
        param_4 = ap.Parameter()
        param_4.name = u'Assessment_Feature'
        param_4.displayName = u'Assessment Feature'
        param_4.parameterType = 'Required'
        param_4.direction = 'Input'
        param_4.datatype = u'Feature Set'
        # param_4.value = u'in_memory\\{DA9393B7-7574-4602-9E71-34FBD4BD5500}'

        # Conservation_Feature
        param_5 = ap.Parameter()
        param_5.name = u'Conservation_Feature'
        param_5.displayName = u'Conservation Feature'
        param_5.parameterType = 'Required'
        param_5.direction = 'Input'
        param_5.datatype = u'Feature Set'
        # param_5.value = u'in_memory\\{B59932FD-3155-48B0-988B-4664221D3034}'

        return [param_1, param_2, param_3, param_4, param_5]

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
        # pass
        # Aliases
        add_message = messages.addMessage
        add_error = messages.addErrorMessage

        # Get user inputs
        self.raw_title = parameters[0].valueAsText  # title
        self.description = parameters[1].valueAsText  # description
        self.geom_context = parameters[2]  # geom (feature set)
        self.geom_assessment = parameters[3]  # geom (feature set)
        self.geom_conservation = parameters[4]  # geom (feature set)
        self.sane_title = self.raw_title.lower().replace(" ", "_")
        mxd_path = ap.mapping.MapDocument("current").filePath
        self.gdb_path = split(mxd_path)[0]
        self.gdb_name = "context_{0}".format(self.sane_title) + ".gdb"
        self.gdb = join(self.gdb_path, self.gdb_name)
        # self.table_full = join(self.gdb, "loss_full")
        self.table_summ = join(self.gdb, "loss_summary")
        self.table_ahims = join(self.gdb, "ahims_summary")
        self.context = join(self.gdb, "context_{0}".format(self.sane_title))
        self.assessment = join(self.gdb, "assessment_{0}".format(self.sane_title))
        self.conservation = join(self.gdb, "conservation_{0}".format(self.sane_title))
        self.areas["Context"] = [self.context, self.geom_context]
        self.areas["Assessment"] = [self.assessment, self.geom_assessment]
        self.areas["Conservation"] = [self.conservation, self.geom_conservation]
        self.success = "Context calculation {0} successful ({1})"
        self.success = self.success.format(self.raw_title, self.gdb)

        # nc.check_areas() TODO ?

        # Make the required file system
        ok_msg = "Geodatabase {0} created"
        err_msg = "Error creating {0}: {1}"
        try:
            ap.Copy_management(ASDST_EXTENSION.config.template_context_gdb, self.gdb)
            add_message(ok_msg.format(self.gdb))
        except Exception as e:
            add_error(err_msg.format(self.gdb, e.message))
            raise ap.ExecuteError

        # Import calculation areas into project workspace i.e. save the geometry to be used
        m = "{0} area imported: {1} ({2} - {3})"
        for k, v in self.areas.iteritems():
            try:
                # might be a feature set
                v[1].save(v[0])
                msg = m.format(k, v[0], "New Feature set", "in_memory")
                add_message(msg)
            except:
                try:
                    # or might be a layer
                    ap.CopyFeatures_management(v[1], v[0])
                    msg = m.format(k, v[0], "Feature layer", v[1])
                    add_message(msg)
                except Exception as e:
                    # or fuck knows what it is
                    add_error("Could not copy aoi geometry {0}".format(e.message))
                    raise ap.ExecuteError

        # Build loss data
        add_message("Getting layer dictionary...")
        self.layer_dict = ASDST_EXTENSION.project.layer_dictionary()

        # Calc stats
        add_message("Calculating statistics...")
        n = 0
        res_tot = []
        for k, v in self.layer_dict.iteritems():
            n += 1
            res = [n]
            res2 = [n]
            res.extend([k, ASDST_EXTENSION.codes[k]])  # model_code, model_desc
            res2.extend([k, ASDST_EXTENSION.codes[k]])  # model_code, model_desc
            lyr = v["name"]
            add_message("...{0}".format(lyr))
            lyr = v["1750_local"]
            # context
            tmp_ras = join(self.gdb, "context_{0}_1750".format(k))
            ap.Clip_management(lyr, "#", tmp_ras, self.context, "#", "ClippingGeometry")
            sumcont1750 = ap.RasterToNumPyArray(tmp_ras, nodata_to_value=0).sum()
            res.append(sumcont1750)  # context_sum_1750
            lyr = v["curr_local"]
            tmp_ras = join(self.gdb, "context_{0}_curr".format(k))
            ap.Clip_management(lyr, "#", tmp_ras, self.context, "#", "ClippingGeometry")
            sumcontcurr = ap.RasterToNumPyArray(tmp_ras, nodata_to_value=0).sum()
            res.append(sumcontcurr)  # context_sum_current
            sumchange = (sumcontcurr - sumcont1750)
            res.append(sumchange)  # context_change
            if sumcont1750 == 0:
                loss = 0
            elif sumchange == sumcont1750:
                loss = 100
            else:
                loss = int(-sumchange * 100.0 / sumcont1750)
            res.append(loss)  # context_loss

            # assessment
            tmp_ras = join(self.gdb, "assessment_{0}_curr".format(k))
            ap.Clip_management(lyr, "#", tmp_ras, self.assessment, "#", "ClippingGeometry")
            sumass = ap.RasterToNumPyArray(tmp_ras, nodata_to_value=0).sum()
            res.append(sumass)  # assessment_sum
            if sumcontcurr == 0:
                pcass = 0
            else:
                pcass = int(sumass * 100.0 / sumcontcurr)
            res.append(pcass)  # assessment_pc

            # conservation
            tmp_ras = join(self.gdb, "conservation_{0}_curr".format(k))
            ap.Clip_management(lyr, "#", tmp_ras, self.conservation, "#", "ClippingGeometry")
            sumcons = ap.RasterToNumPyArray(tmp_ras, nodata_to_value=0).sum()
            res.append(sumcons)  # conservation_sum
            if sumcontcurr == 0:
                pccons = 0
            else:
                pccons = int(sumcons * 100.0 / sumcontcurr)
            res.append(pccons)  # conservation_pc

            res_tot.append(res)

        ic = ap.da.InsertCursor(self.table_summ, "*")
        for r in res_tot:
            ic.insertRow(r)
        del ic

        # Build AHIMS data if configured
        if ASDST_EXTENSION.config.ahims_sites:
            add_message("Analysing AHIMS points...")
            res_tot = []
            n = 0
            for k, v in ASDST_EXTENSION.codes_ex.iteritems():
                add_message("...{0}".format(v))
                n += 1
                res = [n]
                res.extend([k, ASDST_EXTENSION.codes_ex[k]])  # model_code, model_desc

                tmp_fc = join(self.gdb, "ahims_{0}_context".format(k))
                if ASDST_EXTENSION.config.ahims_sites:
                    ap.Intersect_analysis([ASDST_EXTENSION.config.ahims_sites, self.context], tmp_fc)
                    sc = ap.da.SearchCursor(tmp_fc, "*", '"{0}" IS NOT NULL'.format(k))
                    l = [r for r in sc]
                    res.append(len(l))  # context_pts
                else:
                    res.append(None)

                tmp_fc = join(self.gdb, "ahims_{0}_assessment".format(k))
                if ASDST_EXTENSION.config.ahims_sites:
                    ap.Intersect_analysis([ASDST_EXTENSION.config.ahims_sites, self.assessment], tmp_fc)
                    sc = ap.da.SearchCursor(tmp_fc, "*", '"{0}" IS NOT NULL'.format(k))
                    l = [r for r in sc]
                    res.append(len(l))  # context_pts
                else:
                    res.append(None)

                tmp_fc = join(self.gdb, "ahims_{0}_conservation".format(k))
                if ASDST_EXTENSION.config.ahims_sites:
                    ap.Intersect_analysis([ASDST_EXTENSION.config.ahims_sites, self.conservation], tmp_fc)
                    sc = ap.da.SearchCursor(tmp_fc, "*", '"{0}" IS NOT NULL'.format(k))
                    l = [r for r in sc]
                    res.append(len(l))  # conservation_pts
                    del sc
                else:
                    res.append(None)

                res_tot.append(res)

            ic = ap.da.InsertCursor(self.table_ahims, "*")
            for r in res_tot:
                ic.insertRow(r)
            del ic

        # Compact the FGDB workspace
        add_message(ASDST_EXTENSION.compact_fgdb(self.gdb))  # note the side effect

        # Add data to map
        add_message("Adding feature layers to map...")
        lyrs = {k: v[0] for k, v in self.areas.iteritems()}
        ASDST_EXTENSION.project.add_layers(lyrs, "Context {}".format(self.sane_title), "calc")
        add_message("Adding result tables to map...")
        ASDST_EXTENSION.add_table(ASDST_EXTENSION.project.mxd, self.table_summ, "context_loss")
        ASDST_EXTENSION.add_table(ASDST_EXTENSION.project.mxd, self.table_ahims, "context_ahims")

        # Save and report status
        ASDST_EXTENSION.project.mxd.save()
        add_message(self.success)

    # class NewCalculation:
    #
    #     def __init__(self):
    #         self.raw_title = ""
    #         self.description = ""
    #         self.parent_dir = ""
    #         self.geom_context = None
    #         self.geom_assessment = None
    #         self.geom_conservation = None
    #         self.sane_title = ""
    #         self.gdb_path = ""
    #         self.gdb_name = ""
    #         self.gdb = ""
    #         self.context = ""
    #         # self.table_full = ""
    #         self.table_summ = ""
    #         self.table_ahims = ""
    #         self.assessment = ""
    #         self.conservation = ""
    #         self.areas = {}
    #         self.success = ""
    #         self.layer_dict = {}
    #
    #     def get_inputs(self, parameters, messages):
    #         self.raw_title = parameters[0].valueAsText  # title
    #         self.description = parameters[1].valueAsText  # description
    #         self.geom_context = parameters[2]  # geom (feature set)
    #         self.geom_assessment = parameters[3]  # geom (feature set)
    #         self.geom_conservation = parameters[4]  # geom (feature set)
    #         self.sane_title = self.raw_title.lower().replace(" ", "_")
    #         mxd_path = ap.mapping.MapDocument("current").filePath
    #         self.gdb_path = split(mxd_path)[0]
    #         self.gdb_name = "context_{0}".format(self.sane_title) + ".gdb"
    #         self.gdb = join(self.gdb_path, self.gdb_name)
    #         # self.table_full = join(self.gdb, "loss_full")
    #         self.table_summ = join(self.gdb, "loss_summary")
    #         self.table_ahims = join(self.gdb, "ahims_summary")
    #         self.context = join(self.gdb, "context_{0}".format(self.sane_title))
    #         self.assessment = join(self.gdb, "assessment_{0}".format(self.sane_title))
    #         self.conservation = join(self.gdb, "conservation_{0}".format(self.sane_title))
    #         self.areas["Context"] = [self.context, self.geom_context]
    #         self.areas["Assessment"] = [self.assessment, self.geom_assessment]
    #         self.areas["Conservation"] = [self.conservation, self.geom_conservation]
    #         self.success = "Context calculation {0} successful ({1})"
    #         self.success = self.success.format(self.raw_title, self.gdb)
    #         return self
    #
    #     def make_fs(self):
    #         ok_msg = "Geodatabase {0} created"
    #         err_msg = "Error creating {0}: {1}"
    #         try:
    #             ap.Copy_management(ASDST_EXTENSION.config.template_context_gdb, self.gdb)
    #             LOG.info(ok_msg.format(self.gdb))
    #         except Exception as e:
    #             LOG.error(err_msg.format(self.gdb, e.message))
    #             exit(1)
    #
    #     def import_calculation_areas(self):
    #         m = "{0} area imported: {1} ({2} - {3})"
    #         # add_message(self.new_areas)
    #         # save the new geometry
    #         for k, v in self.areas.iteritems():
    #             try:
    #                 # might be a feature set
    #                 v[1].save(v[0])
    #                 msg = m.format(k, v[0], "New Feature set", "in_memory")
    #                 add_message(msg)
    #             except:
    #                 try:
    #                     # or might be a layer
    #                     ap.CopyFeatures_management(v[1], v[0])
    #                     msg = m.format(k, v[0], "Feature layer", v[1])
    #                     add_message(msg)
    #                 except Exception as e:
    #                     # or fuck knows what it is
    #                     add_error("Could not copy aoi geometry {0}".format(e.message))
    #                     exit(1)
    #
    #     def build_loss_data(self):
    #
    #         add_message("Getting layer dictionary...")
    #         self.layer_dict = asdst.project.layer_dictionary()
    #         # add_message(self.layer_dict)
    #
    #         add_message("Calculating statistics...")
    #         n = 0
    #         res_tot = []
    #         for k, v in self.layer_dict.iteritems():
    #             n += 1
    #             res = [n]
    #             res2 = [n]
    #             res.extend([k, asdst.codes[k]])  # model_code, model_desc
    #             res2.extend([k, asdst.codes[k]])  # model_code, model_desc
    #             lyr = v["name"]
    #             add_message("...{0}".format(lyr))
    #             lyr = v["1750_local"]
    #             # context
    #             tmp_ras = join(self.gdb, "context_{0}_1750".format(k))
    #             ap.Clip_management(lyr, "#", tmp_ras, self.context, "#", "ClippingGeometry")
    #             sumcont1750 = ap.RasterToNumPyArray(tmp_ras, nodata_to_value=0).sum()
    #             res.append(sumcont1750)  # context_sum_1750
    #             lyr = v["curr_local"]
    #             tmp_ras = join(self.gdb, "context_{0}_curr".format(k))
    #             ap.Clip_management(lyr, "#", tmp_ras, self.context, "#", "ClippingGeometry")
    #             sumcontcurr = ap.RasterToNumPyArray(tmp_ras, nodata_to_value=0).sum()
    #             res.append(sumcontcurr)  # context_sum_current
    #             sumchange = (sumcontcurr - sumcont1750)
    #             res.append(sumchange)  # context_change
    #             if sumcont1750 == 0:
    #                 loss = 0
    #             elif sumchange == sumcont1750:
    #                 loss = 100
    #             else:
    #                 loss = int(-sumchange * 100.0 / sumcont1750)
    #             res.append(loss)  # context_loss
    #
    #             # assessment
    #             tmp_ras = join(self.gdb, "assessment_{0}_curr".format(k))
    #             ap.Clip_management(lyr, "#", tmp_ras, self.assessment, "#", "ClippingGeometry")
    #             sumass = ap.RasterToNumPyArray(tmp_ras, nodata_to_value=0).sum()
    #             res.append(sumass)  # assessment_sum
    #             if sumcontcurr == 0:
    #                 pcass = 0
    #             else:
    #                 pcass = int(sumass * 100.0 / sumcontcurr)
    #             res.append(pcass)  # assessment_pc
    #
    #             # conservation
    #             tmp_ras = join(self.gdb, "conservation_{0}_curr".format(k))
    #             ap.Clip_management(lyr, "#", tmp_ras, self.conservation, "#", "ClippingGeometry")
    #             sumcons = ap.RasterToNumPyArray(tmp_ras, nodata_to_value=0).sum()
    #             res.append(sumcons)  # conservation_sum
    #             if sumcontcurr == 0:
    #                 pccons = 0
    #             else:
    #                 pccons = int(sumcons * 100.0 / sumcontcurr)
    #             res.append(pccons)  # conservation_pc
    #
    #             res_tot.append(res)
    #
    #         # add_message(res)
    #         ic = ap.da.InsertCursor(self.table_summ, "*")
    #         for r in res_tot:
    #             ic.insertRow(r)
    #         del ic
    #
    #         # # populate the summary table
    #         # ap.Append_management(self.table_full, self.table_summ, "NO_TEST")
    #
    #     def build_ahims_data(self):
    #         add_message("Analysing AHIMS points...")
    #         res_tot = []
    #         n = 0
    #         for k, v in asdst.codes_ex.iteritems():
    #             add_message("...{0}".format(v))
    #             n += 1
    #             res = [n]
    #             res.extend([k, asdst.codes_ex[k]])  # model_code, model_desc
    #
    #             tmp_fc = join(self.gdb, "ahims_{0}_context".format(k))
    #             if asdst.config.ahims_sites:
    #                 ap.Intersect_analysis([asdst.config.ahims_sites, self.context], tmp_fc)
    #                 sc = ap.da.SearchCursor(tmp_fc, "*", '"{0}" IS NOT NULL'.format(k))
    #                 l = [r for r in sc]
    #                 res.append(len(l))  # context_pts
    #             else:
    #                 res.append(None)
    #
    #             tmp_fc = join(self.gdb, "ahims_{0}_assessment".format(k))
    #             if asdst.config.ahims_sites:
    #                 ap.Intersect_analysis([asdst.config.ahims_sites, self.assessment], tmp_fc)
    #                 sc = ap.da.SearchCursor(tmp_fc, "*", '"{0}" IS NOT NULL'.format(k))
    #                 l = [r for r in sc]
    #                 res.append(len(l))  # context_pts
    #             else:
    #                 res.append(None)
    #
    #             tmp_fc = join(self.gdb, "ahims_{0}_conservation".format(k))
    #             if asdst.config.ahims_sites:
    #                 ap.Intersect_analysis([asdst.config.ahims_sites, self.conservation], tmp_fc)
    #                 sc = ap.da.SearchCursor(tmp_fc, "*", '"{0}" IS NOT NULL'.format(k))
    #                 l = [r for r in sc]
    #                 res.append(len(l))  # conservation_pts
    #                 del sc
    #             else:
    #                 res.append(None)
    #
    #             res_tot.append(res)
    #
    #         ic = ap.da.InsertCursor(self.table_ahims, "*")
    #         for r in res_tot:
    #             ic.insertRow(r)
    #         del ic
    #
    #     def add_data_to_map(self):
    #         add_message("Adding feature layers to map...")
    #
    #         lyrs = {k: v[0] for k, v in self.areas.iteritems()}
    #         asdst.project.add_layers(lyrs, "Context {}".format(self.sane_title), "calc")
    #
    #         add_message("Adding result tables to map...")
    #         asdst.add_table(asdst.project.mxd, self.table_summ, "context_loss")
    #         asdst.add_table(asdst.project.mxd, self.table_ahims, "context_ahims")

# def main():
#     """ Main entry
#
#     Args:
#
#     Returns:
#
#     Raises:
#       No raising or catching
#
#     """
#     nc = NewCalculation().get_inputs()
#     # nc.check_areas()
#     nc.make_fs()
#     nc.import_calculation_areas()
#     nc.build_loss_data()
#     if asdst.config.ahims_sites:
#         nc.build_ahims_data()
#     add_message(asdst.compact_fgdb(nc.gdb))
#     nc.add_data_to_map()
#     asdst.project.mxd.save()
#     add_message(nc.success)
#
# if __name__ == '__main__':
#     main()

"""

add_message = ap.AddMessage
add_error = ap.AddError


class NewCalculation:

    def __init__(self):
        self.raw_title = ""
        self.description = ""
        self.parent_dir = ""
        self.geom_context = None
        self.geom_assessment = None
        self.geom_conservation = None
        self.sane_title = ""
        self.gdb_path = ""
        self.gdb_name = ""
        self.gdb = ""
        self.context = ""
        # self.table_full = ""
        self.table_summ = ""
        self.table_ahims = ""
        self.assessment = ""
        self.conservation = ""
        self.areas = {}
        self.success = ""
        self.layer_dict = {}

    def get_inputs(self):
        self.raw_title = ap.GetParameterAsText(0)  # title
        self.description = ap.GetParameterAsText(1)  # description
        self.geom_context = ap.GetParameter(2)  # geom (feature set)
        self.geom_assessment = ap.GetParameter(3)  # geom (feature set)
        self.geom_conservation = ap.GetParameter(4)  # geom (feature set)
        self.sane_title = self.raw_title.lower().replace(" ", "_")
        mxd_path = ap.mapping.MapDocument("current").filePath
        self.gdb_path = split(mxd_path)[0]
        self.gdb_name = "context_{0}".format(self.sane_title) + ".gdb"
        self.gdb = join(self.gdb_path, self.gdb_name)
        # self.table_full = join(self.gdb, "loss_full")
        self.table_summ = join(self.gdb, "loss_summary")
        self.table_ahims = join(self.gdb, "ahims_summary")
        self.context = join(self.gdb, "context_{0}".format(self.sane_title))
        self.assessment = join(self.gdb, "assessment_{0}".format(self.sane_title))
        self.conservation = join(self.gdb, "conservation_{0}".format(self.sane_title))
        self.areas["Context"] = [self.context, self.geom_context]
        self.areas["Assessment"] = [self.assessment, self.geom_assessment]
        self.areas["Conservation"] = [self.conservation, self.geom_conservation]
        self.success = "Context calculation {0} successful ({1})"
        self.success = self.success.format(self.raw_title, self.gdb)
        return self

    def make_fs(self):
        ok_msg = "Geodatabase {0} created"
        err_msg = "Error creating {0}: {1}"
        try:
            ap.Copy_management(asdst.config.template_context_gdb, self.gdb)
            add_message(ok_msg.format(self.gdb))
        except Exception as e:
            add_error(err_msg.format(self.gdb, e.message))
            exit(1)

    def import_calculation_areas(self):
        m = "{0} area imported: {1} ({2} - {3})"
        # add_message(self.new_areas)
        # save the new geometry
        for k, v in self.areas.iteritems():
            try:
                # might be a feature set
                v[1].save(v[0])
                msg = m.format(k, v[0], "New Feature set", "in_memory")
                add_message(msg)
            except:
                try:
                    # or might be a layer
                    ap.CopyFeatures_management(v[1], v[0])
                    msg = m.format(k, v[0], "Feature layer", v[1])
                    add_message(msg)
                except Exception as e:
                    # or fuck knows what it is
                    add_error("Could not copy aoi geometry {0}".format(e.message))
                    exit(1)

    def build_loss_data(self):

        add_message("Getting layer dictionary...")
        self.layer_dict = asdst.project.layer_dictionary()
        # add_message(self.layer_dict)

        add_message("Calculating statistics...")
        n = 0
        res_tot = []
        for k, v in self.layer_dict.iteritems():
            n += 1
            res = [n]
            res2 = [n]
            res.extend([k, asdst.codes[k]])  # model_code, model_desc
            res2.extend([k, asdst.codes[k]])  # model_code, model_desc
            lyr = v["name"]
            add_message("...{0}".format(lyr))
            lyr = v["1750_local"]
            # context
            tmp_ras = join(self.gdb, "context_{0}_1750".format(k))
            ap.Clip_management(lyr, "#", tmp_ras, self.context, "#", "ClippingGeometry")
            sumcont1750 = ap.RasterToNumPyArray(tmp_ras, nodata_to_value=0).sum()
            res.append(sumcont1750)  # context_sum_1750
            lyr = v["curr_local"]
            tmp_ras = join(self.gdb, "context_{0}_curr".format(k))
            ap.Clip_management(lyr, "#", tmp_ras, self.context, "#", "ClippingGeometry")
            sumcontcurr = ap.RasterToNumPyArray(tmp_ras, nodata_to_value=0).sum()
            res.append(sumcontcurr)  # context_sum_current
            sumchange = (sumcontcurr - sumcont1750)
            res.append(sumchange)  # context_change
            if sumcont1750 == 0:
                loss = 0
            elif sumchange == sumcont1750:
                loss = 100
            else:
                loss = int(-sumchange*100.0/sumcont1750)
            res.append(loss)  # context_loss

            # assessment
            tmp_ras = join(self.gdb, "assessment_{0}_curr".format(k))
            ap.Clip_management(lyr, "#", tmp_ras, self.assessment, "#", "ClippingGeometry")
            sumass = ap.RasterToNumPyArray(tmp_ras, nodata_to_value=0).sum()
            res.append(sumass)  # assessment_sum
            if sumcontcurr == 0:
                pcass = 0
            else:
                pcass = int(sumass*100.0/sumcontcurr)
            res.append(pcass)  # assessment_pc

            # conservation
            tmp_ras = join(self.gdb, "conservation_{0}_curr".format(k))
            ap.Clip_management(lyr, "#", tmp_ras, self.conservation, "#", "ClippingGeometry")
            sumcons = ap.RasterToNumPyArray(tmp_ras, nodata_to_value=0).sum()
            res.append(sumcons)  # conservation_sum
            if sumcontcurr == 0:
                pccons = 0
            else:
                pccons = int(sumcons*100.0/sumcontcurr)
            res.append(pccons)  # conservation_pc

            res_tot.append(res)

        # add_message(res)
        ic = ap.da.InsertCursor(self.table_summ, "*")
        for r in res_tot:
            ic.insertRow(r)
        del ic

        # # populate the summary table
        # ap.Append_management(self.table_full, self.table_summ, "NO_TEST")

    def build_ahims_data(self):
        add_message("Analysing AHIMS points...")
        res_tot = []
        n = 0
        for k, v in asdst.codes_ex.iteritems():
            add_message("...{0}".format(v))
            n += 1
            res = [n]
            res.extend([k, asdst.codes_ex[k]])  # model_code, model_desc

            tmp_fc = join(self.gdb, "ahims_{0}_context".format(k))
            if asdst.config.ahims_sites:
                ap.Intersect_analysis([asdst.config.ahims_sites, self.context], tmp_fc)
                sc = ap.da.SearchCursor(tmp_fc, "*", '"{0}" IS NOT NULL'.format(k))
                l = [r for r in sc]
                res.append(len(l))  # context_pts
            else:
                res.append(None)

            tmp_fc = join(self.gdb, "ahims_{0}_assessment".format(k))
            if asdst.config.ahims_sites:
                ap.Intersect_analysis([asdst.config.ahims_sites, self.assessment], tmp_fc)
                sc = ap.da.SearchCursor(tmp_fc, "*", '"{0}" IS NOT NULL'.format(k))
                l = [r for r in sc]
                res.append(len(l))  # context_pts
            else:
                res.append(None)

            tmp_fc = join(self.gdb, "ahims_{0}_conservation".format(k))
            if asdst.config.ahims_sites:
                ap.Intersect_analysis([asdst.config.ahims_sites, self.conservation], tmp_fc)
                sc = ap.da.SearchCursor(tmp_fc, "*", '"{0}" IS NOT NULL'.format(k))
                l = [r for r in sc]
                res.append(len(l))  # conservation_pts
                del sc
            else:
                res.append(None)

            res_tot.append(res)

        ic = ap.da.InsertCursor(self.table_ahims, "*")
        for r in res_tot:
            ic.insertRow(r)
        del ic

    def add_data_to_map(self):
        add_message("Adding feature layers to map...")

        lyrs = {k: v[0] for k, v in self.areas.iteritems()}
        asdst.project.add_layers(lyrs, "Context {}".format(self.sane_title), "calc")

        add_message("Adding result tables to map...")
        asdst.add_table(asdst.project.mxd, self.table_summ, "context_loss")
        asdst.add_table(asdst.project.mxd, self.table_ahims, "context_ahims")


def main():
     Main entry

    Args:

    Returns:

    Raises:
      No raising or catching


    nc = NewCalculation().get_inputs()
    # nc.check_areas()
    nc.make_fs()
    nc.import_calculation_areas()
    nc.build_loss_data()
    if asdst.config.ahims_sites:
        nc.build_ahims_data()
    add_message(asdst.compact_fgdb(nc.gdb))
    nc.add_data_to_map()
    asdst.project.mxd.save()
    add_message(nc.success)


if __name__ == '__main__':
    main()
"""