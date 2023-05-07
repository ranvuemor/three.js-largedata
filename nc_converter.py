# for Python 3.8
import sys  # to change print write to log and not console
import os  # read directories
import netCDF4 as nc  # to read netCDF4 files from simulations
import numpy as np  # nc imports and np
import math  # sqrt and such
import png  # to save as png is called pypng for importing
import multiprocessing as mp  # for multiprocessing
import starmap  # import to apply patch to multiprocessing, NOTE!!! this is used don't trust hints
from tqdm import tqdm  # create progressbar
import pandas as pd  # dataframe for better editing of data tables
import functools
from scipy import interpolate

from warnings import filterwarnings

filterwarnings(action='ignore', category=DeprecationWarning, message='`np.bool` is a deprecated alias')


def list_files_with_ext(directory, ext):
    """
    lists all files in dir and its sub dirs with the given extension
    :param directory: string of filepath
    :param ext: string of extension ".vtk" for example
    :return:
    """
    filelist = []
    for file in os.listdir(directory):
        if file.endswith(ext):
            filelist.append(os.path.join(directory, file))
    return filelist


def rescale_x_bit(data, bit=8, vmin=None, vmax=None):
    """
    takes any np array. and rescales it to use the full bit range of integer values.
    :param data: data array of numbers
    :param bit: bit range of 8, 16 or 32
    :param vmin: minimum value to be set the new 0, values that were smaller will also be 0
    :param vmax: maximum value, values that are larger will be capt at the maximum
    :return: returns np array with 16bit int of the data shape
    """

    # check if bit range is acceptable
    if bit != 8 and bit != 16 and bit != 32:
        raise RuntimeError('only select bit range of 8, 16 or 32')

    # minus 1 because we start from 0
    bit_range = (2 ** bit) - 1

    # checking if min or max are used
    if vmin == vmax:
        vmin = data.min()
        value_range = data.max() - vmin
    else:
        if vmin > vmax:
            raise RuntimeError('min can not be smaller than max')
        value_range = vmax - vmin
        # clipping the array so no values are over the int16 limit or under
        data = data.clip(min=vmin, max=vmax)

    if value_range == 0:  # to avoid division by 0
        rescaled_data = np.zeros(np.shape(data), dtype=data.dtype)  # everything will be set 0 as well
    else:
        rescaled_data = (bit_range * ((data - vmin) / value_range))

    # set datatype to the proper bit range
    if bit == 8:
        rescaled_data = rescaled_data.astype(np.uint8)
    elif bit == 16:
        rescaled_data = rescaled_data.astype(np.uint16)
    else:
        rescaled_data = rescaled_data.astype(np.uint32)

    # print('bitrange:', bit_range, 'bit:', bit)
    # print('min source:', np.min(data), 'max source:', np.max(data))
    # print('min rescaled:', np.min(rescaled_data), 'max rescaled:', np.max(rescaled_data))

    return rescaled_data


