import json
import struct
import os
import re

# const panjang dan posisi data (byte)
START_POS = 2
IMEI_LEN = 15
IMEI_KEY = "IMEI"
AVL_PREAMBLE_LEN = 4
AVL_LENGTH_LEN = 4
AVL_LENGTH_KEY = "field-length"
AVL_CODEC_ID_LEN = 1
AVL_CODEC_ID_KEY = "codec-id"
AVL_NUM_OF_DATA_1_LEN = 1
AVL_NUM_OF_DATA_1_KEY = "number-of-data-1"
AVL_DATA_KEY = "AVL-data"
AVL_TIMESTAMP_LEN = 8
AVL_TIMESTAMP_KEY = "ts"
AVL_PRIORITY_LEN = 1
AVL_PRIORITY_KEY = "priority"
AVL_LONGITUDE_LEN = 4
AVL_LONGITUDE_KEY = "longitude"
AVL_LATITUDE_LEN = 4
AVL_LATITUDE_KEY = "latitude"
AVL_ALTITUDE_LEN = 2
AVL_ALTITUDE_KEY = "altitude"
AVL_ANGLE_LEN = 2
AVL_ANGLE_KEY = "angle"
AVL_SATELLITES_LEN = 1
AVL_SATELLITES_KEY = "satellites"
AVL_SPEED_LEN = 2
AVL_SPEED_KEY = "speed"
AVL_IO_ELEMENT_KEY = "io-element"
AVL_EVENT_IO_ID_LEN = 2
AVL_EVENT_IO_ID_KEY = "event-io-id"
AVL_N_TOTAL_IO_LEN = 2
AVL_N_TOTAL_IO_KEY = "total-io"
AVL_N1_TOTAL_IO_LEN = 2
AVL_N1_TOTAL_IO_KEY = "n1-total-io"
AVL_N1_IO_KEY = "n1-data"
AVL_N1_IO_ID_LEN = 2
AVL_N1_IO_ID_KEY = "n1-id"
AVL_N1_IO_VALUE_LEN = 1
AVL_N1_IO_VALUE_KEY = "n1-value"
AVL_N2_TOTAL_IO_LEN = 2
AVL_N2_TOTAL_IO_KEY = "n2-total-io"
AVL_N2_IO_KEY = "n2-data"
AVL_N2_IO_ID_LEN = 2
AVL_N2_IO_ID_KEY = "n2-id"
AVL_N2_IO_VALUE_LEN = 2
AVL_N2_IO_VALUE_KEY = "n2-value"
AVL_N4_TOTAL_IO_LEN = 2
AVL_N4_TOTAL_IO_KEY = "n4-total-io"
AVL_N4_IO_ID_LEN = 2
AVL_N4_IO_KEY = "n4-data"
AVL_N4_IO_ID_KEY = "n4-id"
AVL_N4_IO_VALUE_LEN = 4
AVL_N4_IO_VALUE_KEY = "n4-value"
AVL_N8_TOTAL_IO_LEN = 2
AVL_N8_TOTAL_IO_KEY = "n8-total-io"
AVL_N8_IO_KEY = "n8-data"
AVL_N8_IO_ID_LEN = 2
AVL_N8_IO_ID_KEY = "n8-id"
AVL_N8_IO_VALUE_LEN = 8
AVL_N8_IO_VALUE_KEY = "n8-value"
AVL_NX_TOTAL_IO_LEN = 2
AVL_NX_TOTAL_IO_KEY = "nx-total-io"
AVL_NX_IO_KEY = "nx-data"
AVL_NX_IO_ID_LEN = 2
AVL_NX_IO_ID_KEY = "nx-id"
AVL_NX_IO_LENGTH_LEN = 2
AVL_NX_IO_LENGTH_KEY = "nx-length"
AVL_NX_IO_VALUE_KEY = "nx-value"
NUM_OF_DATA_2_LEN = 1
NUM_OF_DATA_2_KEY = "number-of-data-2"
CRC_16_LEN = 4
CRC_16_KEY = "CRC16"


