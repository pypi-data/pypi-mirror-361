from collections import defaultdict
import glob
import matplotlib.pyplot as plt
import netrc
import os
import numpy as np
import pydicom
import pymysql
import re
import sys
import struct
from tabulate import tabulate
import xnat
from skimage.draw import polygon
from skimage.transform import resize
import json


verbose=1
rootDir="/data/projects/RCR03-400/experiments"

#########################################################################################################################
#
#########################################################################################################################
class Grid3D:
    def __init__(self, grid, origin, spacing):
        self.grid = np.array(grid)
        self.origin = np.array(origin)
        self.spacing = np.array(spacing)

#########################################################################################################################
    def get_value_from_index(self, index):
       nx   = self.grid.shape[2]
       ny   = self.grid.shape[1]
       nz   = self.grid.shape[0]
       #print(f"nx {nx} ny {ny} nz {nz}")

       nxny    = nx * ny
       iz      = int(int(index)/nxny);
       oIndex2 = int(int(index)-iz*nxny);
       iy = int(oIndex2/nx);
       ix = int(oIndex2-iy*nx);

       return self.grid[iz,iy,ix]
    def get_value_at_position(self, position):
        """
        Given a position in real-world coordinates, return the value at that position in the grid.

        Args:
            position (tuple or list): The (x, y, z) coordinates in real-world space.
        Returns:
            value (float): The value at the given position in the grid.
        """
        indices = self.get_index_from_position(position)

        if np.any(indices < 0) or np.any(indices >= self.grid.shape):
            return 0.
        return self.grid[tuple(indices)]
    
    def get_position_from_index(self, index):
        """
        Given an index in the grid, return the real-world position.

        Args:
            index (tuple or list): The (i, j, k) indices in the grid.
        Returns:
            position (np.ndarray): The (x, y, z) coordinates in real-world space.
        """
        return self.origin + np.array(index) * self.spacing

    def get_index_from_position(self, position):
        """
        Given a position in real-world coordinates, return the index in the grid.

        Args:
            position (tuple or list): The (x, y, z) coordinates in real-world space.
        Returns:
            index (np.ndarray): The (i, j, k) indices in the grid.
        """
        return np.round((np.array(position) - self.origin) / self.spacing).astype(int)
########################################################################################################    
#
########################################################################################################    
class voxelSpectrum:
    def __init__(self, index, h_min, delta_e, n_bins, n_entries, entries, dose, let ):
        self.index     = index
        self.h_min     = h_min 
        self.delta_e   = delta_e
        self.n_bins    = n_bins
        self.n_entries = n_entries
        self.entries   = entries
        self.dose      = dose
        self.let       = let 
    def __repr__(self):
        entries_str = "\n".join(f"{i:<10} {val:>10}" for i, val in enumerate(self.entries))
        return f"<voxelSpectrum index:{self.index} dose:{self.dose} let:{self.let} \n histo:{{{entries_str}}}>"
    def __str__(self):
        entries_str = "\n".join(f"{i:<10} {val:>10}" for i, val in enumerate(self.entries))
        return f"<voxelSpectrum index:{self.index} dose:{self.dose} let:{self.let} \n histo:{{{entries_str}}}>"

    def set_index(self, new_index):
        self.index = new_index
########################################################################################################    
#
########################################################################################################    
def accumulate_dose_from_files(dicom_files):
    accumulated_dose = None
    slice_thickness = None

    for file in dicom_files:
        ds = pydicom.dcmread(file)

        # Get dose data
        dose_data = ds.pixel_array
        dose_grid_scaling = ds.DoseGridScaling
        dose_data = dose_data * dose_grid_scaling

        if accumulated_dose is None:
            accumulated_dose = dose_data
            slice_thickness = ds.GridFrameOffsetVector[1] - ds.GridFrameOffsetVector[0]
        else:
            accumulated_dose += dose_data

    return accumulated_dose, slice_thickness
###################################################################################################################################
#
###################################################################################################################################
def add_voxel_histos(histos_array):

    histos_dict = defaultdict(list)  # Initialize as a defaultdict
    for histos in histos_array:
        for index, histo in histos.items():
              histos_dict[index].append(histo)  # Add voxelSpectrum object to list


    # Resulting list of summed voxelSpectrum objects
    summed_voxel_spectra = {}

    print("Doing the addition")
    for index, voxel_list in histos_dict.items():
        total_dose        = sum(voxel.dose for voxel in voxel_list)
        total_entries     = sum(voxel.n_entries for voxel in voxel_list)
        dose_weighted_let = sum(voxel.let * voxel.dose for voxel in voxel_list) / total_dose if total_dose != 0 else 0
        
        # Find the maximum length of the entries arrays
        max_length = max(voxel.n_bins for voxel in voxel_list)
        
        # Check that h_min and delta_e are the same for all elements in the voxel list
        h_min = voxel_list[0].h_min
        delta_e = voxel_list[0].delta_e
        if not all(voxel.h_min == h_min for voxel in voxel_list):
            raise ValueError("Mismatch in h_min values h_min", h_min," voxel.h_min ", voxel.h_min)
        if not all(voxel.delta_e == delta_e for voxel in voxel_list):
            raise ValueError("Mismatch in delta_e values")

        # Sum entries, padding with zeros where necessary
        summed_entries = np.zeros(max_length)
        for voxel in voxel_list:
            padded_entries = np.pad(voxel.entries, (0, max_length - len(voxel.entries)), 'constant')
            summed_entries += padded_entries
        
        # Add the summed voxelSpectrum object to the result list
        summed_voxel_spectra[index]=voxelSpectrum(index, h_min, delta_e, max_length, total_entries, summed_entries.tolist(), total_dose, dose_weighted_let)


    return summed_voxel_spectra

#
################################################################################################
#
################################################################################################
def clean_temp_dir ( temp_dir ):
    shutil.rmtree(temp_dir)
################################################################################################
#
################################################################################################
def fetch_patient_fdc_dose(xnat_info, patient_id):
    return fetch_patient_info ( xnat_info, patient_id, "FDC FRBE Dose", "DICOM" )
def fetch_patient_tps_dose(xnat_info, patient_id):
    return fetch_patient_info ( xnat_info, patient_id, "Dose", "DICOM" )
################################################################################################
#
################################################################################################
def fetch_patient_info(xnat_info, patient_id, variable, resource, verbose=0):
    plans = get_plans(xnat_info, patient_id)

    grids    = []
    origins  = []
    spacings = []

    if verbose>0: print(f"fetch_patient_info patient_id {patient_id} variable {variable} ")

    lastUID=None
    lastSpacing=None
    for plan_label in plans:
        if verbose > 0:
            print("plan_label ", plan_label)
        info_grid3D = fetch_plan_info(xnat_info, plan_label, variable, resource)

        scan_id = get_scan_id_by_scan_type(xnat_info, plan_label, "CTs")
        if scan_id is None:
            print("CTs not found for ", plan_label)
            continue

        if xnat_info['session'] is None:
            print("xnat_session could not be opened ")
            return

        project = xnat_info['session'].projects[xnat_info['project_id']]
        subject = project.subjects[patient_id]
        experiment = subject.experiments[plan_label]

        scan = experiment.scans[scan_id]

        if verbose > 2:
            print("info_grid.shape ", info_grid3D.grid.shape)
            print("info_origin ", info_grid3D.origin)
            print("info_spacing ", info_grid3D.spacing)
            print("info_grid ", np.sum(info_grid3D.grid))
        if lastUID != None:
           if lastUID != scan.uid:
               print("Problem different plans have different UID ")
               return None
           if not np.array_equal(lastSpacing,info_grid3D.spacing):
               print("Problem different plans have different UID ")
               return None

        lastUID=scan.uid
        lastSpacing=info_grid3D.spacing
       
        grids.append(info_grid3D.grid)
        origins.append(np.array(info_grid3D.origin))
        spacings.append(np.array(info_grid3D.spacing))

    shapes = np.array([grid.shape for grid in grids])
    min_extents = np.min(origins, axis=0)
    max_extents = np.max(origins + shapes * spacings, axis=0)
