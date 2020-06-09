# LEGO Racers 2 TDF Decoder

A script to split a TERRDATA.TDF file into its components

## How to run

`pip install -r requirements.txt`

`python tdf_loader.py`

## TDF information

[RockRaidersUnited thread](https://www.rockraidersunited.com/topic/8171-tdf-terrain-format/) about the TDF format. I used the script in this thread as a basis for my explorations.

### Overview:

The terrain is divided into 1024 (32x32) tiles.

There are 4 levels of detail, and each tile's surface consists of a grid of 17x17, 9x9, 5x5 and 3x3 vertices, with each grid popping in and out of view depending on how far you are from it. They can be edited separately.

Each vertex consists of a height, 3 bytes for a normal map, and 3 bytes which determine texture blending.

Here is the format for each 8 byte vertex

```
01 2 3 4 5 6 7
h  b b b b b b
```

* The first two bytes are a 16 bit integer heightmap

* The next three bytes are the x, y, and z (Y up, like OBJ) channels of a normal map

* The next byte is... weird. The top and bottom bits are set if the vertex is to be removed (like for cave entrances) and the 6 bits in between look like a jumbled version of the skybox texture

* the following two bytes are each divided into two four-bit maps, presumably for texture blending. I'm wondering if this has anything to do with the `TERRAIN LAYERS.MIP` file

