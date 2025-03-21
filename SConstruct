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

injected_pipeline_RC2 = os.path.join(
    PKG_ROOT,
    "pipelines",
    "HSC",
    "DRP-RC2-post-injected-stars.yaml",
)

injection_descriptions = {
    "stars": "Bright stars",
    "DC2": "DC2 stars and galaxies",
}
injected_pipelines_LSSTComCam = {
    suffix: os.path.join(
        PKG_ROOT,
        "pipelines",
        "LSSTComCam",
        f"DRP-post-injected-{suffix}.yaml",
    )
    for suffix in injection_descriptions
}

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
            f"make_injection_pipeline -t deepCoadd -r $SOURCE -f $TARGET -a {injected_pipeline_RC2} "
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
            f"make_injection_pipeline -t deepCoadd -r $SOURCE -f $TARGET -a {injected_pipeline_RC2} "
            f"-s {subset_name} -d '{subset_description}' --overwrite",
        ]
    ),
)
LSSTComCam_excluded_tasks = ','.join([
    "gbdesAstrometricFit",
    "fgcmBuildFromIsolatedStars",
    "fgcmFitCycle",
    "fgcmOutputProducts",
    "skyCorr",
])

subset_name = "injected_{suffix}_coadd_analysis"

LSSTComCam_injected = [
    env.Command(
        target=os.path.join(
            PKG_ROOT, "pipelines", "LSSTComCam", f"DRP+injected_deep_coadd_{suffix}.yaml"
        ),
        source=os.path.join(PKG_ROOT, "pipelines", "LSSTComCam", "DRP-v2-compat.yaml"),
        action=" ".join(
            [
                libraryLoaderEnvironment(),
                f"make_injection_pipeline -t deep_coadd_predetection -r $SOURCE -f $TARGET -a {pipeline_post} "
                f"-s {subset_name.format(suffix=suffix)} -d '{injection_descriptions[suffix]}' "
                f"-x {LSSTComCam_excluded_tasks} --overwrite",
            ]
        ),
    )
    for suffix, pipeline_post in injected_pipelines_LSSTComCam.items()
]
Default(
    [
        rc2_subset_injected_deepCoadd_stars,
        RC2_injected_deepCoadd_stars,
    ] + LSSTComCam_injected
)