#   print("Min extents:", min_extents)
#   print("Max extents:", max_extents)

    # Calculate new shape and spacing
    new_spacing = np.min(spacings, axis=0)
    new_shape = np.ceil((max_extents - min_extents) / new_spacing).astype(int)
#   print("New spacing:", new_spacing)
#   print("New shape:", new_shape)
        
    resampled_grids=[]
    for grid, origin, spacing in zip(grids,origins,spacings):
       shift1 = ((origin - min_extents)/spacing).astype(int)
       shift2 = ((max_extents - origin - grid.shape * spacing)/spacing ).astype(int)
       #print("shift1 ", shift1, "shift2 ", shift2)
       padded_grid = np.pad(grid,((shift1[0],shift2[0]),(shift1[1],shift2[1]),(shift1[2],shift2[2])))

       pGrid=Grid3D(padded_grid, min_extents, new_spacing)
       #print(" padded_grid.shape ", padded_grid.shape)
       resampled_grids.append(padded_grid)

    combined_grid_data = np.sum(resampled_grids, axis=0)

    return Grid3D(combined_grid_data, min_extents, new_spacing)
################################################################################################
#
################################################################################################
def fetch_patient_fdc_let ( xnat_info, patient_id, verbose=0 ):

   plans=get_plans(xnat_info, patient_id)

   lastUID=None
   last_spacing=None
   dose3Ds=[]
   let3Ds=[]
   for plan_label in plans:
       if verbose > 0: print(" plan_label ", plan_label)
       #dose3D = fetch_plan_fdc_dose ( xnat_info, plan_label )
       let3D, dose3D = fetch_plan_let ( xnat_info, plan_label )

       if not np.array_equal(dose3D.spacing,let3D.spacing):
           print("LET and Dose have different spacing for ", plan_label)
           return None

       scan_id=get_scan_id_by_scan_type(xnat_info, plan_label, "CTs")
       if scan_id == None:
           print("CTs not found for ", plan_label)
           continue
       
       if xnat_info['session'] == None:
           print("xnat_session could not be opened ")
           return

       project = xnat_info['session'].projects[xnat_info['project_id']]
       subject = project.subjects[patient_id]
       experiment = subject.experiments[plan_label]
       
       scan = experiment.scans[scan_id]
       
       if verbose > 1:
          print("dose3D.shape ", dose3D.shape)
          print("dose3D.origin ", dose3D.origin)
          print("dose3D.spacing ", dose3D.spacing)
       if lastUID != None:
           if lastUID != scan.uid:
               print("Problem different plans have different CT UID ")
               return None

           if not np.array_equal(last_spacing, dose3D.spacing):
               print("Problem different dose grid scaling ")
               return None

           if not np.array_equal(last_spacing, let3D.spacing):
               print("Problem different LET grid scaling ")
               return None

       dose3Ds.append(dose3D)
       let3Ds.append(let3D)

       lastUID=scan.uid
       last_spacing=dose3D.spacing

   dose_grids  = np.array([dose3D.grid for dose3D in dose3Ds])
   let_grids   = np.array([let3D.grid for let3D in let3Ds])

   shapes = np.array([dose_grid.shape for dose_grid in dose_grids]+[let_grid.shape for let_grid in let_grids])

   origins  = np.array([dose3D.origin for dose3D in dose3Ds]+[let3D.origin for let3D in let3Ds])

   spacings   = np.array([dose3D.spacing for dose3D in dose3Ds]+[let3D.spacing for let3D in let3Ds])
   if verbose>2:
      print("shapes ", shapes)
      print("origins ", origins)
      print("spacings ", spacings)
 
   #spacings = dose_spacings + let_spacings
   #print("spacings ", spacings)

   min_extents = np.min(origins, axis=0)
   max_extents = np.max(origins + shapes * spacings, axis=0)
    # Calculate new shape and spacing
   new_spacing = np.min(spacings, axis=0)
   new_shape = np.ceil((max_extents - min_extents) / new_spacing).astype(int)
   if verbose>2:
      print("Min extents:", min_extents)
      print("Max extents:", max_extents)
      print("New spacing:", new_spacing)
      print("New shape:", new_shape)

   total_let  = np.zeros(new_shape, dtype=np.float64)
   total_dose = np.zeros(new_shape, dtype=np.float64)

   for dose3D, let3D in zip(dose3Ds, let3Ds):
      shift1 = ((dose3D.origin - min_extents)/dose3D.spacing).astype(int)
      shift2 = ((max_extents - dose3D.origin - dose3D.grid.shape * dose3D.spacing)/dose3D.spacing ).astype(int)
      #print("shift1 ", shift1, "shift2 ", shift2)
      dose_padded_grid = np.pad(dose3D.grid,((shift1[0],shift2[0]),(shift1[1],shift2[1]),(shift1[2],shift2[2])))

      shift1 = ((let3D.origin - min_extents)/let3D.spacing).astype(int)
      shift2 = ((max_extents - let3D.origin - let3D.grid.shape * let3D.spacing)/let3D.spacing ).astype(int)
      #print("shift1 ", shift1, "shift2 ", shift2)
      let_padded_grid = np.pad(let3D.grid,((shift1[0],shift2[0]),(shift1[1],shift2[1]),(shift1[2],shift2[2])))

      total_dose += dose_padded_grid
      total_let  += let_padded_grid * dose_padded_grid 

   dose_averaged_let = np.divide(total_let, total_dose, out=np.zeros_like(total_let), where=total_dose!=0)

   return Grid3D(dose_averaged_let, min_extents, new_spacing), Grid3D(total_dose, min_extents, new_spacing)
################################################################################################
#
################################################################################################
def fetch_beam_info ( xnat_info, experiment_id, requested_beam_number, variable, resource ):
   if verbose>0: print(f"fetch_beam_info plan:{experiment_id} beam:{requested_beam_number} variable:{variable} ")

   scan_id=get_scan_id_by_scan_type(xnat_info, experiment_id, variable, verbose=0)
   if scan_id == None:
       print(" fetch_beam_info: Dose not found")
       return None
   info_files = fetch_xnat_files(xnat_info,experiment_id,scan_id, resource)
   if info_files == None:
       print(" fetch_beam_info: ", variable, " files not found")
       return None

   selected_file=None
   for info_file in info_files:
      info = pydicom.dcmread(info_file)
      beam_number = info.ReferencedRTPlanSequence[0].ReferencedFractionGroupSequence[0].ReferencedBeamSequence[0].ReferencedBeamNumber
      #print("beam_number ", beam_number )
      if beam_number == requested_beam_number:
          selected_file = info_file
          break

   #print("selected_file ", selected_file)
   if selected_file == None:
      print(requested_beam_number," not found ")
      return None

   return load_info_grid([selected_file])
