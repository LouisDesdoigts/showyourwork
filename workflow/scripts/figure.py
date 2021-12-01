"""
Generates a figure output.
This script is called from the ``figure`` rule.

"""
import subprocess
from pathlib import Path
import shutil
import json
import os
import sys


# Hack to import our custom exception
sys.path.insert(0, str(Path(__file__).parents[1]))
from helpers.exceptions import ShowyourworkException


# Params defined in `../rules/figure.smk`
script_name = snakemake.params["script_name"]
script_cmd = snakemake.params["script_cmd"]
this_figure = snakemake.output[0]
this_figure_name = Path(this_figure).name
FIGURES = snakemake.params["FIGURES"]
TEMP = snakemake.params["TEMP"]
EXCEPTIONFILE = snakemake.params["EXCEPTIONFILE"]


# Get the names of all _other_ figures generated by the
# current script. Once they are created, we will move them
# to a temporary cache folder; the rule to generate them
# (which will be run later) will then simply copy them over
# to the output directory.
try:
    with open(TEMP / "scripts.json", "r") as f:
        scripts = json.load(f)
    for entry in scripts["figures"].values():
        if Path(entry["script"]).name == script_name:
            other_figures = [
                Path(file).name for file in entry["files"] if file != this_figure
            ]
            break
    else:
        other_figures = []
except FileNotFoundError:
    # If `scripts.json` doesn't exist for some reason,
    # fail silently without caching
    other_figures = []


# Add the `~/bin` directory to the PATH in case we require
# the `latex` installation.
env = dict(os.environ)
HOME = env["HOME"]
env["PATH"] += f":{HOME}/bin"


# Only enable caching if the script has multiple outputs,
# but the current rule only has one output!
if len(other_figures) != 0 and len(snakemake.output) == 1:

    # This script has multiple outputs.
    if (TEMP / this_figure_name).exists():

        # The figure exists in the cache; copy it over
        shutil.move(str(TEMP / this_figure_name), str(FIGURES / this_figure_name))

    else:

        # If the _other_ figures don't exist, we'll generate them and move them
        # to the cache file so the next time the rule is run, they will simply
        # be copied over. But if they *do* exist, we want to keep them in the
        # figures directory. We copy them over to the cache directory in case
        # they are deleted by a later rule for easy re-generation.
        copy_figures = []
        move_figures = []
        for figure in other_figures:
            if (FIGURES / figure).exists():
                copy_figures.append(figure)
            else:
                move_figures.append(figure)

        # We need to run the script
        try:
            subprocess.check_call(
                script_cmd.format(script=script_name, figure=this_figure_name),
                cwd=FIGURES,
                shell=True,
                env=env,
            )
        except Exception as e:
            raise ShowyourworkException(
                e,
                exception_file=EXCEPTIONFILE,
                script="figure.py",
                rule_name="figure",
                brief=f"An error occurred while running figure script {script_name}.",
                context=f"showyourwork attempted to run the script {script_name} to "
                f"to produce the figure file {this_figure_name}, but an error "
                "occurred. Please search the logs above for the detailed error "
                "message.",
            )

        # Cache the other figures
        for figure in copy_figures:
            shutil.copy2(str(FIGURES / figure), str(TEMP / figure))
        for figure in move_figures:
            shutil.move(str(FIGURES / figure), str(TEMP / figure))

else:

    # This script has only one output, so no need for caching
    try:
        subprocess.check_call(
            script_cmd.format(script=script_name, figure=this_figure_name),
            cwd=FIGURES,
            shell=True,
            env=env,
        )
    except Exception as e:
        raise ShowyourworkException(
            e,
            exception_file=EXCEPTIONFILE,
            script="figure.py",
            rule_name="figure",
            brief=f"An error occurred while running figure script {script_name}.",
            context=f"showyourwork attempted to run the script {script_name} to "
            f"to produce the figure file {this_figure_name}, but an error "
            "occurred. Please search the logs above for the detailed error "
            "message.",
        )
