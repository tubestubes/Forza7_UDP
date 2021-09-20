### Tools to record UDP Telemetry from Forza 7 
#  (c) William Kane 2021
#
### INSTRUCTIONS
#   Point your games Date Out to this IP of this machine (you can get this from ipconfig)
#   Set the port in game to match this port (you can set this to be anything)
PORT = 6969
#
### API
#   FUNC: receive(port)
#       USAGE: Call with port = PORT
#       RETURNS: One packet of telemetry as a dict
#
#   FUNC: receive_one(port, param)
#       USAGE: Call with port = PORT, param = 'param' where 'param' is a STRING of the paramater you want
#       RETURNS: One element of one packet of telemetry
#
#   Func: record_one(port, param, length)
#       USAGE: Call with port = PORT, param = string: the parameter you want, length = int: the time to record for
#       RETURNS: a list of that param over time
#
#   Func: record_list(port, param, length)
#       USAGE: Call with port = PORT, param = LIST of STRINGS: the parameters you want, length = int: the time to record for
#       RETURNS: a list of lists of the params over time



import socket
import struct
import logging; logging.basicConfig(level=logging.WARNING)
import time
import jupyterplot

# Tools to convert raw data to numbers
# The format of each of the 85 parameters.
formats = ['s32','u32','f32','f32','f32','f32','f32','f32','f32','f32','f32','f32','f32','f32','f32','f32','f32',
'f32','f32','f32','f32','f32','f32','f32','f32','f32','f32','f32','f32','s32','s32','s32','s32','f32','f32','f32',
'f32','f32','f32','f32','f32','f32','f32','f32','f32','f32','f32','f32','f32','f32','f32','f32','f32','s32','s32',
's32','s32','s32','f32','f32','f32','f32','f32','f32','f32','f32','f32','f32','f32','f32','f32','f32','f32','f32',
'f32','u16','u8','u8','u8','u8','u8','u8','s8','s8','s8'
]

keys = [ 'On/Off', 'Time', 'MaxRPM', 'IdleRPM', 'RPM', 'AccX', 'AccY', 'AccZ', 'VelX', 'VelY', 'VelZ', 'RotX', 
'RotY', 'RotZ', 'Yaw', 'Pitch', 'Roll', 'NSusFL', 'NSusFR', 'NSusRL', 'NSusRR', 'SlipFL', 'SlipFR', 'SlipRL','SlipRR', 
'WSpeedFL', 'WSpeedFR', 'WSpeedRL', 'WSpeedRR', 'OnRumFL', 'OnRumFR', 'OnRumRL', 'OnRumRR', 'PuddleFL', 'PuddleFR', 
'PuddleRL', 'PuddleRR', 'sRumFL', 'sRumFR', 'sRumRL', 'sRumRR', 'SAngFL', 'SAngFR', 'SAngRL', 'SAngRR', 'CSlipFL', 
'CSlipFR','CSlipRL','CSlipRR', 'SusFL', 'SusFR', 'SusRL', 'SusRR', 'Car', 'Class', 'PI', 'DriveTrain', 'NCylinders', 
'X', 'Y', 'Z', 'Speed', 'Power', 'Torque', 'TempFL', 'TempFR', 'TempRL', 'TempRR', 'Boost', 'Fuel', 'Dist', 'BestLap',
'LastLap', 'CurrentLap', 'RaceTime', 'Lap', 'Pos', 'Acc', 'Brake', 'Clutch', 'Handbreak', 'Gear', 'Steer', 'NLine', 'AiBreak'
]
logging.debug(dict(zip(keys, formats)))

def convert(raw):

    raw_i = 0  # Working index in the raw data
    output = {}

    for i, fmt in enumerate(formats):

        key = keys[i]
        logging.debug((i,fmt, key, raw_i))

        if fmt == 'f32':
            output[key] = struct.unpack('<f', raw[raw_i : raw_i + 4])[0]
            raw_i = raw_i + 4 

        if fmt == 'u32':
            output[key] = struct.unpack('<L',raw[raw_i : raw_i + 4])[0]
            raw_i = raw_i + 4 

        if fmt == 'u16':
            output[key] = struct.unpack('<H',raw[raw_i : raw_i + 2])[0]
            raw_i = raw_i + 2 
        
        if fmt == 's32':
            output[key] = struct.unpack('<i',raw[raw_i:raw_i + 4])[0]
            raw_i = raw_i + 4 
        
        if fmt == 'u8':
            output[key] = struct.unpack('<B',raw[raw_i:raw_i + 1])[0]
            raw_i = raw_i + 1 

        if fmt == 's8':
            output[key] = struct.unpack('<B',raw[raw_i:raw_i + 1])[0]
            raw_i = raw_i + 1 

    return output

# Connect to UDP and receive packet
def receive(port:int ):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as soc:
        soc.bind(('', port))
        raw = soc.recv(port)
        logging.info('Received data')
    logging.debug(raw)

    data = convert(raw)
    return data

def receive_one(port:int, param:str ):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as soc:
        soc.bind(('', port))
        raw = soc.recv(port)
        logging.info('Received data')
    logging.debug(raw)

    data = convert(raw)
    return data[param]

# Record one paramater live, with graph
def record_one(port, param, length):
    points = []
    plot = jupyterplot.ProgressPlot()
    start = time.time()
    while time.time() < start + length:
        data = receive(port)
        points.append( data[param])
        plot.update(data[param])
    plot.finalize()
    return points

def record_list(port, params: list, length):
    points = []
    plot = jupyterplot.ProgressPlot(line_names=params)
    start = time.time()
    while time.time() < start + length:
        data = receive(port)
        points.append( [data[param] for param in params] )
        plot.update( [[data[param] for param in params]] )
    plot.finalize()
    return points