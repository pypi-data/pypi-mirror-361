import csv
import glob
import matplotlib.pyplot as plt
import netrc
import numpy as np
import os
import pydicom
import pymysql
from pyxnat import Interface
import pandas as pd
from skimage.draw import polygon
from skimage.transform import resize
import sys
from scipy import interpolate
from tqdm import tqdm
import xnat


verbose=0

rootDir="/data/projects/RCR03-400/experiments"
xnat_url = 'https://xnat.rice.edu'
project_id = 'RCR03-400'
base_dir = '/xnat/'+project_id+'/experiments'
tempDir = '/tmp'
strScanId="103"
verbose=0

################################################################################################
#
################################################################################################
def calculate_dosimetric_indices(structures, indices, dvh_dir):
    results = {}
    warnings = []

    for structure in structures:
        file_path = os.path.join(dvh_dir, f'{structure}.csv')

        if not os.path.isfile(file_path):
            warnings.append(f"Warning: Structure {structure} not found")
            continue

        # Read the DVH data
        df = pd.read_csv(file_path)
        #print(structure," df ", df)

        # Ensure the CSV has the required columns
        if df.shape[1] < 2:
            warnings.append(f"Warning: File for {structure} is improperly formatted")
            continue

        mask = df['volume'] != df['volume'].shift(1)
        # Filter the DataFrame using the mask
        d_df = df[mask]
        if verbose>10: print(d_df)
        d_dose = d_df.iloc[:, 0].values
        d_volume = d_df.iloc[:, 1].values

        mask = df['dose'] != df['dose'].shift(1)
        # Filter the DataFrame using the mask
        v_df = df[mask]
        if verbose>10: print(d_df)
        v_dose   = d_df.iloc[:, 0].values
        v_volume = d_df.iloc[:, 1].values


        # Initialize a dictionary to hold the results for the current structure
        structure_results = {}

        for index in indices:
            if index.lower() == 'mean':
                vv_dose = np.array(v_dose)
                vv_volume = np.array(v_volume)
                dose_bin_centers = (vv_dose[:-1] + vv_dose[1:]) / 2
                dd_volume = -np.diff(v_volume)
                total_dose = np.sum(dose_bin_centers * dd_volume)
                total_volume = np.sum(dd_volume)
                mean_dose = round(total_dose / total_volume,3)
                structure_results[index] = mean_dose
            elif index.lower() == 'min':
                vv_dose = np.array(v_dose)
                structure_results[index] = round(np.min(vv_dose[1:]),3) if vv_dose.size > 0 else 0
            elif index.lower() == 'max':
                vv_dose = np.array(v_dose)
                structure_results[index] = round(np.max(vv_dose),3) if vv_dose.size > 0 else 0
            elif index.startswith('D'):
                # Dose at specified volum
                volume_level = float(index[1:])
                try:
                    # Interpolating the dose at the given volume level
                    spline_interpolator = interpolate.PchipInterpolator(d_volume[::-1], d_dose[::-1])
                    interpolated_dose = spline_interpolator(volume_level)
                    structure_results[index] = round(interpolated_dose.item(),3)
                except Exception as e:
                    warnings.append(f"Warning: Unable to calculate {index} for {structure} because {e}")
            elif index.startswith('V'):
                # Volume at specified dose
                dose_level = float(index[1:])
                try:
                    # Interpolating the volume at the given dose level
                    spline_interpolator = interpolate.PchipInterpolator(d_dose, d_volume)
                    interpolated_volume = spline_interpolator(dose_level)
                    structure_results[index] = round(interpolated_volume.item(),3)
                except Exception as e:
                    warnings.append(f"Warning: Unable to calculate {index} for {structure}")
            else:
                warnings.append(f"Warning: Invalid index {index}")

        # Add the results for the current structure to the main results dictionary
        results[structure] = structure_results
        if verbose>2:print("Results:")
        if verbose>2:print(results)

    return results, warnings

