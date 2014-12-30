# Python script to parse MBR image files
# This just parses the first 512 bytes
#
# Tom Yarrish
# Version 2.0
#
# To run, simply type: mbr_parse.py <file to parse>
#
# To do:
# - Only bring in first 512 bytes in case it's run against an image
# - Handle extended partitions

import sys
import struct
import binascii
from binascii import hexlify

# This is a dictionary listing to identify the partition type

def check_partition_type(file_type_hex):
    file_system = { '0x0' : "Empty", '0x1' : "FAT12", '0x2' : "XENIX root", '0x3' : "XENIX usr",
                      '0x4' : "FAT16", '0x5' : "Extended", '0x6' : "FAT16B", '0x7' : "NTFS", '0x8' : "AIX" ,
                      '0x9' : "AIX Bootable" , '0xA' : "OS/2 Boot" , '0xB' : "Win95 FAT32" , '0xC' : "Win95 FAT32" ,
                      '0xD' : "Reserved" , '0xE' : "Win95 FAT16" , '0xF' : "Win95 Ext" , '0x10' : "OPUS" ,
                      '0x11' : "FAT12 Hidden" , '0x12' : "Compaq Diag" , '0x13' : "N/A" , '0x14' : "FAT16 Hidden" ,
                      '0x15' : "Extended Hidden" , '0x16' : "FAT16 Hidden" , '0x17' : "NTFS Hidden" , '0x18' : "AST" ,
                      '0x19' : "Willowtech" , '0x1A' : "N/A" , '0x1B' : "Hidden FAT32" , '0x1C' : "Hidden FAT32X" ,
                     '0x1D' : "N/A" , '0x1E' : "Hidden FAT16X" }
    try:
        file_partition_type = file_system[file_type_hex]
    except:
        file_partition_type = "File system not recognized."
    return file_partition_type

# This function is used to parse out the partition start and partition length data

def partition_value(decode):
    byte_1 = struct.pack("<B", decode[0])
    byte_2 = struct.pack("<B", decode[1])
    byte_3 = struct.pack("<B", decode[2])
    byte_4 = struct.pack("<B", decode[3])
    combine_bytes = byte_1 + byte_2 + byte_3 + byte_4
    partition_data = struct.unpack("<L",combine_bytes)[0]
    return partition_data
    
# This function does the heavy lifting and parses out the parition information

def parse_partition(partition):
    # Check to see if there is an actual partition.  This checks the start_head, start_sector,
    # start_cylinder, partition_type, and partition_start
    if (partition[1] == 0) and (partition[2] == 0) and (partition[3] == 0) and (partition[4] == 0) and (partition_value(partition[8:12]) == 0):
        return False
    else:
        try:
            boot_ind = hex(partition[0]) # Boot indicator
            start_head = (partition[1])     # Get start head value
            start_sector = (partition[2])   # Get start sector value
            start_cylinder = (partition[3]) # Get start cylinder value
            partition_type = hex(partition[4]) # Get file system type
            end_head = (partition[5])       # Get end head value
            end_sector = (partition[6])     # Get end sector value
            end_cylinder = (partition[7])   # Get end cylinder value
            partition_start = partition_value(partition[8:12])
            partition_length = partition_value(partition[12:16]) # Get the length of the partition
            return boot_ind, start_head, start_sector, start_cylinder, partition_type, end_head,\
            end_sector, end_cylinder, partition_start, partition_length
        except:
            print "Unable to parse partition."
            
mbr_file = sys.argv[1]


with open(mbr_file, "rb") as f:
    mbr_data = f.read()
    disk_sig = struct.unpack("<L", mbr_data[440:444])
    start = 446
    end = 462

# This section reads in each 16 bytes of data from the MBR partition section and interprets the data

    num_partitions = 0
    while(num_partitions <= 3): # stop when we have iterated 4 times
        # grab data
        partition_data = struct.unpack("<BBBBBBBBBBBBBBBB", mbr_data[start:end])
        #do_something(partition_data)
        format_partition = parse_partition(partition_data)
        if format_partition == False:
            print "Partition {} is not a valid....skipping".format(num_partitions)
        else:
            print "Here is the information for partition {}:\n ".format(num_partitions)
            print "Disk Signature is {}\n".format(hex(disk_sig[0]))
            if (format_partition[0]) == "0x80":                   # Is it bootable or no?
                print "Partition is bootable"
            else:
                print "Partition is not bootable"
            print "Start head is {}".format(format_partition[1])
            print "Start sector is {}".format(format_partition[2])
            print "Start cylinder is {}".format(format_partition[3])
            print "Partition type is {} {}".format((format_partition[4]), check_partition_type((format_partition[4])))
            print "End head is {}".format(format_partition[5])
            print "End sector is {}".format(format_partition[6])
            print "End cylinder is {}".format(format_partition[7])
            print "Partition start is at sector {}".format(format_partition[8])
            print "Partition size is {}".format(format_partition[9])
        # increment our variables
        start = end # after the first pass, 446 becomes 462
        end = end + 16 # after the first pass, 462 becomes 478
        num_partitions = num_partitions + 1
