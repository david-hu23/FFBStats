FIGURE_OPTIONS = {
    "All Time Record": 0,
    "All Time Record - Adjusted (%)": 1,
    "All Time Points": 2,
    "All Time Points - Adjusted (Per Game)": 3,
    0: "All Time Record",
    1: "All Time Record - Adjusted (%)",
    2: "All Time Points",
    3: "All Time Points - Adjusted (Per Game)"
}

def is_all_time_point_figure(figure) -> bool:
    """ Returns True if a given figure option is related to All Time Points.
    Expects either string or int from dictionary FIGURE_FIGURE_OPTIONS.
    """
    if figure in [
            FIGURE_OPTIONS.get("All Time Points"),
            FIGURE_OPTIONS.get("All Time Points - Adjusted (Per Game)")]:
        return True
    elif figure in [FIGURE_OPTIONS.get(2), FIGURE_OPTIONS.get(3)]:
        return True
    else:
        return False

def is_all_time_record_figure(figure) -> bool:
    """ Returns True if a given figure option is related to All Time Records.
        Expects either string or int from dictionary FIGURE_FIGURE_OPTIONS.
    """
    if figure in [
            FIGURE_OPTIONS.get("All Time Record"),
            FIGURE_OPTIONS.get("All Time Record - Adjusted (%)")]:
        return True
    elif figure in [FIGURE_OPTIONS.get(0), FIGURE_OPTIONS.get(1)]:
        return True
    else:
        return False

def is_adjusted_figure_option(figure: int) -> bool:
    if figure == FIGURE_OPTIONS.get("All Time Points - Adjusted (Per Game)"):
        return True
    elif figure == FIGURE_OPTIONS.get("All Time Record - Adjusted (%)"):
        return True
    return False
