"""
Date: 22 Mar. 2019
The script is to convert the label format into the YOLO format

Author: Zhou Jiadong
e-mail: zhou0251@e.ntu.edu.sg
"""

import os
import glob
from PIL import Image


def read_label_file(filename):
    """Return te contents of the provided filename as a list """
    try:
        with open(filename) as file_object:
            lines = []
            for line in file_object:
                line = line.strip()
                if line:
                    lines.append(line)
    except IOError:
        print("Error! Fail to find the file: " + filename)
        return None
    else:
        return lines


def write_label_file(filename, lines):
    """Write the content of the lines list into the file named filename"""
    with open(filename, 'w') as file_object:
        for index, line in enumerate(lines):
            if index == len(lines) - 1:
                file_object.write(convert_list_2_str(line))
            else:
                file_object.write(convert_list_2_str(line) + "\n")



def get_image_size(imagepath):
    """Return the size of the image giving the image name"""
    try:
        with Image.open(imagepath) as img_object:
            return img_object.size
    except IOError:
        print("Error! Cannot find the image file: " + imagepath)
        return None


def get_classes(filename):
    """Return the list of classes from the filename"""
    try:
        with open(filename) as file_object:
            lines = file_object.readlines()
    except IOError:
        print("Error! Cannot find the classname files: " + filename)
        exit(-1)
    else:
        class_names = []
        for line in lines:
            # remove the spaces
            line = line.strip()
            # ignore the empty lines
            if line:
                class_names.append(line.strip())
        return class_names


def convert_list_2_str(numbers):
    """Convert a list of numbers into a sting"""
    output_str = ''
    for number in numbers:
        output_str += (str(number) + " ")
    return output_str.strip()


def convert_box_str_2_list(box_str, classes):
    """convert each box str into the lists and convert class type into integer format"""
    box_list = box_str.split()
    values = []
    for value in box_list:
        try:
            value = int(value)
        except ValueError:
            try:
                value = classes.index(value)
            except ValueError:
                print("Unexpected class type is found in the label file.")
                return None
        finally:
            values.append(value)
    return values


def convert(size, box):
    """convet the bbox-formatted box into the yolo-formatted box"""
    # in case the bbox is out of the image region
    box[0] = size[0] - 1 if box[0] >= size[0] else 0 if box[0] < 0 else box[0]
    box[1] = size[1] - 1 if box[1] >= size[1] else 0 if box[1] < 0 else box[1]
    box[2] = size[0] - 1 if box[2] >= size[0] else 0 if box[2] < 0 else box[2]
    box[3] = size[1] - 1 if box[3] >= size[1] else 0 if box[3] < 0 else box[3]

    dw = 1. / size[0]
    dh = 1. / size[1]
    x = (box[0] + box[2]) / 2.0
    y = (box[1] + box[3]) / 2.0
    w = box[2] - box[0]
    h = box[3] - box[1]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return [x, y, w, h]


if __name__ == "__main__":

    # define the label file location
    src_label_prefix = "Labels/003"
    yolo_label_prefix = "Labels_YOLO/003"

    # define the image file info
    image_prefix = "Images/003"
    image_formats = [".jpg", ".jpeg", ".JPG"]

    # define the labelled classes
    class_path = "class.txt"
    classes = get_classes(class_path)
    print("The labelled classes are {}.".format(classes))

    # get the list of file names
    image_full_paths = []
    for image_format in image_formats:
        image_names_formatted = glob.glob(os.path.join(image_prefix, "*" + image_format))
        image_full_paths += image_names_formatted
        print("Number of {} images is {}.".format(image_format, len(image_names_formatted)))
    print("Number of image files is {}.".format(len(image_full_paths)))
    print(image_full_paths[:5])

    # iterate for processing each image and label file
    while image_full_paths:

        # get the single image path
        image_path = image_full_paths.pop()

        # get the image size
        image_size = get_image_size(image_path)
        # print("Image size: {}".format(image_size))

        # get the image name
        label_name = image_path.replace(image_prefix + "/", "")
        label_name = label_name.split('.')[0] + ".txt"
        src_label_path = os.path.join(src_label_prefix, label_name)
        yolo_label_path = os.path.join(yolo_label_prefix, label_name)

        print("Input file: " + src_label_path)
        print("Output file: " + yolo_label_path)

        # get the box string list
        bbox_lines = read_label_file(src_label_path)
        bbox_info = []
        if bbox_lines:
            # get the number of the boxes
            num_of_bbox = int(bbox_lines[0])
            for i in range(num_of_bbox):
                # convert string into list and convert box type into integer format
                bbox_list = convert_box_str_2_list(bbox_lines[i+1], classes)

                # convert to yolo format
                bbox_list_yolo = convert(image_size, bbox_list[:])
                bbox_list_yolo = bbox_list[-1:] + bbox_list_yolo
                print("{} {} --> {}".format(image_size, bbox_list, bbox_list_yolo))

                # save the new bbox
                bbox_info.append(bbox_list_yolo)

        # save the yolo format label file
        write_label_file(yolo_label_path, bbox_info)