def tile_array(data, base2=True):
    """
    takes 3d array and tiles all the slices of the z dimension next to each other in a 2d array
    :param data: 3d data array of the shape (z, y, x)
    :param base2: if true the output array as well as its tiles will have a shape of a multiple of 2
    :return: 2d np array
    """

    # calculate size of 2d array
    (z_length, y_length, x_length) = np.shape(data)  # NOTE!!! the order of the Z,Y,X given by np.shape

    if base2:  # calculating size of base to image and its tiling
        new_x_length, new_y_length = 2, 2
        while x_length > new_x_length:  # image with base 2 to fit one tile in x length
            new_x_length = new_x_length * 2
        while y_length > new_y_length:  # image with base 2 to fit one tile in y length
            new_y_length = new_y_length * 2

        new_x_tiling_length, new_y_tiling_length = new_x_length, new_y_length
        z, x_offset, y_offset = 0, 0, 0
        while z < z_length:  # check if all tiles fit into image
            x_offset += new_x_tiling_length  # next column
            if x_offset > (new_x_length - new_x_tiling_length):  # new row
                if new_x_length <= new_y_length:
                    new_x_length += new_x_length  # expand image to the side, because we are out of space
                else:
                    new_y_length += new_y_length  # expand image below, because we are out of space
                    x_offset = 0  # back to column 0
                    y_offset += new_y_tiling_length
            z = math.ceil((new_x_length / new_x_tiling_length) * (new_y_length / new_y_tiling_length))  # update z
        new_data = np.zeros((new_y_length, new_x_length), dtype=data.dtype)
    else:
        number_of_rows = math.ceil(math.sqrt(z_length))
        new_x_tiling_length, new_y_tiling_length = x_length, y_length
        new_x_length, new_y_length = number_of_rows * x_length, number_of_rows * y_length
        new_data = np.zeros((new_y_length, new_x_length), dtype=data.dtype)

    # place the slices of the 3d array in the new empty 2d array
    x_offset, y_offset = 0, 0  # where we place the next image

    for z in range(z_length):
        # place array (x and y are flipped cause im dumb, but has to stay like this)
        new_data[y_offset:y_offset + y_length, x_offset:x_offset + x_length] = data[z]
        x_offset += new_x_tiling_length  # next column
        if x_offset > (new_x_length - new_x_tiling_length):
            x_offset = 0  # back to column 0
            y_offset += new_y_tiling_length  # new row

    number_of_tile = math.ceil(new_y_length / new_y_tiling_length) * math.ceil(new_x_length / new_x_tiling_length)
    # squared col_and_row_number because the other tiles will be empty but needed for proper scaling
    shape = (number_of_tile, new_x_tiling_length, new_y_tiling_length)

    return new_data, shape


def save_png(data, outputfile, bit=8):
    """
    saves a up to 4 2 dimensional arrays into a png
    :param data: array in the shape (1-4, X, Y) filled with integers from 0 - (2^bit)-1
        Note:   1 2D array will make a greyscale image
                2 2D arrays will make a grayscale image with alpha
                3 2D arrays will make a RGB image
                4 2D arrays will make a RGBA image
    :param outputfile: path of the png file
    :param bit: 8 or 16 for 8 or 16 bit per channel
    :return:
    """

    if data.__len__() > 4:
        raise RuntimeError('No more than 4 variables per PNG. PNGs have only four channels.')
    elif data.__len__() == 1:
        greyscale, alpha = True, False
        png_data = data[0]
    elif data.__len__() == 2:
        greyscale, alpha = True, True
        png_data = np.array([np.concatenate(row) for row in np.dstack(data)])
    elif data.__len__() == 3:
        greyscale, alpha = False, False
        png_data = np.array([np.concatenate(row) for row in np.dstack(data)])
    else:
        greyscale, alpha = False, True
        png_data = np.array([np.concatenate(row) for row in np.dstack(data)])

    # Use pypng to write z as a color PNG.
    with open(outputfile, 'wb') as f:
        writer = png.Writer(width=np.shape(data[0])[1], height=np.shape(data[0])[0],
                            bitdepth=bit, greyscale=greyscale, alpha=alpha)
        writer.write(f, png_data.copy())


