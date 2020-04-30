#################################################
"""
Create an OD Cost Matrix for ArcPro
Current ArcPro 2.x NA does not allow for multiple accumulation cost values.
Using function "Make OD Cost Matrix Analysis Layer" 
to initiate multiple accumulation cost values.
"""
#################################################

"""
Stuff
"""

try:
    # Import libraries
    import arcpy
    from arcpy import env
    import arcpy.na
    import os
    
    # Check for NA Extension
    if arcpy.CheckExtension("network") == "Available":
        arcpy.CheckOutExtension("network")
    else:
        raise arcpy.ExecuteError("Network Analyst Extension not available.")

    # Environment settings
    output_dir = r'D:\Python_Tools_Code\OD_Matrix_arcpy\OD_Matrix_arcpy' # switch out with your workspace file path
    env.workspace = os.path.join(output_dir, "OD_Matrix_arcpy.gdb")
    env.overwriteOutput = True

    # Set network route feature dataset and input data -- set local envrionment parameters
    na_network_data_source = r'C:\ArcGIS\Business Analyst\US_2018\Data\Streets Data\NorthAmerica.gdb\Routing\Routing_ND' # point to Routing_ND feature dataset
    input_gdb = r'D:\Python_Tools_Code\OD_Matrix_arcpy\OD_Matrix_arcpy\ODCost_Matrix.gdb' # point to user geodatabase file path
    
    layer_name = str('DC_SC_OD_Matrix') # create layer name for OD Cost Matrix
    travel_mode = "Driving Time" # call travel mode for analysis
           
    origin = os.path.join(input_gdb, "DC_Sites", "DC_Sites") # point to assigned origins shapefile, currently pointing to file structure database --> feature dataset --> point shapefile
    destination = os.path.join(input_gdb, "SC_Sites", "SC_Sites") # point to assigned destinations shapefile, currently pointing to file structurE database --> feature dataset --> point shapefile

    output_layer_file = os.path.join(output_dir, layer_name + ".lyrx") # out directory and file type for OD Cost Matrix, lyrx Pro layer file type


    # Create OD Cost matrix layer
    result_object = arcpy.MakeODCostMatrixAnalysisLayer_na(na_network_data_source, layer_name=layer_name, travel_mode=travel_mode, accumulate_attributes="Miles") # creating OD Cost Matrix and adding in drive distance miles for accumulated values in OD Matrix
    layer_object = result_object.getOutput(0)

    sub_layers = arcpy.na.GetNAClassNames(layer_object)
    origin_layer_name = sub_layers["Origins"]
    destination_layer_name = sub_layers["Destinations"]

    field_mapping_origin = arcpy.na.NAClassFieldMappings(layer_object, origin_layer_name)
    field_mapping_origin["Name"].mappedFieldName = "DC_ID" # establish DC_ID as the "Name" primary key to rectify origin location data after analysis
    arcpy.na.AddLocations(layer_object, origin_layer_name, origin, field_mapping_origin)

      
    field_mapping_destination = arcpy.na.NAClassFieldMappings(layer_object, destination_layer_name)
    field_mapping_destinaiton["Name"].mappedFieldName = "SC_ID" # establish SC_ID as the "Name" primary key to rectify destination location data after analysis
    arcpy.na.AddLocations(layer_object, destination_layer_name, destination, field_mapping_destination)

    # Solve OD MAtrix
    arcpy.na.Solve(layer_object)

    # Save the solved OD cost matrix layer
    layer_object.saveACopy(output_layer_file)

    print("OD Cost Matrix solved.")

except Exception as e:
    # If error occured print line number
    import traceback, sys
    tb = sys.exc_info()[2]
    print("An error has occured at line %i" % tb.tb_lineno)
    print(str(e))
