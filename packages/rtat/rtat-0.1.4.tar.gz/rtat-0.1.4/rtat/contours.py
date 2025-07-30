import cv2 
import numpy as np
import matplotlib.pyplot as plt
import os
import pydicom
from pydicom.uid import generate_uid
from pydicom.dataset import Dataset
import sys
from tqdm import tqdm



verbose=0


def delete_roi_by_name(ds, roi_name_to_delete):
    """
    Deletes ROI from StructureSetROISequence and ROIContourSequence by name.

    Parameters:
        ds (Dataset): The RT Structure Set DICOM dataset.
        roi_name_to_delete (str): The name of the ROI to delete.

    Returns:
        Dataset: Modified DICOM dataset with ROI removed.
    """
    # Step 1: Identify ROINumber(s) to delete
    roinumbers_to_delete = []
    if "StructureSetROISequence" in ds:
        updated_roi_seq = []
        for roi_item in ds.StructureSetROISequence:
            if roi_item.ROIName == roi_name_to_delete:
                roinumbers_to_delete.append(roi_item.ROINumber)
            else:
                updated_roi_seq.append(roi_item)
        ds.StructureSetROISequence = updated_roi_seq

    # Step 2: Remove matching ROIContourSequence items
    if "ROIContourSequence" in ds:
        updated_contour_seq = []
        for contour_item in ds.ROIContourSequence:
            if contour_item.ReferencedROINumber not in roinumbers_to_delete:
                updated_contour_seq.append(contour_item)
        ds.ROIContourSequence = updated_contour_seq

    # Step 2: Remove matching ROIContourSequence items
    if "RTROIObservationsSequence" in ds:
        updated_contour_seq = []
        for contour_item in ds.RTROIObservationsSequence:
            if contour_item.ReferencedROINumber not in roinumbers_to_delete:
                updated_contour_seq.append(contour_item)
        ds.RTROIObservationsSequence = updated_contour_seq

    return ds


def detect_density_drop(image, threshold=100):
    """
    Detects sudden drops in image density along the y-plane.

    Parameters:
        image (ndarray): Input 2D CT image.
        threshold (int): Threshold value for detecting density drop.

    Returns:
        list: List of tuples containing coordinates (x, y) where density drops occur.
    """
    density_drops = []
    yLoop = range(image.shape[1])
    #print("image.shape ", image.shape[1])
    #yLoop = [ 200 ]
    threshold=24
    jump=100
    for y in yLoop:
    #    print(" y ", y)
        column = image[:, y]
        #column = [x - threshold for x in column]
        #column.reverse()
        column = image[:, y].astype(np.int32)[::-1]
        adjusted = column - threshold
        diff = np.diff(adjusted)

        #print ("column ", column)
        #diff = np.diff(column)
        drop_indices = np.where(diff < -jump)[0]
        if len(drop_indices) > 0:
            lastIndex = 10000
            nLocal = 0;
            for index in drop_indices:
                #print(" index ",image.shape[0]-index," diff ", diff[index])
                if index - lastIndex == 1: 
                    density_drops.pop()                    
                    nLocal=nLocal-1
                density_drops.append((image.shape[0]-index, y))
                lastIndex = index 
                nLocal=nLocal+1
                if nLocal > 2 : break
    return density_drops

def detect_density_drop1(image, threshold=24, jump=10, max_drops_per_column=2):
    if image.ndim != 2:
        raise ValueError("Input must be a 2D image.")

    density_drops = []
    for y in range(image.shape[1]):
        column = image[:, y][::-1]  # Reverse directly
        adjusted = column - threshold
        diff = np.diff(adjusted)

        drop_indices = np.where(diff < -jump)[0]
        last_index = -1000
        drop_count = 0

        for idx in drop_indices:
            if idx - last_index == 1:
                density_drops.pop()
                drop_count -= 1
            density_drops.append((image.shape[0] - idx, y))
            last_index = idx
            drop_count += 1
            if drop_count >= max_drops_per_column:
                break

    return density_drops

