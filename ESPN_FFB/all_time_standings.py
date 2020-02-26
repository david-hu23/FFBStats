import matplotlib.pyplot as plt
import numpy as np
from ESPN_FFB.axes_labels import AxesLabels
from ESPN_FFB.url_info import URLInfo
from ESPN_FFB.league_info import LeagueInfo
from ESPN_FFB.constants import ESPN_ID_TO_TEAM
from ESPN_FFB.figure_options import FIGURE_OPTIONS

def generate_all_time_graph(league_info: LeagueInfo, figure_option: int) -> bool:
    """ Main function for AllTimeStandings. Given a passed in figure_option, generates that figure.

        If parsed_json is populated, this is assumed to be cached off data from a previous request
        and we will not request new data from ESPN. If parsed_json is not populated, new requests
        will be sent to ESPN and parsed results will be stored.
    """
    url_info = URLInfo("mTeam", league_info)
    if league_info.is_cache_empty():
        league_info.cached_json, success = url_info.get_formatted_espn_data()
        if success is False:
            return False
    axes_labels = AxesLabels(figure_option)

    figure_heights = league_info.get_figure_heights(figure_option)
    prepare_figure(figure_option, figure_heights, axes_labels)
    plt.show()
    return True

def prepare_figure(figure_option, figure_heights: list, axes_labels: AxesLabels):
    """ Stating point for preparing bar graph.
    """
    x_ticks = np.arange(len(axes_labels.x_labels))
    figure, axes = plt.subplots(figsize=(16, 6))

    assign_figure_attributes(
        axes_labels, x_ticks, axes,
        FIGURE_OPTIONS.get(figure_option))

    prepare_figure_bars(figure_heights, x_ticks, figure, axes)

def assign_figure_attributes(axes_labels: AxesLabels, x_ticks, axes, title: str):
    axes.set_ylabel(axes_labels.y_label)
    axes.set_title(title)
    axes.set_xticks(x_ticks)
    axes.set_xticklabels(axes_labels.x_labels)

def prepare_figure_bars(figure_heights: list, x_ticks, fig, axes, width: float = 0.075):
    """ Generates the actual bars to display in a bar graph.
        Currently hardcoded to appropriately display and space 12 bars.
    """
    rects = generate_bars_per_team(figure_heights, x_ticks, axes, width)
    add_bar_labels(axes, rects)
    axes.legend(fontsize='medium', shadow=True, title='Teams', title_fontsize='large')
    fig.tight_layout()

def generate_bars_per_team(figure_heights: list, x_ticks, axes, width: float = 0.075):
    bars = []
    i = width*-6
    for team in ESPN_ID_TO_TEAM:
        bars.append(
            axes.bar(
                x_ticks + i,
                figure_heights[team - 1],
                width,
                label=ESPN_ID_TO_TEAM.get(team),
                linewidth=1,
                edgecolor='black')
            )
        i += width
    return bars

def add_bar_labels(axes, group_rects: list, vertical_offset: int = 3):
    """ Expects a list of responses from ax.bar(), each of which should itself be a list of bars.
        Prints value of the bar above the bar itself.
    """
    for rects in group_rects:
        for rect in rects:
            height = rect.get_height()
            if height == 0:
                continue
            axes.annotate('{}'.format(height),
                          xy=(rect.get_x() + rect.get_width() / 2, height),
                          xytext=(0, vertical_offset),
                          textcoords="offset points",
                          ha='center', va='bottom')

if __name__ == "__main__": #For Testing Purposes
    TEST_JSON = list()
    generate_all_time_graph(TEST_JSON, 3)
    generate_all_time_graph(TEST_JSON, 1)
