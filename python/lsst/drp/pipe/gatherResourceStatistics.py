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

"""A script-module (intended to be run via ``python -m``) that
machine-generates pipelines for running
`lsst.analysis.drp.GatherResourceStatisticsTask`.
"""

__all__ = ()

import sys

from lsst.analysis.drp.gatherResourceStatistics import GatherResourceStatisticsTask

if __name__ == "__main__":
    GatherResourceStatisticsTask.make_pipeline_cli(sys.argv[1:])