################################################################################################
#
################################################################################################
def calculate_dvh(structures, dose_grid, dose_origin, dose_spacing, selected_structures=None):
    dvh_data = {}
    dose_bins = np.arange(0, np.max(dose_grid) + 1, .1)

    # Initialize the progress bar
    progress_bar = tqdm(structures.items(), desc="Calculating DVH", unit="structure")

    for structure_name, contours in progress_bar:
        if structure_name == "none" : continue
        if verbose>1: print("structure ", structure_name )
        if selected_structures and structure_name not in selected_structures:
            continue

        structure_mask = np.zeros(dose_grid.shape, dtype=np.uint8)

        for contour in contours:
            contour_points = (contour - dose_origin) / dose_spacing 
            contour_points = np.rint(contour_points).astype(int)

            for z in np.unique(contour_points[:, 2]):
                slice_contour = contour_points[contour_points[:, 2] == z]
                if slice_contour.shape[0] > 0:
                    rr, cc = polygon(slice_contour[:, 1], slice_contour[:, 0], structure_mask.shape[:2])
                    try:
                        structure_mask[int(z), rr, cc] = 1
                    except IndexError:
                        continue

        if structure_mask.shape != dose_grid.shape:
            structure_mask = resize(structure_mask, dose_grid.shape, preserve_range=True, order=0).astype(np.uint8)

        structure_dose = dose_grid[structure_mask > 0]
        histogram, _ = np.histogram(structure_dose, bins=dose_bins)
        if verbose > 4:
           print(structure_name, "min structure_dose ", np.min(structure_dose))
           print(structure_name, "max structure_dose ", np.max(structure_dose))
           print(structure_name, "mean structure_dose ", np.mean(structure_dose))
           print("histogram ", histogram )
        volume_histogram = np.cumsum(histogram[::-1])[::-1] / np.sum(histogram) * 100.0

        dvh_data[structure_name] = {
            'dose': dose_bins[:-1],
            'volume': volume_histogram,
        }

    return dvh_data

################################################################################################
#
################################################################################################
def fetch_dvhs_from_xnat(xnat_session, project_id, subject_id, experiment_id, scan_id):
    try:
        scan = xnat_session.projects[project_id].subjects[subject_id].experiments[experiment_id].scans[scan_id]
        dvh_resource = scan.resources.get('dvhs')
        if dvh_resource is None:
            raise Exception(f"No 'dvhs' resource found for scan {scan_id}")

        
        # Download DVH files to a temporary directory

        dvh_dir=os.path.join(base_dir,experiment_id,"SCANS",scan_id,"dvhs")
        #os.makedirs(dvh_dir, exist_ok=True)
        if verbose>2: print("before download base_dir ", base_dir, " dvh_dir ",dvh_dir)
        dvh_resource.download_dir(base_dir)
        #dvh_resource.download_dir(dvh_dir)

        return dvh_dir

    except Exception as e:
        print(f"Failed to fetch DVHs from XNAT: {e}")
        return None
################################################################################################
#
################################################################################################
def get_dosimetric_indices(experiment_id, scan_id, structures, indices):
    dvh_dir = get_dvh_directory ( xnat_url, experiment_id, scan_id )

    return calculate_dosimetric_indices(structures, indices, dvh_dir)

################################################################################################
#
################################################################################################
def get_dvh_directory ( xnat_url, experiment_id, scan_id ):

    dvh_dir = os.path.join(base_dir, experiment_id, 'SCANS', scan_id, 'dvhs')
    if os.path.exists(dvh_dir):
        return dvh_dir
    else:
        get_dvhs ( xnat_url, experiment_id, scan_id )
        return dvh_dir


################################################################################################
#
################################################################################################
def get_xnat_files(xnat_session, experiment_id, scan_id, resType, delete_after=False):
    subject_id = experiment_id.split('-')[0]
   
