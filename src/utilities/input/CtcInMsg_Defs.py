class CtcInDataHeader:
    def __init__(self, srcID, msgBlockSeries, msgType, srcType, msgLength,
                 msgNumber, measurementTime_LSW, measurementTime_MSW):
        self.srcID = srcID
        self.msgBlockSeries = msgBlockSeries
        self.msgType = msgType
        self.srcType = srcType
        self.msgLength = msgLength
        self.msgNumber = msgNumber
        self.measurementTime_LSW = measurementTime_LSW
        self.measurementTime_MSW = measurementTime_MSW


class CtcInCommonMeasurement_3DPositionStruct:
    def __init__(self, hdr, trackNumber, range, azimuth, elevation, velocityNorth,
                 velocityEast, velocityUp, SNR, RCS, doppler, trackDescriptorFlag):
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
    def __init__(self, hdr, trackNumber):
        self.hdr = hdr
        self.trackNumber = trackNumber


class CtcInCommonSensorStatusStruct:
    def __init__(self, hdr, globalTimestampSeconds, globalTimestampNanoSeconds, synchronizationWord,
                 sensorStatus, warningFlag, sensorLat, sensorLon, sensorAlt, antennaAz):
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