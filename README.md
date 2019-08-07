# Fan's automatic ANnotation tool (FAN tool)

FAN tool is developed by Fan to help automate SEM measurements. 

## Installation

1) Clone/download this repository.

2) In the repository, execute `pip install -r requirements.txt`.

3) Run python .\FAN.py

### Dependencies

opencv_python==4.1.0.25

pytesseract==0.2.7

numpy==1.16.4

Pillow==6.1.0

Python >= 3.5

### SEM image format

Prepare your SEM image according to format.jpg. 1024x768 recommended, the scalebar should be at the lower left corner. (Alternatively change the code to suit your perference)

### Usage
```
python FAN.py
```

1. Automatically reads the scalebar

2. Finds gap/layer thickness automatically

3. Label lines and save them

4. Calculate etch rate

Tested on:

Windows 10 64 bit + Python64 3.7.4

### Todos/known bugs

1. Auto scallop (find scallop size of Bosch process) not yet implemented

2. Draw line/annotation sometimes have a glitch

3. Clear All button sometimes does not work

4. Needs a high contract to identify gaps/layers - can be tuned by adjusting the threshold 

### Acknowledgments

1) inspired by and borrowed some GUI code from [https://github.com/virajmavani/semi-auto-image-annotation-tool]

