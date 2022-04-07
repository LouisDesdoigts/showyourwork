from ... import paths
from ..conda_env import run
from ..error_handler import error_handler


def build(options=""):
    """Build the article."""
    snakefile = paths.showyourwork().workflow / "build.smk"
    snakemake = f"SNAKEMAKE_OUTPUT_CACHE={paths.user().cache} snakemake -c1 --use-conda --reason --cache"
    command = f"{snakemake} {options} -s {snakefile}"
    result = run(command, check=False)
    error_handler(result.returncode)