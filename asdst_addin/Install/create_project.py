import arcpy as ap
from arcpy import env as env
from os import system
from os.path import join, split
from sys import exit
from asdst_addin import asdst

# ------------------------------------------------------------------------------
# execute

add_message = ap.AddMessage
add_error = ap.AddError


class NewProject:

    def __init__(self):
        self.raw_title = ""
        self.description = ""
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

    def get_inputs(self):
        self.raw_title = ap.GetParameterAsText(0)  # title
        self.description = ap.GetParameterAsText(1)  # title
        self.directory = ap.GetParameterAsText(2)  # parent directory
        self.geometry = ap.GetParameter(3)  # geometry (feature set)
        self.sane_title = self.raw_title.lower().replace(" ", "_")
        self.base = join(self.directory, self.sane_title)
        self.mxd_file = self.base + ".mxd"
        self.gdb = self.base + ".gdb"
        self.area = join(self.gdb, "project_area")
        self.loss = join(self.gdb, "project_loss")
        self.success = "ASDST project '{0}' launched in new window"
        self.success = self.success.format(self.raw_title)
        self.layer_dict = asdst.config.layer_dictionary(self.gdb)
        return self

    def make_fs(self):
        ok_msg = "Project {0} created: {1}"
        err_msg = "Error creating {0}: {1}"
        try:
            ap.Copy_management(asdst.config.template_project_gdb, self.gdb)
            add_message(ok_msg.format("geodatabase", self.gdb))
        except Exception as e:
            add_error(err_msg.format(self.gdb, e.message))
            exit(1)
        try:
            ap.Copy_management(asdst.config.template_mxd, self.mxd_file)
            add_message(ok_msg.format("map document", self.mxd_file))
            self.mxd = ap.mapping.MapDocument(self.mxd_file)
        except Exception as e:
            add_error(err_msg.format(self.mxd, e.message))
            exit(1)

    def fix_mxd(self):
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

    def import_project_area(self):
        add_message("Importing areas...")
        msg = "...area imported: {0} ({1} - {2})"
        # save the new geometry
        try:
            # might be a feature set
            self.geometry.save(self.area)
            msg = msg.format(self.area, "Feature set created by user",
                             "Temporary")
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
                exit(1)

    def build_data(self):
        add_message("Building data...")

        add_message("...clipping model reliability layer...")
        src = join(asdst.config.source_fgdb, "drvd_rel")
        add_message("... ...{0}".format(split(src)[1]))
        lcl = join(self.gdb, "drvd_rel")
        ap.Clip_management(src, "#", lcl, self.area, "#", "ClippingGeometry")
        self.layer_dict2["reliability"] = lcl

        add_message("...clipping survey priority layer...")
        src = join(asdst.config.source_fgdb, "drvd_srv")
        add_message("... ...{0}".format(split(src)[1]))
        lcl = join(self.gdb, "drvd_srv")
        ap.Clip_management(src, "#", lcl, self.area, "#", "ClippingGeometry")
        self.layer_dict2["priority"] = lcl

        add_message("...clipping regionalisation layers...")
        for i in range(1, 5):
            n = "aslu_lvl{0}".format(i)
            src = join(asdst.config.source_fgdb, n)
            add_message("... ...{0}".format(n))
            lcl = join(self.gdb, n)
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
        src = join(asdst.config.source_fgdb, "cu_param3")
        lup = join(self.gdb, "cu_param3")
        ap.Clip_management(src, "#", lup, self.area, "#", "ClippingGeometry")
        loss_rasters = {}
        env.workspace = self.gdb
        for k, v in self.layer_dict.iteritems():
            add_message("... ...{0}".format(v["name"]))
            ras_par = ap.sa.Lookup(lup, k)  #lcl_lup_ras, k)
            ras_1750 = ap.Raster(v["1750_local"])
            ras_curr = ap.sa.Int((ras_par/100.0) * ras_1750)
            lcl = v["curr_local"]
            ras_curr.save(lcl)
            ras_loss = ap.sa.Minus(ras_1750, ras_curr)
            ras_loss.save(join(self.gdb, "loss_{0}".format(k.lower())))
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
        acc_ds = join(self.gdb, "acc_impact_unscaled")
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
        acc_ds = join(self.gdb, "acc_impact_scaled")
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
                loss = int((sum_1750 - sum_curr)*100.0/sum_1750)
            vals = (n, k, v["name"], sum_1750, sum_curr, sum_change, loss)
            ic.insertRow(vals)
        del ic

    def add_layers_to_map(self):
        add_message("Adding data layers to map...")

        asdst.add_table(self.mxd, self.loss)

        lyrs = {"Model Reliability": self.layer_dict2["reliability"]}
        asdst.add_layers(self.mxd, lyrs, "Derived", "relia")

        lyrs = {"Survey Priority": self.layer_dict2["priority"]}
        asdst.add_layers(self.mxd, lyrs, "Derived", "prior")

        lyrs = {"Accumulated Impact": self.layer_dict2["impact"]}
        asdst.add_layers(self.mxd, lyrs, "Derived", "accim")

        lyrs = {"Regionalisation Level {0}".format(i): self.layer_dict2["aslu_lvl{0}".format(i)] for i in range(1, 5)}
        asdst.add_layers(self.mxd, lyrs, "Regionalisation", "regio")

        lyrs = {v["name"]: v["1750_local"] for k, v in self.layer_dict.iteritems()}
        asdst.add_layers(self.mxd, lyrs, "Pre-1750", "model")

        lyrs = {v["name"]: v["curr_local"] for k, v in self.layer_dict.iteritems()}
        asdst.add_layers(self.mxd, lyrs, "Current", "model")


def main():
    """ Main entry

    Args:

    Returns:

    Raises:
      No raising or catching

    """
    np = NewProject().get_inputs()
    np.make_fs()
    np.fix_mxd()
    np .import_project_area()
    np.build_data()
    add_message(asdst.compact_fgdb(np.gdb))
    np.add_layers_to_map()
    np.mxd.save()
    system(np.mxd_file)
    add_message(np.success)


if __name__ == '__main__':
    main()

