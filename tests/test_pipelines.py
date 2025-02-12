# This file is part of drp_pipe.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (http://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Unit tests for tracking edits to drp_pipe pipelines.
"""

import os
import tempfile
import unittest
from typing import Any

from lsst.daf.butler import Butler, Config
from lsst.daf.butler.tests import DatastoreMock
from lsst.daf.butler.tests.utils import makeTestTempDir, removeTestTempDir
from lsst.pipe.base.tests.pipelineStepTester import PipelineStepTester

PIPELINES_DIR = os.path.join(os.path.dirname(__file__), "..", "pipelines")
TEST_DIR = os.path.abspath(os.path.dirname(__file__))

# mostly common inputs
COMMON_INPUTS = {
    "bfKernel",
    "bias",
    "camera",
    "crosstalk",
    "dark",
    "flat",
    "fringe",
    "isrOverscanCorrected",
    "raw",
    "skyMap",
    # New ISR task inputs (LATISS, LSSTComCam, LSSTCam)
    "ptc",
    "linearizer",
    "bfk",
    "pretrainedModelPackage",
    # Optional preloaded solar system objects.
    "preloaded_DRP_SsObjects",
}

# HSC common inputs, in addition to COMMON_INPUTS
HSC_INPUTS = {
    "brightObjectMask",
    "brighterFatterKernel",
    "defects",
    "gaia_dr2_20200414",
    "gaia_dr3_20230707",
    "linearizer",
    "ps1_pv3_3pi_20170110",
    "sky",
    "transmission_atmosphere",
    "transmission_filter",
    "transmission_optics",
    "transmission_sensor",
    "yBackground",
}

# LATISS common inputs, in addition to COMMON_INPUTS
LATISS_INPUTS = {
    "atlas_refcat2_20220201",
    "defects",
    "gaia_dr3_20230707",
    "sky",
    "transmission_atmosphere_fgcm",
}

# LSSTCam-imSim common inputs, in addition to COMMON_INPUTS
LSSTCAM_IMSIM_INPUTS = {
    "bfk",
    "cal_ref_cat_2_2",
    "truth_summary",
    "cosmodc2_1_1_4_redmapper_v0_8_1_redgals"
}

# LSSTCam common inputs, in addition to COMMON_INPUTS
LSSTCAM_INPUTS = {
    "bfk",
    "linearizer",
    "defects",
    "the_monster_20240904",
    "gaia_dr3_20230707",
}

# LSSTComCam common inputs, in addition to COMMON_INPUTS
LSSTCOMCAM_INPUTS = {
    "bfk",
    "ptc",
    "linearizer",
    "defects",
    "cti",
    "the_monster_20240904",
}

# LSSTComCamSim common inputs, in addition to COMMON_INPUTS
LSSTCOMCAMSIM_INPUTS = {
    "uw_stars_20240524",
    "ptc",
    "bfk",
}

# a selection of mostly common outputs
COMMON_OUTPUTS = {
    "ccdVisitTable",
    "compare_warp_artifact_mask",
    "deepCoaddVisits",
    "deepCoadd",
    "deepCoadd_calexp",
    "deepCoadd_calexp_background",
    "deepCoadd_det",
    "deepCoadd_directWarp",
    "deepCoadd_forced_src",
    "deepCoadd_inputMap",
    "deepCoadd_meas",
    "deepCoadd_mergeDet",
    "deepCoadd_nImage",
    "deepCoadd_obj",
    "deepCoadd_psfMatchedWarp",
    "deepCoadd_ref",
    "deepCoadd_scarletModelData",
    "finalized_src_table",
    "finalVisitSummary",
    "initial_astrometry_match_detector",
    "initial_photometry_match_detector",
    "initial_psf_stars_footprints_detector",
    "initial_psf_stars_detector",
    "calexp",
    "calexpBackground",
    "src",
    "source",
    "objectTable",
    "objectTable_tract",
    "postISRCCD",
    "sourceTable_visit",
    "visitSummary",
    "visitTable",
    "isolated_star_presource_associations",
    "isolated_star_presources",
}

# HSC common outputs, in addition to COMMON_OUTPUTS
HSC_OUTPUTS = {
    "calexp_skyCorr_visit_mosaic",
    "calexpBackground_skyCorr_visit_mosaic",
    "forced_src",
    "preSourceTable",
    "preSourceTable_visit",
    "skyCorr",
}

# LATISS common outputs, in addition to COMMON_OUTPUTS
LATISS_OUTPUTS = {
    "diaObjectTable_tract",
    "diaSourceTable",
    "diaSourceTable_tract",
    "fgcm_Cycle0_FitParameters",
    "fgcm_Cycle1_FitParameters",
    "fgcm_Cycle2_FitParameters",
    "fgcm_Cycle3_FitParameters",
    "fgcm_Cycle4_FitParameters",
    "fgcm_Cycle0_FlaggedStars",
    "fgcm_Cycle1_FlaggedStars",
    "fgcm_Cycle2_FlaggedStars",
    "fgcm_Cycle3_FlaggedStars",
    "fgcm_Cycle4_FlaggedStars",
    "fgcm_reference_stars",
    "fgcm_star_ids",
    "fgcm_star_observations",
    "forcedSourceOnDiaObjectTable",
    "forcedSourceOnDiaObjectTable_tract",
    "forcedSourceTable",
    "forcedSourceTable_tract",
    "forced_diff",
    "forced_diff_diaObject",
    "forced_src_diaObject",
    "goodSeeingCoadd",
    "goodSeeingCoadd_nImage",
    "goodSeeingDiff_assocDiaSrcTable",
    "goodSeeingDiff_diaObjTable",
    "goodSeeingDiff_diaSrc",
    "goodSeeingDiff_diaSrcTable",
    "goodSeeingDiff_differenceExp",
    "goodSeeingDiff_differenceTempExp",
    "goodSeeingDiff_fullDiaObjTable",
    "goodSeeingDiff_matchedExp",
    "goodSeeingDiff_templateExp",
    "goodSeeingVisits",
    "mergedForcedSource",
    "mergedForcedSourceOnDiaObject",
    "transmission_atmosphere_fgcm",
}

# LSSTCam-imSim common outputs, in addition to COMMON_OUTPUTS
LSSTCAM_IMSIM_OUTPUTS = {
    "diaObjectTable_tract",
    "diaSourceTable",
    "diaSourceTable_tract",
    "forcedSourceOnDiaObjectTable",
    "forcedSourceOnDiaObjectTable_tract",
    "forcedSourceTable",
    "forcedSourceTable_tract",
    "forced_diff",
    "forced_diff_diaObject",
    "forced_src",
    "forced_src_diaObject",
    "goodSeeingCoadd",
    "goodSeeingCoadd_nImage",
    "goodSeeingDiff_assocDiaSrcTable",
    "goodSeeingDiff_diaObjTable",
    "goodSeeingDiff_diaSrc",
    "goodSeeingDiff_diaSrcTable",
    "goodSeeingDiff_differenceExp",
    "goodSeeingDiff_differenceTempExp",
    "goodSeeingDiff_fullDiaObjTable",
    "goodSeeingDiff_matchedExp",
    "goodSeeingDiff_templateExp",
    "goodSeeingVisits",
    "mergedForcedSource",
    "mergedForcedSourceOnDiaObject",
}

# Outputs common to all "quickLook" pipelines, which only iclude
QUICKLOOK_OUTPUTS = {
    "calexp", "visitSummary"
}

# All refcats used by any pipelines, for inclusion as the initial_dataset_types
# argument to PipelineStepTester; the intent is just to allow the 'skypix'
# dimension placeholder used in these connections to be resolved.
REFCATS = [
    ("ps1_pv3_3pi_20170110", {"htm7"}, "SimpleCatalog", False),
    ("gaia_dr2_20200414", {"htm7"}, "SimpleCatalog", False),
    ("gaia_dr3_20230707", {"htm7"}, "SimpleCatalog", False),
    ("the_monster_20240904", {"htm7"}, "SimpleCatalog", False),
    ("atlas_refcat2_20220201", {"htm7"}, "SimpleCatalog", False),
    ("cal_ref_cat_2_2", {"htm7"}, "SimpleCatalog", False),
    ("uw_stars_20240524", {"htm7"}, "SimpleCatalog", False),
]


class PipelineTestCase(unittest.TestCase):
    def setUp(self):
        self.root = makeTestTempDir(TEST_DIR)
        self.maxDiff = None

    def tearDown(self):
        removeTestTempDir(self.root)

    def makeButler(self, **kwargs: Any) -> Butler:
        """Return new Butler instance on each call."""
        config = Config()

        # make separate temporary directory for registry of this instance
        tmpdir = tempfile.mkdtemp(dir=self.root)
        config["registry", "db"] = f"sqlite:///{tmpdir}/gen3.sqlite3"
        config = Butler.makeRepo(self.root, config)
        butler = Butler.from_config(config, **kwargs)
        DatastoreMock.apply(butler)
        return butler

    def test_decam_isrForCrosstalkSources(self):
        butler = self.makeButler(writeable=True)
        tester = PipelineStepTester(
            os.path.join(PIPELINES_DIR, "DECam", "isrForCrosstalkSources.yaml"),
            ["#step0"],
            initial_dataset_types=REFCATS,
            expected_inputs={
                "camera",
                "raw",
            },
            expected_outputs={"overscanRaw"},
        )
        tester.run(butler, self)

    def test_decam_drp_merian(self):
        butler = self.makeButler(writeable=True)
        tester = PipelineStepTester(
            os.path.join(PIPELINES_DIR, "DECam", "DRP-Merian.yaml"),
            [
                "#step1",
                "#step2a",
                "#step2b",
                "#step2d",
                "#step2e",
                "#step3",
            ],
            initial_dataset_types=REFCATS,
            expected_inputs=COMMON_INPUTS
            | {
                "defects",
                "gaia_dr2_20200414",
                "gaia_dr3_20230707",
                "linearizer",
                "overscanRaw",
                "ps1_pv3_3pi_20170110",
            },
            expected_outputs=COMMON_OUTPUTS
            | {
                "goodSeeingCoadd",
                "goodSeeingCoadd_nImage",
                "goodSeeingVisits",
                "preSourceTable",
                "preSourceTable_visit",
            },
        )
        tester.run(butler, self)

    def test_hsc_drp_ci_hsc(self):
        butler = self.makeButler(writeable=True)
        tester = PipelineStepTester(
            os.path.join(PIPELINES_DIR, "HSC", "DRP-ci_hsc.yaml"),
            [""],
            initial_dataset_types=REFCATS,
            expected_inputs=COMMON_INPUTS
            | HSC_INPUTS
            | {"jointcalPhotoCalibCatalog", "jointcalSkyWcsCatalog"},
            expected_outputs=COMMON_OUTPUTS
            | HSC_OUTPUTS
            | {
                "diaObjectTable_tract",
                "diaSourceTable",
                "diaSourceTable_tract",
                "forcedSourceOnDiaObjectTable",
                "forcedSourceOnDiaObjectTable_tract",
                "forcedSourceTable",
                "forcedSourceTable_tract",
                "forced_diff",
                "forced_diff_diaObject",
                "forced_src_diaObject",
                "goodSeeingCoadd",
                "goodSeeingCoadd_nImage",
                "goodSeeingDiff_assocDiaSrcTable",
                "goodSeeingDiff_diaObjTable",
                "goodSeeingDiff_diaSrc",
                "goodSeeingDiff_diaSrcTable",
                "goodSeeingDiff_differenceExp",
                "goodSeeingDiff_differenceTempExp",
                "goodSeeingDiff_fullDiaObjTable",
                "goodSeeingDiff_matchedExp",
                "goodSeeingDiff_templateExp",
                "goodSeeingVisits",
                "mergedForcedSource",
                "mergedForcedSourceOnDiaObject",
            },
        )
        tester.run(butler, self)

    def test_hsc_drp_prod(self):
        butler = self.makeButler(writeable=True)
        tester = PipelineStepTester(
            os.path.join(PIPELINES_DIR, "HSC", "DRP-Prod.yaml"),
            [
                "#step1",
                "#step2a",
                "#step2b",
                "#step2c",
                "#step2d",
                "#step2e",
                "#step3",
                "#step4",
                "#step7",
            ],
            initial_dataset_types=REFCATS,
            expected_inputs=COMMON_INPUTS | HSC_INPUTS | {"fgcmLookUpTable"},
            expected_outputs=COMMON_OUTPUTS
            | HSC_OUTPUTS
            | {
                "fgcm_Cycle6_AtmosphereParameters",
                "fgcm_Cycle0_FitParameters",
                "fgcm_Cycle1_FitParameters",
                "fgcm_Cycle2_FitParameters",
                "fgcm_Cycle3_FitParameters",
                "fgcm_Cycle4_FitParameters",
                "fgcm_Cycle5_FitParameters",
                "fgcm_Cycle6_FitParameters",
                "fgcm_Cycle0_FlaggedStars",
                "fgcm_Cycle1_FlaggedStars",
                "fgcm_Cycle2_FlaggedStars",
                "fgcm_Cycle3_FlaggedStars",
                "fgcm_Cycle4_FlaggedStars",
                "fgcm_Cycle5_FlaggedStars",
                "fgcm_Cycle6_FlaggedStars",
                "fgcm_reference_stars",
                "fgcm_Cycle6_StandardStars",
                "fgcm_star_ids",
                "fgcm_star_observations",
                "fgcm_Cycle6_Zeropoints",
                "transmission_atmosphere_fgcm",
            },
        )
        tester.run(butler, self)

    def test_hsc_drp_rc2(self):
        butler = self.makeButler(writeable=True)
        tester = PipelineStepTester(
            os.path.join(PIPELINES_DIR, "HSC", "DRP-RC2.yaml"),
            [
                "#step1",
                "#step2a",
                "#step2b",
                "#step2cde",
                "#step3",
                "#step4",
                "#step5",
                "#step6",
                "#step7",
            ],
            initial_dataset_types=REFCATS,
            expected_inputs=COMMON_INPUTS | HSC_INPUTS | {"fgcmLookUpTable"},
            expected_outputs=COMMON_OUTPUTS
            | HSC_OUTPUTS
            | {
                "diaObjectTable_tract",
                "diaSourceTable",
                "diaSourceTable_tract",
                "fgcm_Cycle4_AtmosphereParameters",
                "fgcm_Cycle0_FitParameters",
                "fgcm_Cycle1_FitParameters",
                "fgcm_Cycle2_FitParameters",
                "fgcm_Cycle3_FitParameters",
                "fgcm_Cycle4_FitParameters",
                "fgcm_Cycle0_FlaggedStars",
                "fgcm_Cycle1_FlaggedStars",
                "fgcm_Cycle2_FlaggedStars",
                "fgcm_Cycle3_FlaggedStars",
                "fgcm_Cycle4_FlaggedStars",
                "fgcm_reference_stars",
                "fgcm_Cycle4_StandardStars",
                "fgcm_star_ids",
                "fgcm_star_observations",
                "fgcm_Cycle4_Zeropoints",
                "forcedSourceOnDiaObjectTable",
                "forcedSourceOnDiaObjectTable_tract",
                "forcedSourceTable",
                "forcedSourceTable_tract",
                "forced_diff",
                "forced_diff_diaObject",
                "forced_src_diaObject",
                "goodSeeingCoadd",
                "goodSeeingCoadd_nImage",
                "goodSeeingDiff_assocDiaSrcTable",
                "goodSeeingDiff_diaObjTable",
                "goodSeeingDiff_diaSrc",
                "goodSeeingDiff_diaSrcTable",
                "goodSeeingDiff_differenceExp",
                "goodSeeingDiff_differenceTempExp",
                "goodSeeingDiff_fullDiaObjTable",
                "goodSeeingDiff_matchedExp",
                "goodSeeingDiff_templateExp",
                "goodSeeingVisits",
                "mergedForcedSource",
                "mergedForcedSourceOnDiaObject",
                "transmission_atmosphere_fgcm",
            },
        )
        tester.run(butler, self)

    def test_hsc_drp_rc2_subset(self):
        butler = self.makeButler(writeable=True)
        tester = PipelineStepTester(
            os.path.join(PIPELINES_DIR, "HSC", "DRP-RC2_subset.yaml"),
            [
                "#nightlyStep1",
                "#nightlyStep2a",
                "#nightlyStep2b",
                "#nightlyStep2c",
                "#nightlyStep2d",
                "#nightlyStep3",
                "#nightlyStep4",
            ],
            initial_dataset_types=REFCATS,
            expected_inputs=COMMON_INPUTS | HSC_INPUTS | {"fgcmLookUpTable"},
            expected_outputs=COMMON_OUTPUTS
            | HSC_OUTPUTS
            | {
                "fgcm_Cycle4_AtmosphereParameters",
                "fgcm_Cycle0_FitParameters",
                "fgcm_Cycle1_FitParameters",
                "fgcm_Cycle2_FitParameters",
                "fgcm_Cycle3_FitParameters",
                "fgcm_Cycle4_FitParameters",
                "fgcm_Cycle0_FlaggedStars",
                "fgcm_Cycle1_FlaggedStars",
                "fgcm_Cycle2_FlaggedStars",
                "fgcm_Cycle3_FlaggedStars",
                "fgcm_Cycle4_FlaggedStars",
                "fgcm_reference_stars",
                "fgcm_Cycle4_StandardStars",
                "fgcm_star_ids",
                "fgcm_star_observations",
                "fgcm_Cycle4_Zeropoints",
                "transmission_atmosphere_fgcm",
            },
        )
        tester.run(butler, self)

    def test_latiss_drp(self):
        butler = self.makeButler(writeable=True)
        tester = PipelineStepTester(
            os.path.join(PIPELINES_DIR, "LATISS", "DRP.yaml"),
            [
                "#step1",
                "#step2a",
                "#step2bcde",
                "#step3a",
                "#step3b",
                "#step3c",
                "#step4",
                "#step5",
                "#step6",
            ],
            initial_dataset_types=REFCATS,
            expected_inputs=COMMON_INPUTS | LATISS_INPUTS | {"fgcmLookUpTable"},
            expected_outputs=COMMON_OUTPUTS | LATISS_OUTPUTS,
        )
        tester.run(butler, self)

    def test_lsstcam_quickLook(self):
        butler = self.makeButler(writeable=True)
        tester = PipelineStepTester(
            os.path.join(PIPELINES_DIR, "LSSTCam", "quickLook.yaml"),
            [
                "#step1",
                "#step2a",
                "#nightlyRollup",
            ],
            initial_dataset_types=REFCATS,
            expected_inputs=COMMON_INPUTS | LSSTCAM_INPUTS,
            expected_outputs=QUICKLOOK_OUTPUTS,
        )
        tester.run(butler, self)

    def test_lsstcam_imsim_drp_ci_imsim(self):
        butler = self.makeButler(writeable=True)
        tester = PipelineStepTester(
            os.path.join(PIPELINES_DIR, "LSSTCam-imSim", "DRP-ci_imsim.yaml"),
            [""],
            initial_dataset_types=REFCATS,
            expected_inputs=COMMON_INPUTS | LSSTCAM_IMSIM_INPUTS,
            expected_outputs=COMMON_OUTPUTS | LSSTCAM_IMSIM_OUTPUTS,
        )
        tester.run(butler, self)

    def test_lsstcam_imsim_drp_test_med_1(self):
        butler = self.makeButler(writeable=True)
        tester = PipelineStepTester(
            os.path.join(PIPELINES_DIR, "LSSTCam-imSim", "DRP-test-med-1.yaml"),
            [f"#step{N}" for N in range(1, 8)],
            initial_dataset_types=REFCATS,
            expected_inputs=COMMON_INPUTS | LSSTCAM_IMSIM_INPUTS,
            expected_outputs=COMMON_OUTPUTS | LSSTCAM_IMSIM_OUTPUTS,
        )
        tester.run(butler, self)

    def test_lsstcam_imsim_drp(self):
        butler = self.makeButler(writeable=True)
        tester = PipelineStepTester(
            os.path.join(PIPELINES_DIR, "LSSTCam-imSim", "DRP.yaml"),
            [f"#step{N}" for N in range(1, 8)],
            initial_dataset_types=REFCATS,
            expected_inputs=COMMON_INPUTS | LSSTCAM_IMSIM_INPUTS,
            expected_outputs=COMMON_OUTPUTS | LSSTCAM_IMSIM_OUTPUTS,
        )
        tester.run(butler, self)

    def test_lsstcam_imsim_nightly_validation(self):
        butler = self.makeButler(writeable=True)
        tester = PipelineStepTester(
            os.path.join(PIPELINES_DIR, "LSSTCam-imSim", "nightly-validation.yaml"),
            [
                "#step1",
                "#step2",
                "#step3",
                "#step7",
            ],
            initial_dataset_types=REFCATS,
            expected_inputs=COMMON_INPUTS | LSSTCAM_IMSIM_INPUTS,
            expected_outputs=COMMON_OUTPUTS,
        )
        tester.run(butler, self)

    def test_lsstcomcamsim_drp(self):
        butler = self.makeButler(writeable=True)
        tester = PipelineStepTester(
            os.path.join(PIPELINES_DIR, "LSSTComCamSim", "DRP.yaml"),
            [
                "#step1",
                "#step2a",
                "#step2b",
                "#step2c",
                "#step2d",
                "#step2e",
                "#step3",
                "#step4",
                "#step5",
                "#step6",
                "#step7",
            ],
            initial_dataset_types=REFCATS,
            expected_inputs=COMMON_INPUTS | LSSTCOMCAMSIM_INPUTS | {"fgcmLookUpTable"},
            expected_outputs=COMMON_OUTPUTS,
        )
        tester.run(butler, self)

    def test_lsstcomcamsim_nightly_validation(self):
        butler = self.makeButler(writeable=True)
        tester = PipelineStepTester(
            os.path.join(PIPELINES_DIR, "LSSTComCamSim", "nightly-validation.yaml"),
            [
                "#step1",
                "#step2a",
                "#nightlyRollup",
                "#step2b",
                "#step2d",
                "#step2e",
                "#step3",
                "#step7",
            ],
            initial_dataset_types=REFCATS,
            expected_inputs=COMMON_INPUTS | LSSTCOMCAMSIM_INPUTS,
            expected_outputs=COMMON_OUTPUTS,
        )
        tester.run(butler, self)

    def test_lsstcomcamsim_quickLook(self):
        butler = self.makeButler(writeable=True)
        tester = PipelineStepTester(
            os.path.join(PIPELINES_DIR, "LSSTComCamSim", "quickLook.yaml"),
            [
                "#step1",
                "#step2a",
                "#nightlyRollup",
            ],
            initial_dataset_types=REFCATS,
            expected_inputs=COMMON_INPUTS | LSSTCOMCAMSIM_INPUTS,
            expected_outputs=QUICKLOOK_OUTPUTS,
        )
        tester.run(butler, self)

    def test_lsstcomcam_drp(self):
        butler = self.makeButler(writeable=True)
        tester = PipelineStepTester(
            os.path.join(PIPELINES_DIR, "LSSTComCam", "DRP.yaml"),
            [
                "#step1",
                "#step2a",
                "#step2b",
                "#step2c",
                "#step2d",
                "#step2e",
                "#step3a",
                "#step3b",
                "#step4",
                "#step5",
                "#step6",
                "#step7",
            ],
            initial_dataset_types=REFCATS,
            expected_inputs=COMMON_INPUTS | LSSTCOMCAM_INPUTS | {"fgcmLookUpTable"},
            expected_outputs=COMMON_OUTPUTS,
        )
        tester.run(butler, self)

    def test_lsstcomcam_nightly_validation(self):
        butler = self.makeButler(writeable=True)
        tester = PipelineStepTester(
            os.path.join(PIPELINES_DIR, "LSSTComCam", "nightly-validation.yaml"),
            [
                "#step1",
                "#step2a",
                "#nightlyRollup",
                "#step2b",
                "#step2d",
                "#step2e",
                "#step3a",
                "#step3b",
                "#step7",
            ],
            initial_dataset_types=REFCATS,
            expected_inputs=COMMON_INPUTS | LSSTCOMCAM_INPUTS,
            expected_outputs=COMMON_OUTPUTS,
        )
        tester.run(butler, self)

    def test_lsstcomcam_quickLook(self):
        butler = self.makeButler(writeable=True)
        tester = PipelineStepTester(
            os.path.join(PIPELINES_DIR, "LSSTComCam", "quickLook.yaml"),
            [
                "#step1",
                "#step2a",
                "#nightlyRollup",
            ],
            initial_dataset_types=REFCATS,
            expected_inputs=COMMON_INPUTS | LSSTCOMCAM_INPUTS,
            expected_outputs=QUICKLOOK_OUTPUTS,
        )
        tester.run(butler, self)


if __name__ == "__main__":
    unittest.main()