################################################################################################
#
################################################################################################
def fetch_beam_fdc_dose ( xnat_info, experiment_id, requested_beam_number ):
    return fetch_beam_info ( xnat_info, experiment_id, requested_beam_number, "FDC FRBE Dose", "DICOM" )

################################################################################################
#
################################################################################################
def fetch_beam_let ( xnat_info, experiment_id, requested_beam_number ):
    return fetch_beam_info ( xnat_info, experiment_id, requested_beam_number, "LET Dose", "DICOM" )

################################################################################################
#
################################################################################################
def fetch_beam_tps_dose ( xnat_info, experiment_id, requested_beam_number ):
    return fetch_beam_info ( xnat_info, experiment_id, requested_beam_number, "Dose", "DICOM" )

################################################################################################
#
################################################################################################
def fetch_plan_info ( xnat_info, experiment_id, variable, resource ):
   if verbose>0: print(f"fetch_plan_info plan:{experiment_id} variable:{variable} ")

   scan_id=get_scan_id_by_scan_type(xnat_info, experiment_id, variable, verbose=0)
   if scan_id == None:
       print(" fetch_plan_info: Dose not found")
       quit()
       #return None
   dose_files = fetch_xnat_files(xnat_info,experiment_id,scan_id, resource)
   if dose_files == None or dose_files ==[] :
       print(" fetch_plan_info: Dose files not found")
       quit()
       #return None

   return load_info_grid(dose_files)
################################################################################################
#
################################################################################################
def fetch_plan_let ( xnat_info, experiment_id, verbose=0 ):

   scan_id=get_scan_id_by_scan_type(xnat_info, experiment_id, "FDC FRBE Dose", verbose=0)
   if scan_id == None:
       print(" fetch_let: Dose not found")
       return None
   dose_files = fetch_xnat_files(xnat_info,experiment_id,scan_id, "DICOM")
   if dose_files == None:
       print(" fetch_Let: Dose files not found")
       return None

   scan_id=get_scan_id_by_scan_type(xnat_info, experiment_id, "LET Dose", verbose=0)
   if scan_id == None:
       print("fetch_let: LET files not found ")
       return None

   let_files = fetch_xnat_files(xnat_info,experiment_id,scan_id,"DICOM")
   if let_files == None:
       print("fetch_let: LET Files not found ")
       return
   if verbose > 1: print("let_files ", fdc_let_files)

   return load_let_grid(dose_files, let_files)
#########################################################################################################################
#
#########################################################################################################################
def fetch_structure_info ( xnat_info, experiment_id, selected_structures, dose_grid, dose_cutoff=0 ):

   structure_masks = fetch_structure_mask ( xnat_info, experiment_id, selected_structures, dose_grid, dose_cutoff )

   structure_doses={}
   for structure_name, structure_mask in structure_masks.items():
       structure_dose = dose_grid.grid[structure_mask > 0]
       structure_doses[structure_name]=structure_dose

   return structure_doses

#########################################################################################################################
#
#########################################################################################################################
def fetch_structure_3Dinfo ( xnat_info, experiment_id, selected_structures, dose_grid, dose_cutoff=0 ):

   structure_masks = fetch_structure_mask ( xnat_info, experiment_id, selected_structures, dose_grid, dose_cutoff )
   structure_doses={}
   for structure_name, structure_mask in structure_masks.items():
       #structure_dose = dose_grid.grid[structure_mask > 0]
       structure_dose = np.where(structure_mask, dose_grid.grid, 0)
       structure_doses[structure_name]=Grid3D(structure_dose, dose_grid.origin, dose_grid.spacing)

   return structure_doses
#########################################################################################################################
#
#########################################################################################################################
def fetch_structure_mask ( xnat_info, experiment_id, selected_structures, dose_3D, dose_cutoff=0 ):

    #print(f"TTTTT fetch_structure_mask structures {selected_structures}")
   scan_id=get_scan_id_by_scan_type(xnat_info, experiment_id, "Structures")
   #print("TTTTT scan_id ", scan_id)
   if scan_id == None:
       print(" fetch_structure_mask: Structures not found")
       return None
   if verbose>1: print("scan_id ", scan_id)
   structure_files = fetch_xnat_files(xnat_info,experiment_id,scan_id, "secondary")
   if structure_files == None:
       print(" fetch_structure_mask: Structure file not found")
       return None

   structures = load_structure_set(structure_files)
   if structures == None:
       print("fetch_structures: structures not found in ", structure_files)
       return None
   #print(f"TTTTT fetch_structure_mask structures {structures}")

   #progress_bar = tqdm(structures.items(), desc="Calculating DVH", unit="structure")
   dose_array = dose_3D.grid.copy()

   structure_masks={}
   for structure_name, contours in structures.items():
        if structure_name == "none" : continue
        if verbose>1: print("structure ", structure_name )
        if selected_structures and structure_name not in selected_structures:
            continue

        structure_mask = np.zeros(dose_3D.grid.shape, dtype=np.uint8)

        for contour in contours:
            contour_points = (contour - dose_3D.origin) / dose_3D.spacing 
            contour_points = np.rint(contour_points).astype(int)

            for z in np.unique(contour_points[:, 2]):
                slice_contour = contour_points[contour_points[:, 2] == z]
                if slice_contour.shape[0] > 0:
                    rr, cc = polygon(slice_contour[:, 1], slice_contour[:, 0], structure_mask.shape[:2])
                    try:
                        structure_mask[int(z), rr, cc] = 1
                    except IndexError:
                        continue

        if structure_mask.shape != dose_3D.grid.shape:
            structure_mask = resize(structure_mask, dose_3D.grid.shape, preserve_range=True, order=0).astype(np.uint8)
       
        structure_mask[dose_array<dose_cutoff]=0
        structure_masks[structure_name]=structure_mask

   return structure_masks;
################################################################################################
#
################################################################################################
def fetch_plan_cts ( xnat_info, experiment_id ):
    scan_id=get_scan_id_by_scan_type(xnat_info, experiment_id, "CTs")
    if scan_id==None:
        print(f"Images not found for {experiment_id}")
        return None
    return fetch_xnat_files( xnat_info, experiment_id,scan_id, "DICOM")
################################################################################################
#
################################################################################################
def fetch_plan_tps_dose ( xnat_info, experiment_id ):
    return fetch_plan_info ( xnat_info, experiment_id, "Dose", "DICOM" )
################################################################################################
#
################################################################################################
def fetch_plan_fdc_dose ( xnat_info, plan_id ):
    return fetch_plan_info ( xnat_info, plan_id, "FDC FRBE Dose", "DICOM" )
