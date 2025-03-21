# -*- python -*-
import os

from lsst.sconsUtils import scripts
from lsst.sconsUtils.state import env
from lsst.sconsUtils.utils import libraryLoaderEnvironment
from SCons.Script import Default

# Python-only package
# Force shebang and policy to come first so the file first appears in the bin
# directory before it is used. This is required to run on macos.
targetList = (
    "version",
    "shebang",
    "policy",
) + scripts.DEFAULT_TARGETS
scripts.BasicSConstruct(
    "drp_pipe", disableCc=True, noCfgFile=True, defaultTargets=targetList
)
PKG_ROOT = env.ProductDir("drp_pipe")

additional_pipeline_RC2 = os.path.join(
    PKG_ROOT,
    "pipelines",
    "HSC",
    "DRP-RC2-post-injected-stars.yaml",
)

additional_pipeline_LSSTComCam = os.path.join(
    PKG_ROOT,
    "pipelines",
    "LSSTComCam",
    "DRP-post-injected-stars.yaml",
)

subset_name = "injected_stars_coadd_analysis"
subset_description = "Analysis tasks for object_table level injected catalogs."


# Make deepCoadd injection pipelines for rc2_subset, RC2, and LSSTComCam.
rc2_subset_injected_deepCoadd_stars = env.Command(
    target=os.path.join(
        PKG_ROOT, "pipelines", "HSC", "DRP-RC2_subset+injected_deepCoadd_stars.yaml"
    ),
    source=os.path.join(PKG_ROOT, "pipelines", "HSC", "DRP-RC2_subset.yaml"),
    action=" ".join(
        [
            libraryLoaderEnvironment(),
            f"make_injection_pipeline -t deepCoadd -r $SOURCE -f $TARGET -a {additional_pipeline_RC2} "
            f"-s {subset_name} -d '{subset_description}' --overwrite",
        ]
    ),
)
RC2_injected_deepCoadd_stars = env.Command(
    target=os.path.join(
        PKG_ROOT, "pipelines", "HSC", "DRP-RC2+injected_deepCoadd_stars.yaml"
    ),
    source=os.path.join(PKG_ROOT, "pipelines", "HSC", "DRP-RC2.yaml"),
    action=" ".join(
        [
            libraryLoaderEnvironment(),
            f"make_injection_pipeline -t deepCoadd -r $SOURCE -f $TARGET -a {additional_pipeline_RC2} "
            f"-s {subset_name} -d '{subset_description}' --overwrite",
        ]
    ),
)
LSSTComCam_excluded_tasks = [
    "jointcal",
    "gbdesAstrometricFit",
    "fgcmBuildFromIsolatedStars",
    "fgcmFitCycle",
    "fgcmOutputProducts",
    "skyCorr",
]
LSSTComCam_injected_deepCoadd_stars = env.Command(
    target=os.path.join(
        PKG_ROOT, "pipelines", "LSSTComCam", "DRP+injected_deepCoadd_stars.yaml"
    ),
    source=os.path.join(PKG_ROOT, "pipelines", "LSSTComCam", "DRP.yaml"),
    action=" ".join(
        [
            libraryLoaderEnvironment(),
            f"make_injection_pipeline -t deepCoadd -r $SOURCE -f $TARGET -a {additional_pipeline_LSSTComCam} "
            f"-s {subset_name} -d '{subset_description}' -x {','.join(LSSTComCam_excluded_tasks)} "
            "--overwrite",
        ]
    ),
)
Default(
    [
        rc2_subset_injected_deepCoadd_stars,
        RC2_injected_deepCoadd_stars,
        LSSTComCam_injected_deepCoadd_stars,
    ]
)
