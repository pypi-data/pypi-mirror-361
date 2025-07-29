

cfg = {
    "output_dir": "autotopas",
    "overwrite_scorer_outputs": False, # Whether to sett all scorers to "overwrite" if file exists
    "output_format": "binary",  # Default output format
    "topas_path": None,  # Path to the TOPAS executable, if None it will search in PATH and bashrc
    "suppress_topas_output": True,  # Whether to suppress TOPAS output in the console
    "geometry:print_children": True,  # Whether to print children in geometry dumps
    "write_parameter_summary": False,
}

