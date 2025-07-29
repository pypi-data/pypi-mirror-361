from topasio.elements.geometry import Ge
from topasio.elements.source import So
from topasio.elements.scorer import Sc
from topasio.spaces.Ts import Ts
from topasio.spaces.Gr import Gr
from topasio.spaces.Ma import Ma

from topasio.config import cfg
from topasio.output_conversion.output_conversion import write_to_parquet
from pprint import pprint
import os
import subprocess
import re
import logging
from pprint import pformat


logger = logging.getLogger("topasio")
spaces = [Ge, Gr, So, Sc, Ts, Ma] # Ge must be first since it adds header to all files it creates


def dump_spaces():
    scorer_format = cfg["output_format"]

    if scorer_format not in ["binary", "csv", "parquet"]:
        raise ValueError(
            f"Invalid scorer output format: {scorer_format}. Choose from 'binary', 'csv', or 'parquet'."
        )
    if scorer_format != "parquet":
        Sc.set_outputs_to(scorer_format)
    else:
        Sc.set_outputs_to(
            "binary"
        )  # Parquet is not supported by TOPAS, so we use binary instead

    for space in spaces:  
        if space["_modified"]:
            logger.info(
                f"Dumping {space['_name']} to file: {cfg['output_dir']}. It has {len(space['_modified'])} modified attributes."
            )
            space.dumpToFile(cfg['output_dir'])

def set_scorer_output_path() -> str:
    output_dir = cfg["output_dir"]
    i = 0
    while True:
        output_path = os.path.join(output_dir, "outputs", f"topas_output_{i}")

        if os.path.exists(output_path):
            if len(os.listdir(output_path)) == 0:
                break

        if not os.path.exists(output_path):
            os.makedirs(output_path)
            break
        i += 1
    
    for elemName in Sc["_modified"]:
        Sc[elemName].OutputFile = os.path.join(output_path, elemName)
    
    return output_path


def find_topas_executable():
    # Check if TOPAS is installed in the default location

    if cfg["topas_path"]:
        return os.path.expanduser(os.path.expandvars(cfg["topas_path"]))

    topas_default_path = (
        f"/home/{os.getenv('USER')}/Applications/TOPAS/OpenTOPAS-install/bin/topas"
    )
    if os.path.exists(topas_default_path):
        print(f"Found TOPAS executable at its default path: {topas_default_path}")
        return topas_default_path

    for path in os.environ["PATH"].split(os.pathsep):
        # Check if the path contains topas
        matches = re.findall(r"topas", path, re.IGNORECASE)
        if matches:
            potential_path = os.path.join(path, "topas")
            if os.path.exists(potential_path):
                print(f"Found TOPAS executable at: {potential_path}")
                return potential_path

    with open(f"/home/{os.getenv('USER')}/.bashrc", "r") as f:
        for line in f.readlines():
            alias = re.findall(r"alias\s+(.+)\s*=\s*['\"]?([^'\"]+)['\"]?", line)

            if not alias:
                continue
            alias_name, alias_path = alias[0]
            alias_path = alias_path.strip("\n\"'")
            alias_path = alias_path.strip()
            alias_path = os.path.expanduser(alias_path)  # Expand ~ to home directory
            alias_path = os.path.expandvars(alias_path)  # Expand environment variables

            if "topas" in alias_name.lower():
                # Check if the alias points to a valid path

                if os.path.exists(alias_path):
                    # print(f"Found TOPAS executable since 'topas' is in name.  {alias_name} -> {alias_path}")
                    return alias_path
            if "topas" in alias_path.lower():
                # Check if the alias path is a valid executable
                if os.path.exists(alias_path):
                    # print(f"Found TOPAS executable since 'topas' is in path. Full alias is: {alias_name} -> {alias_path}")
                    return alias_path

    raise FileNotFoundError(
        """
Could not find the TOPAS executable. Please ensure that TOPAS is installed. 
When searching for the executable, the following locations were checked:
    1. $PATH environment variable
    2. $HOME/.bashrc aliases with 'topas' in the name or path
    3. Default TOPAS installation path: /home/{os.getenv('USER')}/Applications/TOPAS/OpenTOPAS-install/bin/topas
If TOPAS is installed in a different location, please set the 'topas_path' in
topasio.config.cfg to the correct path of the TOPAS executable.""".removeprefix(
            "\n"
        ).strip()
    )


