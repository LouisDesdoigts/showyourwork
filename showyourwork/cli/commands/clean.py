from ... import paths
from ..conda_env import run
import shutil


def clean(options=""):
    """Clean the article build."""
    for file in ["build.smk", "preprocess.smk"]:
        snakefile = paths.showyourwork().workflow / file
        snakemake = f"SNAKEMAKE_OUTPUT_CACHE={paths.user().cache} snakemake -c1 --use-conda --reason --cache"
        command = f"{snakemake} {options} -s {snakefile} --delete-all-output"
        result = run(command)
    if (paths.user().repo / "arxiv.tar.gz").exists():
        (paths.user().repo / "arxiv.tar.gz").unlink()
    if paths.user().temp.exists():
        shutil.rmtree(paths.user().temp)