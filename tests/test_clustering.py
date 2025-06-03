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

import os
import unittest

from lsst.ctrl.bps import BpsConfig, check_clustering_config
from lsst.pipe.base import Pipeline

# Pipelines to check the clustering YAMLs
# In everyday practice, pipelines and clustering configs do not map 1:1.
# But for testing purposes, choose a pipeline that the clustering is
# expected to work with. Keys are clustering yamls. Values are pipelines.
CLUSTERING_PIPELINE_MAPPING = {
    'LSSTCam/DRP-clustering.yaml': 'LSSTCam/DRP.yaml',
    'HSC/DRP-RC2-clustering.yaml': 'HSC/DRP-RC2.yaml',
    'LSSTCam-imSim/DRP-DC2-clustering.yaml': 'LSSTCam-imSim/DRP-test-med-1.yaml',
    'LSSTCam-imSim/DRP-OR5-clustering.yaml': 'LSSTCam-imSim/DRP.yaml',
}

PIPELINES_DIR = os.path.join(os.path.dirname(__file__), "..", "pipelines")
CLUSTERING_DIR = os.path.join(os.path.dirname(__file__), "..", "bps", "clustering")


class ClusteringTestCase(unittest.TestCase):

    def test_clusters(self) -> None:
        """Check clustering yamls.

        Confirm that they do not produce cycles and that the
        two required keys, 'pipetasks' and 'dimensions', are
        are present in each cluster definition.
        """
        for clustering_path, pipeline_path in CLUSTERING_PIPELINE_MAPPING.items():
            # construct pipeline graph from URI
            full_pipeline_path = os.path.join(PIPELINES_DIR, pipeline_path)
            pipeline = Pipeline.from_uri(full_pipeline_path)
            pipeline_graph = pipeline.to_graph()

            # construct bps config from clustering yaml
            full_clustering_path = os.path.join(CLUSTERING_DIR, clustering_path)
            bps_config = BpsConfig(full_clustering_path)

            try:
                check_clustering_config(bps_config["cluster"], pipeline_graph.make_task_xgraph())
            except Exception as e:
                self.fail(f"Clustering config in {clustering_path} is not compatible with pipeline"
                          f" {pipeline_path}: {e}")

            for cluster_name, cluster_info in bps_config["cluster"].items():
                for required_key in ["pipetasks", "dimensions"]:
                    self.assertIn(required_key, cluster_info,
                                  f"Missing '{required_key}' in {clustering_path} for {cluster_name}")


if __name__ == "__main__":
    unittest.main()