def create_script():
    if Gr["_enable"] or Gr.Enable:
        redirection = ""
    else:
        redirection = "&> "
        if cfg["suppress_topas_output"]:
            redirection += "/dev/null"
        else:
            redirection += os.path.join(cfg["output_dir"], "topas_output.log")

    topas_exe_location = find_topas_executable()

    script_content = f"""#!/bin/bash
    start_time=$(date +%m)
    {topas_exe_location} {cfg["output_dir"]}/main.tps {redirection}
    duration=$SECONDS
    hours=$(($duration / 3600))
    minutes=$((($duration % 3600) / 60))
    seconds=$(($duration % 60))
    echo "Simulation completed in $hours hours, $minutes minutes, and $seconds seconds."
    """
    print(f'executing: {topas_exe_location} {cfg["output_dir"]}/main.tps {redirection}')
    script_path = os.path.join(cfg["output_dir"], "temp.sh")

    with open(script_path, "w+") as script_file:
        script_file.write(script_content)

    os.chmod(script_path, 0o755)  # Make the script executable

    return script_path


def clean_dir():
    for dirpath, dirnames, filenames in os.walk(cfg["output_dir"]):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if file_path.endswith(".tps"):
                # print(f"Removing existing file: {file_path}")
                os.remove(file_path)


def run_simulation(view_only=False):

    if view_only:
        Gr.enable()
        for elemName in So["_modified"]:
            if hasattr(So[elemName], "Type"):
                So[elemName].NumberOfHistoriesInRun = 0
                So[elemName].NumberOfRuns = 0

    # remove previous tps files
    logger.info(
        f"Removing previous .tps files from output directory {cfg['output_dir']}."
    )
    clean_dir()

    output_location = set_scorer_output_path()

    # write new files
    dump_spaces()
    
    if cfg["write_parameter_summary"] and not view_only:
        with open(os.path.join(output_location, "topas_params.txt"), "w+") as f:
            res = dict()
            for space in spaces:
                res[space["_name"]] = dict()
                for elemName in space["_modified"]:
                    if hasattr(space[elemName], "items"):
                        res[space["_name"]][elemName] = {k: v for k, v in space[elemName].items() if k in space[elemName]["_modified"] and not k.startswith("_")}
                    else:
                        res[space["_name"]][elemName] = space[elemName]
            f.write(pformat(res, indent=4))

    script_path = create_script()
    logger.info(f"Simulation script created at: {script_path}")
    logger.info(f"Running simulation script: {script_path}")
    print(flush=True, end="")

    # Run the script
    try:
        subprocess.call(script_path)
    except subprocess.CalledProcessError as e:
        logger.error("Error occurred while running the simulation script:")
        logger.error(e.stderr)
        raise RuntimeError(f"Simulation failed with error: {e.stderr.strip()}") from e

    os.remove(script_path)  # Clean up the script after execution

    if cfg["output_format"] == "parquet":
        for filename in os.listdir(output_location):
            if filename.endswith(".bin") or filename.endswith(".csv"):
                filepath = os.path.join(output_location, filename)
                write_to_parquet(filepath)

        for filename in os.listdir(output_location):
            if filename.endswith(".bin") or filename.endswith(".csv") or filename.endswith(".binheader"):
                filepath = os.path.join(output_location, filename)
                parent = os.path.dirname(filepath)
                new_folder = os.path.join(parent, "original_output")
                os.makedirs(new_folder, exist_ok=True)
                # print("old path:", filepath)
                # print("new path:", os.path.join(new_folder, filename))
                os.rename(filepath, os.path.join(new_folder, filename))

            