# mengonversi data biner koordinat menjadi float
def convert_coordinate(data):
    converted_data = struct.unpack('>I', data)[0]
    is_negative = (converted_data >> 31) & 0x01
    if is_negative:
        converted_data = converted_data ^ 0xFFFFFFFF
    float_coordinate = converted_data / 10000000.0
    if is_negative:
        float_coordinate *= -1
    return float_coordinate

# mengonversi data biner AVL menjadi format JSON
def decode(data):
    data_len = len(data)
    if data_len < 20:
        raise ValueError("length is invalid")

    data_map = {}
    current_position = START_POS

    # Membaca IMEI
    last_position = current_position + IMEI_LEN
    data_map[IMEI_KEY] = data[current_position:last_position].decode('ascii')

    current_position = last_position
    last_position += AVL_PREAMBLE_LEN
    # NO ACTION

    current_position = last_position
    last_position += AVL_LENGTH_LEN
    data_map[AVL_LENGTH_KEY] = struct.unpack('>I', data[current_position:last_position])[0]

    current_position = last_position
    last_position += AVL_CODEC_ID_LEN
    data_map[AVL_CODEC_ID_KEY] = f"{data[current_position:last_position].hex()}"

    current_position = last_position
    last_position += AVL_NUM_OF_DATA_1_LEN
    avl_records = data[current_position:last_position][0]
    data_map[AVL_NUM_OF_DATA_1_KEY] = avl_records

    avl_array = []
    for avl_index in range(avl_records):
        avl_data = {}

        # AVL_N_DATA_1
        current_position = last_position
        last_position += AVL_TIMESTAMP_LEN
        avl_data[AVL_TIMESTAMP_KEY] = struct.unpack('>Q', data[current_position:last_position])[0]

        current_position = last_position
        last_position += AVL_PRIORITY_LEN
        avl_data[AVL_PRIORITY_KEY] = data[current_position:last_position][0]

        current_position = last_position
        last_position += AVL_LONGITUDE_LEN
        avl_data[AVL_LONGITUDE_KEY] = convert_coordinate(data[current_position:last_position])

        current_position = last_position
        last_position += AVL_LATITUDE_LEN
        avl_data[AVL_LATITUDE_KEY] = convert_coordinate(data[current_position:last_position])

        current_position = last_position
        last_position += AVL_ALTITUDE_LEN
        avl_data[AVL_ALTITUDE_KEY] = struct.unpack('>H', data[current_position:last_position])[0]

        current_position = last_position
        last_position += AVL_ANGLE_LEN
        avl_data[AVL_ANGLE_KEY] = struct.unpack('>H', data[current_position:last_position])[0]

        current_position = last_position
        last_position += AVL_SATELLITES_LEN
        avl_data[AVL_SATELLITES_KEY] = int(data[current_position:last_position][0])

        current_position = last_position
        last_position += AVL_SPEED_LEN
        avl_data[AVL_SPEED_KEY] = struct.unpack('>H', data[current_position:last_position])[0]

        # AVL_N_DATA_1 AVL_IO_ELEMENT
        avl_io_element = {}

        current_position = last_position
        last_position += AVL_EVENT_IO_ID_LEN
        avl_io_element[AVL_EVENT_IO_ID_KEY] = struct.unpack('>H', data[current_position:last_position])[0]

        current_position = last_position
        last_position += AVL_N_TOTAL_IO_LEN
        avl_io_element[AVL_N_TOTAL_IO_KEY] = struct.unpack('>H', data[current_position:last_position])[0]

        current_position = last_position
        last_position += AVL_N1_TOTAL_IO_LEN
        avl_n1_total_io = struct.unpack('>H', data[current_position:last_position])[0]

        avl_n1_io_array = []
        for avl_n1_index in range(avl_n1_total_io):
            avl_n1_io_map = {}

            current_position = last_position
            last_position += AVL_N1_IO_ID_LEN
            avl_n1_io_map[AVL_N1_IO_ID_KEY] = struct.unpack('>H', data[current_position:last_position])[0]

            current_position = last_position
            last_position += AVL_N1_IO_VALUE_LEN
            avl_n1_io_map[AVL_N1_IO_VALUE_KEY] = data[current_position:last_position][0]

            avl_n1_io_array.append(avl_n1_io_map)

        avl_io_element[AVL_N1_IO_KEY] = avl_n1_io_array

        current_position = last_position
        last_position += AVL_N2_TOTAL_IO_LEN
        avl_n2_total_io = struct.unpack('>H', data[current_position:last_position])[0]

        avl_n2_io_array = []
        for avl_n2_index in range(avl_n2_total_io):
            avl_n2_io_map = {}

            current_position = last_position
            last_position += AVL_N2_IO_ID_LEN
            avl_n2_io_map[AVL_N2_IO_ID_KEY] = struct.unpack('>H', data[current_position:last_position])[0]

            current_position = last_position
            last_position += AVL_N2_IO_VALUE_LEN
            avl_n2_io_map[AVL_N2_IO_VALUE_KEY] = struct.unpack('>H', data[current_position:last_position])[0]

            avl_n2_io_array.append(avl_n2_io_map)

        avl_io_element[AVL_N2_IO_KEY] = avl_n2_io_array

        current_position = last_position
        last_position += AVL_N4_TOTAL_IO_LEN
        avl_n4_total_io = struct.unpack('>H', data[current_position:last_position])[0]

        avl_n4_io_array = []
        for avl_n4_index in range(avl_n4_total_io):
            avl_n4_io_map = {}

            current_position = last_position
            last_position += AVL_N4_IO_ID_LEN
            avl_n4_io_map[AVL_N4_IO_ID_KEY] = struct.unpack('>H', data[current_position:last_position])[0]

            current_position = last_position
            last_position += AVL_N4_IO_VALUE_LEN
            avl_n4_io_map[AVL_N4_IO_VALUE_KEY] = struct.unpack('>I', data[current_position:last_position])[0]

            avl_n4_io_array.append(avl_n4_io_map)

        avl_io_element[AVL_N4_IO_KEY] = avl_n4_io_array

        current_position = last_position
        last_position += AVL_N8_TOTAL_IO_LEN
        avl_n8_total_io = struct.unpack('>H', data[current_position:last_position])[0]

        avl_n8_io_array = []
        for avl_n8_index in range(avl_n8_total_io):
            avl_n8_io_map = {}

            current_position = last_position
            last_position += AVL_N8_IO_ID_LEN
            avl_n8_io_map[AVL_N8_IO_ID_KEY] = struct.unpack('>H', data[current_position:last_position])[0]

            current_position = last_position
            last_position += AVL_N8_IO_VALUE_LEN
            avl_n8_io_map[AVL_N8_IO_VALUE_KEY] = struct.unpack('>Q', data[current_position:last_position])[0]

            avl_n8_io_array.append(avl_n8_io_map)

        avl_io_element[AVL_N8_IO_KEY] = avl_n8_io_array

        current_position = last_position
        last_position += AVL_NX_TOTAL_IO_LEN
        avl_nx_total_io = struct.unpack('>H', data[current_position:last_position])[0]

        avl_nx_io_array = []
        for avl_nx_index in range(avl_nx_total_io):
            avl_nx_io_map = {}

            current_position = last_position
            last_position += AVL_NX_IO_ID_LEN
            avl_nx_io_map[AVL_NX_IO_ID_KEY] = struct.unpack('>H', data[current_position:last_position])[0]

            current_position = last_position
            last_position += AVL_NX_IO_LENGTH_LEN
            avl_nx_io_map[AVL_NX_IO_LENGTH_KEY] = struct.unpack('>H', data[current_position:last_position])[0]

            current_position = last_position
            last_position += avl_nx_io_map[AVL_NX_IO_LENGTH_KEY]
            avl_nx_io_map[AVL_NX_IO_VALUE_KEY] = data[current_position:last_position].hex()

            avl_nx_io_array.append(avl_nx_io_map)

        avl_io_element[AVL_NX_IO_KEY] = avl_nx_io_array

        avl_data[AVL_IO_ELEMENT_KEY] = avl_io_element
        avl_array.append(avl_data)

        current_position = last_position

    data_map[AVL_DATA_KEY] = avl_array

    current_position = last_position
    last_position += NUM_OF_DATA_2_LEN
    data_map[NUM_OF_DATA_2_KEY] = data[current_position:last_position][0]

    current_position = last_position
    last_position += CRC_16_LEN
    data_map[CRC_16_KEY] = data[current_position:last_position].hex()

    # Mengonversi data hasil parsing menjadi JSON

    return json.dumps(data_map, indent=4)