#    try:
#        xnat_session = xnat.connect(xnat_url, user=username, password=password)
#    except Exception a e:
#        print(f"Error connecting to XNAT: {e}")
#        return None

    try:
        project = xnat_session.projects[project_id]
        subject = project.subjects[subject_id]
        experiment = subject.experiments[experiment_id]

        scan = experiment.scans[scan_id]
        resources = scan.resources

        #if scan_id == '103' : type = 'secondary'
        #if scan_id == '104' : type = 'DICOM'

        experiment_dir = os.path.join(tempDir, experiment_id, 'SCANS', scan_id, resType)
        if not os.path.exists(experiment_dir):
           os.makedirs(experiment_dir)

        if resType in resources :
            structure_resource = resources[resType]
            files = structure_resource.files

            local_paths=[]
            for file in files:
                local_path = os.path.join(experiment_dir, file)
                if os.path.exists(local_path):
                    if verbose>0 : print(f"File {local_path} already exists")
                else:
                    if verbose>0 : print(f"Downloading {file} to {local_path}")
                    structure_resource.files[file].download(local_path)
                local_paths.append(local_path)

            return local_paths

    except KeyError as e:
        print(f"Key error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return None
################################################################################################
#
################################################################################################
def get_structure_names(file_path):
    if not os.path.exists(file_path):
        print(f"file {file_path} does not exist")
        return []

    structure_names = []
    try:
        dicom_data = pydicom.dcmread(file_path)
        if hasattr(dicom_data, 'rtroiobservationssequence'):
            for item in dicom_data.rtroiobservationssequence:
                if hasattr(item, 'roiobservationlabel'):
                    structure_names.append(item.roiobservationlabel)
    except Exception as e:
        print(f"error reading dicom file {file_path}: {e}")
    return structure_names

################################################################################################
#
################################################################################################
def download_dicom_files(scan, output_folder):
    resources = scan.resources().get()
    for resource in resources:
        files = scan.resource(resource).files().get()
        for f in files:
            file_path = scan.resource(resource).file(f).get_copy(os.path.join(output_folder, f))
            print(f'downloaded {f} to {file_path}')
    return output_folder
################################################################################################
#
################################################################################################
def get_dvhs ( xnat_url, experiment_id, scan_id ):

    output_dir=os.path.join(base_dir,experiment_id,"SCANS",scan_id,"dvhs")
    if os.path.isdir(output_dir):
        dvh_files = glob.glob(output_dir+"/*")
        dvh_data = read_dvh_from_csv(dvh_files)
        return dvh_data

    try:
        xnat_session = xnat.connect(xnat_url)
    except Exception as e:
       print(f"Error connecting to XNAT: {e}")
       quit()

    subject_id = experiment_id.split('-')[0]
    #dvhs_dir = fetch_dvhs_from_xnat(xnat_session, project_id, subject_id, experiment_id, strScanId)
    if verbose>1: print("going to get dvhs from xnat")
    dvh_files = get_xnat_files(xnat_session,experiment_id,scan_id,"dvhs")
    if verbose>1: print("dvh_files ",dvh_files)
    if dvh_files is not None and len(dvh_files) > 0 : 
        dvh_data = read_dvh_from_csv(dvh_files)
        xnat_session.disconnect()
        return dvh_data

    if verbose> 0 : print("xnat_session ", xnat_session)

    str_files = get_xnat_files(xnat_session,experiment_id,strScanId,"secondary")
    if verbose>1: print("str_files ", str_files)
#    dose_files = [os.path.join(dose_folder, f) for f in os.listdir(dose_folder) if f.endswith('.dcm')]
    dos_files = get_xnat_files(xnat_session,experiment_id,scan_id,"DICOM")
    if verbose>1: print("dos_files ", dos_files)
    if dos_files == None: 
        print ("Dose files not found ")
        return []

    structures = load_structure_set(str_files)
    dose_grid, dose_origin, dose_spacing = load_info_grid(dos_files)

    selected_structures = []
    # Calculate DVH
    dvh_data = calculate_dvh(structures, dose_grid, dose_origin, dose_spacing, selected_structures)
    output_dir = save_dvh_to_csv(dvh_data,experiment_id,scan_id)
 
    subject_id = experiment_id.split('-')[0]
    upload_dvhs_to_xnat(xnat_session, project_id, subject_id, experiment_id, scan_id, output_dir)

    if xnat_session:
        xnat_session.disconnect()


    return dvh_data
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
                if contour_data:
                    structures[roi_contour.ReferencedROINumber] = contour_data

        if hasattr(ds, 'StructureSetROISequence'):
            for roi in ds.StructureSetROISequence:
                roi_number = roi.ROINumber
                roi_name = roi.ROIName
                if roi_number in structures:
                    structures[roi_name] = structures.pop(roi_number)

    return structures
################################################################################################
#
################################################################################################
def load_info_grid(dose_files):
    dose_data = [pydicom.dcmread(dose_file) for dose_file in dose_files]
    #print("dose_data ", dose_data)
    reference_shape = dose_data[0].pixel_array.shape
    dose_grid = np.zeros(reference_shape, dtype=np.float64)

    for dose_file in dose_data:
        pixel_array = dose_file.pixel_array
        if pixel_array.shape != reference_shape:
            pixel_array = resize(pixel_array, reference_shape, mode='edge', preserve_range=True)
        #print("dose_file ", dose_file)
        dose_grid += pixel_array * dose_file.DoseGridScaling

    dose_grid = dose_grid.astype(np.float64)
    dose_grid[dose_grid < 0] = 0

    dose_origin = np.array(dose_data[0].ImagePositionPatient)
    pixel_spacing = list(dose_data[0].PixelSpacing)
    slice_thickness = dose_data[0].GridFrameOffsetVector[1] - dose_data[0].GridFrameOffsetVector[0]
    dose_spacing = np.array(pixel_spacing + [slice_thickness])
    if verbose>1: print("dose_spacing ", dose_spacing)

    return dose_grid, dose_origin, dose_spacing
################################################################################################
#
################################################################################################
def load_let_grid(dose_files, let_files):
    dose_data = [pydicom.dcmread(dose_file) for dose_file in dose_files]
    reference_shape = dose_data[0].pixel_array.shape

    let_data = [pydicom.dcmread(let_file) for let_file in let_files]
    let_reference_shape = let_data[0].pixel_array.shape
    if let_reference_shape != reference_shape:
        print("LET and Dose have differetn reference shapes")
        return None



    let_grid = np.zeros(reference_shape, dtype=np.float64)

    for dose_file in dose_data:
        pixel_array = dose_file.pixel_array
        if pixel_array.shape != reference_shape:
            pixel_array = resize(pixel_array, reference_shape, mode='edge', preserve_range=True)
        #print("dose_file ", dose_file)
        dose_grid += pixel_array * dose_file.DoseGridScaling

    dose_grid = dose_grid.astype(np.float64)
    dose_grid[dose_grid < 0] = 0

    dose_origin = np.array(dose_data[0].ImagePositionPatient)
    pixel_spacing = list(dose_data[0].PixelSpacing)
    slice_thickness = dose_data[0].GridFrameOffsetVector[1] - dose_data[0].GridFrameOffsetVector[0]
    dose_spacing = np.array(pixel_spacing + [slice_thickness])
    if verbose>1: print("dose_spacing ", dose_spacing)

    return dose_grid, dose_origin, dose_spacing
################################################################################################
#
################################################################################################
def plot_dvhs_structures(exp_id, scan_id, structures, dis=None):
    dvh_dir=get_dvh_directory(xnat_url,exp_id, scan_id)

    dvh_files =[]
    for structure in structures:
        fname=structure.replace(" ", "_")
        fname=fname.replace("[", "_")
        fname=fname.replace("]", "_")
        fname=fname.replace("/", "_")
        filename = os.path.join(dvh_dir, f'{fname}.csv')
        if not os.path.exists(filename):
            print(filename," does not exist ")
            continue
        dvh_files.append(filename)
    dvh_data = read_dvh_from_csv(dvh_files)
    if len(dvh_data)<1:
        print(" No structure data, nothing to plot ")
        return 

    plt.figure(figsize=(10, 6))
    for key, value in dvh_data.items():
        plt.plot(value['dose'],value['volume'],label=key)

    if dis is not None:
       vPoints=[]
       dPoints=[]
       for structure, value in dis.items():
        for di, divalue in value.items():
            if di.startswith('D'):
                dPoints.append((divalue,float(di[1:])))
            elif di.startswith('V'):
                vPoints.append((float(di[1:]),divalue))
            else:
                if verbose>0: print("wrong dosimetric index ", di)
                continue
        # Plot DXX points as dots
            for dose, volume in dPoints:
               plt.plot(dose, volume, 'ro')  # 'ro' means red dots
               plt.text(dose, volume, f'D{volume}', color='red', fontsize=8)

        # Plot VXX points as dots
            for dose, volume in vPoints:
                plt.plot(dose, volume, 'bo')  # 'bo' means blue dots
                plt.text(dose, volume, f'V{dose}', color='blue', fontsize=8)
            


    plt.xlabel('Dose (Gy)')
    plt.xlabel('Dose (Gy)')
    plt.ylabel('Volume (%)')
    plt.title('DVHs from XNAT')
    plt.legend()
    plt.grid(True)
    plt.show()

################################################################################################
#
################################################################################################
def plot_dvhs(dvhs):
    plt.figure(figsize=(10, 6))
    for key, value in dvhs.items():
        plt.plot(value['dose'],value['volume'],label=key)


    plt.xlabel('Dose (Gy)')

    plt.xlabel('Dose (Gy)')
    plt.ylabel('Volume (%)')
    plt.title('DVHs from XNAT')
    plt.legend()
    plt.grid(True)
    plt.show()
################################################################################################
#
################################################################################################
def read_dvh_from_csv(dvh_files):
    dvh_data = {}  # Initialize an empty dictionary to store DVH data

    for filename in dvh_files:
        if filename.endswith(".csv"):
            structure_name = os.path.basename(filename)  # Remove the ".csv" extension
            structure_name = os.path.splitext(structure_name)[0]  # Remove the ".csv" extension
            structure_name = structure_name.replace("_", " ")  # Restore original structure name
            #filepath = os.path.join(output_dir, filename)
            with open(filename, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                dose_values, volume_values = [], []
                for row in reader:
                    dose_values.append(float(row['dose']))
                    volume_values.append(float(row['volume']))

                dvh_data[structure_name] = {'dose': dose_values, 'volume': volume_values}

    return dvh_data
################################################################################################
#
################################################################################################
def save_dvh_to_csv(dvh_data, experiment_id,scan_id):
    output_dir=os.path.join(tempDir,experiment_id,"SCANS",scan_id,"dvhs")
    if verbose>1 :print("output_dir ", output_dir)
    os.system("mkdir -p "+output_dir)

    for structure_name, dvh in dvh_data.items():
        fname=structure_name.replace(" ", "_")
        fname=fname.replace("[", "_")
        fname=fname.replace("]", "_")
        fname=fname.replace("/", "_")
        filename = os.path.join(output_dir, f'{fname}.csv')
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['dose', 'volume']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            reachedZero=0
            for dose, volume in zip(dvh['dose'], dvh['volume']):
                writer.writerow({'dose': round(dose,6), 'volume': round(volume,6)})
                if reachedZero == 1 : break
                if volume == 0 : reachedZero=1
    return output_dir
################################################################################################
#
################################################################################################
def upload_dvhs_to_xnat(xnat_session, project_id, subject_id, experiment_id, scan_id, dvh_dir):
    scan = xnat_session.projects[project_id].subjects[subject_id].experiments[experiment_id].scans[scan_id]

    dvh_resource = scan.resources.get('dvhs')
    if dvh_resource is None:
        try:
           dvh_resource = scan.create_resource('dvhs')
        except Exception as e:
            try:
                dvh_resource = scan.resources.get('dvhs')
            except Exception as e:
               print(" problem creating resource ", e )

    for file_name in os.listdir(dvh_dir):
        file_path = os.path.join(dvh_dir, file_name)
        try: 
           dvh_resource.upload(file_path, file_name)
        except Exception as e:
            print(" problem ", e )