########################################################################################################    
#
########################################################################################################    
def get_dose_files ( aplan, engine, beam ):
    
    scan="1104"
    if   engine == "TPS":  scan="104"
    elif engine == "Dose": scan="1104"
    
    expDir = find_plan_directory(aplan)
    bm=beam.lower()
    search_pattern = expDir + "/SCANS/"+scan+"*/DICOM"
    dose_dirs = glob.glob(search_pattern)
    
    if len(dose_dirs) == 1 :
        search_pattern = expDir + "/SCANS/"+scan+"*/DICOM/*.dcm"
        dose_files = glob.glob(search_pattern)
        #print("dose_files ", dose_files)
        
        if beam != None and bm != "all":
            selected_files=[]
            #print("dose_files ", dose_files)
            for dose_file in dose_files:
                #print("dose_file ",dose_file)
                ds = pydicom.dcmread(dose_file)
                referenced_beam_number = None
                if 'ReferencedRTPlanSequence' in ds:
                    rt_plan_sequence = ds.ReferencedRTPlanSequence
    
                    if rt_plan_sequence and len(rt_plan_sequence) > 0:
                       referenced_rt_plan = rt_plan_sequence[0]  # Assuming there's only one referenced RT plan
        
                       if 'ReferencedFractionGroupSequence' in referenced_rt_plan:
                          fraction_group_sequence = referenced_rt_plan.ReferencedFractionGroupSequence
            
                          if fraction_group_sequence and len(fraction_group_sequence) > 0:
                             referenced_fraction_group = fraction_group_sequence[0]  # Assuming there's only one referenced fraction group
                
                             if 'ReferencedBeamSequence' in referenced_fraction_group:
                                 beam_sequence = referenced_fraction_group.ReferencedBeamSequence
                    
                                 if beam_sequence and len(beam_sequence) > 0:
                                    referenced_beam = beam_sequence[0]  # Assuming there's only one referenced beam
                        
                                    if 'ReferencedBeamNumber' in referenced_beam:
                                        referenced_beam_number = referenced_beam.ReferencedBeamNumber
                                        #print("Ref_beam ",referenced_beam_number,"  beam ", beam)
                                        if referenced_beam_number == beam:
                                            selected_files.append(dose_file)
            
            return selected_files
            #print(dose_file)
        else:
            return dose_files
    else:
        print("Get_dose_files, multiple directories found for ",engine)
        return None

########################################################################################################    
#
########################################################################################################    
def get_dose (aplan,engine,beam):
    dose_files = get_dose_files(aplan,engine,beam)
    summed_dose_grid = None
    for dose_file in dose_files:
        ds = pydicom.dcmread(dose_file)
        if ds.Modality != "RTDOSE":
            raise ValueError("The provided DICOM file is not an RTDose file.")
        dose_grid = ds.pixel_array
        dose_grid_scaling = ds.DoseGridScaling
        
        dose_grid = dose_grid * dose_grid_scaling
        
        if summed_dose_grid is None:
            summed_dose_grid = np.zeros_like(dose_grid, dtype=np.float64)
        summed_dose_grid += dose_grid
    return summed_dose_grid    

########################################################################################################    
#
########################################################################################################    
def get_files_by_scan_type(xnat_session, project, experiment, xnat_url, scan_type):

 # Select project and experiment
    project_obj = xnat_session.projects[project]
    experiment_obj = project_obj.experiments[experiment]
    if verbose>1 : print("proj obj ",project_obj," exp_obj ", experiment_obj)

     # Iterate over scans to find the correct scan type
    for scan in experiment_obj.scans.values():
         if scan.type == scan_type:
             # Retrieve all files for this scan
             files = scan.files.values()
             #file_names = [file.name for file in files]
             #return file_names
             file_paths = [f"{xnat_url}{file.uri}" for file in files]
             return file_paths

########################################################################################################    
#
########################################################################################################    
def get_dose_at_voxel(summed_dose_grid, ix, iy, iz):
    if ix < 0 or ix >= summed_dose_grid.shape[2] or iy < 0 or iy >= summed_dose_grid.shape[1] or iz < 0 or iz >= summed_dose_grid.shape[0]:
        raise IndexError("Voxel coordinates are out of bounds.")
        return 0
    return summed_dose_grid[iz, iy, ix]
################################################################################################
#
################################################################################################
def get_experiments(xnat_info, subject_id):
    get_xnat_session(xnat_info)
    if xnat_info['session'] == None:
       return
    try:
        project = xnat_info['session'].projects[xnat_info['project_id']]
    except Exception as e:
        print(xnat_info['project_id']," project not found ", e )
        return
    try:
       subject = project.subjects[subject_id]
    except Exception as e:
        print(subject_id," subject not found ", e )
        return
    
    experiments = subject.experiments.values()
    experiment_list = [exp.label for exp in experiments]
        
    return experiment_list
   
########################################################################################################    
#
########################################################################################################    
def get_lattice_info ( aplan ):
    expDir=rootDir+"/"+aplan
    search_pattern = expDir + "/SCANS/104/voxel_spectra/lattice-info.txt"
    matching_files = glob.glob(search_pattern)
    if verbose > 2 : 
         print(" search_pattern ", search_pattern)
         for file_path in matching_files:
            print(file_path)
    if len(matching_files) == 0 :
        print("get_voxel_info, lattice-info not found")
        return
    if len(matching_files) > 1 :
        print("get_voxel_info, multiple lattice-info files found")
        return 
    
    lattice_info={}
    try:
        with open(matching_files[0], 'r') as file:
            lines = file.readlines()
            for line in lines:
                parts = line.strip().split()
                i = 0
                while i < len(parts):
                    key = parts[i]
                    if key in ['nx', 'ny', 'nz', 'nTot']:
                        lattice_info[key] = int(parts[i + 1])
                        i += 2
                    elif key in ['xmi', 'ymi', 'zmi', 'xma', 'yma', 'zma', 'dx', 'dy', 'dz']:
                        lattice_info[key] = float(parts[i + 1])
                        i += 2
                    else:
                        i += 1  # Move to the next part if key is not recognized
    except e:
        print("get_lattice_info ", e)
    return lattice_info
################################################################################################
#
################################################################################################
def get_plans(xnat_info, subject_id):
    return get_experiments(xnat_info, subject_id)
########################################################################################################    
#
########################################################################################################    
def get_scan_numbers(xnat_session, project, experiment, xnat_url, scan_type):
 # Select project and experiment
    project_obj    = xnat_session.projects[project]
    experiment_obj = project_obj.experiments[experiment]

     # Iterate over scans to find the correct scan type
    scan_ids = []
    for scan in experiment_obj.scans.values():
         #print("scan ", scan, "scan.type ", scan.type, ' scan.id ', scan.id )
         if scan.type == scan_type:
             # Retrieve all files for this scan
             scan_ids.append(scan.id)
    return scan_ids
########################################################################################################    
#
########################################################################################################    
def get_voxel_index(aplan,indices):
    lattice_info = get_lattice_info(aplan)
    
    if lattice_info == None:
        print("get_voxel_indices, lattice_info not found ")
        return (-1,-1,-1)
    
    nx   = int(lattice_info['nx'])
    ny   = int(lattice_info['ny'])
    nz   = int(lattice_info['nz'])

    if len(indices)!= 3:
        print("Wrong dimensions of indices ", indices )        
    index = indices[2]*(nx*ny)+indices[1]*nx+indices[0] ;
    return index
########################################################################################################    
#
########################################################################################################    
def fetch_voxel_index(grid_3D,indices):

    if grid_3D.ndim != 3:
        print("Provided grid is not 3D")
        return (-1,-1,-1)

    nx   = grid_3D.shape[2]
    ny   = grid_3D.shape[1]
    nz   = grid_3D.shape[0]
    nxny = nx * ny

    if len(indices)!= 3:
        print("Wrong dimensions of indices ", indices )        

    index = indices[2]*(nx*ny)+indices[1]*nx+indices[0] ;
    return index
