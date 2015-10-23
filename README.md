# line scan traces extractor
A small python tool to interactively extract time traces from functional imaging line scans. The Image data shape has to be `x = place` and `y = repetition` just as the following

## Usage
in a console, run 
`python interactive_trajectory_extractor.py <path_to_file>` to open two windows, one showing the raw data, and one showing the extracted trace based on a) mouse position b) ROI width. The ROI itself is shown as a box, and the width can be changed by scrolling the mouse wheel. The x span shown by the ROI is averaged and the time trace is previewed in a seperate figure.

alternatively, you can run 
`python interactive_trajectory_extractor.py <path_to_file> <start> <stop>` to automatically rescale the data to dF/F , using the lines between `start` and `stop` to calculate the background value

### output
upon closing the windows, a `.csv` file ws written with the x0:x1 coordinates of the ROI as the first two lines after the header (which just contains the order of clicks from 0 on)

happy slicing!
