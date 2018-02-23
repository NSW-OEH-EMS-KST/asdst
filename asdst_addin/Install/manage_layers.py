import arcpy
from utils import add_layers_to_mxd, add_group_layers
from asdst_addin import get_system_config


LAYERS = {
    "AHIMS": {
        "AHIMS All sites": {
            "AHIMS black": r"C:\Data\asdst\asdst_addin\AHIMS_metro\AHIMS_data.gdb\ahims_20150306s",
            "AHIMS white": r"C:\Data\asdst\asdst_addin\AHIMS_metro\AHIMS_data.gdb\ahims_20150306s",
            "AHIMS red": r"C:\Data\asdst\asdst_addin\AHIMS_metro\AHIMS_data.gdb\ahims_20150306s"},
        "AHIMS Filtered": {
            "AHIMS permits": r"C:\Data\asdst\asdst_addin\AHIMS_metro\AHIMS_data.gdb\ahims_20150306s",
            "AHIMS status": r"C:\Data\asdst\asdst_addin\AHIMS_metro\AHIMS_data.gdb\ahims_20150306s"},
        "AHIMS Features": {
            "Ceremony & dreaming": r"C:\Data\asdst\asdst_addin\AHIMS_metro\AHIMS_data.gdb\ahims_20150306s",
            "Resource gathering": r"C:\Data\asdst\asdst_addin\AHIMS_metro\AHIMS_data.gdb\ahims_20150306s",
            "Stone artefacts": r"C:\Data\asdst\asdst_addin\AHIMS_metro\AHIMS_data.gdb\ahims_20150306s",
            "Rock art": r"C:\Data\asdst\asdst_addin\AHIMS_metro\AHIMS_data.gdb\ahims_20150306s",
            "Non-human bone": r"C:\Data\asdst\asdst_addin\AHIMS_metro\AHIMS_data.gdb\ahims_20150306s",
            "Burials": r"C:\Data\asdst\asdst_addin\AHIMS_metro\AHIMS_data.gdb\ahims_20150306s",
            "Conflict": r"C:\Data\asdst\asdst_addin\AHIMS_metro\AHIMS_data.gdb\ahims_20150306s",
            "Ceremonial ring": r"C:\Data\asdst\asdst_addin\AHIMS_metro\AHIMS_data.gdb\ahims_20150306s",
            "Earth mounds": r"C:\Data\asdst\asdst_addin\AHIMS_metro\AHIMS_data.gdb\ahims_20150306s",
            "Fish traps": r"C:\Data\asdst\asdst_addin\AHIMS_metro\AHIMS_data.gdb\ahims_20150306s",
            "Grinding grooves": r"C:\Data\asdst\asdst_addin\AHIMS_metro\AHIMS_data.gdb\ahims_20150306s",
            "Habitation structures": r"C:\Data\asdst\asdst_addin\AHIMS_metro\AHIMS_data.gdb\ahims_20150306s",
            "Hearths": r"C:\Data\asdst\asdst_addin\AHIMS_metro\AHIMS_data.gdb\ahims_20150306s",
            "Ochre quarries": r"C:\Data\asdst\asdst_addin\AHIMS_metro\AHIMS_data.gdb\ahims_20150306s",
            "Potential archaeological deposits": r"C:\Data\asdst\asdst_addin\AHIMS_metro\AHIMS_data.gdb\ahims_20150306s",
            "Archaeological shell": r"C:\Data\asdst\asdst_addin\AHIMS_metro\AHIMS_data.gdb\ahims_20150306s",
            "Stone arrangements": r"C:\Data\asdst\asdst_addin\AHIMS_metro\AHIMS_data.gdb\ahims_20150306s",
            "Stone quarries": r"C:\Data\asdst\asdst_addin\AHIMS_metro\AHIMS_data.gdb\ahims_20150306s",
            "Scarred trees": r"C:\Data\asdst\asdst_addin\AHIMS_metro\AHIMS_data.gdb\ahims_20150306s",
            "Waterholes": r"C:\Data\asdst\asdst_addin\AHIMS_metro\AHIMS_data.gdb\ahims_20150306s",
            "Radiocarbon dates": r"C:\Data\asdst\asdst_addin\AHIMS_metro\AHIMS_data.gdb\radiocarbon_dates"}},
    "Context": {
        "Aboriginal": {
            "Aboriginal Owned Lands": r"P:\Corporate\Themes\Cultural\Aboriginal\Aboriginal.gdb\AboriginalOwnedLands",
            "Aboriginal Places": r"P:\Corporate\Themes\Cultural\Aboriginal\Aboriginal.gdb\AboriginalPlaces",
            "Indigenous Protected Areas Of Australia": r"P:\Corporate\Themes\Tenure\Conservation\Conservation.gdb\IndigenousProtectedAreasOfAustralia",
            "Native Title Application Schedule": r"P:\Corporate\Themes\Cultural\Aboriginal\Aboriginal.gdb\NativeTitleApplicationSchedule",
            "Native Title Claims": r"P:\Corporate\Themes\Cultural\Aboriginal\Aboriginal.gdb\NativeTitleClaims",
            "Native Title Determinations (Australia)": r"P:\Corporate\Themes\Cultural\Aboriginal\Aboriginal.gdb\NativeTitleDeterminations",
            "Native Title ILUA": r"P:\Corporate\Themes\Cultural\Aboriginal\Aboriginal.gdb\NativeTitleIndigenousLandUseAgreements",
            "Tindale Tribal Boundaries": r"P:\Corporate\Themes\Cultural\Aboriginal\Aboriginal.gdb\TindaleTribalBoundariesAust",
            "Archaeological Surveys": r"P:\Corporate\Themes\Cultural\Aboriginal\Aboriginal.gdb\ArchaeologicalSurveys"},
# "Infrastructure":
        "Towns & Places": {
            "Towns": r"P:\Corporate\Themes\Infrastructure\Localities\Localities.gdb\Places",
            "Gazetteer": r"P:\Corporate\Themes\Infrastructure\Localities\Localities.gdb\Gazetteer",
            "Places": r"P:\Corporate\Themes\Infrastructure\Localities\Localities.gdb\Places",
            "Points Of Interest": r"P:\Corporate\Themes\Infrastructure\Localities\Localities.gdb\PointsOfInterest",
            "Major Towns": r"P:\Corporate\Themes\Cultural\Population\Population.gdb\TownPopulationEasternStates2001",
            "Builtup Areas": r"P:\Corporate\Themes\Infrastructure\Localities\Localities.gdb\BuiltupAreas"},
        "Roads": {
            "Roads 250k": r"P:\Corporate\Themes\Infrastructure\Transport\Transport.gdb\Roads250k",
            "Named Roads": r"P:\Corporate\Themes\Infrastructure\Transport\Transport.gdb\Roads"},
# "Drainage":
# "Major Rivers":
        "Rivers, Streams & Lakes": {
            "Major Rivers": r"P:\Corporate\Themes\Water\Drainage\Drainage.gdb\Rivers250K",
            "Main Rivers & Creeks": r"P:\Corporate\Themes\Water\Drainage\Drainage.gdb\Rivers250K",
            "Named Rivers & Creeks": r"P:\Corporate\Themes\Water\Drainage\Drainage.gdb\Rivers250K",
            "Rivers": r"P:\Corporate\Themes\Water\Drainage\Drainage.gdb\Rivers250K",
            "River Styles": r"P:\Corporate\Themes\Water\Classification\Classification.gdb\RiverStyles",
            "Wild Rivers": r"P:\Corporate\Themes\Water\Classification\Classification.gdb\RiversWild",
            "Stream Order": r"P:\Corporate\Themes\Water\Classification\Classification.gdb\StreamOrder",
            "Watercourse": r"P:\Corporate\Themes\Water\Drainage\Drainage.gdb\HydroLine",
            "Lakes 1:250k": r"P:\Corporate\Themes\Water\Drainage\Drainage.gdb\Lakes250k"},
        "Catchments: ": {
            "SubCatchments": r"P:\Corporate\Themes\Water\Classification\Classification.gdb\SubCatchmentsStressedRivers",
            "Major River Catchments": r"P:\Corporate\Themes\Land\Landform\Landform.gdb\Catchments"},
# "Land":
        "Land and Soils": {
            "IBRA v7": r"P:\Corporate\Themes\Land\LandClass\LandClass.gdb\IBRA_Aust",
            "IBRA Sub Regions v7": r"P:\Corporate\Themes\Land\LandClass\LandClass.gdb\IBRASubRegions_Aust",
            "Land Capability": r"P:\Corporate\Themes\Land\LandClass\LandClass.gdb\LandCapability",
            "Mitchell Landscapes": r"P:\Corporate\Themes\Land\LandClass\Landclass.gdb\MitchellLandscapes",
            "Australian Soil Classification NSW Soil Types": r"P:\Corporate\Themes\Soil\SoilType\SoilType.gdb\SoilTypeAustralianSoilClassification",
            "Geology 250k - Rock Type": r"P:\Corporate\Themes\Geology\Structural\Structural.gdb\Geology250k",
            "Vegetation NSWmap v3 VIS_E3848": r"C:\Users\finchl\AppData\Roaming\ESRI\Desktop10.1\ArcCatalog\gis@DC_VISMapCatalogue.sde\VISMapCatalogue.SDE.NSWMAP_V3_03_E_3848"},
        "Tenure": {
            "Biobanking Sites": r"P:\Corporate\Themes\Tenure\Conservation\Conservation.gdb\BiobankingSites",
            "Conservation Agreements": r"P:\Corporate\Themes\Tenure\Conservation\Conservation.gdb\ConservationAgreements",
            "Registered Property Agreements": r"P:\Corporate\Themes\Tenure\Conservation\Conservation.gdb\RegisteredPropertyAgreements",
            "Declared Wilderness": r"P:\Corporate\Themes\Tenure\Conservation\Conservation.gdb\WildernessDeclared",
            "Wildlife Refuges": r"P:\Corporate\Themes\Tenure\Conservation\Conservation.gdb\WildlifeRefuges",
            "World Heritage Areas": r"P:\Corporate\Themes\Tenure\Conservation\Conservation.gdb\WorldHeritageAreas"},
        "NPWS Managed Land": {
            r"NPWS Estate": "P:\Corporate\Themes\Tenure\CrownEstate\CrownEstate.gdb\NPWS_Estate",
            r"NPWS Acquired Not Gazetted": "P:\Corporate\Themes\Tenure\CrownEstate\CrownEstate.gdb\NPWS_AcquiredNotGazetted",
            r"NPWS Managed Crown Land": "P:\Corporate\Themes\Tenure\CrownEstate\CrownEstate.gdb\NPWS_ManagedCrownLand",
            r"Lands Vested in the Minister": "P:\Corporate\Themes\Tenure\CrownEstate\CrownEstate.gdb\NPWS_Vested",
            r"State Forest Estate": "P:\Corporate\Themes\Tenure\CrownEstate\CrownEstate.gdb\FNSW_Boundaries",
            r"Travelling Stock Routes": "P:\Corporate\Themes\Tenure\CrownEstate\CrownEstate.gdb\TravellingStockRoutes",
            r"Crown Land": "P:\Corporate\Themes\Tenure\CrownEstate\CrownEstate.gdb\CrownLand"},
        "Cadastre": {
            "Lot": r"P:\Corporate\Themes\Tenure\Cadastre\Cadastre.gdb\Lot",
            "Road": r"P:\Corporate\Themes\Tenure\Cadastre\Cadastre.gdb\Road",
            "UnidentifiedParcels": r"P:\Corporate\Themes\Tenure\Cadastre\Cadastre.gdb\Unidentified",
            "Water Feature": r"P:\Corporate\Themes\Tenure\Cadastre\Cadastre.gdb\WaterFeature"},
        "Boundaries": {
            "OEH Regional Operations Group Regions": r"P:\Corporate\Themes\Admin\Corporate\Corporate.gdb\OEH_RegionalOperationsRegions",
            "NSW Boundary": r"P:\Corporate\Themes\Admin\Statutory\Statutory.gdb\NSW",
            "LGAs": r"P:\Corporate\Themes\Admin\Statutory\Statutory.gdb\LocalGovernmentArea",
            "Aboriginal Land Councils": r"P:\Corporate\Themes\Admin\Corporate\Corporate.gdb\AboriginalLandCouncil",
            "County": r"P:\Corporate\Themes\Admin\Statutory\Statutory.gdb\County",
            "Parish": r"P:\Corporate\Themes\Admin\Statutory\Statutory.gdb\Parish"},
        "Parks & Wildlife Group": {
            "PWG Branches": r"P:\Corporate\Themes\Admin\Corporate\Corporate.gdb\PWG_Branches",
            "PWG Regions": r"P:\Corporate\Themes\Admin\Corporate\Corporate.gdb\PWG_Regions",
            "PWG Areas": r"P:\Corporate\Themes\Admin\Corporate\Corporate.gdb\PWG_Areas",
            "RFS Districts": r"P:\Corporate\Themes\Admin\Corporate\Corporate.gdb\RFS_Districts"},
        "Terrain": {
            "Trig Stations": r"P:\Corporate\Themes\Infrastructure\Localities\Localities.gdb\TrigStations",
            "Contour Lines - 10m": r"P:\Corporate\Themes\Land\Elevation\Elevation.gdb\Contour_10m",
            "Aspect (30m)": r"P:\Corporate\Grids\Land\Landform\AspectLCC\aspect30m",
            "Slope (30m)": r"P:\Corporate\Grids\Land\Landform\SlopeLCC\slope30m",
            "SRTM DEM 30m": r"P:\Corporate\Grids\Land\Elevation\LCC\DEM30m_SRTM\dem30m",
            "Hillshade (30m)": r"P:\Corporate\Grids\Land\Elevation\LCC\DEM30m_SRTM\hillshade30m"}},
# "Imagery":
# "ADS40 AirPhotos":
# "ADS40 Mosaics":
# "SPOT5 2005":
# "Zone 56":
    "Imagery": {
        "SPOT5 2005 - Zone 56": {
            "sp5col2p5_sh5601.ecw": r"P:\Corporate\Imagery\SPOT\MGA56\2005\sp5col2p5_sh5601.ecw",
            "sp5col2p5_sh5602.ecw": r"P:\Corporate\Imagery\SPOT\MGA56\2005\sp5col2p5_sh5602.ecw",
            "sp5col2p5_sh5603.ecw": r"P:\Corporate\Imagery\SPOT\MGA56\2005\sp5col2p5_sh5603.ecw",
            "sp5col2p5_sh5605.ecw": r"P:\Corporate\Imagery\SPOT\MGA56\2005\sp5col2p5_sh5605.ecw",
            "sp5col2p5_sh5606.ecw": r"P:\Corporate\Imagery\SPOT\MGA56\2005\sp5col2p5_sh5606.ecw",
            "sp5col2p5_sh5607.ecw": r"P:\Corporate\Imagery\SPOT\MGA56\2005\sp5col2p5_sh5607.ecw",
            "sp5col2p5_sh5609.ecw": r"P:\Corporate\Imagery\SPOT\MGA56\2005\sp5col2p5_sh5609.ecw",
            "sp5col2p5_sh5610.ecw": r"P:\Corporate\Imagery\SPOT\MGA56\2005\sp5col2p5_sh5610.ecw",
            "sp5col2p5_sh5613.ecw": r"P:\Corporate\Imagery\SPOT\MGA56\2005\sp5col2p5_sh5613.ecw",
            "sp5col2p5_sh5614.ecw": r"P:\Corporate\Imagery\SPOT\MGA56\2005\sp5col2p5_sh5614.ecw",
            "sp5col2p5_si5601.ecw": r"P:\Corporate\Imagery\SPOT\MGA56\2005\sp5col2p5_si5601.ecw",
            "sp5col2p5_si5602.ecw": r"P:\Corporate\Imagery\SPOT\MGA56\2005\sp5col2p5_si5602.ecw",
            "sp5col2p5_si5605.ecw": r"P:\Corporate\Imagery\SPOT\MGA56\2005\sp5col2p5_si5605.ecw",
            "sp5col2p5_si5609.ecw": r"P:\Corporate\Imagery\SPOT\MGA56\2005\sp5col2p5_si5609.ecw",
            "sp5col2p5_si5613.ecw": r"P:\Corporate\Imagery\SPOT\MGA56\2005\sp5col2p5_si5613.ecw"},
# "Zone 55":
        "SPOT5 2005 - Zone 55": {
            "sp5col2p5_sh5504.ecw": r"P:\Corporate\Imagery\SPOT\MGA55\2005\sp5col2p5_sh5504.alg",
            "sp5col2p5_sh5505.ecw": r"P:\Corporate\Imagery\SPOT\MGA55\2005\sp5col2p5_sh5505.ecw",
            "sp5col2p5_sh5506.ecw": r"P:\Corporate\Imagery\SPOT\MGA55\2005\sp5col2p5_sh5506.ecw",
            "sp5col2p5_sh5507.ecw": r"P:\Corporate\Imagery\SPOT\MGA55\2005\sp5col2p5_sh5507.ecw",
            "sp5col2p5_sh5508.ecw": r"P:\Corporate\Imagery\SPOT\MGA55\2005\sp5col2p5_sh5508.ecw",
            "sp5col2p5_sh5509.ecw": r"P:\Corporate\Imagery\SPOT\MGA55\2005\sp5col2p5_sh5509.ecw",
            "sp5col2p5_sh5510.ecw": r"P:\Corporate\Imagery\SPOT\MGA55\2005\sp5col2p5_sh5510.ecw",
            "sp5col2p5_sh5511.ecw": r"P:\Corporate\Imagery\SPOT\MGA55\2005\sp5col2p5_sh5511.ecw",
            "sp5col2p5_sh5512.ecw": r"P:\Corporate\Imagery\SPOT\MGA55\2005\sp5col2p5_sh5512.ecw",
            "sp5col2p5_sh5513.ecw": r"P:\Corporate\Imagery\SPOT\MGA55\2005\sp5col2p5_sh5513.ecw",
            "sp5col2p5_sh5514.ecw": r"P:\Corporate\Imagery\SPOT\MGA55\2005\sp5col2p5_sh5514.ecw",
            "sp5col2p5_sh5515.ecw": r"P:\Corporate\Imagery\SPOT\MGA55\2005\sp5col2p5_sh5515.ecw",
            "sp5col2p5_sh5516.ecw": r"P:\Corporate\Imagery\SPOT\MGA55\2005\sp5col2p5_sh5516.ecw",
            "sp5col2p5_si5501.ecw": r"P:\Corporate\Imagery\SPOT\MGA55\2005\sp5col2p5_si5501.ecw",
            "sp5col2p5_si5502.ecw": r"P:\Corporate\Imagery\SPOT\MGA55\2005\sp5col2p5_si5502.ecw",
            "sp5col2p5_si5503.ecw": r"P:\Corporate\Imagery\SPOT\MGA55\2005\sp5col2p5_si5503.ecw",
            "sp5col2p5_si5504.ecw": r"P:\Corporate\Imagery\SPOT\MGA55\2005\sp5col2p5_si5504.ecw",
            "sp5col2p5_si5505.ecw": r"P:\Corporate\Imagery\SPOT\MGA55\2005\sp5col2p5_si5505.ecw",
            "sp5col2p5_si5506.ecw": r"P:\Corporate\Imagery\SPOT\MGA55\2005\sp5col2p5_si5506.ecw",
            "sp5col2p5_si5507.ecw": r"P:\Corporate\Imagery\SPOT\MGA55\2005\sp5col2p5_si5507.ecw",
            "sp5col2p5_si5508.ecw": r"P:\Corporate\Imagery\SPOT\MGA55\2005\sp5col2p5_si5508.ecw",
            "sp5col2p5_si5509.ecw": r"P:\Corporate\Imagery\SPOT\MGA55\2005\sp5col2p5_si5509.ecw",
            "sp5col2p5_si5510.ecw": r"P:\Corporate\Imagery\SPOT\MGA55\2005\sp5col2p5_si5510.ecw",
            "sp5col2p5_si5511.ecw": r"P:\Corporate\Imagery\SPOT\MGA55\2005\sp5col2p5_si5511.ecw",
            "sp5col2p5_si5512.ecw": r"P:\Corporate\Imagery\SPOT\MGA55\2005\sp5col2p5_si5512.ecw",
            "sp5col2p5_si5513.ecw": r"P:\Corporate\Imagery\SPOT\MGA55\2005\sp5col2p5_si5513.ecw",
            "sp5col2p5_si5514.ecw": r"P:\Corporate\Imagery\SPOT\MGA55\2005\sp5col2p5_si5514.ecw",
            "sp5col2p5_si5515.ecw": r"P:\Corporate\Imagery\SPOT\MGA55\2005\sp5col2p5_si5515.ecw",
            "sp5col2p5_si5516.ecw": r"P:\Corporate\Imagery\SPOT\MGA55\2005\sp5col2p5_si5516.ecw",
            "sp5col2p5_sj5503.ecw": r"P:\Corporate\Imagery\SPOT\MGA55\2005\sp5col2p5_sj5503.ecw",
            "sp5col2p5_sj5504.ecw": r"P:\Corporate\Imagery\SPOT\MGA55\2005\sp5col2p5_sj5504.ecw",
            "sp5col2p5_sj5508.ecw": r"P:\Corporate\Imagery\SPOT\MGA55\2005\sp5col2p5_sj5508.ecw"},
# "Zone 54":
        "SPOT5 2005 - Zone 54": {
            "sp5col2p5_sh5407.ecw": r"P:\Corporate\Imagery\SPOT\MGA54\2005\sp5col2p5_sh5407.ecw",
            "sp5col2p5_sh5408.ecw": r"P:\Corporate\Imagery\SPOT\MGA54\2005\sp5col2p5_sh5408.ecw",
            "sp5col2p5_sh5411.ecw": r"P:\Corporate\Imagery\SPOT\MGA54\2005\sp5col2p5_sh5411.ecw",
            "sp5col2p5_sh5412.ecw": r"P:\Corporate\Imagery\SPOT\MGA54\2005\sp5col2p5_sh5412.ecw",
            "sp5col2p5_sh5415.ecw": r"P:\Corporate\Imagery\SPOT\MGA54\2005\sp5col2p5_sh5415.ecw",
            "sp5col2p5_sh5416.ecw": r"P:\Corporate\Imagery\SPOT\MGA54\2005\sp5col2p5_sh5416.ecw",
            "sp5col2p5_si5403.ecw": r"P:\Corporate\Imagery\SPOT\MGA54\2005\sp5col2p5_si5403.ecw",
            "sp5col2p5_si5404.ecw": r"P:\Corporate\Imagery\SPOT\MGA54\2005\sp5col2p5_si5404.ecw",
            "sp5col2p5_si5407.ecw": r"P:\Corporate\Imagery\SPOT\MGA54\2005\sp5col2p5_si5407.ecw",
            "sp5col2p5_si5408.ecw": r"P:\Corporate\Imagery\SPOT\MGA54\2005\sp5col2p5_si5408.ecw",
            "sp5col2p5_si5411.ecw": r"P:\Corporate\Imagery\SPOT\MGA54\2005\sp5col2p5_si5411.ecw",
            "sp5col2p5_si5412.ecw": r"P:\Corporate\Imagery\SPOT\MGA54\2005\sp5col2p5_si5412.ecw",
            "sp5col2p5_si5416.ecw": r"P:\Corporate\Imagery\SPOT\MGA54\2005\sp5col2p5_si5416.ers"},
# r"SPOT5 2011": "P:\Corporate\Imagery\SPOT\sp5col2p5_nsw_ll_2011.ecw",
        "SPOT5 2011 & TOPO Maps": {
            "SPOT5 2011": r"P:\Corporate\Imagery\SPOT\sp5col2p5_nsw_ll_2011.ecw"},
            "Topo maps": r"P:\Corporate\Imagery\Topographic\Geographics\TopoMosaic_NSW.ecw"}}
