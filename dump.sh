#!/bin/bash
set -e
echo DECam/DRP-Merian
python -m lsst.pipe.base.pipeline_graph $DRP_PIPE_DIR/pipelines/DECam/DRP-Merian.yaml --dump $DRP_PIPE_DIR/dumps/DECam/DRP-Merian
echo DECam/isrForCrosstalkSources
python -m lsst.pipe.base.pipeline_graph $DRP_PIPE_DIR/pipelines/DECam/isrForCrosstalkSources.yaml --dump $DRP_PIPE_DIR/dumps/DECam/isrForCrosstalkSources
echo HSC/DRP-ci_hsc
python -m lsst.pipe.base.pipeline_graph $DRP_PIPE_DIR/pipelines/HSC/DRP-ci_hsc.yaml --dump $DRP_PIPE_DIR/dumps/HSC/DRP-ci_hsc
echo HSC/DRP-Prod
python -m lsst.pipe.base.pipeline_graph $DRP_PIPE_DIR/pipelines/HSC/DRP-Prod.yaml --dump $DRP_PIPE_DIR/dumps/HSC/DRP-Prod
echo HSC/DRP-RC2
python -m lsst.pipe.base.pipeline_graph $DRP_PIPE_DIR/pipelines/HSC/DRP-RC2.yaml --dump $DRP_PIPE_DIR/dumps/HSC/DRP-RC2
echo HSC/DRP-RC2_subset
python -m lsst.pipe.base.pipeline_graph $DRP_PIPE_DIR/pipelines/HSC/DRP-RC2_subset.yaml --dump $DRP_PIPE_DIR/dumps/HSC/DRP-RC2_subset
echo HSC/pipelines_check
python -m lsst.pipe.base.pipeline_graph $DRP_PIPE_DIR/pipelines/HSC/pipelines_check.yaml --dump $DRP_PIPE_DIR/dumps/HSC/pipelines_check
echo LATISS/DRP
python -m lsst.pipe.base.pipeline_graph $DRP_PIPE_DIR/pipelines/LATISS/DRP.yaml --dump $DRP_PIPE_DIR/dumps/LATISS/DRP
echo LSSTCam/DRP
python -m lsst.pipe.base.pipeline_graph $DRP_PIPE_DIR/pipelines/LSSTCam/DRP.yaml --dump $DRP_PIPE_DIR/dumps/LSSTCam/DRP
echo LSSTCam/nightly-validation
python -m lsst.pipe.base.pipeline_graph $DRP_PIPE_DIR/pipelines/LSSTCam/nightly-validation.yaml --dump $DRP_PIPE_DIR/dumps/LSSTCam/nightly-validation
echo LSSTCam/quickLook
python -m lsst.pipe.base.pipeline_graph $DRP_PIPE_DIR/pipelines/LSSTCam/quickLook.yaml --dump $DRP_PIPE_DIR/dumps/LSSTCam/quickLook
echo LSSTCam-imSim/DRP-ci_imsim
python -m lsst.pipe.base.pipeline_graph $DRP_PIPE_DIR/pipelines/LSSTCam-imSim/DRP-ci_imsim.yaml --dump $DRP_PIPE_DIR/dumps/LSSTCam-imSim/DRP-ci_imsim
echo LSSTCam-imSim/DRP-test-med-1
python -m lsst.pipe.base.pipeline_graph $DRP_PIPE_DIR/pipelines/LSSTCam-imSim/DRP-test-med-1.yaml --dump $DRP_PIPE_DIR/dumps/LSSTCam-imSim/DRP-test-med-1
echo LSSTComCam/DRP
python -m lsst.pipe.base.pipeline_graph $DRP_PIPE_DIR/pipelines/LSSTComCam/DRP.yaml --dump $DRP_PIPE_DIR/dumps/LSSTComCam/DRP
echo LSSTComCam/nightly-validation
python -m lsst.pipe.base.pipeline_graph $DRP_PIPE_DIR/pipelines/LSSTComCam/nightly-validation.yaml --dump $DRP_PIPE_DIR/dumps/LSSTComCam/nightly-validation
echo LSSTComCam/quickLook
python -m lsst.pipe.base.pipeline_graph $DRP_PIPE_DIR/pipelines/LSSTComCam/quickLook.yaml --dump $DRP_PIPE_DIR/dumps/LSSTComCam/quickLook
echo LSSTComCamSim/DRP
python -m lsst.pipe.base.pipeline_graph $DRP_PIPE_DIR/pipelines/LSSTComCamSim/DRP.yaml --dump $DRP_PIPE_DIR/dumps/LSSTComCamSim/DRP
echo LSSTComCamSim/nightly-validation
python -m lsst.pipe.base.pipeline_graph $DRP_PIPE_DIR/pipelines/LSSTComCamSim/nightly-validation.yaml --dump $DRP_PIPE_DIR/dumps/LSSTComCamSim/nightly-validation
echo LSSTComCamSim/quickLook
python -m lsst.pipe.base.pipeline_graph $DRP_PIPE_DIR/pipelines/LSSTComCamSim/quickLook.yaml --dump $DRP_PIPE_DIR/dumps/LSSTComCamSim/quickLook