########################################################################################################    
#
########################################################################################################    
def get_voxel_indices(aplan,voxel):
    lattice_info = get_lattice_info(aplan)
    
    if lattice_info == None:
        print("get_voxel_indices, lattice_info not found ")
        return (-1,-1,-1)
    
    nx   = int(lattice_info['nx'])
    ny   = int(lattice_info['ny'])
    nz   = int(lattice_info['nz'])
    nxny = int(lattice_info['nx'])*int(lattice_info['ny'])
    #print(" voxel ", voxel, "nxny ",nxny)
    iz      = int(int(voxel)/nxny);
    oIndex2 = int(int(voxel)-iz*nxny);
    iy = int(oIndex2/nx);
    ix = int(oIndex2-iy*nx);
    return (ix,iy,iz)
########################################################################################################    
#
########################################################################################################    
def fetch_voxel_indices(grid_3D,index):
    
    if grid_3D.ndim != 3:
        print("Provided grid is not 3D")
        return (-1,-1,-1)

    nx   = grid_3D.shape[2]
    ny   = grid_3D.shape[1]
    nz   = grid_3D.shape[0]
    nxny = nx * ny

    #print(" voxel ", voxel, "nxny ",nxny)
    iz      = int(int(index)/nxny);
    oIndex2 = int(int(index)-iz*nxny);
    iy = int(oIndex2/nx);
    ix = int(oIndex2-iy*nx);
    return (ix,iy,iz)



########################################################################################################    
#
########################################################################################################    
def get_voxel_indices_bare(lattice_info,voxel):
    
    nx   = int(lattice_info['nx'])
    ny   = int(lattice_info['ny'])
    nz   = int(lattice_info['nz'])
    nxny = int(lattice_info['nx'])*int(lattice_info['ny'])
    #print(" voxel ", voxel, "nxny ",nxny)
    iz      = int(int(voxel)/nxny);
    oIndex2 = int(int(voxel)-iz*nxny);
    iy = int(oIndex2/nx);
    ix = int(oIndex2-iy*nx);
    return (ix,iy,iz)


########################################################################################################    
#
########################################################################################################    
def get_voxel_position(aplan,voxel):
    
    lattice_info = get_lattice_info(aplan)
    if lattice_info == None:
        print("get_voxel_indices, lattice_info not found ")
        return (-1,-1,-1)
    indices = get_voxel_indices_bare(lattice_info,voxel)
    
    xmi = float(lattice_info['xmi'])
    ymi = float(lattice_info['ymi'])
    zmi = float(lattice_info['zmi'])
    dx  = float(lattice_info['dx'])
    dy  = float(lattice_info['dy'])
    dz  = float(lattice_info['dz'])

    x  = xmi + (indices[0]+0.5)*dx
    y  = ymi + (indices[1]+0.5)*dy
    z  = zmi + (indices[2]+0.5)*dz
     
    return (x,y,z)
########################################################################################################    
#
########################################################################################################    
def get_voxel_spectra ( fileName, desired_voxels=[3504496, 3505782] ):

    if verbose>0:print(f"get_voxel_spectra, fileName {fileName}")
    if "-lin-" in fileName or "-log-" in fileName: # old format
       histos = read_bin_spectra(fileName)
    else:
       print("Format not supported any more")
       return None
       #histos = read_bin_spectra0(fileName)
    #print("after calling find_voxel_spectra len ", len(histos))

    if len(desired_voxels) < 1: 
        return histos

# Convert the selected indices to a set for O(1) lookups
    desired_voxels_set = set(desired_voxels)
    #print("desired_voxels_set ", desired_voxels_set )

    filtered_histos = {index: voxel for index, voxel in histos.items() if index in desired_voxels_set}
    
    return filtered_histos
########################################################################################################    
#
########################################################################################################    
def get_voxel_spectra_histos(xnat_info, aplan, type_histogram, voxels=[3504495, 3505782], beam="all"):
    if verbose>0: print("get_voxel_spectra_histos: beam ", beam, " len(voxels) ", len(voxels) )
    expDir = find_plan_directory(aplan)
    files = find_voxel_spectra_files(expDir, type_histogram, beam)

    if files is None or len(files) == 0:
        #print("Going to fetch_xnat_files")
        all_files = fetch_xnat_files(xnat_info, aplan, "104", "voxel_spectra")
        #print("all_files ", all_files)
        if all_files is None or len(all_files) == 0:
            print("No voxel_spectra files found for", aplan)
            return None
        files = find_voxel_spectra_files(expDir, type_histogram, beam)

    if len(files) == 1:
       histos = get_voxel_spectra(files[0], voxels)
       return histos;

    histos_array = []
    if len(files) > 1:
        for file_path in files:
            if verbose>2:print("file_path", file_path)
            histos = get_voxel_spectra(file_path, voxels)
            histos_array.append(histos)

    summed_voxel_spectra=add_voxel_histos(histos_array)

    files = find_voxel_spectra_files(expDir, type_histogram, beam)
    if len(files)>1 and len(voxels)==0:
        if verbose>1:print("more than one file, save sum in ")
        filename=files[0]
        if filename.endswith('voxel-spectra.bin'):
           new_filename = re.sub(r'beam_\d+', 'beam_all', filename)
           new_filename = re.sub(r'beam-\d+', 'beam-all', new_filename)
           if verbose>1:print("Save as ",new_filename)
           write_bin_spectra(new_filename, summed_voxel_spectra)

    return summed_voxel_spectra
#############################################################################################################################################
#
#############################################################################################################################################
def get_voxel_histos_patient(xnat_info, patient_id, voxels, type_histogram):

   if verbose>0: print(f"get_voxel_histos_patient: patient_id {patient_id} len(voxels): {len(voxels)}")

   plans = get_plans(xnat_info, patient_id)
   beam = "all"

   parsed_plans = [(plan, int(plan.split('-plan')[1])) for plan in plans]
   # Find the entry with the minimum ZZZ value
   min_plan = min(parsed_plans, key=lambda x: x[1])[0]
   expDir = find_plan_directory(min_plan)
   search_pattern = expDir + "/SCANS/104/voxel_spectra/fdc*-patient-"+type_histogram+"-voxel-spectra.bin"
   if verbose > 2: print("search_pattern ", search_pattern)
   matching_files = glob.glob(search_pattern)
   if len(matching_files) == 1:
      histos = get_voxel_spectra(matching_files[0], voxels)
      return histos
   elif len(matching_files) > 1:
       print(f"Something wrong more than one patient file {len(matching_files)}")
       return None

   histos_array=[]
   for plan in plans:
      print("Get ",plan)
      voxel_spectra_plan = get_voxel_spectra_histos ( xnat_info, plan, type_histogram, voxels, beam )
      #print("voxel_spectra_plan ", voxel_spectra_plan)
      if voxel_spectra_plan == None:
          print(f"histos for {plan} not found")
          return None
      histos_array.append(voxel_spectra_plan)

   pt_voxel_histos=add_voxel_histos(histos_array)

   if len(voxels)==0:
      print("going to write")
      file_patient = expDir + "/SCANS/104/voxel_spectra/fdc-patient-"+type_histogram+"-voxel-spectra.bin"
      write_bin_spectra(file_patient, pt_voxel_histos)
 
   return pt_voxel_histos 
