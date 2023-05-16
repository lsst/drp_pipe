# Pipeline Definitions

This directory contains pipeline definition YAML files which are used when processing data with the LSST Science Pipelines.
The pipelines defined here are science ready and come in two flavors: generic (top-level) and camera-specific (within sub-directories).
Use of camera-specific pipelines is encouraged where possible as they are optimized for the particular characteristics of that camera.

The pipelines defined here tend to import other pipelines, including ingredient pipelines in the [ingredients](../ingredients) directory.
To expand a pipeline YAML and resolve such imports for the purposes of visualizing it, the `pipetask build` command can be used.
For example, to visualize the step 1 subset of the [LATISS DRP pipeline](https://github.com/lsst/drp_pipe/blob/main/pipelines/LATISS/DRP.yaml) pipeline, run:

```bash
pipetask build \
-p $DRP_PIPE_DIR/pipelines/LATISS/DRP.yaml#step1 \
--show pipeline
```
