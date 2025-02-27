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

# make deepCoadd injection pipelines for rc2_subset and RC2
rc2_subset_injected_deepCoadd = env.Command(
    target=os.path.join(
        PKG_ROOT, "pipelines", "HSC", "DRP-RC2_subset+injected_deepCoadd.yaml"
    ),
    source=os.path.join(PKG_ROOT, "pipelines", "HSC", "DRP-RC2_subset.yaml"),
    action=" ".join(
        [
            libraryLoaderEnvironment(),
            "make_injection_pipeline -t deepCoadd -r $SOURCE -f $TARGET --overwrite",
        ]
    ),
)
RC2_injected_deepCoadd = env.Command(
    target=os.path.join(
        PKG_ROOT, "pipelines", "HSC", "DRP-RC2+injected_deepCoadd.yaml"
    ),
    source=os.path.join(PKG_ROOT, "pipelines", "HSC", "DRP-RC2.yaml"),
    action=" ".join(
        [
            libraryLoaderEnvironment(),
            "make_injection_pipeline -t deepCoadd -r $SOURCE -f $TARGET --overwrite",
        ]
    ),
)
Default([rc2_subset_injected_deepCoadd, RC2_injected_deepCoadd])
