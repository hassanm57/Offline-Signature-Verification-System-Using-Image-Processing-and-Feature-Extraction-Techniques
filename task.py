from PIL import Image
import numpy as np
import os
from scipy.stats import linregress # for calculating the skew/slants angle

# load the signatures from folder - 25 signs and converting to B/W!!
def load_signatures(folder_path):
    images = []
    for i in range(1, 26):
        image_path = os.path.join(folder_path, f"R{i:03}.png")
        images.append(Image.open(image_path).convert("1"))
    return images

# Bounding box 
def get_bounding_box(img_np):
    height, width = img_np.shape
    left, right, top, bottom = width, 0, height, 0
    for y in range(height):
        for x in range(width):
            if img_np[y, x] == 0:  # Black pixel
                if x > right:
                    right = x
                if x < left:
                    left = x
                if y > bottom:
                    bottom = y
                if y < top:
                    top = y
    return left, right, top, bottom

# Centroid calculation
def get_centroid(img_np, bounding_box):
    left, right, top, bottom = bounding_box
    cx, cy, n = 0, 0, 0
    for y in range(top, bottom + 1):  # Include bottom row
        for x in range(left, right + 1):  # Include right column
            if img_np[y, x] == 0:  # This is code for detecting a BLACK pixel
                cx += x
                cy += y
                n += 1
    return (cx / n, cy / n) if n > 0 else (0, 0)

# Segmenting into 64 cells...

def split_image(img_np, left, right, top, bottom, depth=0):
    segments = []
    if depth < 3:  # depth = 3, equals 64 cells..
        cx, cy = get_centroid(img_np, (left, right, top, bottom))
        cx, cy = int(cx), int(cy)  

        # recursion used for splitting
        segments += split_image(img_np, left, cx, top, cy, depth + 1)
        segments += split_image(img_np, cx + 1, right, top, cy, depth + 1)
        segments += split_image(img_np, left, cx, cy + 1, bottom, depth + 1)
        segments += split_image(img_np, cx + 1, right, cy + 1, bottom, depth + 1)
    else:
        segments.append((left, right, top, bottom))
    return segments


# count black to white transitions
def count_black_to_white_transitions(img_np, segment):
    left, right, top, bottom = segment
    transitions = 0
    prev = img_np[top][left]  # Initial pixel (fixed indexing)
    for y in range(top, bottom + 1): 
        for x in range(left, right + 1):  
            curr = img_np[y][x]
            if curr == 1 and prev == 0:
                transitions += 1
            prev = curr
    return transitions

# Aspect ratio calculation 
def calculate_aspect_ratio(segment):
    left, right, top, bottom = segment
    width = right - left + 1   
    height = bottom - top + 1   
    return width / height if height != 0 else float('inf') 


# get features of each segment
def extract_features_from_cells(img_np, segments):
    centroids = []
    transitions = []
    aspect_ratios = []
    
    for segment in segments:
        cx, cy = get_centroid(img_np, segment)
        centroids.append((cx, cy))
        
        transitions.append(count_black_to_white_transitions(img_np, segment))
        
        aspect_ratios.append(calculate_aspect_ratio(segment))
    
    return centroids, transitions, aspect_ratios

# Compare transitions 
def compare_transitions_across_signatures(segments_transitions):
    num_signatures = len(segments_transitions)
    num_cells = len(segments_transitions[0])
    
    # list to display stable cells
    stable_cells = [True] * num_cells

    # Iterate over each cell and compare transitions across all signatures
    for cell_idx in range(num_cells):
        first_signature_transitions = segments_transitions[0][cell_idx]
        for sig_idx in range(1, num_signatures):
            if segments_transitions[sig_idx][cell_idx] != first_signature_transitions:
                stable_cells[cell_idx] = False
                break 
    
    return stable_cells

