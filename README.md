# Cell-Level Intensity Quantification and Classification

This script processes segmentation masks (from StarDist_2D) to:

- Measure **mean fluorescence intensity** per cell across channels (C2, C3, C4)
- Classify cells as **positive or negative** using the Triangle thresholding method
- Generate:
  - `.csv` tables with per-cell intensity + positivity
  - Histograms showing threshold decisions
  - Binary masks highlighting positive cells

---

##  Input Structure

- **Segmentation masks**: `_filtered.tif` files (labeled masks with unique cell IDs)  
- **Channel images**: raw fluorescence TIFFs with `"C2"`, `"C3"`, `"C4"` in filenames

### Example:

```text
/medial_stardist_filtered/
├── sample1_C1_filtered.tif   ← labeled mask
├── sample1_C2.tif            ← fluorescence channel
├── sample1_C3.tif
├── sample1_C4.tif