# hex_data = bytes.fromhex('000F38363337313930363530383432323100000000000003BB8E07000001919E520441003FAAD25FFC3CAD10002200490B00000000001D001200160100470200F00100150400C80000EF01025800025900025A00025B00025D00025E00026100026B00026C00026D00029900029A02000B004322090044003400B5000000B600000042379800180000025C0000025F000002600000026900FF026A00FF000000000000000001919E520441003FAAD25FFC3CAD10002200490B00000000001D001200160100470200F00100150400C80000EF01025800025900025A00025B00025D00025E00026100026B00026C00026D00029900029A02000B004322090044003400B5000000B600000042379800180000025C0000025F000002600000026900FF026A00FF000000000000000001919E520441003FAAD25FFC3CAD10002200490B00000000001D001200160100470200F00100150400C80000EF01025800025900025A00025B00025D00025E00026100026B00026C00026D00029900029A02000B004322090044003400B5000000B600000042379800180000025C0000025F000002600000026900FF026A00FF000000000000000001919E520441003FAAD25FFC3CAD10002200490B00000000001D001200160100470200F00100150400C80000EF01025800025900025A00025B00025D00025E00026100026B00026C00026D00029900029A02000B004322090044003400B5000000B600000042379800180000025C0000025F000002600000026900FF026A00FF000000000000000001919E520441003FAAD25FFC3CAD10002200490B00000000001D001200160100470200F00100150400C80000EF01025800025900025A00025B00025D00025E00026100026B00026C00026D00029900029A02000B004322090044003400B5000000B600000042379800180000025C0000025F000002600000026900FF026A00FF000000000000000001919E520441003FAAD25FFC3CAD10002200490B00000000001D001200160100470200F00100150400C80000EF01025800025900025A00025B00025D00025E00026100026B00026C00026D00029900029A02000B004322090044003400B5000000B600000042379800180000025C0000025F000002600000026900FF026A00FF000000000000000001919E520441003FAAD25FFC3CAD10002200490B00000000001D001200160100470200F00100150400C80000EF01025800025900025A00025B00025D00025E00026100026B00026C00026D00029900029A02000B004322090044003400B5000000B600000042379800180000025C0000025F000002600000026900FF026A00FF000000000000070000680E000000000000008B8E01000001919E527D4A003FAAD306FC3CACEF002200490C00000000001D001200160100470300F00100150400C80000EF01025800025900025A00025B00025D00025E00026100026B00026C00026D00029900029A02000B004322210044003400B5001300B600110042377F00180000025C0000025F000002600000026900FF026A00FF000000000000010000AFE5')
# json_result = decode(hex_data)
# print(json_result)


raw_dir = "raw-data-teltonika"
dest_dir = "parsed"
files = os.listdir(raw_dir)
for f in files:
    if not re.match("^\\w+\\.json$", f):
        continue

    with open(raw_dir + "\\" + f, 'r') as file:
        json_file = json.load(file)

    data = json_file['data']

    if not data.startswith("000F"):
        continue
    if len(data) < 418:
        continue

    print(f)
    hex_data = bytes.fromhex(data)
    json_result = decode(hex_data)

    with open(dest_dir + "\\" + f, "w") as outfile:
        outfile.write(json_result)