class CtcInDataHeader:
    """
    Represents the CtcInDataHeader messages passed from the radar during listen mode.

    Attributes:
        srcID: The ID of the sensor producing this message.
        msgBlockSeries: The message block series of the message (likely to be 30).
        msgType: The message type of the message (either 1, 2, or 3).
        srcType: The type of system producing this message.
        msgLength: The total message length, including header and body (in bytes).
        msgNumber: The message number of the message.
        measurementTime_LSW: The measurement of the message (time since UTC midnight).
        measurementTime_MSW: The measurement of the message (time since UTC midnight).
    """
    def __init__(self, srcID, msgBlockSeries, msgType, srcType, msgLength,
                 msgNumber, measurementTime_LSW, measurementTime_MSW):
        """
        Initializes the CtcInDataHeader class attributes.
        :param srcID: The ID of the sensor producing this message.
        :param msgBlockSeries: The message block series of the message (likely to be 30).
        :param msgType: The message type of the message (either 1, 2, or 3).
        :param srcType: The type of system producing this message.
        :param msgLength: The total message length, including header and body (in bytes).
        :param msgNumber: The message number of the message.
        :param measurementTime_LSW: The measurement of the message (time since UTC midnight).
        :param measurementTime_MSW: The measurement of the message (time since UTC midnight).
        """
        self.srcID = srcID
        self.msgBlockSeries = msgBlockSeries
        self.msgType = msgType
        self.srcType = srcType
        self.msgLength = msgLength
        self.msgNumber = msgNumber
        self.measurementTime_LSW = measurementTime_LSW
        self.measurementTime_MSW = measurementTime_MSW


class CtcInCommonMeasurement_3DPositionStruct:
    """
    Represents the CtcInCommonMeasurement_3DPositionStruct messages passed from the radar during listen mode.

    Attributes:
        hdr: The message header (a CtcInDataHeader object).
        trackNumber: The track number of the message.
        range: The distance of the object from the sensor (in meters).
        azimuth: The azimuth angle of the object (degrees clockwise from true north, looking down).
        elevation: The elevation angle of the object (degrees up from vertical plane).
        velocityNorth: The northward component of the object's velocity (in meters per second).
        velocityEast: The eastward component of the object's velocity (in meters per second).
        velocityUp: The upward component of the object's velocity (in meters per second).
        SNR: The signal-to-noise ratio (in dB).
        RCS: The radar cross-section of the object (in dBsm).
        doppler: The measured range rate (in meters per second).
        trackDescriptorFlag: The track descriptor flag of the object.
    """
    def __init__(self, hdr, trackNumber, range, azimuth, elevation, velocityNorth,
                 velocityEast, velocityUp, SNR, RCS, doppler, trackDescriptorFlag):
        """
        Initializes the CtcInCommonMeasurement_3DPositionStruct class attributes.
        :param hdr: The message header (a CtcInDataHeader object).
        :param trackNumber: The track number of the message.
        :param range: The distance of the object from the sensor (in meters).
        :param azimuth: The azimuth angle of the object (degrees clockwise from true north, looking down).
        :param elevation: The elevation angle of the object (degrees up from vertical plane).
        :param velocityNorth: The northward component of the object's velocity (in meters per second).
        :param velocityEast: The eastward component of the object's velocity (in meters per second).
        :param velocityUp: The upward component of the object's velocity (in meters per second).
        :param SNR: The signal-to-noise ratio (in dB).
        :param RCS: The radar cross-section of the object (in dBsm).
        :param doppler: The measured range rate (in meters per second).
        :param trackDescriptorFlag: The track descriptor flag of the object.
        """
        self.hdr = hdr
        self.trackNumber = trackNumber
        self.range = range
        self.azimuth = azimuth
        self.elevation = elevation
        self.velocityNorth = velocityNorth
        self.velocityEast = velocityEast
        self.velocityUp = velocityUp
        self.SNR = SNR
        self.RCS = RCS
        self.doppler = doppler
        self.trackDescriptorFlag = trackDescriptorFlag


class CtcInCommonTrackDropStruct:
    """
    Represents the CtcInCommonTrackDropStruct messages passed from the radar during listen mode.

    Attributes:
        hdr: The message header (a CtcInDataHeader object).
        trackNumber: The track number to be dropped.
    """
    def __init__(self, hdr, trackNumber):
        """
        Initializes the CtcInCommonTrackDropStruct class attributes.
        :param hdr: The message header (a CtcInDataHeader object).
        :param trackNumber: The track number to be dropped.
        """
        self.hdr = hdr
        self.trackNumber = trackNumber


class CtcInCommonSensorStatusStruct:
    """
    Represents the CtcInCommonSensorStatusStruct messages passed from the radar during listen mode.

    Attributes:
        hdr: The message header (a CtcInDataHeader object).
        globalTimestampSeconds: Global time stamp in seconds.
        globalTimestampNanoSeconds: Global time stamp in nanoseconds.
        synchronizationWord: Always 1,129,208,147.
        sensorStatus: Bit field.
        warningFlag: Bit field.
        sensorLat: The latitude of the sensor.
        sensorLon: The longitude of the sensor.
        sensorAlt: The altitude of the sensor.
        antennaAz: The azimuth angle of the sensor antenna.
    """
    def __init__(self, hdr, globalTimestampSeconds, globalTimestampNanoSeconds, synchronizationWord,
                 sensorStatus, warningFlag, sensorLat, sensorLon, sensorAlt, antennaAz):
        """
        Initializes the CtcInCommonSensorStatusStruct class attributes.
        :param hdr: The message header (a CtcInDataHeader object).
        :param globalTimestampSeconds: Global time stamp in seconds.
        :param globalTimestampNanoSeconds: Global time stamp in nanoseconds.
        :param synchronizationWord: Always 1,129,208,147.
        :param sensorStatus: Bit field.
        :param warningFlag: Bit field.
        :param sensorLat: The latitude of the sensor.
        :param sensorLon: The longitude of the sensor.
        :param sensorAlt: The altitude of the sensor.
        :param antennaAz: The azimuth angle of the sensor antenna.
        """
        self.hdr = hdr
        self.globalTimestampSeconds = globalTimestampSeconds
        self.globalTimestampNanoSeconds = globalTimestampNanoSeconds
        self.synchronizationWord = synchronizationWord
        self.sensorStatus = sensorStatus
        self.warningFlag = warningFlag
        self.sensorLat = sensorLat
        self.sensorLon = sensorLon
        self.sensorAlt = sensorAlt
        self.antennaAz = antennaAz
