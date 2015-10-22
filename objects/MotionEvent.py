__author__ = 'adean'


class MotionEvent(object):
    def __init__(self, mediaFile, sendNotification, eventTime, eventId, fileType):
        self.mediaFile = mediaFile
        self.eventTime = eventTime
        self.sendNotification = sendNotification
        self.eventId = eventId
        self.fileType = fileType
