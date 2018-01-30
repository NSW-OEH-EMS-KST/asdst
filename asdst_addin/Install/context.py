import arcpy
from os.path import split, join
from utils import compact_fgdb
from config import get_system_config, get_map_config, get_user_config, get_layer_map, get_codes, get_codes_ex
from utils import add_layers_to_mxd, add_table_to_mxd


class ContextCalculationTool(object):

    def __init__(self):

        self.label = u'Calculate Context'
        self.description = u'Calculate project context data'
        self.canRunInBackground = True

        return

    def getParameterInfo(self):

        empty_poly_layer = get_system_config()["empty_polyf_layer"]

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

        # Context_Feature
        param_3 = arcpy.Parameter()
        param_3.name = u'Context_Feature'
        param_3.displayName = u'Context Feature'
        param_3.parameterType = 'Required'
        param_3.direction = 'Input'
        param_3.datatype = u'Feature Set'
        param_3.value = empty_poly_layer

        # Assessment_Feature
        param_4 = arcpy.Parameter()
        param_4.name = u'Assessment_Feature'
        param_4.displayName = u'Assessment Feature'
        param_4.parameterType = 'Required'
        param_4.direction = 'Input'
        param_4.datatype = u'Feature Set'
        param_4.value = empty_poly_layer

        # Conservation_Feature
        param_5 = arcpy.Parameter()
        param_5.name = u'Conservation_Feature'
        param_5.displayName = u'Conservation Feature'
        param_5.parameterType = 'Required'
        param_5.direction = 'Input'
        param_5.datatype = u'Feature Set'
        param_5.value = empty_poly_layer

        return [param_1, param_2, param_3, param_4, param_5]

    def execute(self, parameters, messages):

        # Get user inputs
        messages.addMessage("Reading inputs")
        raw_title = parameters[0].valueAsText  # title
        description = parameters[1].valueAsText  # description
        geom_context = parameters[2].value  # geom (feature set)
        geom_assessment = parameters[3].value  # geom (feature set)
        geom_conservation = parameters[4].value  # geom (feature set)
        sane_title = raw_title.lower().replace(" ", "_")

        mxd = arcpy.mapping.MapDocument("CURRENT")
        mxd_path = mxd.filePath
        gdb_path = split(mxd_path)[0]
        gdb_name = "context_{}".format(sane_title) + ".gdb"
        gdb = join(gdb_path, gdb_name)

        table_summ = join(gdb, "loss_summary")
        table_ahims = join(gdb, "ahims_summary")
        context = join(gdb, "context_{}".format(sane_title))
        assessment = join(gdb, "assessment_{}".format(sane_title))
        conservation = join(gdb, "conservation_{}".format(sane_title))

        areas = {"Context": [context, geom_context],
                 "Assessment": [assessment, geom_assessment],
                 "Conservation": [conservation, geom_conservation]}

        messages.addMessage("Reading configuration")
        config = get_system_config()
        proj_gdb = get_map_config()["gdb"]

        # Make the required file system
        arcpy.Copy_management(config["template_context_gdb"], gdb)
        messages.addMessage("Context geodatabase '{}' created".format(gdb))

        # Import calculation areas into project workspace i.e. save the geometry to be used
        m = "{} area imported: {} ({} - {})"
        for k, v in areas.iteritems():
            try:
                # might be a feature set
                v[1].save(v[0])
                msg = m.format(k, v[0], "New Feature set", "in_memory")
                messages.addMessage(msg)

            except:
                try:
                    # or might be a layer
                    arcpy.CopyFeatures_management(v[1], v[0])
                    msg = m.format(k, v[0], "Feature layer", v[1])
                    messages.addMessage(msg)

                except Exception as e:
                    # or who knows what it is, so throw up
                    messages.addErrorMessage("Could not copy aoi geometry {0}".format(e.message))
                    raise arcpy.ExecuteError

        # Build loss data
        messages.addMessage("Getting layer dictionary...")
        layer_dict = get_layer_map(proj_gdb)

        # Calc stats
        messages.addMessage("Calculating statistics...")
        codes = get_codes()
        n = 0
        res_tot = []

        # layer_dict is like this:

        # {k: {"name": v,
        #      "1750_source": (join(source_ws, k.lower() + "_v7")),
        #      "1750_local": (join(local_workspace, k.lower() + "_1750")),
        #      "curr_local": (join(local_workspace, k.lower() + "_curr"))}
        # for k, v in get_codes().iteritems()}

        for k, v in layer_dict.iteritems():
            n += 1
            res = [n]
            res.extend([k, codes[k]])  # model_code, model_desc
            messages.addMessage("...{}".format(v["name"]))

            # 1750 context
            lyr = v["1750_local"]
            tmp_ras = join(gdb, "context_{}_1750".format(k))
            arcpy.Clip_management(lyr, "#", tmp_ras, context, "#", "ClippingGeometry")
            sumcont1750 = arcpy.RasterToNumPyArray(tmp_ras, nodata_to_value=0).sum()
            res.append(sumcont1750)  # context_sum_1750

            # current context
            lyr = v["curr_local"]
            tmp_ras = join(gdb, "context_{}_curr".format(k))
            arcpy.Clip_management(lyr, "#", tmp_ras, context, "#", "ClippingGeometry")
            sumcontcurr = arcpy.RasterToNumPyArray(tmp_ras, nodata_to_value=0).sum()
            res.append(sumcontcurr)  # context_sum_current

            # context change
            sumchange = (sumcontcurr - sumcont1750)
            res.append(sumchange)  # context_change
            if sumcont1750 == 0:
                loss = 0
            elif sumchange == sumcont1750:
                loss = 100
            else:
                loss = int(-sumchange * 100.0 / sumcont1750)
            res.append(loss)  # context_loss
            messages.addMessage("... context: curr={} 1750={} change={} loss={}".format(sumcontcurr, sumcont1750, sumchange, loss))

            # unsure about these last two calcs... why do they use current context?

            # assessment
            tmp_ras = join(gdb, "assessment_{0}_curr".format(k))
            arcpy.Clip_management(lyr, "#", tmp_ras, assessment, "#", "ClippingGeometry")
            sumass = arcpy.RasterToNumPyArray(tmp_ras, nodata_to_value=0).sum()
            res.append(sumass)  # assessment_sum
            pcass = 0 if sumcontcurr == 0 else int(sumass * 100.0 / sumcontcurr)
            res.append(pcass)  # assessment_pc
            messages.addMessage("... assessment: curr={} sum={} %={}".format(sumcontcurr, sumass, pcass))

            # conservation
            tmp_ras = join(gdb, "conservation_{0}_curr".format(k))
            arcpy.Clip_management(lyr, "#", tmp_ras, conservation, "#", "ClippingGeometry")
            sumcons = arcpy.RasterToNumPyArray(tmp_ras, nodata_to_value=0).sum()
            res.append(sumcons)  # conservation_sum
            pccons = 0 if sumcontcurr == 0 else int(sumcons * 100.0 / sumcontcurr)
            res.append(pccons)  # conservation_pc
            res_tot.append(res)
            messages.addMessage("... conservation: curr={} sum={} %={}".format(sumcontcurr, sumcons, pccons))

        # build summary table
        ic = arcpy.da.InsertCursor(table_summ, "*")
        for r in res_tot:
            ic.insertRow(r)
        del ic

        # Build AHIMS data if configured
        ahims_sites = get_user_config()["ahims_sites"]

        if ahims_sites:
            messages.addMessage("Analysing AHIMS points...")
            codes_ex = get_codes_ex()
            res_tot = []
            n = 0
            for k, v in codes_ex.iteritems():
                messages.addMessage("...{0}".format(v))
                n += 1
                res = [n]
                res.extend([k, codes_ex[k]])  # model_code, model_desc

                tmp_fc = join(gdb, "ahims_{0}_context".format(k))
                arcpy.Intersect_analysis([ahims_sites, context], tmp_fc)
                sc = arcpy.da.SearchCursor(tmp_fc, "*", '"{0}" IS NOT NULL'.format(k))
                point_count = len([r for r in sc])
                messages.addMessage("... found {} in {}".format(point_count, tmp_fc))
                res.append(point_count)  # context_pts

                tmp_fc = join(gdb, "ahims_{0}_assessment".format(k))
                arcpy.Intersect_analysis([ahims_sites, assessment], tmp_fc)
                sc = arcpy.da.SearchCursor(tmp_fc, "*", '"{0}" IS NOT NULL'.format(k))
                point_count = len([r for r in sc])
                messages.addMessage("... found {} in {}".format(point_count, tmp_fc))
                res.append(point_count)  # context_pts

                tmp_fc = join(gdb, "ahims_{0}_conservation".format(k))
                arcpy.Intersect_analysis([ahims_sites, conservation], tmp_fc)
                sc = arcpy.da.SearchCursor(tmp_fc, "*", '"{0}" IS NOT NULL'.format(k))
                point_count = len([r for r in sc])
                messages.addMessage("... found {} in {}".format(point_count, tmp_fc))
                res.append(point_count)  # conservation_pts
                del sc

                res_tot.append(res)

            ic = arcpy.da.InsertCursor(table_ahims, "*")

            for r in res_tot:
                ic.insertRow(r)

            del ic

        # Compact the workspace
        messages.addMessage(compact_fgdb(gdb))

        # Add data to map
        messages.addMessage("Adding feature layers to map...")
        lyrs = {k: v[0] for k, v in areas.iteritems()}
        add_layers_to_mxd(lyrs, "Context {}".format(sane_title), "calc", get_system_config(), messages)
        messages.addMessage("Adding result tables to map...")
        add_table_to_mxd(table_summ, "context_loss", messages)
        add_table_to_mxd(table_ahims, "context_ahims", messages)

        # Save and report status
        mxd.save()
        messages.addMessage("Context calculation {0} successful ({1})".format(raw_title, gdb))