def nc_to_png(file_path, png_library, dict_lib, png_path=None, base2=True, flip=None):
    """
    opens a volumetric nc file and saves it as a png for unreal engine
    :param file_path: filepath to the nc file
    :param png_library: a list of dictionaries for each png, in the form:
        [{'variables': [string], 'bit': int, 'selection': (in, int, int, int, int, int)}]
        variables: string of the variable name in the nc file, 'qc' for example, None for empty layer
        bit = int 8, 16 for the bit depth per channel of the image
        selection: tuple of six integers describing a square (x, y, width, height)
            z coordinate of the square, corner
            x coordinate of the square, corner
            y coordinate of the square, corner
            height: height of the square
            width: of the square
            depth: of the square
    :param dict_lib: dictionary of the form:
        {variable_name: {'flip': Bool, 'func': func, 'vmin': Int, 'vmax': Int, 'bit': Int}}
        variable_name: string name of variable in nc file
        func: partialfunction or none to apply to variable
        vmin: smallest value that should be black, everything smaller will also be black (not affected by invert!)
        vmax: largest value that should be white, everything larger will also be white (not affected by invert!)
    :param png_path: optional output path of the file. default is same name and dir as original nc file
    :param base2: optional bool, True if the texture should have a resolution base 2. Note, if yours selection is not
        also base 2 ue4 will not generate mip maps making this switch pointless.
    :param flip: optional None = no flip, else a list with the axis to flip (0, 2) to flip Z and Y axis (0=Z, 1=X, 2=Y)
    :return:
    """

    for png_dict in png_library:
        if png_dict['variables'].__len__() > 4:
            raise RuntimeError('No more than 4 variables per PNG. PNGs have only four channels.')

    # check if png is being used, else save png with next to original
    if (png_path == '') or (png_path is None):
        png_path = os.path.splitext(file_path)[0] + '.png'

    # read nc file
    datastructure = nc.Dataset(file_path)

    for png_dict in png_library:

        shape = ''
        png_data = []
        for variable in png_dict['variables']:
            if variable is not None:
                # read data from structure maybe trim with selection cube
                if png_dict['selection'] is None:
                    data = datastructure[variable][0, :, :, :]
                elif variable == 'red' or 'green' or 'blue':
                    print("at ", dict_lib[variable])
                    (z, x, y, height, width, depth) = png_dict['selection']
                    data = datastructure[variable][z: (z + height), x:(x + width), y: (y + depth)]
                elif variable == 'elev' or 'Lon' or 'Lat':
                    print("at ", dict_lib[variable])
                    (z, x, y, height, width, depth) = png_dict['selection']
                    data = datastructure[variable][z: (z + height), x:(x + width), y: (y + depth)]
                else:
                    # print("at ", dict_lib[variable])
                    (z, x, y, height, width, depth) = png_dict['selection']
                    data = datastructure[variable][0, z: (z + height), x:(x + width), y: (y + depth)]

                # flip values
                if flip is not None:
                    data = np.flip(data, flip)  # reverse order

                # invert values
                if dict_lib[variable]['func'] is not None:
                    data = dict_lib[variable]['func'](data)

                # tile 3D array to a 2D array
                tiled_data, shape = tile_array(data, base2=base2)

                # after the tiling so 0 will also become scales and flow_maps will not have black edges
                # rescale array to be 8bit int range
                bit_data = rescale_x_bit(tiled_data, bit=png_dict['bit'], vmin=dict_lib[variable]['vmin'],
                                         vmax=dict_lib[variable]['vmax'])

                # add color to png_group
                png_data.append(bit_data)

            else:
                # if we already have channels created read their shape
                if not png_path:
                    channelshape = np.shape(png_path[0])
                else:
                    if png_dict['selection'] is None:
                        # if we didn't define a shape
                        data = datastructure[variable][0, :, :, :]
                        # tile 3D array to a 2D array
                        tiled_data, shape = tile_array(data, base2=base2)
                        channelshape = np.shape(tiled_data)
                    else:
                        # if we did make a tiled zeros array and get its shape. Ugly but it is a rare case
                        (z, x, y, height, width, depth) = png_dict['selection']
                        data = np.zeros((height, width, depth), dtype=np.uint8)
                        tiled_data, shape = tile_array(data, base2=base2)
                        channelshape = np.shape(tiled_data)

                bit_data = np.zeros(channelshape, dtype=np.uint8)  # its 0 so it shouldn't matter if its 16 bit or not

                # add color to png_group
                png_data.append(bit_data)

        # channel names as string
        channel_names = ''
        for variable in png_dict['variables']:
            if variable is not None:
                channel_names += '_' + variable

        # shape to string
        shape_name = '_x' + str(shape[1]) + '_y' + str(shape[2]) + '_z' + str(shape[0])

        # insert dimensions into path
        outputpath = os.path.splitext(png_path)[0] + channel_names + shape_name + os.path.splitext(png_path)[1]

        # save png
        save_png(png_data, outputpath, bit=png_dict['bit'])
        # print('saved to ', outputpath)

    # closing the translated dataset
    datastructure.close()