def select_peak_position(image,density_drops):
    """
    Selects the position of the second peak from the histogram of y-values based on the condition specified.

    Parameters:
        density_drops (list): List of tuples containing average coordinates (x, y) of density drops.

    Returns:
        float: Position of the second peak.
    """
    y_values = [drop[0] for drop in density_drops]
    hist, bin_edges = np.histogram(y_values, bins=image.shape[1])
    
    # Find the position of the second peak from the highest value to the lowest above 30% of the maximum
    max_value = np.max(hist)
    threshold_value = 0.4 * max_value
    #print("max_value ",max_value," thresh ", threshold_value)
    second_peak_position = -1000000
    nPeaks = 0 ;
    lastPeak=100000000
    for i in range(len(hist)-1, -1, -1):
        #print(" i ", i, "bin ", bin_edges[i], "hist ", hist[i], " thres ", threshold_value)
        if hist[i] > threshold_value:
            second_peak_position = bin_edges[i]
            if abs(second_peak_position-lastPeak) > 50:
               nPeaks=nPeaks+1
               lastPeak=second_peak_position
               if nPeaks > 1 : 
                  break
    if verbose > 1 : print("second_peak_position ", second_peak_position) 
    return int(second_peak_position)

def plot_projection(image, density_drops):
    """
    Plots the projection along the y-plane and marks detected density drops.

    Parameters:
        image (ndarray): Input 2D CT image.
        density_drops (list): List of tuples containing coordinates (x, y) of density drops.
    """
 #   plt.figure(figsize=(10, 5))
 #   plt.imshow(image, cmap='gray')
 #   plt.title('CT Image with Density Drops along Y-Plane')
 #   plt.xlabel('Y')
 #   plt.ylabel('X')
 #   for drop in density_drops:
 #       plt.plot(drop[1], drop[0], 'ro')  # Mark density drops as red dots
 #   plt.show()

    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.imshow(image, cmap='gray')
    plt.title('CT Image with Density Drops')
    for drop in density_drops:
        plt.plot(drop[1], drop[0], 'ro')  # Mark density drops as red dots
    plt.xlabel('Y')
    plt.ylabel('X')

    # Plot y-projection
    plt.subplot(1, 2, 2)
    y_values = [drop[0] for drop in density_drops]
    plt.hist(y_values, bins=image.shape[1], color='blue', alpha=0.7)
    plt.title('Histogram of Y-Values of Density Drop Points')
    plt.xlabel('Y-Value')
    plt.ylabel('Frequency')

    plt.tight_layout()
    plt.show()


def exclude_below_line(image, line_y):
    """
    Creates a new image by excluding everything below the specified line.

    Parameters:
        image (ndarray): Input 2D CT image.
        line_y (int): Y-coordinate of the line.

    Returns:
        ndarray: New image with everything below the line excluded.
    """
    new_image = np.copy(image)
    new_image[line_y:, :] = 0
    return new_image

 
def pixel_to_world_coordinates(contour, dcm):
    # Get pixel spacing
    pixel_spacing = dcm.PixelSpacing
    if not pixel_spacing:
        raise ValueError("Pixel spacing information not found in DICOM file.")
    pixel_spacing_x, pixel_spacing_y = pixel_spacing

    # Get image position
    image_position = dcm.ImagePositionPatient
    if not image_position:
        raise ValueError("Image position information not found in DICOM file.")
    image_position_x, image_position_y, image_position_z = image_position

    # Get slice location
    slice_location = dcm.SliceLocation
    if slice_location is None:
        raise ValueError("Slice location information not found in DICOM file.")

    # Calculate z-coordinate based on slice location
    z_coord = image_position_z + (slice_location - image_position_z)

    # Convert contour points to world coordinates
    world_coordinates = []
    for point in contour:
        point1 = point[0]
        pixel_x, pixel_y = point1
        world_x = image_position_x + pixel_x * pixel_spacing_x
        world_y = image_position_y + pixel_y * pixel_spacing_y
        world_coordinates.append((world_x, world_y, z_coord))

    return world_coordinates

def get_contour(dcmFile):
    if verbose > 0: print(dcmFile)
    dcm = pydicom.dcmread(dcmFile)

    # Check if the SliceLocation attribute exists
    instance_number=0
    if hasattr(dcm, 'InstanceNumber'):
        instance_number = float(dcm.InstanceNumber)
    else:
        print("InstanceNumber not found.")

    # Check if the SliceLocation attribute exists
    instance_number=0
    if hasattr(dcm, 'InstanceNumber'):
        instance_number = float(dcm.InstanceNumber)
    else:
        print("InstanceNumber not found.")

    sopInstanceUID=0
    if hasattr(dcm, 'SOPInstanceUID'):
        sopInstanceUID = dcm.SOPInstanceUID
    else:
        print("InstanceNumber not found.")




    image = dcm.pixel_array

    # Detect density drops
    density_drops = detect_density_drop(image, threshold=50)
    #plot_projection(image, density_drops)


    # Select the position of the second peak
    second_peak_position = select_peak_position(image,density_drops)
    if ( second_peak_position < -10000 ): return instance_number, [], [], sopInstanceUID
    if verbose > 1 : print("Position of the second peak:", second_peak_position)

    new_image = exclude_below_line(image, second_peak_position-10)
    threshold_value = 800
    _, binary_image = cv2.threshold(new_image, threshold_value, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(binary_image.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #contours, _ = cv2.findContours(binary_image.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)

    min_area_threshold=400;
    filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) >= min_area_threshold]


    #print("contour ",contours)
