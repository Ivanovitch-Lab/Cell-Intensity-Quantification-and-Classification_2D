import os
import numpy as np
import pandas as pd
from tifffile import imread
from skimage.measure import regionprops_table, label
import matplotlib.pyplot as plt
from skimage.filters import threshold_triangle

# Folders
mask_folder = r"C:\Users\ucklkdi\OneDrive - University College London\Desktop\transfer 10_6_25\medial_stardist_filtered"
image_folder = r"C:\Users\ucklkdi\OneDrive - University College London\Desktop\transfer 10_6_25\medial"
output_folder = mask_folder  # CSVs will be saved here

channels = ["C2", "C3", "C4"]

for mask_file in os.listdir(mask_folder):
    if not mask_file.endswith("_filtered.tif"):
        continue

    base = mask_file.replace("_filtered.tif", "")
    mask_path = os.path.join(mask_folder, mask_file)
    mask = imread(mask_path)

    # Prepare a DataFrame to store results
    df = pd.DataFrame()
    df['ID'] = np.unique(mask)[1:]  # skip background (ID 0)

    for ch in channels:
        # Find corresponding image file
        image_file = base.replace("C1", ch) + ".tif"
        image_path = os.path.join(image_folder, image_file)
        if not os.path.exists(image_path):
            print(f"Missing channel image: {image_path}")
            df[f"mean_{ch}"] = np.nan
            continue

        img = imread(image_path)
        if img.ndim > 2:
            img = img[..., 0]

        # Get mean intensity for each region
        props = regionprops_table(mask, intensity_image=img, properties=['label', 'mean_intensity'])
        mean_int = np.array(props['mean_intensity'])
        # Align with IDs in df
        df = df.merge(pd.DataFrame({'ID': props['label'], f'mean_{ch}': mean_int}), on='ID', how='left')

        # Threshold using Otsu's method
        try:
            thresh = threshold_triangle(mean_int)
        except ValueError:
            thresh = np.nan
        df[f'positive_{ch}'] = (df[f'mean_{ch}'] > thresh).astype(int)

        # Plot histogram and threshold
        plt.figure()
        plt.hist(mean_int, bins=30, alpha=0.7)
        if not np.isnan(thresh):
            plt.axvline(thresh, color='red', linestyle='--', label=f'Otsu threshold: {thresh:.2f}')
        plt.title(f"{base} {ch} mean intensity")
        plt.xlabel("Mean intensity")
        plt.ylabel("Cell count")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, f"{base}_{ch}_intensity_hist.png"))
        plt.close()

                # Save a binary mask image showing only positive cells for this channel
        positive_ids = df.loc[df[f'positive_{ch}'] == 1, 'ID'].values
        positive_mask = np.isin(mask, positive_ids).astype(np.uint16)
        pos_mask_path = os.path.join(output_folder, f"{base}_{ch}_positive_mask.tif")
        from tifffile import imwrite
        imwrite(pos_mask_path, positive_mask)

    # Save CSV
    csv_path = os.path.join(output_folder, f"{base}_intensities.csv")
    df.to_csv(csv_path, index=False)
    print(f"Saved: {csv_path}")