def multi_nc_to_png(folder_path, png_library, png_path=None, dict_lib=None, base2=True, flip=None):
    """
    translates all nc files in folder into pngs. It will skip nc files that have translated pngs already.
    :param folder_path: folder that contains .nc (netcdf files)
    :param png_library: a list of dictionaries for each png, in the form:
        [{'variables': [string], 'bit': int, 'selection': (in, int, int, int, int, int)}]
        variables: string of the variable name in the nc file, 'qc' for example, None for empty layer
        bit = int 8, 16 for the the bit depth per channel of the image
        selection: tuple of four integers describing a square (x, y, width, height) !CAN NOT be larger than dataset
            z coordinate of the square, corner
            x coordinate of the square, corner
            y coordinate of the square, corner
            height: height of the square
            width: of the square
            depth: of the square
    :param png_path: directory where the output pngs should be stored, default is in same folder as nc files
    :param dict_lib: dictionary of the form:
        {variable_name: {'flip': Bool, 'func': func, 'vmin': Int, 'vmax': Int, 'bit': Int}}
        variable_name: string name of variable in nc file
        func: partial function or none to apply to variable
        vmin: smallest value that should be black, everything smaller will also be black (not affected by invert!)
        vmax: largest value that should be white, everything larger will also be white (not affected by invert!)
    :param base2: bool, True if the texture should have a resolution base 2. Note, if yours selection is not also base
        2 ue4 will not generate mip maps making this switch pointless.
    :param flip: None for no flip, else a list with the axis to flip (0, 2) to flip Z and Y axis (0=Z, 1=X, 2=Y)
    :return:
    """

    # check if output_path is used, if so create the current output file name
    if png_path is not None:
        # test if png_path exist otherwise create it
        if not os.path.exists(png_path):
            os.mkdir(png_path)
    else:  # else set it to folderpath
        png_path = folder_path

    # find all pngs in goal dir and filter for only filename
    existing_png_list = np.array(list_files_with_ext(png_path, '.png'))
    existing_png_list = [os.path.splitext(os.path.basename(file_path))[0] for file_path in existing_png_list]
    png_variables = np.concatenate([x['variables'] for x in png_library])

    # make list of all the nc files in folder dir
    file_list = list_files_with_ext(folder_path, '.nc')

    to_do_list = []
    for file_path in file_list:
        filename = os.path.splitext(os.path.basename(file_path))[0]

        output_file_path = os.path.join(png_path, filename + '.png')

        if len(existing_png_list):  # if pngs were found
            # lists all index of occurrences of the filename in the existing_png_list
            index_occurrence = np.flatnonzero(np.core.defchararray.find(existing_png_list, filename) != -1)
            if len(index_occurrence):  # if he found any matches
                # fetches filename with index and joins them for easy search
                matching_pngs = ' '.join(np.take(existing_png_list, index_occurrence))
                if all([x in matching_pngs for x in png_variables]):  # if ALL of the png_variables are in the matches
                    print('skipping', filename)
                    continue  # we can safely skip this file

        # builds a list that has all the arguments for each process
        to_do_list.append((file_path, png_library, dict_lib, output_file_path, base2, flip))

    # runs mutiprossessing for every file in the list of files
    with mp.Pool(processes=4) as pool:
        # pool.starmap(nc_to_png, to_do_list)  # without progressbar
        for _ in tqdm(pool.starmap(nc_to_png, to_do_list), total=len(to_do_list)):  # adds progressbar for mp
            pass
    # print('finished converting ', folder_path)


def list_empty(data, vmin=None, vmax=None):
    """
    returns list of all z arrays that are outside of the range vmin-vmax or if min==max
    :param data: 3d array
    :param vmin: optional minimum cut of values
    :param vmax: optional maximum cut of values
    :return: list of z indices that are empty
    """

    if vmin is None:
        vmin = 0
    if vmax is None:
        vmax = 0

    empty_index = []
    for z in range(len(data)):
        max_value = np.max(data[z])
        min_value = np.min(data[z])
        if max_value < vmin or min_value > vmax or max_value == min_value:
            empty_index.append(z)

    if len(empty_index) == len(data):
        empty_index = ['!!! EVERY VALUE IS EMPTY !!!']
    return empty_index


