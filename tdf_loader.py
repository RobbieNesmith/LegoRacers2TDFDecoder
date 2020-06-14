from struct import unpack
from os import path
import imageio
import numpy
import pathlib

CHUNK_SIZE = [17, 9, 5, 3]
NUM_CHUNKS = 32
VERTEX_OFFSET = [0x20, 0x242020, 0x2e4020, 0x316020]
PART_2_OFFSET = [0x328020, 0x34a020, 0x35c020, 0x366020]
WORLD_VERTEX_TOTAL = [x ** 2 * NUM_CHUNKS ** 2 for x in CHUNK_SIZE]
NUM_PARAMS = 7
MAX_INT = 2 ** 16

infilepath = input("path to TERRDATA.TDF: ")
outfilepath = input("path to directory for output images: ")
#RES = int(input("mipmap level (high res 0, 1, 2, 3 low res): "))

#infilepath = r'C:\Program Files\Games\LEGO Racers 2\GAMEDATA\GAME DATA\EDITOR GEN\TERRAIN\SANDY ISLAND\TERRDATA.TDF'
#infilepath = "/mnt/c/Program Files/Games/Lego Racers 2/GAMEDATA/GAME DATA/EDITOR GEN/TERRAIN/SANDY ISLAND/TERRDATA.TDF"
#infilepath = "/mnt/c/Program Files/Games/Lego Racers 2/GAMEDATA/GAME DATA/EDITOR GEN/TERRAIN/ADVENTURERS/TERRDATA.TDF"
#infilepath = "/mnt/c/Program Files/Games/Lego Racers 2/GAMEDATA/GAME DATA/EDITOR GEN/TERRAIN/LOM/OKSES_LOVECHILD/TERRDATA.TDF"

def render_heightmap(res):
    imgres = (CHUNK_SIZE[res] - 1) * NUM_CHUNKS + 1
    heightmap_arr = numpy.empty((imgres, imgres))
    normalmap_arr = numpy.empty((imgres, imgres, 3))
    params_arrs = [numpy.empty((imgres, imgres)) for i in range(NUM_PARAMS)]

    f = open(infilepath, "rb")
    f.seek(VERTEX_OFFSET[res])
    T = CHUNK_SIZE[res]
    for v in range(WORLD_VERTEX_TOTAL[res]):
        tile_y = (T - 1) * ((v // (T**2)) % NUM_CHUNKS)
        tile_x = (T - 1) * (v // (T**2 * NUM_CHUNKS))
        vert_y = ((v // T) % T)
        vert_x = (v % T)
        vertex_data = unpack("hbbbbbb", f.read(8))

        heightmap_arr[imgres - (vert_y + tile_y + 1)][vert_x + tile_x] = vertex_data[0]
        normalmap_arr[imgres - (vert_y + tile_y + 1)][vert_x + tile_x] = [vertex_data[1] + 127, vertex_data[3] + 127, vertex_data[2] + 127]

        # cut out sections
        params_arrs[0][imgres - (vert_y + tile_y + 1)][vert_x + tile_x] = 255 if (vertex_data[4] & 0b10000000) > 0 else 0

        # skybox texture but skewed?
        params_arrs[1][imgres - (vert_y + tile_y + 1)][vert_x + tile_x] = (vertex_data[4]) & 0b01111110

        # cut out sections again
        params_arrs[2][imgres - (vert_y + tile_y + 1)][vert_x + tile_x] = 255 if (vertex_data[4] & 0b00000001) > 0 else 0

        # These next 4 look like 4 bit data maybe
        params_arrs[3][imgres - (vert_y + tile_y + 1)][vert_x + tile_x] = vertex_data[5] & 0b11110000

        params_arrs[4][imgres - (vert_y + tile_y + 1)][vert_x + tile_x] = (vertex_data[5] & 0b00001111) << 4

        params_arrs[5][imgres - (vert_y + tile_y + 1)][vert_x + tile_x] = vertex_data[6] & 0b11110000

        params_arrs[6][imgres - (vert_y + tile_y + 1)][vert_x + tile_x] = (vertex_data[6] & 0b00001111) << 4

    pathlib.Path(outfilepath).mkdir(parents=True, exist_ok=True)
    heightmap_arr = heightmap_arr.astype("int16")
    imageio.imwrite(path.join(outfilepath, f"heightmap_mip{res}.tiff"), heightmap_arr)
    normalmap_arr = normalmap_arr.astype("uint8")
    imageio.imwrite(path.join(outfilepath, f"normalmap_mip{res}.png"), normalmap_arr)
    for i in range(NUM_PARAMS):
        params_arrs[i] = params_arrs[i].astype("uint8")
        imageio.imwrite(path.join(outfilepath, f"params_{i}_mip{res}.png"), params_arrs[i])
    f.close()

def render_unknown(res):
    imgshape = (CHUNK_SIZE[res] * NUM_CHUNKS, NUM_CHUNKS * 2)
    imgshape_odd = (NUM_CHUNKS * 2, CHUNK_SIZE[res] * NUM_CHUNKS)
    test_arr = numpy.empty(imgshape)
    test_arr2 = numpy.empty(imgshape_odd)
    f = open(infilepath, "rb")
    f.seek(PART_2_OFFSET[res])
    for v in range(CHUNK_SIZE[res] * NUM_CHUNKS * NUM_CHUNKS):
        data = unpack("hhhh", f.read(8))
        for i in range(4):
            short_index = v * 4 + i
            chunk_index = short_index % (CHUNK_SIZE[res] * 4)
            chunk_num = short_index // (CHUNK_SIZE[res] * 4)
            chunk_x = (chunk_num % NUM_CHUNKS)
            chunk_y = chunk_num // NUM_CHUNKS

            x = chunk_index % CHUNK_SIZE[res]
            y = chunk_index // CHUNK_SIZE[res]

            even_x = x + CHUNK_SIZE[res] * chunk_x
            even_y = (y + 4 * chunk_y) // 2

            odd_x = (4 * chunk_x + y) // 2
            odd_y = CHUNK_SIZE[res] * chunk_y + x

            if y % 2 == 0:
                test_arr[CHUNK_SIZE[res] * NUM_CHUNKS - even_x - 1][even_y] = data[i]
            else:
                test_arr2[2 * NUM_CHUNKS - odd_x - 1][odd_y] = data[i]

    pathlib.Path(outfilepath).mkdir(parents=True, exist_ok=True)
    test_arr = test_arr.astype("int16")
    imageio.imwrite(path.join(outfilepath, f"test_mip{res}_even.tiff"), test_arr)
    test_arr2 = test_arr2.astype("int16")
    imageio.imwrite(path.join(outfilepath, f"test_mip{res}_odd.tiff"), test_arr2)
    f.close()


for i in range(4):
    render_heightmap(i)
    render_unknown(i)