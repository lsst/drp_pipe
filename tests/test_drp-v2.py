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

from __future__ import annotations

import logging
import os
import re
import tempfile
import unittest
from collections.abc import Set
from typing import Any

from lsst.daf.butler import Butler, Config, DatasetType
from lsst.daf.butler.tests.utils import makeTestTempDir, removeTestTempDir
from lsst.pipe.base import Pipeline, PipelineGraph

from lsst.drp.pipe.tests.correspondence import Correspondence

_LOG = logging.getLogger(__name__)


PIPELINES_DIR = os.path.join(os.path.dirname(__file__), "..", "pipelines")
TEST_DIR = os.path.abspath(os.path.dirname(__file__))


COMCAM_REFCAT = "the_monster_20250219"
COMCAM_INPUTS = {
    COMCAM_REFCAT,
    "raw",
    "flat",
    "dark",
    "bias",
    "bfk",
    "linearizer",
    "cti",
    "ptc",
    "crosstalk",
    "camera",
    "defects",
    "skyMap",
    "fgcmLookUpTable",
    "pretrainedModelPackage",
    "preloaded_DRP_SsObjects",
    "illuminationCorrection",
}


class DrpV2TestCase(unittest.TestCase):
    """Self-consistency and overall-input checks for the DRP-v2 pipeline
    variants.
    """

    def setUp(self):
        self.root = makeTestTempDir(TEST_DIR)
        self.maxDiff = None

    def tearDown(self):
        removeTestTempDir(self.root)

    def make_butler(self, **kwargs: Any) -> Butler:
        """Construct a butler repository and return a `Butler` client."""
        config = Config()

        # make separate temporary directory for registry of this instance
        tmpdir = tempfile.mkdtemp(dir=self.root)
        config["registry", "db"] = f"sqlite:///{tmpdir}/gen3.sqlite3"
        config = Butler.makeRepo(self.root, config)
        butler = Butler.from_config(config, **kwargs)
        return butler

    def register_refcat(self, butler: Butler, name: str) -> None:
        butler.registry.registerDatasetType(
            DatasetType(
                name,
                {"htm7"},
                "SimpleCatalog",
                isCalibration=False,
                universe=butler.dimensions,
            )
        )

    def register_dataset(self, butler: Butler, name: str, dimensions: set(str), storageClass: str) -> None:
        butler.registry.registerDatasetType(
            DatasetType(
                name,
                dimensions,
                storageClass,
                isCalibration=False,
                universe=butler.dimensions,
            )
        )

    def test_comcam_full_load(self) -> None:
        """Test the LSSTComCam/DRP-v2 pipeline after reading the full pipeline
        at once.
        """
        butler = self.make_butler(writeable=True)
        self.register_refcat(butler, COMCAM_REFCAT)
        pipeline = Pipeline.from_uri(
            os.path.join(PIPELINES_DIR, "LSSTComCam/DRP-v2.yaml")
        )
        # Just constructing and resolving the pipeline graph does a lot of
        # validation, since it checks that the step flow and dimensions are
        # valid (step flow is what the PipelineStepTester checks for the v1
        # pipelines).
        pipeline_graph = pipeline.to_graph(registry=butler.registry)
        self.check_stage(
            pipeline_graph, pipeline_graph.task_subsets["stage1-single-visit"], "step1"
        )
        self.check_stage(
            pipeline_graph, pipeline_graph.task_subsets["stage2-recalibrate"], "step2"
        )
        self.check_stage(
            pipeline_graph, pipeline_graph.task_subsets["stage3-coadd"], "step3"
        )
        self.check_stage(
            pipeline_graph,
            pipeline_graph.task_subsets["stage4-measure-variability"],
            "step4",
        )
        # Check that the overall inputs are only the ones we expect.
        overall_inputs = {name for name, _ in pipeline_graph.iter_overall_inputs()}
        self.assertEqual(overall_inputs, COMCAM_INPUTS)

    def test_comcam_stage_load(self) -> None:
        """Test the LSSTComCam/DRP-v2 pipeline after reading the pipeline
        one stage at a time.
        """
        butler = self.make_butler(writeable=True)
        self.register_refcat(butler, COMCAM_REFCAT)
        # Pre-define visit_table.
        # It is stored as ArrowAstropy but read as a DataFrame.
        self.register_dataset(butler, "visit_table", {"instrument"}, "ArrowAstropy")
        pipeline_graph_1 = Pipeline.from_uri(
            os.path.join(PIPELINES_DIR, "LSSTComCam/DRP-v2.yaml#stage1-single-visit")
        ).to_graph(registry=butler.registry)
        pipeline_graph_1.register_dataset_types(butler)
        self.check_stage(pipeline_graph_1, pipeline_graph_1.tasks.keys(), "")
        pipeline_graph_2 = Pipeline.from_uri(
            os.path.join(PIPELINES_DIR, "LSSTComCam/DRP-v2.yaml#stage2-recalibrate")
        ).to_graph(registry=butler.registry)
        pipeline_graph_2.register_dataset_types(butler)
        self.check_stage(
            pipeline_graph_2, pipeline_graph_2.task_subsets["stage2-recalibrate"], ""
        )
        pipeline_graph_3 = Pipeline.from_uri(
            os.path.join(PIPELINES_DIR, "LSSTComCam/DRP-v2.yaml#stage3-coadd")
        ).to_graph(registry=butler.registry)
        pipeline_graph_3.register_dataset_types(butler)
        self.check_stage(
            pipeline_graph_3, pipeline_graph_3.task_subsets["stage3-coadd"], ""
        )
        pipeline_graph_4 = Pipeline.from_uri(
            os.path.join(
                PIPELINES_DIR, "LSSTComCam/DRP-v2.yaml#stage4-measure-variability"
            )
        ).to_graph(registry=butler.registry)
        pipeline_graph_4.register_dataset_types(butler)
        self.check_stage(
            pipeline_graph_4,
            pipeline_graph_4.task_subsets["stage4-measure-variability"],
            "",
        )
        # Spot-check a few prominent outputs for each stage.
        self.assertIsNotNone(pipeline_graph_1.producer_of("single_visit_star"))
        self.assertIsNotNone(pipeline_graph_1.producer_of("preliminary_visit_image"))
        self.assertIsNotNone(pipeline_graph_1.producer_of("preliminary_visit_summary"))
        self.assertIsNotNone(pipeline_graph_1.producer_of("preliminary_visit_table"))
        self.assertIsNotNone(
            pipeline_graph_1.producer_of("preliminary_visit_detector_table")
        )
        self.assertIsNotNone(
            pipeline_graph_1.producer_of("single_visit_star_association_metrics")
        )
        self.assertIsNotNone(pipeline_graph_2.producer_of("recalibrated_star"))
        self.assertIsNotNone(
            pipeline_graph_2.producer_of("recalibrated_star_association_metrics")
        )
        self.assertIsNotNone(pipeline_graph_2.producer_of("visit_summary"))
        self.assertIsNotNone(pipeline_graph_2.producer_of("visit_table"))
        self.assertIsNotNone(pipeline_graph_2.producer_of("visit_detector_table"))
        self.assertIsNotNone(pipeline_graph_3.producer_of("deep_coadd"))
        self.assertIsNotNone(pipeline_graph_3.producer_of("template_coadd"))
        self.assertIsNotNone(pipeline_graph_3.producer_of("object"))
        self.assertIsNotNone(pipeline_graph_4.producer_of("dia_source"))
        self.assertIsNotNone(pipeline_graph_4.producer_of("dia_object"))
        self.assertIsNotNone(pipeline_graph_4.producer_of("source"))
        self.assertIsNotNone(
            pipeline_graph_4.producer_of("analysis_source_association_metrics")
        )
        self.assertIsNotNone(pipeline_graph_4.producer_of("visit_image"))
        self.assertIsNotNone(pipeline_graph_4.producer_of("object_forced_source"))
        self.assertIsNotNone(pipeline_graph_4.producer_of("dia_object_forced_source"))

    def check_stage(
        self, pipeline_graph: PipelineGraph, stage_members: Set[str], step_prefix: str
    ) -> None:
        """Check that the formal steps that should subdivide a stage subset
        actually do.

        Parameters
        ----------
        pipeline_graph : `lsst.pipe.base.pipeline_graph.PipelineGraph`
            A pipeline graph that has step definitions.
        stage_members : `Set` [ `str` ]
            The task labels that belong to the stage being tested.
        step_prefix : `str`
            String prefix for all steps that are part of this stage.  May be
            an empty string to match all steps in the pipeline and check that
            only the desired steps are in the pipeline.
        """
        step_labels = [
            label for label in pipeline_graph.steps if label.startswith(step_prefix)
        ]
        # Steps should be sorted alphabetically.
        self.assertEqual(sorted(step_labels), step_labels)
        # Test that the checkpoint/stage subset is the unions of its steps.
        step_member_union = set()
        for step_label in step_labels:
            step_member_union.update(pipeline_graph.task_subsets[step_label])
        self.assertSetEqual(step_member_union, set(stage_members))

    def test_comcam_correspondence(self) -> None:
        butler = self.make_butler(writeable=True)
        self.register_refcat(butler, COMCAM_REFCAT)
        correspondence_filename = os.path.join(PIPELINES_DIR, "LSSTComCam/DRP-v2.yaml")
        new_pipeline_graph = Pipeline.from_uri(correspondence_filename).to_graph(
            registry=butler.registry
        )
        old_steps = [
            "step1",
            "step2a",
            "step2b",
            "step2c",
            "step2d",
            "step2e",
            "step3a",
            "step3b",
            "step4",
            "step5",
            "step6",
            "step7",
        ]
        old_pipeline_graph = Pipeline.from_uri(
            os.path.join(PIPELINES_DIR, f"LSSTComCam/DRP.yaml#{','.join(old_steps)}")
        ).to_graph(registry=butler.registry)
        ignore_edges = {
            # Use recalibrated_star instead of single_visit_star for calib
            # flag propagation.
            ("measureObjectUnforced", "sourceTableHandles"),
            # Use deep_coadd instead of deep_coadd_preliminary for WCS.
            ("measureObjectForced", "refWcs"),
        }
        correspondence_filename = os.path.join(
            TEST_DIR, "migration_data", "LSSTComCam", "DRP-v2.json"
        )
        correspondence = Correspondence.read(correspondence_filename)
        if correspondence.check(
            new_pipeline_graph,
            old_pipeline_graph,
            "LSSTComCam/DRP-v2",
            "LSSTComCam/DRP",
            ignore_edges=ignore_edges,
        ):
            new_correspondence = correspondence.find_matches(
                new_pipeline_graph, old_pipeline_graph
            ).sorted(new_pipeline_graph, old_pipeline_graph)
            new_correspondence_filename = (
                f"{os.path.splitext(correspondence_filename)[0]}.new.json"
            )
            new_correspondence.write(new_correspondence_filename)
            print(
                "An attempt to fix the correspondence file has "
                f"been written to {new_correspondence_filename!r}."
            )
            if messages := new_correspondence.check(
                new_pipeline_graph,
                old_pipeline_graph,
                "LSSTComCam/DRP-v2",
                "LSSTComCam/DRP",
                ignore_edges=ignore_edges,
            ):
                print("Some problems remain that require manual edits:")
                for message in messages:
                    print(message)
            else:
                print("This file should be reviewed and moved to replace the original.")
            raise AssertionError(
                f"Pipeline correspondence file {correspondence_filename!r} is out of date."
            )
        for new_label, old_label in correspondence.tasks_new_to_old.items():
            new_node = new_pipeline_graph.tasks[new_label]
            old_node = old_pipeline_graph.tasks[old_label]
            task_config_diff = correspondence.diff_task_configs(new_node, old_node)
            if task_config_diff:
                print(task_config_diff)
                raise AssertionError(
                    f"Differences detected in configs for task {new_label!r} (previously {old_label!r})."
                )

    def test_comcam_compat(self) -> None:
        """Test the LSSTComCam/DRP-v2-compat pipeline, which should be
        identical to DRP-v2 aside from replacing 'source' -> 'source2'
        throughout.
        """
        butler = self.make_butler(writeable=True)
        self.register_refcat(butler, COMCAM_REFCAT)
        pipeline = Pipeline.from_uri(
            os.path.join(PIPELINES_DIR, "LSSTComCam/DRP-v2.yaml")
        )
        pipeline_graph = pipeline.to_graph(registry=butler.registry)
        pipeline_compat = Pipeline.from_uri(
            os.path.join(PIPELINES_DIR, "LSSTComCam/DRP-v2-compat.yaml")
        )
        pipeline_graph_compat = pipeline_compat.to_graph(registry=butler.registry)
        self.assertFalse(
            Correspondence(
                dataset_types_new_to_old={"source2": "source"},
            ).find_matches(pipeline_graph_compat, pipeline_graph).check(
                pipeline_graph_compat, pipeline_graph, "DRP-v2-compat", "DRP-v2"
            )
        )

    def test_comcam_release_id_parameter(self) -> None:
        """Test that changing the release_id parameter affects all appropriate
        config options in the pipeline.
        """
        pipeline = Pipeline.fromString(
            """
            description: test pipeline
            imports:
                - $DRP_PIPE_DIR/pipelines/LSSTComCam/DRP-v2.yaml
            parameters:
                release_id: 52
            """
        )
        pipeline_graph = pipeline.to_graph()
        regex = re.compile(r"config\.(.+)\.release_id\=")
        release_id_options = []
        for task_node in pipeline_graph.tasks.values():
            for match_string in regex.findall(task_node.get_config_str()):
                attribute_path: list[str] = match_string.split(".")
                if any(not term.isidentifier() for term in attribute_path):
                    _LOG.warning(
                        f"Not checking config option {task_node.label}:{match_string}.release_id "
                        "because the test code is not sophisticated enough.  Please improve it."
                    )
                    continue
                config_attribute = task_node.config
                for term in attribute_path:
                    config_attribute = getattr(config_attribute, term)
                self.assertEqual(config_attribute.release_id, 52)
                release_id_options.append((task_node.label, attribute_path))
        # Spot check a few expected entries to make sure a logic bug or bad
        # regex isn't preventing this test from doing anything.
        self.assertIn(("calibrateImage", ["id_generator"]), release_id_options)
        self.assertIn(("detectCoaddPeaks", ["idGenerator"]), release_id_options)


if __name__ == "__main__":
    unittest.main()