# Find the largest contour based on area
    #plt.figure(figsize=(10, 5))
    #plt.imshow(new_image, cmap='gray')
    #plt.imshow(binary_image, cmap='gray')
    #plt.title('CT Image with Density Drops')
    #plt.xlabel('Y')
    #plt.ylabel('X')

    largest_contour=[]
    worldContour=[]
    if len(filtered_contours) > 0 :
       largest_contour = max(filtered_contours, key=cv2.contourArea)
       largest_contour_area = cv2.contourArea(largest_contour)
    
    # Calculate the center of the contour
       M = cv2.moments(largest_contour)
       if M["m00"] != 0:
          cx = int(M["m10"] / M["m00"])
          cy = int(M["m01"] / M["m00"])
       else:
          cx, cy = 0, 0
    
    # Check if the contour meets the conditions
       minDist = image.shape[1]/6
       if abs(cy - second_peak_position) >  minDist or cv2.contourArea(largest_contour) > 3000:
         largest_contour = np.append(largest_contour, [largest_contour[0]], axis=0)
         #plt.plot(largest_contour[:, 0, 0], largest_contour[:, 0, 1], color='blue', linewidth=2)
         #print("largest_contour ", largest_contour)
         worldContour = pixel_to_world_coordinates(largest_contour, dcm)
       else:
          print(" contour too close to couch cy ", cy, " couch ", second_peak_position, ' min Dist ', minDist)
          print(" contour area ", cv2.contourArea(largest_contour))
          largest_contour=[]
          worldContour=[]


    #plt.title('Contours on CT Image')
# Extract filename from the dcmFile path
    filename = os.path.splitext(os.path.basename(dcmFile))[0]

    # Define the directory to save the plot
    save_dir = "results"
    os.makedirs(save_dir, exist_ok=True)  # Create directory if it doesn't exist

    # Construct the filepath for saving the plot with the modified filename
    save_path = os.path.join(save_dir, filename + ".jpg")

    #plt.savefig(save_path)
    #plt.show(block=False)
    #plt.close()

    return instance_number, worldContour, largest_contour, sopInstanceUID
    
def check_contours_overlap(contour1, contour2):
    """
    Checks if two contours overlap.

    Parameters:
        contour1 (ndarray): First contour.
        contour2 (ndarray): Second contour.

    Returns:
        bool: True if contours overlap, False otherwise.
    """
    if contour1 is None or contour2 is None:
        return False
    
    # Your overlap check logic here...
    # For demonstrat/on, let's just check if the bounding rectangles overlap
    x1, y1, w1, h1 = cv2.boundingRect(contour1)
    x2, y2, w2, h2 = cv2.boundingRect(contour2)
    if (x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2):
        return True
    else:
        return False

