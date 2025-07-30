from enum import StrEnum


class PROJECT_FOLDERS(StrEnum):
    rawdata = "data_raw"
    treated_data = "data_treated"
    scripts = "py_scripts"
    nb_models = "notebooks_models"
    nb_exploration = "notebooks_exploration_cleaning" 