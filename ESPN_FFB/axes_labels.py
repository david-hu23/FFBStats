from ESPN_FFB.constants import STATS_TAGS, AXES_LABELS
from ESPN_FFB.figure_options import (is_all_time_point_figure, is_all_time_record_figure,
                                     is_adjusted_figure_option)

class AxesLabels():

    def __init__(self, figure_option: int):
        if is_all_time_record_figure(figure_option):
            self._set_all_time_record_labels(figure_option)
        elif is_all_time_point_figure(figure_option):
            self._set_all_time_point_labels()
        else:
            self.x_labels = None
            self.y_label = None

    def _set_all_time_record_labels(self, figure_option: int):
        self.x_labels = [STATS_TAGS.get(0), STATS_TAGS.get(1), STATS_TAGS.get(2)]

        if is_adjusted_figure_option(figure_option):
            self.y_label = AXES_LABELS.get(2)
        else:
            self.y_label = AXES_LABELS.get(0)

    def _set_all_time_point_labels(self):
        self.x_labels = [STATS_TAGS.get(3), STATS_TAGS.get(4)]
        self.y_label = AXES_LABELS.get(1)