def nc_scan(file_path, logpath=None, variables=None, qc_vmin=None, qc_vmax=None):
    """
    saves information about the parameters inside the nc file to a log files at dir of file_path
    :param file_path: file path to the .nc file
    :param logpath: optional path for log file, defualt is same location as filepath as txt
    :param variables: optional array filled with strings of the variables to look at. other will be skipped.
    :param qc_vmin: optional minimum for qc list of empty arrays
    :param qc_vmax: optional maximum for qc list of empty arrays
    :return:
    """

    # read nc file
    datastructure = nc.Dataset(file_path)

    if logpath is None:  # if None is given it'll be saved next to file as txt
        log_print_path = os.path.splitext(file_path)[0] + '.txt'
    else:  # if logpath is given extension is gut and set to txt just to be save
        log_print_path = os.path.splitext(logpath)[0] + '.txt'

    original_stdout = sys.stdout
    with open(log_print_path, 'w') as f:
        sys.stdout = f  # makes print write to file

        print(datastructure)
        print('VARIABLES_______________________________________________________________________')

        if variables is None:  # if we don't specify all variables are asked for min and max
            variables = datastructure.variables
        for var in variables:
            print(datastructure[var])

            data = datastructure[var][:]
            print('   ', var, 'max:', np.max(data))
            print('   ', var, 'min:', np.min(data))
            if var == 'qc':
                print('   ', var, 'empty:', list_empty(data[0], qc_vmin, qc_vmax))
            print('______________________________________')

        sys.stdout = original_stdout  # makes print write to console again
        datastructure.close()

    print('saved log to: ', log_print_path)

    # with open(log_path, 'a') as f:


def find_common(list_list):
    """
    finds the common elements shared between all lists
    :param list_list: list of lists like this [[a, b, c], [a, b]]
    :return: list of elements that occurred in all lists of list_list
    """

    shared = set(list_list[0])
    for s in list_list[1:]:
        shared.intersection_update(s)
    return shared


def multi_nc_scan(folder_path, variables, logpath=None, qcmin=None, qcmax=None):
    """
    opens ALL nc files one by one and saves the min max and empty into a csv file as well as the global min max and
    shared empty tiles into a txt in the dir of the folder
    :param folder_path: folderpath of the .nc files
    :param variables: list of string variables from the .nc file to read
    :param logpath: optional path of log file, default is in folder
    :param qcmin: optional min value for qc (changes empty tiles)
    :param qcmax: optional max value for qc (changes empty tiles)
    :return:
    """

    # make list of all the nc files in folder dir
    file_list = list_files_with_ext(folder_path, '.nc')

    if logpath is None:  # if none is given, log will be in folder dir
        log_df_path = os.path.join(folder_path, 'nc_folder_scan.csv')
        log_print_path = os.path.join(folder_path, 'nc_folder_scan.txt')
    else:  # split path+filename from extension add proper extension just in case
        log_df_path = os.path.splitext(logpath)[0] + '.csv'
        log_print_path = os.path.splitext(logpath)[0] + '.txt'

    if os.path.exists(log_df_path):  # read csv if already there
        df = pd.read_csv(log_df_path)
    else:  # else make a new df
        columns = ['name']
        for var in variables:
            if 'qc' == var:
                columns.append('qc_empty')
            columns.append(var + '_min')
            columns.append(var + '_max')
        df = pd.DataFrame(columns=columns)

    pbar = tqdm(total=len(file_list) + 1)  # create progressbar + because we load a the first file in the end again

    for file_path in file_list:
        filename = os.path.splitext(os.path.basename(file_path))[0]

        if any(df['name'] == filename):
            # print('skipping', filename)
            pbar.update(1)  # increment progressbar
            continue

        # read nc file
        datastructure = nc.Dataset(file_path)

        new_row = {'name': filename}  # build new row
        for var in variables:
            data = datastructure[var][:]
            if var == 'qc':
                new_row['qc_empty'] = list_empty(data[0], qcmin, qcmax)
            new_row[var + '_min'] = np.min(data)
            new_row[var + '_max'] = np.max(data)

        df_length = len(df)
        df.loc[df_length] = new_row  # append new row (not using 'append' cause that copies the df)
        df.to_csv(log_df_path, header=True, index=False)  # save data fame as csv

        datastructure.close()  # closes the nc file
        pbar.update(1)  # increment progressbar

    datastructure = nc.Dataset(file_list[0])  # opening just one files for general information
    original_stdout = sys.stdout
    with open(log_print_path, 'w') as f:
        sys.stdout = f  # makes print write to file

        print(datastructure)
        print('DICT____________________________________________________________________________')
        for var in variables:
            print(datastructure[var])

            print('   ', var, 'global_min:', np.min(df[var + '_min']))
            print('   ', var, 'global_max:', np.max(df[var + '_max']))
            if var == 'qc':
                shared = find_common(df['qc_empty'])
                print('   ', var, 'empty_shared:', shared)
            print('______________________________________')

        sys.stdout = original_stdout  # makes print write to console again
        datastructure.close()  # closes the nc file

    pbar.update(1)  # increment progressbar
    pbar.close()  # close progressbar

    # print('saved df to: ', log_df_path)
    # print('saved log to: ', log_print_path)