#############################################################################################################################################
#
#############################################################################################################################################
def get_voxel_histos_patient_for_structures (xnat_info, patient_id, structures, type_histogram, dose_cutoff=0):

   plans = get_plans(xnat_info, patient_id)
   if len(plans)==0:
       print(f"plan for patient {patient_id} not found ")
       return

   fdc_dose_3D  = fetch_patient_fdc_dose ( xnat_info, patient_id )

   #print("TTTTTAAAAAA structures ", structures)
   structure_masks = fetch_structure_mask ( xnat_info, plans[0], structures, fdc_dose_3D, dose_cutoff )

   histo_dict={}
   for structure in structures:
       #print("structure ", structure)
      mask = structure_masks[structure]
      #print("mask      ", mask)
      nz, ny, nx = mask.shape
      non_zero_indices = np.argwhere(mask != 0)
      structure_indices = non_zero_indices[:, 0] * (nx * ny) + non_zero_indices[:, 1] * nx + non_zero_indices[:, 2]
      #print(f"len(structure_indices) {len(structure_indices)} ")

      histos=get_voxel_histos_patient(xnat_info, patient_id, structure_indices, type_histogram)
      histo_dict[structure]=histos

   return histo_dict
################################################################################################
#
################################################################################################
def get_referenced_beam_number(dataset):
    try:
        # Accessing nested sequences to find ReferencedBeamNumber
        return dataset.ReferencedRTPlanSequence[0].ReferencedFractionGroupSequence[0].ReferencedBeamSequence[0].ReferencedBeamNumber
    except AttributeError:
        return None
###############################################################################################3
#
###############################################################################################3
def get_scan_id_by_scan_type(xnat_info, experiment, scan_type, verbose=0):
    # Select project and experiment

    get_xnat_session(xnat_info)
    if xnat_info['session'] == None:
       return

    project_obj = xnat_info['session'].projects[xnat_info['project_id']]
    try:
       experiment_obj = project_obj.experiments[experiment]
    except:
        print(f"Experiment/plan {experiment} not found")

    if verbose > 1: 
        print("proj obj ", project_obj, " exp_obj ", experiment_obj)

    # Iterate over scans to find the correct scan type
    for scan_id, scan in experiment_obj.scans.items():
        if scan.type == scan_type:
            if verbose > 0:
                print(f"Found scan with type {scan_type}: scan_id {scan_id}")
            return scan_id

    if verbose > 0:
        print(f"No scan found with type {scan_type}")
    return None
###############################################################################################3
#
###############################################################################################3
def get_structure_list(xnat_info, experiment):
   scan_id=get_scan_id_by_scan_type(xnat_info, experiment, "Structures")
   if scan_id == None:
       print("Structures not found")
       return None
   localStructureFile=os.path.join(rootDir,experiment,"SCANS",scan_id,"secondary")
   #print("localStructureFile ",localStructureFile)
   structure_files = glob.glob(localStructureFile+"/*")

   structure_file=None
   if structure_files:
      structure_file = max(structure_files, key=os.path.getmtime)
   else:
      get_xnat_session(xnat_info)
      if  xnat_info['session'] == None:
         return
      print("No local structure file found")
      structure_files=fetch_xnat_files(xnat_info, experiment, scan_id, "secondary")
      if structure_files:
         structure_file = max(structure_files, key=os.path.getmtime)

   if structure_file == None:
       print("Going to return ")
       return 
   
   if verbose > 1: print("structure_file ", structure_file) 

   rtstruct = pydicom.dcmread(structure_file)
    
    # Check if the file is indeed an RTSTRUCT
   if rtstruct.Modality != 'RTSTRUCT':
        raise ValueError("The provided file is not an RTSTRUCT file.")
    
    # Extract the structures
   structures = []
   for roi in rtstruct.StructureSetROISequence:
       structures.append(roi.ROIName)
       #structures.append([
       #    roi.ROINumber,
       #    roi.ROIName,
       #])
   if verbose > 1: print("structures ", structures)
   return structures
################################################################################################
#
################################################################################################
def get_patients_by_group(xnat_info, group_name):
    """
    Connects to an XNAT database and returns a list of patients belonging to a particular group.

    Parameters:
    xnat_info (dict): Dictionary containing XNAT connection information.
    group_name (str): The name of the group.

    Returns:
    list: A list of patients belonging to the specified group.
    """
    get_xnat_session(xnat_info)
    if xnat_info['session'] == None:
       return

     # Perform the search
    subjects = xnat_info['session'].get(f"/data/subjects?group={group_name}")

            # Extract patient labels
    patient_labels = [subject['label'] for subject in subjects.json()['ResultSet']['Result']]
    return patient_labels
################################################################################################
#
################################################################################################
def get_plans(xnat_info, subject_id):
    return get_experiments(xnat_info, subject_id)
###############################################################################################3
#
###############################################################################################3
def get_xnat_session ( xnat_info ):
    if xnat_info['session'] == None:
       try:
          xnat_info['session'] = xnat.connect(xnat_info['url'], xnat_info['user'], loglevel='ERROR')
       except Exception as e:
          print("xnat session cannot be opened ", e)
          return None
    #print("get_xnat_session xnat_info end ", xnat_info)
###############################################################################################3
#
###############################################################################################3
def load_info_grid(dose_files):

    if len(dose_files) < 1 :
        print(f"load_info_grid dose_file list is empty")
        return quit()
    dose_data = [pydicom.dcmread(dose_file) for dose_file in dose_files]
    reference_shape = dose_data[0].pixel_array.shape
    dose_grid = np.zeros(reference_shape, dtype=np.float64)

    for dose_file in dose_data:
        pixel_array = dose_file.pixel_array
        if pixel_array.shape != reference_shape:
            pixel_array = resize(pixel_array, reference_shape, mode='edge', preserve_range=True)
        dose_grid += pixel_array * dose_file.DoseGridScaling

    dose_grid = dose_grid.astype(np.float64)
    dose_grid[dose_grid < 0] = 0

    dose_origin = np.array(dose_data[0].ImagePositionPatient)
    pixel_spacing = list(dose_data[0].PixelSpacing)
    slice_thickness = dose_data[0].GridFrameOffsetVector[1] - dose_data[0].GridFrameOffsetVector[0]
    dose_spacing = np.array(pixel_spacing + [slice_thickness])

#    return total_let, let_origin, let_spacing, 
    return Grid3D(dose_grid, dose_origin, dose_spacing)

################################################################################################
#
################################################################################################
def load_let_grid(dose_files, let_files):
    # Load all dose and LET files
    dose_data = [pydicom.dcmread(dose_file) for dose_file in dose_files]
    let_data = [pydicom.dcmread(let_file) for let_file in let_files]
    
    # Check that the number of dose files and LET files match
    if len(dose_data) != len(let_data):
        raise ValueError("The number of dose files and LET files must match.")
    
    dose_data.sort(key=get_referenced_beam_number)
    let_data.sort(key=get_referenced_beam_number)

    #print("dose_data ", dose_data)
    #print("let_data ", let_data)
    
   # Ensure that beam numbers match between dose and LET files
    for dose, let in zip(dose_data, let_data):
        if get_referenced_beam_number(dose) != get_referenced_beam_number(let):
            raise ValueError(f"Referenced beam numbers do not match: {get_referenced_beam_number(dose)} vs {get_referenced_beam_number(let)}")

    # Initialize arrays
    reference_shape = dose_data[0].pixel_array.shape
    total_let  = np.zeros(reference_shape, dtype=np.float64)
    total_dose = np.zeros(reference_shape, dtype=np.float64)

    # Process and accumulate dose and LET data
    for dose_file, let_file in zip(dose_data, let_data):
        dose_array = dose_file.pixel_array * dose_file.DoseGridScaling
        let_array = let_file.pixel_array * let_file.DoseGridScaling

        if dose_array.shape != reference_shape:
            dose_array = resize(dose_array, reference_shape, mode='edge', preserve_range=True)
        if let_array.shape != reference_shape:
            let_array = resize(let_array, reference_shape, mode='edge', preserve_range=True)
        
        total_dose += dose_array
        total_let += let_array * dose_array 

    # Calculate dose-averaged LET
    dose_averaged_let = np.divide(total_let, total_dose, out=np.zeros_like(total_let), where=total_dose!=0)

    dose_origin = np.array(dose_data[0].ImagePositionPatient)
    pixel_spacing = list(dose_data[0].PixelSpacing)
    slice_thickness = dose_data[0].GridFrameOffsetVector[1] - dose_data[0].GridFrameOffsetVector[0]
    dose_spacing = np.array(pixel_spacing + [slice_thickness])

    return Grid3D(dose_averaged_let, dose_origin, dose_spacing), Grid3D(total_dose, dose_origin, dose_spacing)
