# These are not Task defaults because they are only appropriate
# for large areas that you'd find in a DRP.
# Task defaults were tuned for small cutouts
# They are appropriate for all cameras
config.arrayType = "float"
config.imageRemappingConfig.absMax = 16500
config.luminanceConfig.Q = 0.7
config.doPSFDeconcovlve = False
config.exposureBrackets = None
config.localContrastConfig.doLocalContrast = False
config.luminanceConfig.stretch = 600
config.luminanceConfig.max = 100
config.luminanceConfig.highlight = 0.91
config.luminanceConfig.shadow = 0
config.luminanceConfig.midtone = 0.2
config.colorConfig.maxChroma = 80
config.colorConfig.saturation = 0.6
config.recenterNoise = 0.3
config.cieWhitePoint = (0.28, 0.28)
config.gamutMethod = "mapping"
