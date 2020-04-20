# -*- coding: utf-8 -*-

from datetime import datetime


class ProgressTracker(object):
    """
    From https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
    """

    def __init__(self, number_of_objects_for_processing, object_type_name='objects', decimals=1, length=50, fill='#'):
        self._number_of_objects_for_processing = number_of_objects_for_processing

        self._object_type_name = object_type_name
        self._decimals=decimals
        self._length=length
        self._fill = fill

        self._objects_processed = 0
        self.start = datetime.now()

    def processed_object(self, progress=None):
        if progress is None:
            self._objects_processed += 1
        else:
            self._objects_processed = progress

        duration = datetime.now() - self.start

        prefix = 'Processing %d/%d %s: ' %\
                 (self._objects_processed, self._number_of_objects_for_processing, self._object_type_name)

        filled_length = int(self._length * self._objects_processed // self._number_of_objects_for_processing)
        progress_bar = self._fill * filled_length + '-' * (self._length - filled_length)

        suffix = ' Duration: %s' % str(duration)

        percent = 100 * (self._objects_processed / float(self._number_of_objects_for_processing))
        percent_str = ("{0:." + str(self._decimals) + "f}").format(percent)

        print('\r%s |%s| %s%% %s' % (prefix, progress_bar, percent_str, suffix), end='\r')

        if self._objects_processed == self._number_of_objects_for_processing:
            print()