################################################################################################
#
################################################################################################
def load_structure_set(structure_files):
    structures = {}
    for structure_file in structure_files:
        ds = pydicom.dcmread(structure_file)
        if hasattr(ds, 'ROIContourSequence'):
            for roi_contour in ds.ROIContourSequence:
                contour_data = []
                if hasattr(roi_contour, 'ContourSequence'):
                    for contour_seq in roi_contour.ContourSequence:
                        contour_data.append(np.array(contour_seq.ContourData).reshape(-1, 3))
#               print(f"roi_contour_ReferencedROINumber {roi_contour.ReferencedROINumber} len(contour_data) {len(contour_data)}")
                if contour_data:
                    structures[roi_contour.ReferencedROINumber] = contour_data

        if hasattr(ds, 'StructureSetROISequence'):
            for roi in ds.StructureSetROISequence:
                roi_number = roi.ROINumber
                roi_name = roi.ROIName
                if roi_number in structures:
                    structures[roi_name] = structures.pop(roi_number)
                #else:
                #    print(f"TTTTTTTTTTTTTTTTT roi_name {roi_name} roi_number {roi_number} not found in strutures")

    return structures

###############################################################################################3
#
###############################################################################################3
def print_structure_list(xnat_info, experiment):
   structures=get_structure_list(xnat_info, experiment)
   headers = ["ROI Number", "ROI Name"]
   print(tabulate(structures, headers, tablefmt="grid"))


################################################################################################
#
################################################################################################
def verify_dose_let_per_file(dose_files, let_files, total_let_grid, num_samples=20):
    dose_data = [pydicom.dcmread(dose_file) for dose_file in dose_files]
    let_data = [pydicom.dcmread(let_file) for let_file in let_files]

    dose_data.sort(key=get_referenced_beam_number)
    let_data.sort(key=get_referenced_beam_number)

    reference_shape = dose_data[0].pixel_array.shape

    dose_array = dose_data[0].pixel_array * dose_data[0].DoseGridScaling
    valid_indices = np.argwhere(dose_array > 5.5)

    if len(valid_indices) < num_samples:
        raise ValueError("Not enough valid indices (dose > 0.5) to sample from.")

    sampled_indices = valid_indices[np.random.choice(valid_indices.shape[0], num_samples, replace=False)]
   
    print("Sampled Indices (z, y, x) and Values for Each File:\n")

    for idx in sampled_indices:
        
        z, y, x = idx
        print(f"Index ({z}, {y}, {x}):")

        tLet = total_let_grid[z,y,x]
        print("total LET ", tLet)
        for dose_file, let_file in zip(dose_data, let_data):
            dose_array = dose_file.pixel_array
            let_array = let_file.pixel_array * let_file.DoseGridScaling

            if dose_array.shape != reference_shape:
                dose_array = resize(dose_array, reference_shape, mode='edge', preserve_range=True)
            if let_array.shape != reference_shape:
                let_array = resize(let_array, reference_shape, mode='edge', preserve_range=True)

            dose_value = dose_array[z, y, x] * dose_file.DoseGridScaling
            let_value = let_array[z, y, x]
            beam_number1 = get_referenced_beam_number(dose_file)
            beam_number2 = get_referenced_beam_number(let_file)

            print(f"  Beam {beam_number1}{beam_number2}: Dose = {dose_value}, LET = {let_value}")


###############################################################################################
#
################################################################################################
def fetch_xnat_files(xnat_info, experiment_id, scan_id, resType, delete_after=False):
    subject_id = experiment_id.split('-')[0]
   
#    try:
#        xnat_session = xnat.connect(xnat_url, user=username, password=password)
#    except Exception a e:
#        print(f"Error connecting to XNAT: {e}")
#        return None

    get_xnat_session ( xnat_info )
    if xnat_info['session'] == None:
        return 

    project = xnat_info['session'].projects[xnat_info['project_id']]
    subject = project.subjects[subject_id]
    experiment = subject.experiments[experiment_id]

    scan = experiment.scans[scan_id]
    resources = scan.resources

        #if scan_id == '103' : type = 'secondary'
        #if scan_id == '104' : type = 'DICOM'

    experiment_dir = os.path.join(rootDir, experiment_id, 'SCANS', scan_id, resType)
    if not os.path.exists(experiment_dir):
       os.makedirs(experiment_dir)

    if resType in resources :
        structure_resource = resources[resType]
        files = structure_resource.files

        local_paths=[]
        for file in files:
            local_path = os.path.join(experiment_dir, file)
            if os.path.exists(local_path):
                if verbose>1 : print(f"File {local_path} already exists")
            else:
                if verbose>1 : print(f"Downloading {file} to {local_path}")
                structure_resource.files[file].download(local_path)
            local_paths.append(local_path)

        return local_paths

    return None

########################################################################################################    
#
########################################################################################################    
def find_highest_dose_voxel(summed_dose_grid):
    # Find the index of the maximum dose value
    max_index = np.argmax(summed_dose_grid)
#   print("map_index ", max_index)
    # Convert the flat index to 3D indices
    max_coords = np.unravel_index(max_index, summed_dose_grid.shape)
    return max_coords

########################################################################################################    
#
########################################################################################################    
def find_plan_directory(aplan):
#   return expDir
# Construct the expected directory path
    expDir = os.path.join(rootDir, aplan)

    # Check if the directory exists
    if not os.path.exists(expDir):
       print(f"{expdir} does not exist")
       quit()
        # If the directory does not exist, create a temporary directory
    #    temp_expDir = expDir.replace(rootDir, tempDir)
    #    os.makedirs(temp_expDir, exist_ok=True)  # Create the directory
    #    expDir = temp_expDir  # Update expDir to the temp directory

    return expDir
