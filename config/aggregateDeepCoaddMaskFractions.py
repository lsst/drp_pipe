# This content needs to go in a file, not a Python block or YAML override,
# because in (at least) _ingredients/LSSTCam/DRP.yaml, it needs to fire before
# another file-based config
# ($ANALYSIS_TOOLS_DIR/config/wholeTractMaskFractionMetrics.py) override and
# files always apply first.

# Reset to just the mask planes actually present in the cell-based coadds.
config.maskPlanes = [
    "NO_DATA",
    "INTRP",
    "CR",
    "SAT",
    "EDGE",
    "CLIPPED",
    "REJECTED",
    "DETECTED",
    "INEXACT_PSF",
]
