# These are not Task defaults because they are only appropriate
# for large areas that you'd find in a DRP.
# Task defaults were tuned for small cutouts
# They are appropriate for all cameras
config.arrayType = "float"
config.luminanceConfig.midtone = 0.2
config.luminanceConfig.highlight = 1
config.luminanceConfig.doDenoise = False
config.luminanceConfig.stretch = 400
config.luminanceConfig.max = 1
config.localContrastConfig.highlights = 0
config.localContrastConfig.shadows = 0
config.localContrastConfig.sigma = 0.5
config.localContrastConfig.clarity = 1.3
config.localContrastConfig.maxLevel = 2
config.localContrastConfig.doDiffusion = True
config.exposureBracketerConfig.exposureBrackets = [1.1, 1, 0.8]
config.doPsfDeconvolve = False
config.recenterNoise = 0.05
config.doRemapGamut = True
config.doLocalContrast = True
config.gamutMapperConfig.gamutMethod = "inpaint"
config.colorConfig.saturation = 0.65
config.cieWhitePoint = (0.265, 0.265)
config.luminanceConfig.floor = 1.5 / parameters.abs_max  # noqa: F821
config.imageRemappingConfig.absMax = parameters.abs_max  # noqa: F821
