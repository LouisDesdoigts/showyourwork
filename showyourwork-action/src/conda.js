// Imports
const core = require("@actions/core");
const cache = require("@actions/cache");
const shell = require("shelljs");
const { makeId, exec, getInputAsArray } = require("./utils");

// Exports
module.exports = { setupConda };


/**
 * Setup a conda distribution or restore it from cache.
 *
 */
async function setupConda(SHOWYOURWORK_VERSION) {

  // Cache settings
  const CONDA_CACHE_NUMBER = core.getInput("conda-cache-number");
  const RUNNER_OS = shell.env["RUNNER_OS"];
  const conda_key = `conda-dev3-${SHOWYOURWORK_VERSION}-${RUNNER_OS}-${CONDA_CACHE_NUMBER}`;
  const conda_restoreKeys = [];
  const conda_paths = ["~/.conda", "~/.condarc", "~/conda_pkgs_dir", "envs"];
  const CACHE_CONDA = !(CONDA_CACHE_NUMBER == null || CONDA_CACHE_NUMBER == "");

  // Restore conda cache
  if (CACHE_CONDA) {
    core.startGroup("Restore conda cache");
    const conda_cacheKey = await cache.restoreCache(
      conda_paths,
      conda_key,
      conda_restoreKeys
    );
    core.endGroup();
  }

  // Download and setup conda
  if (!shell.test("-d", "~/.conda")) {
    const CONDA_URL = core.getInput("conda-url");
    exec(`wget --no-verbose ${CONDA_URL} -O ./conda.sh`, "Download conda");
    exec("bash ./conda.sh -b -p ~/.conda && rm -f ./conda.sh", "Install conda");
    exec(
      ". ~/.conda/etc/profile.d/conda.sh && " +
        "conda config --add pkgs_dirs ~/conda_pkgs_dir"
    );
  }

  // Display some info
  exec(". ~/.conda/etc/profile.d/conda.sh && conda info", "Conda info");

  // Create environment
  if (!shell.test("-d", "./envs")) {
    exec(
      ". ~/.conda/etc/profile.d/conda.sh && conda create -y -p ./envs",
      "Create environment"
    );
    exec(
      "conda install -y -c defaults -c conda-forge -c bioconda mamba==0.17.0 snakemake-minimal==6.12.3 jinja2==2.11.3",
      "Install mamba, snakemake-minimal, and jinja2"
    );
  }

  // Save conda cache (failure OK)
  if (CACHE_CONDA) {
    try {
      core.startGroup("Update conda cache");
      const conda_cacheId = await cache.saveCache(conda_paths, conda_key);
      core.endGroup();
    } catch (error) {
      core.warning(error.message);
    }
  }
}