def normalize_data(data):
    """
    takes an array and rescales the values using its min and max value to rescale to an range of 0-1
    :param data: and kind of array
    :return: array with values from 0-1
    """
    return (data - np.min(data)) / (np.max(data) - np.min(data))


def save_curve(file_path, var_selection, output_filepath=None, bit=16):
    """
    creates csvs with curves for unreal for each var in selection
    :param bit: bit depth of png output image
    :param file_path: dir of file
    :param var_selection: dict of vars with list if selection in this shape {var: (x, range)}
    :param output_filepath: optional dir of output file
    :return:
    """

    # read nc file
    datastructure = nc.Dataset(file_path)

    # get data into dict
    data = {}
    for var in var_selection:
        (lowerbound, fullrange) = var_selection[var]
        data[var] = normalize_data(datastructure[var][lowerbound: (lowerbound + fullrange)])

    uv_dict = {}
    x_shape = ''
    for var in var_selection:
        # build name addon
        minimum_value = datastructure[var][var_selection[var][0]]
        value_range = datastructure[var][var_selection[var][0] + var_selection[var][1] - 1] - minimum_value
        string_shape = '_' + var + '_m' + "%.2f" % minimum_value + '_r' + "%.2f" % value_range

        if output_filepath is None:  # if None is given it'll be saved next to file as txt
            csv_path = os.path.splitext(file_path)[0] + string_shape + '.csv'
            png_path = os.path.splitext(file_path)[0] + string_shape + '.png'
        else:  # if logpath is given extension is gut and set to txt just to be save
            csv_path = os.path.splitext(output_filepath)[0] + string_shape + '.csv'
            png_path = os.path.splitext(output_filepath)[0] + string_shape + '.png'

        length_data = len(data[var])
        percentage = [i / (length_data - 1) for i in range(length_data)]
        values = data[var]

        if var.__contains__('h'):  # flipping x and y coordinates cause i dont understand why
            df = pd.DataFrame({var: values, 'input': percentage})

            # swaps x and y with assistance of interpolation for the textures only
            xnew = np.linspace(0, 1, length_data)
            f_BSpline = interpolate.make_interp_spline(values, percentage)
            values = f_BSpline(xnew)  # overwriting the old values
        else:
            df = pd.DataFrame({'input': percentage, var: values})

        if 'x' in var or 'y' in var:
            uv_dict[var] = values
            x_shape = '_m' + "%.2f" % minimum_value + '_r' + "%.2f" % value_range

        # makes a png texture out of it. it can not be channel packed cause they are not the same size most of the time
        image_data = np.array([[values]])
        image_data = rescale_x_bit(image_data, bit=bit)
        save_png(image_data, png_path, bit=bit)  # save as image

        df.to_csv(csv_path, header=True, index=False)  # save data fame as csv

    # build UV texture from XY coordinated that have been flipped with interpolation
    if uv_dict:
        xmatch = [x for x in uv_dict.keys() if 'x' in x]
        uv_r = uv_dict[xmatch[0]]

        if any('y' in s for s in uv_dict.keys()):
            ymatch = [x for x in uv_dict.keys() if 'y' in x]
            uv_g = uv_dict[ymatch[0]]
        else:
            ymatch = xmatch
            uv_g = uv_r

        uv_r = np.array([uv_r for x in range(len(uv_g))])
        uv_g = np.array([uv_g for x in range(len(uv_r))])
        uv_g = np.swapaxes(uv_g, 0, 1)  # flip it for V coordinates
        uv_b = np.zeros((len(uv_r), len(uv_g)), dtype=int)  # make 0 for blue channel

        data = np.array([uv_r, uv_g, uv_b])  # join them
        data = rescale_x_bit(data, bit=bit)  # rescale them to the color range of image

        if output_filepath is None:  # if None is given it'll be saved next to file as txt
            png_path = os.path.splitext(file_path)[0] + '_' + xmatch[0] + '_' + ymatch[0] + x_shape + '.png'
        else:  # if logpath is given extension is gut and set to txt just to be save
            png_path = os.path.splitext(output_filepath)[0] + '_' + xmatch[0] + '_' + ymatch[0] + x_shape + '.png'

        save_png(data, png_path, bit=bit)  # save as image


