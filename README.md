# line scan traces extractor
A small python tool to interactively extract time traces from functional imaging line scans. The Image data shape has to be `x = place` and `y = repetition` just as the following

![ ](https://github.com/grg2rsr/line_scan_traces_extractor/blob/master/example_scan.jpg  "Example Data")


## Usage
in a console, run 
`python interactive_trajectory_extractor.py <path_to_file>` to open two windows, one showing the raw data, and one showing the extracted trace based on 
+ a) mouse position 
+ b) ROI width

The ROI itself is shown as a box, and the width can be changed by scrolling the mouse wheel. The x span shown by the ROI is averaged and the time trace is previewed in a seperate figure.

alternatively, you can run 
`python interactive_trajectory_extractor.py <path_to_file> <start> <stop>` to automatically rescale the data to dF/F , using the lines between `start` and `stop` to calculate the background value

![ ](https://github.com/grg2rsr/line_scan_traces_extractor/blob/master/screenshot.png  "program screenshot")

Traces are extracted by clicking the the middle mouse button.

### Output
upon closing the windows, a `.csv` file is written with the following format
+ header: ROI number, starting at 0
+ x0: the start x coordinate of the ROI
+ x1: the end x coordinate of the ROI 
+ rest: each line y coordinate (line number) and corresponding value of each ROI 

happy slicing! Leave me a comment if you think a specific feature would be useful ...