# "ASDST":
# "Current":
# "Pre-1750":
# "Derived":
# "Regionalisation":


# def layer_specs_from_csv(csv):
#
#     try:
#         df = pd.read_csv(csv)
#
#         # df['Display'] = df[["Type", "Category", "Title"]].apply(lambda x: "{} | {} | {}".format(*x), axis=1)
#         df['Display'] = df[["Category", "Title"]].apply(lambda x: "{} | {}".format(*x), axis=1)
#
#         layer_specs = zip(df["Category"], df["Title"], df["Datasource"], df["Display"])
#
#         del df
#     except:
#         layer_specs = [["CSV error"] * 5]
#
#     return layer_specs


# def get_categories():
#     lyrs = []
#     for k, v  in LAYERS.iteritems():
#         if isinstance(v, basestring):
#             lyrs.append([k, v, ])
#
#     return LAYERS.keys()


class ManageLayersTool(object):

    def __init__(self):

        self.label = "Manage Group Layers"
        self.description = "Manage ASDST and context group layers within the map"
        self.canRunInBackground = False

    def getParameterInfo(self):

        params = []

        for cat, dic in LAYERS.iteritems():

            param = arcpy.Parameter(
                displayName="",
                name="{}_{}".format(cat, dic).replace(" ", "_"),
                datatype="GPString",
                parameterType="Optional",
                direction="Input",
                multiValue=True,
                category=cat)

            param.filter.list = dic.keys()

            params.append(param)

        return params

    def execute(self, parameters, messages):

        group_layers = []

        for p in parameters:
            v = p.valueAsText
            if v:
                g_layers = v.split(";")
                group_layers.extend(g_layers)

        group_layers = [v.strip("'") for v in group_layers]

        if not group_layers:
            messages.AddMessage("No group layers selected")
            return

        # list top level group layers
        layer_structure = []
        for k, v in LAYERS.iteritems():
            for vk in v.keys():
                if vk in group_layers:
                    layer_structure.append((k, vk, v[vk]))

        messages.AddMessage("top_group_layers: {}".format(layer_structure))

        sys_cfg = get_system_config()

        # add the layers
        for k, v, l in layer_structure:
            # add group layers
            add_group_layers([v], k, sys_cfg, messages=messages)

            # def add_layers_to_mxd(layers, group_name, layer_type, sys_cfg, messages=None, add_position="BOTTOM"):
            add_layers_to_mxd(l, v, None, sys_cfg, messages=messages)  # top level
            # add_layers_to_mxd({}, v, k, get_system_config(), messages=messages)  # second level
            # add layers


        # # add the second-level group layers
        # for k, v, l in top_group_layers:
        #     add_layers_to_mxd({}, k, None, get_system_config(), messages=messages)


        # add the actual layers

        # layers = []
        # layers  = parameters[1].valueAsText
        # messages.AddMessage("layers)
        # layers  = parameters[2].valueAsText
        # messages.AddMessage("layers)
        # df = arcpy.mapping.ListDataFrames(arcpy.mapping.MapDocument("CURRENT"), parameters[2].valueAsText)[0]
        # df_name = df.name
        #
        # pos = parameters[3].valueAsText
        #
        # lyrs = [v.strip().strip("'") for v in parameters[0].ValueAsText.split(";")]
        #
        # if lyrs:
        #     messages.AddMessage("Adding layers...")
        #
        #     for lyr in lyrs:
        #         src = self.layer_dict[lyr]
        #
        #         messages.AddMessage("... adding layer '{}' from '{}' to dataframe '{}' at position '{}'".format(lyr, src, df_name, pos))
        #         try:
        #             layer = arcpy.mapping.Layer(src)
        #             layer.visible = False
        #             arcpy.mapping.AddLayer(df, layer, pos)
        #
        #         except Exception as e:
        #             messages.AddErrorMessage(e.message)
        #
        # else:
        #     messages.AddMessage("No layers selected")

        return