def add_contours_to_rtstruct(rtstruct_path, contours):
    # Read the existing DICOM RTSTRUCT file
    rtstruct_ini = pydicom.dcmread(rtstruct_path)
    roi_to_remove = "BODY_A"
    rtstruct = delete_roi_by_name(rtstruct_ini, roi_to_remove)

    # Create a new Structure Set ROI for all contours
    highest_roi_number = max(int(item.ROINumber) for item in rtstruct.StructureSetROISequence)
    new_roi_sequence_item = Dataset()
    roi_name = "BODY_A"
    new_roi_sequence_item.ROINumber = highest_roi_number + 1
    new_roi_sequence_item.ROIName = roi_name
    new_roi_sequence_item.ROIGenerationAlgorithm = 'SEMIAUTOMATIC'
    if hasattr(rtstruct, 'ReferencedFrameOfReferenceSequence'):
        new_roi_sequence_item.ReferencedFrameOfReferenceUID = rtstruct.ReferencedFrameOfReferenceSequence[0].FrameOfReferenceUID
    else:
        print("Reference Frame not found") 

    rtstruct.StructureSetROISequence.append(new_roi_sequence_item)

    # Create a new ROIContourSequence for the new ROI
    new_roi_contour_sequence = Dataset()
    new_roi_contour_sequence.ReferencedROINumber = new_roi_sequence_item.ROINumber
    new_roi_contour_sequence.ROIDisplayColor = [255, 0, 0]  # RGB color for visualization

    # Iterate over contours and add contour sequences for each DICOM image
    contour_sequence = []
    for instance_number, contour, sopInstanceUID in contours:
        contour_data = Dataset()
        contour_data.ContourImageSequence = [Dataset()]
        # Fill in ReferencedSOPClassUID and ReferencedSOPInstanceUID with appropriate values
        contour_data.ContourImageSequence[0].ReferencedSOPClassUID = "CTImageStorage"
        contour_data.ContourImageSequence[0].ReferencedSOPInstanceUID = sopInstanceUID 
        #contour_data.ContourSequence = [Dataset()]
        contour_data.NumberOfContourPoints = len(contour)
        contour_data.ContourGeometricType = "CLOSED_PLANAR"
        contour_data.ContourData = [str(coord) for point in contour for coord in point]
        contour_sequence.append(contour_data)

    new_roi_contour_sequence.ContourSequence = contour_sequence

    # Append the new ROIContourSequence to the existing DICOM RTSTRUCT file
    if hasattr(rtstruct, 'ROIContourSequence'):
        rtstruct.ROIContourSequence.append(new_roi_contour_sequence)
    else:
        rtstruct.ROIContourSequence = [new_roi_contour_sequence]

        

        # Create a new RTROIObservationsSequence item
    new_observation = Dataset()

    new_observation.ObservationNumber = len(rtstruct.RTROIObservationsSequence) + 1 
    new_observation.ROIObservationLabel  = roi_name
    new_observation.ReferencedROINumber = new_roi_sequence_item.ROINumber
    new_observation.RTROIInterpretedType = "ORGAN"
    new_observation.ROIInterpreter = ""

# Append to RTROIObservationsSequence
    if hasattr(rtstruct, 'RTROIObservationsSequence'):
       rtstruct.RTROIObservationsSequence.append(new_observation)
    else:
       rtstruct.RTROIObservationsSequence = [new_observation]

    # Save the modified DICOM RTSTRUCT file
    new_file=rtstruct_path.replace('.dcm', '_modified.dcm')
    rtstruct.save_as(new_file)
    return new_file


def add_body_contour(ctsDir,strFileName):
    path    = ctsDir
    rtstruct_path = strFileName

    instance_3Dcontour_pairs = []
    instance_2Dcontour_pairs = []

    if os.path.isfile(path):
       instance_number, contour3D, contour2D, sopInstanceUID = get_contour(path)
       if len(contour2D) > 0 : instance_2Dcontour_pairs.append((instance_number, contour2D))
       #print("instance ",instance_number)
       #print("contour ",contour)
    elif os.path.isdir(path):
       file_list = os.listdir(path)
       for filename in tqdm(file_list, desc="Processing CT layers", unit="file"):
          if not filename.endswith(".dcm"):
             continue 
          file_path = os.path.join(path, filename)
          instance_number, contour3D, contour2D, sopInstanceUID = get_contour(file_path)
          if len(contour2D) > 0 : 
              instance_2Dcontour_pairs.append((instance_number, contour2D))
              instance_3Dcontour_pairs.append((instance_number, contour3D, sopInstanceUID))
          if verbose > 0 : print("instance ",instance_number)
    else:
        print("Invalid path:", path)

    instance_2Dcontour_pairs.sort(key=lambda x: x[0])
    if verbose > 1: print(instance_2Dcontour_pairs)

# Check for overlap between contours of contiguous instance numbers
    for i in range(len(instance_2Dcontour_pairs) - 1):
        current_instance_number, current_contour = instance_2Dcontour_pairs[i]
        next_instance_number, next_contour = instance_2Dcontour_pairs[i + 1]
        if check_contours_overlap(current_contour, next_contour):
            if verbose > 0 :
                print(f"Contours for instance numbers {current_instance_number} and {next_instance_number} overlap.")
        else:
            print(f"Contours for instance numbers {current_instance_number} and {next_instance_number} do not overlap.")

    return add_contours_to_rtstruct(rtstruct_path, instance_3Dcontour_pairs)
