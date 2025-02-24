# DRP CONFIGURATION FOR CalibrateImageTask
#
# This configuration can't go in the task defaults, because those are shared
# with AP.  It could be moved directly into a pipeline YAML after the v1->v2
# migration is done.

# In DRP not calibrating the pixels (or the backgrounds) until we have
# our final photometric calibration makes everything downstream much
# simpler.
config.do_calibrate_pixels = False

# TODO[DM-47320]: for now we make output catalog as similar to the old 'src' as
# possible; we'll try to go back to calibrateImage defaults with a smaller
# catalog after it's integrated. Goal is to remove all of these overrides
# except the aperture radii, which we instead want to set to the same as the
# compensated to-phat radii below for
# lsst.fgcmcal.fgcmOutputProducts.FgcmOutputProductsTask
config.star_detection.includeThresholdMultiplier = 1.0
config.star_selector["science"].doUnresolved = False
config.star_selector["science"].doSignalToNoise = False
config.star_measurement.plugins["base_CircularApertureFlux"].radii = [
    3.0, 6.0, 9.0, 12.0, 17.0, 25.0, 35.0, 50.0, 70.0
]
config.star_measurement.plugins.names |= [
    "base_Variance",
    "ext_shapeHSM_HsmPsfMomentsDebiased",
    "ext_shapeHSM_HsmShapeRegauss",
    "base_Blendedness",
    "base_Jacobian",
]

# fgcmcal needs an inner and outer aperture and may want an estimate of
# the local background
config.star_measurement.plugins["base_CircularApertureFlux"].maxSincRadius = 12.0
config.star_measurement.plugins["base_CompensatedTophatFlux"].apertures = [12, 17]
config.star_measurement.plugins.names |= ["base_LocalBackground"]
