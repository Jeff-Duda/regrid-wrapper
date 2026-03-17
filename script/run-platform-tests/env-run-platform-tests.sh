#!/usr/bin/env bash


# ----------
# test flags
# ----------

# if TRUE, run unit tests using pytest
run_unit_tests=TRUE
# if TRUE, run the chem_regrid application test
run_chem_regrid=TRUE

# -------------------------------
# platform-specific configuration
# -------------------------------

if [[ ${HOSTNAME} == gaea6* ]]; then
  platform="gaeac6"
  account="bil-fire8"
  cluster="--clusters=c6"
  partition=" --partition=batch"

  # root directory of the regrid-wrapper project
  rw_dir=/gpfs/f6/bil-fire8/scratch/Benjamin.Koziol/sandbox/git-benkozi/regrid-wrapper
  # temporary directory for test outputs
  rw_test_dir=/autofs/ncrc-svm1_home2/Benjamin.Koziol/htmp/rw-testing

  # -----------
  # chem_regrid
  # -----------

  # cycle time in YYYYMMDDHH format
  cr_cycle=2026031600
  # input directory for chem_regrid
  cr_input_dir=/gpfs/f6/gsl-data-depot/world-shared/data/grids/nesdis/3km_fire_emissions
  # output directory for chem_regrid
  cr_output_dir=/gpfs/f6/bil-fire8/scratch/Benjamin.Koziol/data/mpas-aerosols/test-chem-regrid
  # path to source UGRID file
  cr_scrip_path=/gpfs/f6/drsa-fire3/world-shared/Sudheer/MPAS/mpas-jedi/regridderBen/scrip_files/ugrid_fwx1.25km.nc
  # path to destination grid file (init.nc)
  cr_dst_path=/gpfs/f6/drsa-fire3/world-shared/Sudheer/Retros/MPAS/FWx1.25km/fwx.20250310/stmp/20260310/rrfs_ic_00_v2.1.2/det/ic_00/init.nc

elif [[ ${HOSTNAME} == ufe* ]]; then
  platform="ursa"
  account="epic"
  cluster=""
  partition=""

  # temporary directory for test outputs
  rw_test_dir=/home/Benjamin.Koziol/htmp/rw-testing
  # root directory of the regrid-wrapper project
  rw_dir=/scratch3/NCEPDEV/stmp/Benjamin.Koziol/sandbox/git-benkozi/regrid-wrapper

  # -----------
  # chem_regrid
  # -----------

  # cycle time in YYYYMMDDHH format
  cr_cycle=2026031200
  # input directory for chem_regrid
  cr_input_dir=/scratch4/BMC/public/data/grids/nesdis/3km_fire_emissions
  # output directory for chem_regrid
  cr_output_dir=/scratch3/NCEPDEV/stmp/Benjamin.Koziol/sandbox/data/mpas-aerosols/test-chem-regrid
  # path to source SCRIP file
  cr_scrip_path=/scratch4/BMC/acomp/Sudheer/Fire-nest/Shared/to_JeffDuda/scrip_files/ugrid_fwx1.25km.nc
  # path to destination grid file (init.nc)
  cr_dst_path=/scratch3/NCEPDEV/stmp/Benjamin.Koziol/sandbox/data/mpas-aerosols/init_5055722_cells.nc

else
  echo "${HOSTNAME}" not recognized && exit 1
fi

# --------------------------------
# global chem_regrid configuration
# --------------------------------

# if TRUE, remove all files in cr_output_dir before running
cr_clean_output_dir=TRUE
# number of MPI tasks for srun
cr_ntasks=192
# wall time for srun
cr_wtime=00:15:00
# emissions cycle type
export EBB_DCYCLE=1
# name of the input dataset to regrid
cr_dataset_name=RAVE
# working directory for chem_regrid
cr_workdir=${cr_output_dir}
# directory for storing regrid weights
cr_weight_dir=${cr_output_dir}
# name of the mesh/domain
cr_mesh_name=1_25

# ---------------------------------------------
# set up modules and regrid-wrapper environment
# ---------------------------------------------

module purge

# directory for log files
export REGRID_WRAPPER_LOG_DIR=$(readlink -f .)
# target platform name
export REGRID_WRAPPER_PLATFORM=${platform}
# temporary directory for tests
export REGRID_WRAPPER_TEST_TMPDIR=${rw_test_dir}

module use modulefiles
module load regrid-wrapper-spack-stack.${platform}
module list
# include project src in PYTHONPATH
export PYTHONPATH=${rw_dir}/src:${PYTHONPATH:-}