# save to files
def save_features_to_files(centroids, transitions, aspect_ratios, file_prefix):
   
    os.makedirs("Processed/Centroid", exist_ok=True)
    os.makedirs("Processed/Ratio", exist_ok=True)
    os.makedirs("Processed/Transitions", exist_ok=True)

    centroid_file_path = os.path.join("Processed", "Centroid", f"{file_prefix}_centroids.txt")
    np.savetxt(centroid_file_path, centroids, fmt="%.2f")

    transition_file_path = os.path.join("Processed", "Transitions", f"{file_prefix}_transitions.txt")
    np.savetxt(transition_file_path, transitions, fmt="%d")

    ratio_file_path = os.path.join("Processed", "Ratio", f"{file_prefix}_aspect_ratios.txt")
    np.savetxt(ratio_file_path, aspect_ratios, fmt="%.2f")



# calculate skew angle
def calculate_skew(img_np, segment):
    left, right, top, bottom = segment
    x_coords = []
    y_coords = []
    
    # Collect all black pixel coordinates
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            if img_np[y, x] == 0: 
                x_coords.append(x)
                y_coords.append(y)

    if len(x_coords) < 2: 
        return 0.0
    
    # Perform linear regression to find the slope
    slope, _, _, _, _ = linregress(x_coords, y_coords)
    skew_angle = np.degrees(np.arctan(slope))  # Convert slope to angle in degrees
    return skew_angle

# Calculating the slant angle
def calculate_slant(img_np, segment):
    left, right, top, bottom = segment
    slant_angles = []
    
    # collect vertical strokes
    for x in range(left, right + 1):
        start_y = None
        for y in range(top, bottom + 1):
            if img_np[y, x] == 0:
                if start_y is None:
                    start_y = y
            elif start_y is not None:
                # Calculate slant angle for this vertical stroke
                length = y - start_y
                slant_angle = np.degrees(np.arctan(length / (x - left + 1)))  # slant condition
                slant_angles.append(slant_angle)
                start_y = None

    if not slant_angles:
        return 0.0
    return np.mean(slant_angles)  # average of slant

# Compare skew/slant angles for stability across signatures

###def compare_angles_across_signatures(angles_list):
   # num_signatures = len(angles_list)
    #num_cells = len(angles_list[0])
    
   # stable_cells = [True] * num_cells
    
    #for cell_idx in range(num_cells):
     #   first_signature_angle = angles_list[0][cell_idx]
      #  for sig_idx in range(1, num_signatures):
        #    if abs(angles_list[sig_idx][cell_idx] - first_signature_angle) > 5:  # Threshold for stability
         #       stable_cells[cell_idx] = False
         #       break
    
    #return stable_cells

# save segments
def save_segmented_images(segments, img_np, folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    for idx, segment in enumerate(segments):
        left, right, top, bottom = segment
        segment_img = img_np[top:bottom+1, left:right+1]
        Image.fromarray(segment_img).save(os.path.join(folder, f"segment_{idx}.png"))

# feature extraction
def process_signatures(folder_path):
    signatures = load_signatures(folder_path)
    
    all_transitions = []
    for i, img in enumerate(signatures):
        img_np = np.array(img)
        img_height, img_width = img_np.shape
        
        # Split the image into 64 cells
        segments = split_image(img_np, 0, img_width - 1, 0, img_height - 1)
        
        centroids, transitions, aspect_ratios = extract_features_from_cells(img_np, segments)
        
        # save to text files
        file_prefix = f"signature_{i+1:03}"
        save_features_to_files(centroids, transitions, aspect_ratios, file_prefix)
        
        all_transitions.append(transitions)
        skews, slants = process_skew_and_slant(img_np, segments)
    
    # compare transitions
    stable_cells = compare_transitions_across_signatures(all_transitions)
    print("Stable cells:", stable_cells)

    # Save segments of images

    # save_segmented_images(segments, np.array(signatures[0]), "segmented_signatures")

def process_skew_and_slant(img_np, segments):
    skews = []
    slants = []
    
    for segment in segments:
        skew_angle = calculate_skew(img_np, segment)
        slant_angle = calculate_slant(img_np, segment)
        
        skews.append(skew_angle)
        slants.append(slant_angle)
        
        print(f"Skew angle for segment {segment}: {skew_angle:.2f} degrees")
        print(f"Slant angle for segment {segment}: {slant_angle:.2f} degrees")
    
    return skews, slants

# main pipeline...
folder_path = "H:/Lab ML/Reference"
# load_signatures(folder_path) # exclude/ignore this code, Ali

process_signatures(folder_path)