########################################################################################################    
#
########################################################################################################    
def find_voxel_spectra_files(expDir,type_histogram,beam=None):
   if verbose>0:print(f"find_voxel_spectra_files: expDir {expDir} beam {beam}")
   beam=str(beam)
   if beam == None or beam.lower() == 'all'  :
      search_pattern = expDir + "/SCANS/104/voxel_spectra/fdc*-beam*all*"+type_histogram+"-voxel-spectra.bin"
      if verbose > 2: print("search_pattern ", search_pattern)
      matching_files = glob.glob(search_pattern)
      if len(matching_files) == 0:
         search_pattern = expDir + "/SCANS/104/voxel_spectra/fdc*-beam*"+type_histogram+"-voxel-spectra.bin"
         matching_files = glob.glob(search_pattern)
         if verbose > 2 : 
            if verbose > 0: print(" search_pattern ", search_pattern)
            for file_path in matching_files:
               print(file_path)
      return matching_files
   else:
      search_pattern = expDir + "/SCANS/104/voxel_spectra/fdc*-beam*"+str(beam)+"*"+type_histogram+"-voxel-spectra.bin"
      if verbose > 2 : 
         print(" search_pattern ", search_pattern)
      matching_files = glob.glob(search_pattern)
      if verbose > 1 and len(matching_files) == 0:
         print(" Voxel spectra not found ")
      return matching_files


########################################################################################################    
#
########################################################################################################    
def plot_dose_slice(dicom_file, slice_index):
    # Load the DICOM RTDOSE file
    ds = pydicom.dcmread(dicom_file)

    # Get dose data
    dose_data = ds.pixel_array  # Assuming dose values are stored as pixel_array

    # Get slice thickness (assuming it's along the z-axis)
    slice_thickness = ds.GridFrameOffsetVector[1] - ds.GridFrameOffsetVector[0]

    # Plotting
    plt.figure(figsize=(8, 6))
    plt.imshow(dose_data[:, :, slice_index], cmap='jet', interpolation='nearest', origin='lower')
    plt.colorbar(label='Dose (Gy)')
    plt.title(f"Dose Distribution - Slice {slice_index} (z = {slice_index * slice_thickness} mm)")
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.show()
########################################################################################################    
#
########################################################################################################    
def plot_accumulated_dose(dicom_files, slice_index):
    accumulated_dose, slice_thickness = accumulate_dose_from_files(dicom_files)

    # Plotting
    plt.figure(figsize=(8, 6))
    plt.imshow(accumulated_dose[:, :, slice_index], cmap='jet', interpolation='nearest', origin='lower')
    plt.colorbar(label='Accumulated Dose (Gy)')
    plt.title(f"Accumulated Dose Distribution - Slice {slice_index} (z = {slice_index * slice_thickness} mm)")
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.show()
########################################################################################################    
#
########################################################################################################    
def read_bin_spectra(file_name):
    if verbose>0:print(f"reading new histo structure file_name {file_name} ")
    histos = {}
    delta_e = 0

    with open(file_name, 'rb') as fin:
        # Read the number of voxels in structures

# Read the 4 bytes and unpack them as a 4-character string
        file_type = struct.unpack('4s', fin.read(4))[0]
        file_type = file_type.decode('utf-8')
        # Read deltaE
        n_voxels_in_structures = struct.unpack('i', fin.read(4))[0]
        if verbose>1: print(f'nVoxelsInStructures: {n_voxels_in_structures}')

        h_min   = struct.unpack('f', fin.read(4))[0]
        delta_e = struct.unpack('f', fin.read(4))[0]

        if verbose>1: print(f'deltaE: {delta_e}')
        # Read arrayStruct
        array_struct = struct.unpack(f'{n_voxels_in_structures}i', fin.read(n_voxels_in_structures * 4))
        #print("array_struct ", array_struct)
        # Read spectraPointers
        spectra_pointers = struct.unpack(f'{n_voxels_in_structures}i', fin.read(n_voxels_in_structures * 4))
        # Read histograms
        counter=0
        for i in range(n_voxels_in_structures):
            #print("i ", i, "spectra_pointers ", spectra_pointers[i])
            if spectra_pointers[i] > 0:
                fin.seek(spectra_pointers[i])
                n_entries = struct.unpack('i', fin.read(4))[0]
                dose      = struct.unpack('f', fin.read(4))[0]
                let       = struct.unpack('f', fin.read(4))[0]
                n_bins    = struct.unpack('i', fin.read(4))[0]
                #print(f"array_struct {array_struct[i]} n_entries {n_entries} dose {dose} let {let} n_bins {n_bins}")
                if n_bins < 1: continue

                entries = struct.unpack(f'{n_bins}i', fin.read(n_bins * 4))
                histo =voxelSpectrum(array_struct[i],h_min, delta_e, n_bins, n_entries, entries, dose,let)
                histos[array_struct[i]]=histo
                counter=counter+1
                #print("read_bin_spectra, pointer index dose let entries ", spectra_pointers[i], histo.index, histo.dose, histo.let, histo.entries)

    #print(f"n_voxels_in_structures {n_voxels_in_structures} counter {counter}")

    return histos
################################################################################################
#
################################################################################################
def upload_file_to_xnat(xnat_session, project_id, experiment_id, scan_id, resource, file_name):
    #scan = xnat_session.projects[project_id].subjects[subject_id].experiments[experiment_id].scans[scan_id]
    scan = xnat_session.projects[project_id].experiments[experiment_id].scans[scan_id]

    file_resource = scan.resources.get(resource)
    if file_resource is None:
        try:
           file_resource = scan.create_resource(resource)
        except Exception as e:
            try:
                file_resource = scan.resources.get(resource)
            except Exception as e:
               print(" problem creating resource ", e )

    try: 
       file_resource.upload(file_name, os.path.basename(file_name))
    except Exception as e:
       print(" problem ", e )
################################################################################################
#
################################################################################################
def write_bin_spectra(file_name, histos):
    with open(file_name, 'wb') as fout:
        # Write file type as 4 bytes string
        file_type = 'SPEC'.encode('utf-8')
        fout.write(struct.pack('4s', file_type))
        
        # Write the number of voxels in structures
        n_voxels_in_structures = len(histos)
        #print(f"n_voxels_in_structures {n_voxels_in_structures}")
        fout.write(struct.pack('i', n_voxels_in_structures))
        
        # Extract common h_min and delta_e from the first voxelSpectrum object
        h_min = next(iter(histos.values())).h_min
        delta_e = next(iter(histos.values())).delta_e
        fout.write(struct.pack('f', h_min))
        fout.write(struct.pack('f', delta_e))
        
        # Write arrayStruct
        array_struct = [voxel.index for voxel in histos.values()]
        fout.write(struct.pack(f'{n_voxels_in_structures}i', *array_struct))
        
        # Placeholder for spectraPointers
        spectra_pointers = [0] * n_voxels_in_structures
        pointer_offset_pos = fout.tell()
        fout.write(struct.pack(f'{n_voxels_in_structures}i', *spectra_pointers))
        
        # Write histograms and update spectraPointers
        spectra_pointers = []
        for voxel in histos.values():
            #print(f"voxel.n_bins {voxel.n_bins}")
            #print(f"voxel.entries {voxel.entries}")
            pointer_pos = fout.tell()
            spectra_pointers.append(pointer_pos)
            fout.write(struct.pack('i', voxel.n_entries))
            fout.write(struct.pack('f', voxel.dose))
            fout.write(struct.pack('f', voxel.let))
            fout.write(struct.pack('i', voxel.n_bins))
            entries_as_ints = [int(entry) for entry in voxel.entries]
            fout.write(struct.pack(f'{voxel.n_bins}i', *entries_as_ints))
        
        # Go back and write the actual pointers
        fout.seek(pointer_offset_pos)
        fout.write(struct.pack(f'{n_voxels_in_structures}i', *spectra_pointers))
       