def minus(x, y):
    return x - y


def invert(x):
    return -x


def main():
    # netCDF4 to unreal engine png translation
    flip = (0, 2)  # flip Z and X !!! remember to invert the corresponding Vectors !!!

    """parameters small simulation"""
    # min_velocity, max_velocity = -35, 35
    # invertfunc = functools.partial(invert)  # cant use lambda cause of multiprocessing
    # minusfunc = functools.partial(minus, 0.016)
    # dict_libary = {
    #     'qc': {'func': None, 'vmin': 0.0, 'vmax': 0.0028},  # Cloud density
    #     'qr': {'func': minusfunc, 'vmin': 0.0, 'vmax': 0.005},  # Rain density
    #     'uinterp': {'func': None, 'vmin': min_velocity, 'vmax': max_velocity},  # X wind velocity
    #     'vinterp': {'func': invertfunc, 'vmin': min_velocity, 'vmax': max_velocity},  # y wind velocity
    #     'winterp': {'func': None, 'vmin': min_velocity, 'vmax': max_velocity}}  # Z wind velocity
    # square64_32 = (3, 18, 18, 32, 64, 64)
    # var_selection = {'xh': (18, 64), 'z': (3, 32)}
    # png_library = [{'variables': ['qc'], 'bit': 16, 'selection': square64_32},
    #                {'variables': ['uinterp', 'vinterp', 'winterp', 'qr'], 'bit': 8, 'selection': square64_32}]
    # var_selection = {'xh': (18, 64), 'z': (3, 32)}
    # input_filepath = os.path.join(os.sep, 'D:' + os.sep, 'BoringStuff', 'Uni-LMU-MMI', 'Master', 'Assets',
    #                               '1Cloud_2h', 'cm1out', 'cm1out_0100.nc')
    # input_folderpath = os.path.join(os.sep, 'D:' + os.sep, 'BoringStuff', 'Uni-LMU-MMI', 'Master', 'Assets',
    #                                 '1Cloud_2h', 'cm1out')
    # output_folderpath = os.path.join(os.sep, 'D:' + os.sep, 'BoringStuff', 'Uni-LMU-MMI', 'Master', 'Assets',
    #                                  '1Cloud_2h', 'png_output')

    """parameters big simulation"""
    min_velocity, max_velocity = -50, 50
    invertfunc = functools.partial(invert)  # cant use lambda because multiprocessing doesnt like lambda
    minusfunc = functools.partial(minus, 0.005)
    dict_libary = {
        # 'qc': {'func': None, 'vmin': 0.0001, 'vmax': 0.0028},  # Cloud density
        # 'qr': {'func': minusfunc, 'vmin': 0.0, 'vmax': 0.005},  # Rain density
        # 'uinterp': {'func': None, 'vmin': min_velocity, 'vmax': max_velocity},  # X wind velocity, --1 = 1
        # 'vinterp': {'func': invertfunc, 'vmin': min_velocity, 'vmax': max_velocity},  # y wind velocity
        # 'winterp': {'func': None, 'vmin': min_velocity, 'vmax': max_velocity}}  # Z wind velocity --1 = 1
        'red': {'func': None, 'vmin': 0, 'vmax': 250},
        'green': {'func': None, 'vmin': 0, 'vmax': 250},
        'blue': {'func': None, 'vmin': 0, 'vmax': 250},
        'elev': {'func': None, 'vmin': 0, 'vmax': 400},
        'Lon': {'func': None, 'vmin': -179.95, 'vmax': 179.95},
        'Lat': {'func': None, 'vmin': -89.95, 'vmax': 89.95}
    }
    selection = (1, 58, 58, 32, 1024, 1024)  # selection to have all data and 8k res
    # selection = (1, 314, 314, 32, 512, 512)  # selection to have all data and 4k res
    var_selection = {'xh': (58, 1024), 'z': (1, 32)}  # selection to have all data and 8k res
    # var_selection = {'xh': (314, 512), 'z': (1, 32)}  # selection to have all data and 4k res
    png_library = [{'variables': ['red', 'green', 'blue'], 'bit': 8, 'selection': selection},
                   {'variables': ['elev', 'Lon', 'Lat'], 'bit': 8, 'selection': selection}]

    # input_filepath = os.path.join(os.sep, 'D:' + os.sep, 'BoringStuff', 'Uni-LMU-MMI', 'Master', 'Assets',
    #                               'rawdata_view', 'cm1out', 'cm1out_001030.nc')
    # output_filepath = os.path.join(os.sep, 'D:' + os.sep, 'BoringStuff', 'Uni-LMU-MMI', 'Master', 'Assets',
    #                                'rawdata_view',  'cm1out', 'cm1out_001030.png')
    # input_folderpath = os.path.join(os.sep, 'D:' + os.sep, 'BoringStuff', 'Uni-LMU-MMI', 'Master', 'Assets',
    #                                 'rawdata_view', 'cm1out')
    # output_folderpath = os.path.join(os.sep, 'D:' + os.sep, 'BoringStuff', 'Uni-LMU-MMI', 'Master', 'Assets',
    #                                  'rawdata_view', 'png_output')

    """Single NC Scan"""
    # scan single nc file
    # nc_scan(input_filepath) #, variables=['qc', 'qr', 'uinterp', 'vinterp', 'winterp', 'z', 'yh', 'xh'])
    #nc_scan("Temperature4D.nc")

    """Multi NC Scan"""
    # scan all nc files in folder
    # multi_nc_scan(input_folderpath, variables=['qc', 'qr', 'uinterp', 'vinterp', 'winterp', 'z', 'yh', 'xh'],
    # qcmin=0.0001, qcmax=0.0028)

    """Single NC to PNG"""
    # read nc file and transform it to png
    nc_to_png("Temperature4D.nc", png_library, png_path='', dict_lib=dict_libary, base2=True, flip=None)

    """Multi NC to PNG"""
    # read all nc files in folder and transform it to png
    # multi_nc_to_png(input_folderpath, png_library, png_path=output_folderpath, dict_lib=dict_libary,
    #                 base2=True, flip=flip)

    """Build Curve"""
    # takes single csv file and builds curves for the scaling
    # save_curve(input_filepath, var_selection, bit=16)


if __name__ == "__main__":
    # execute only if run as a script
    main()
