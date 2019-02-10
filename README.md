## Overnight Owls attempt to find the Bubbles

### Addressing [3D and 2D Bubbles in Rock](https://github.com/amnh/HackTheSolarSystem/wiki/3D-and-2D-Bubbles-In-Rock)

### Created by Overnight Owls
* [Jesse Spielman](http://github.com/heavyimage)
* [Ian Thompson](http://github.com/quornian)
* [Liz Yang](http://github.com/lizranyang)
* [Mohamed Echkouna](http://github.com/echkouna)

### Solution Description

Include in this repository are a few different bits and pieces from our project

1) Nuke scripts for creating the harder bubble edges from Dr. Ebel's CT scans

2) A "Blobber" Python/Qt tool for exploring the 16bit dataset (data not included in this repo)

3) ...

### Installation Instructions

#### Blobber

Requires: Python3, PyQt5, PIL (or Pillow), Numpy

The 16-bit sequence dataset must be downloaded and placed in the relative path:

    Sem2_Z_16a/Sem2_Z_16a_0000.tif
    Sem2_Z_16a/Sem2_Z_16a_0001.tif
    ...
    Sem2_Z_16a/Sem2_Z_16a_0350.tif

A small edit to python/blobber.py will allow different sequences to be used.

 - Change the path
 - Set the _max_x and _max_y to the resolution
 - Set the _min_z and _max_z values to match the frame sequence


