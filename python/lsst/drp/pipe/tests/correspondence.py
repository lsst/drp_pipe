# This file is part of drp_pipe.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Tooling for relating one pipeline to another.

This is intended for cases where the tasks are largely the same, but task
labels and dataset type names have changed substantially.
"""

from __future__ import annotations

__all__ = ("Correspondence",)

import csv
import dataclasses
import logging
import os.path
from collections.abc import Iterable

from lsst.pex.config import compareConfigs
import pydantic

from lsst.pipe.base.pipeline_graph import PipelineGraph, NodeType, TaskNode

_LOG = logging.getLogger(__name__)


def without_automatic_connections(names: Iterable[str]) -> list[str]:
    return [
        name
        for name in names
        if not name.endswith("_config") and not name.endswith("_log") and not name.endswith("_metadata")
    ]


class Correspondence(pydantic.BaseModel):
    """A serializable mapping from one pipeline to another."""

    tasks_new_to_old: dict[str, str] = pydantic.Field(
        default_factory=dict, description="Mapping from new task label to old task label."
    )
    dataset_types_new_to_old: dict[str, str] = pydantic.Field(
        default_factory=dict, description="Mapping from new dataset type name to old dataset type name."
    )
    unmappable_new_tasks: dict[str, str] = pydantic.Field(
        default_factory=dict,
        description="Tasks that exist only in the new pipeline, with values providing reasons why.",
    )
    unmappable_old_tasks: dict[str, str] = pydantic.Field(
        default_factory=dict,
        description="Tasks that exist only in the old pipeline, with values providing reasons why.",
    )
    unmappable_new_dataset_types: dict[str, str] = pydantic.Field(
        default_factory=dict,
        description="Dataset types that exist only in the new pipeline, with values providing reasons why.",
    )
    unmappable_old_dataset_types: dict[str, str] = pydantic.Field(
        default_factory=dict,
        description="Dataset types that exist only in the old pipeline, with values providing reasons why.",
    )
    config_ignores: dict[str, list[str]] = pydantic.Field(
        default_factory=dict,
        description=(
            "Configuration lines to ignore in the diff.  "
            "Keys are new task labels, values are config file line prefixes."
        ),
    )

    @classmethod
    def read(cls, filename: str) -> Correspondence:
        """Read the correspondence from a JSON file."""
        with open(filename, "r") as stream:
            return Correspondence.model_validate_json(stream.read())

    def write(self, filename: str) -> None:
        """Write the correspondence to a JSON file."""
        with open(filename, "w") as stream:
            stream.write(self.model_dump_json(indent=2))

    def sorted(self, new: PipelineGraph, old: PipelineGraph) -> Correspondence:
        """Sort the correspondence by the pipeline graph order.

        Parameters
        ----------
        new : `lsst.pipe.base.PipelineGraph`
            New pipeline graph.
        old : `lsst.pipe.base.PipelineGraph`
            Old pipeline graph.

        Returns
        -------
        correspondence : `Correspondence`
            New sorted mapping between the two pipelines.
        """
        result = Correspondence()
        for new_label in new.tasks.keys():
            if (old_label := self.tasks_new_to_old.get(new_label)) is not None:
                result.tasks_new_to_old[new_label] = old_label
            elif (reason := self.unmappable_new_tasks.get(new_label)) is not None:
                result.unmappable_new_tasks[new_label] = reason
            if new_label in self.config_ignores:
                result.config_ignores[new_label] = self.config_ignores[new_label].copy()
        for old_label in old.tasks.keys():
            if (reason := self.unmappable_old_tasks.get(old_label)) is not None:
                result.unmappable_old_tasks[old_label] = reason
        for new_name in new.dataset_types.keys():
            if (old_name := self.dataset_types_new_to_old.get(new_name)) is not None:
                result.dataset_types_new_to_old[new_name] = old_name
            elif (reason := self.unmappable_new_dataset_types.get(new_name)) is not None:
                result.unmappable_new_dataset_types[new_name] = reason
        for old_name in old.dataset_types.keys():
            if (reason := self.unmappable_old_dataset_types.get(old_name)) is not None:
                result.unmappable_old_dataset_types[old_name] = reason
        assert result.config_ignores.keys() == self.config_ignores.keys()
        return result

    def check(self, new: PipelineGraph, old: PipelineGraph, new_name: str, old_name: str) -> list[str]:
        """Check the correspondence for consistency with the given pipeline
        graphs.

        Parameters
        ----------
        new : `lsst.pipe.base.PipelineGraph`
            New pipeline graph.
        old : `lsst.pipe.base.PipelineGraph`
            Old pipeline graph.
        new_name : `str`
            Name of the new pipeline for use in messages.
        old_name : `str`
            Name of the old pipeline for use in messages.

        Returns
        -------
        messages : `list` [ `str` ]
            List of messages reporting problems.  If empty, there are no
            problems.
        """
        messages: list[str] = []
        tasks_old_to_new = {old_label: new_label for new_label, old_label in self.tasks_new_to_old.items()}
        if len(tasks_old_to_new) != len(self.tasks_new_to_old):
            for new_label, old_label in self.tasks_new_to_old.items():
                if tasks_old_to_new[old_label] != new_label:
                    messages.append(
                        f"Task {old_label} in {old_name} is mapped to both {new_label} and "
                        f"{tasks_old_to_new[old_label]} in {new_name}."
                    )
        for label in sorted(tasks_old_to_new.keys() - old.tasks.keys()):
            messages.append(f"Task {label!r} is mapped but is not part of {old_name}.")
        for label in sorted(self.tasks_new_to_old.keys() - new.tasks.keys()):
            messages.append(f"Task {label!r} is mapped but is not part of {new_name}.")
        for label in sorted(self.unmappable_old_tasks.keys() - old.tasks.keys()):
            messages.append(f"Task {label!r} is marked as unmappable but is not part of {old_name}.")
        for label in sorted(self.unmappable_new_tasks.keys() - new.tasks.keys()):
            messages.append(f"Task {label!r} is marked as unmappable but is not part of {new_name}.")
        missing_old_tasks = set(old.tasks.keys())
        missing_old_tasks.difference_update(tasks_old_to_new.keys())
        missing_old_tasks.difference_update(self.unmappable_old_tasks)
        for label in sorted(missing_old_tasks):
            messages.append(
                f"Task {label!r} in {old_name} is missing from the "
                "correspondence; it needs to be mapped or marked as unmappable."
            )
        missing_new_tasks = set(new.tasks.keys())
        missing_new_tasks.difference_update(self.tasks_new_to_old.keys())
        missing_new_tasks.difference_update(self.unmappable_new_tasks)
        for label in sorted(missing_new_tasks):
            messages.append(
                f"Task {label!r} in {new_name} is missing from the "
                "correspondence; it needs to be mapped or marked as unmappable."
            )
        dataset_types_old_to_new = {
            old_label: new_label for new_label, old_label in self.dataset_types_new_to_old.items()
        }
        old_dataset_types = set(without_automatic_connections(old.dataset_types.keys()))
        new_dataset_types = set(without_automatic_connections(new.dataset_types.keys()))
        if len(dataset_types_old_to_new) != len(self.dataset_types_new_to_old):
            for new_label, old_label in self.dataset_types_new_to_old.items():
                if dataset_types_old_to_new[old_label] != new_label:
                    messages.append(
                        f"Dataset type {old_label} in {old_name} is mapped to both {new_label} and "
                        f"{dataset_types_old_to_new[old_label]} in {new_name}."
                    )
        for name in sorted(dataset_types_old_to_new.keys() - old_dataset_types):
            messages.append(
                f"Dataset type {name!r} is mapped by the correspondence but is not part of {old_name}."
            )
        for name in sorted(self.dataset_types_new_to_old.keys() - new_dataset_types):
            messages.append(
                f"Dataset type {name!r} is mapped by the correspondence but is not part of {new_name}."
            )
        for name in sorted(self.unmappable_old_dataset_types.keys() - old_dataset_types):
            messages.append(f"Dataset type {name!r} is marked as unmappable but is not part of {old_name}.")
        for name in sorted(self.unmappable_new_dataset_types.keys() - new_dataset_types):
            messages.append(f"Dataset type {name!r} is marked as unmappable but is not part of {new_name}.")
        missing_old_dataset_types = set(without_automatic_connections(old.dataset_types.keys()))
        missing_old_dataset_types.difference_update(dataset_types_old_to_new.keys())
        missing_old_dataset_types.difference_update(self.unmappable_old_dataset_types)
        for name in sorted(missing_old_dataset_types):
            messages.append(
                f"Dataset type {name!r} in {old_name} is missing from the "
                "correspondence; it needs to be mapped or marked as unmappable."
            )
        missing_new_dataset_types = set(without_automatic_connections(new_dataset_types))
        missing_new_dataset_types.difference_update(self.dataset_types_new_to_old.keys())
        missing_new_dataset_types.difference_update(self.unmappable_new_dataset_types)
        for name in sorted(missing_new_dataset_types):
            messages.append(
                f"Dataset type {name!r} in {new_name} is missing from the "
                "correspondence; it needs to be mapped or marked as unmappable."
            )
        return messages

    def find_matches(self, new: PipelineGraph, old: PipelineGraph) -> Correspondence:
        """Return a new `Correspondence` that includes new mappings inferred
        from the graph structure.

        Parameters
        ----------
        new : `lsst.pipe.base.PipelineGraph`
            New pipeline graph.
        old : `lsst.pipe.base.PipelineGraph`
            Old pipeline graph.

        Returns
        -------
        correspondence : `Correspondence`
            New mapping between the two pipelines.
        """
        # Switch to a new data structure that's duplicative but more symmetric
        # for matching.  At the same time, we trim out tasks and dataset types
        # that aren't present in their respective pipelines so we have a chance
        # at automatically recovering after updates and renames.
        new_side = _CorrespondenceFinderSide(new)
        tasks_new_to_old = {
            new_label: old_label
            for new_label, old_label in self.tasks_new_to_old.items()
            if new_label in new.tasks.keys() and old_label in old.tasks.keys()
        }
        dataset_types_new_to_old = {
            new_name: old_name
            for new_name, old_name in self.dataset_types_new_to_old.items()
            if new_name in new.dataset_types.keys() and old_name in old.dataset_types.keys()
        }
        new_side.map_tasks.update(tasks_new_to_old)
        new_side.map_dataset_types.update(dataset_types_new_to_old)
        new_side.unmappable_tasks.update(self.unmappable_new_tasks.keys() & new.tasks.keys())
        new_side.unmappable_dataset_types.update(
            self.unmappable_new_dataset_types.keys() & new.dataset_types.keys()
        )
        old_side = _CorrespondenceFinderSide(old)
        old_side.map_tasks.update({old: new for new, old in tasks_new_to_old.items()})
        old_side.map_dataset_types.update({old: new for new, old in dataset_types_new_to_old.items()})
        old_side.unmappable_tasks.update(self.unmappable_old_tasks.keys() & old.tasks.keys())
        old_side.unmappable_dataset_types.update(
            self.unmappable_old_dataset_types.keys() & old.dataset_types.keys()
        )
        # Start by assuming identical names should correspond, as long as they
        # haven't explicitly been matched to something else already.
        for task_label in new_side.unmatched_tasks & old_side.unmatched_tasks:
            if new_side.task_nodes_match(task_label, task_label, old_side):
                new_side.relate_tasks(task_label, task_label, old_side)
        for dataset_type_name in new_side.unmatched_dataset_types & old_side.unmatched_dataset_types:
            if new_side.dataset_type_nodes_match(dataset_type_name, dataset_type_name, old_side):
                new_side.relate_dataset_types(dataset_type_name, dataset_type_name, old_side)
        _LOG.info(
            f"{len(new_side.map_tasks)} tasks, {len(new_side.map_dataset_types)} dataset types "
            "mapped after direct-name matching."
        )
        # Attempt to incrementally improve the correspondence by looking at
        # matching bits of graph structure.
        successes = True
        n_iterations = 0
        while successes:
            successes = 0
            for new_task_label in new_side.unmatched_tasks:
                successes += new_side.match_task_via_output_producers(new_task_label, old_side, "<-")
            for old_task_label in old_side.unmatched_tasks:
                successes += old_side.match_task_via_output_producers(old_task_label, new_side, "->")
            for new_dataset_type_name in new_side.unmatched_dataset_types:
                successes += new_side.match_dataset_type_via_producer_outputs(
                    new_dataset_type_name, old_side, "<-"
                )
            for old_dataset_type_name in old_side.unmatched_tasks:
                successes += old_side.match_dataset_type_via_producer_outputs(
                    old_dataset_type_name, new_side, "->"
                )
            for new_task_label in new_side.unmatched_tasks:
                successes += new_side.match_task_via_input_consumers(new_task_label, old_side, "<-")
            for old_task_label in old_side.unmatched_tasks:
                successes += old_side.match_task_via_input_consumers(old_task_label, new_side, "->")
            for new_dataset_type_name in new_side.unmatched_dataset_types:
                successes += new_side.match_dataset_type_via_consumer_inputs(
                    new_dataset_type_name, old_side, "<-"
                )
            for old_dataset_type_name in old_side.unmatched_tasks:
                successes += old_side.match_dataset_type_via_consumer_inputs(
                    old_dataset_type_name, new_side, "->"
                )
            n_iterations += 1
            _LOG.info(
                f"{len(new_side.map_tasks)} tasks, {len(new_side.map_dataset_types)} dataset types "
                f"after iteration {n_iterations}."
            )
        result = Correspondence()
        result.tasks_new_to_old.update(new_side.map_tasks.items())
        result.dataset_types_new_to_old.update(new_side.map_dataset_types.items())
        result.unmappable_new_tasks.update(
            {label: self.unmappable_new_tasks.get(label, "") for label in new_side.unmappable_tasks}
        )
        result.unmappable_old_tasks.update(
            {label: self.unmappable_old_tasks.get(label, "") for label in old_side.unmappable_tasks}
        )
        result.unmappable_new_dataset_types.update(
            {
                name: self.unmappable_new_dataset_types.get(name, "")
                for name in new_side.unmappable_dataset_types
            }
        )
        result.unmappable_old_dataset_types.update(
            {
                name: self.unmappable_old_dataset_types.get(name, "")
                for name in old_side.unmappable_dataset_types
            }
        )
        result.config_ignores = {
            new_label: ignore_lines.copy() for new_label, ignore_lines in self.config_ignores.items()
        }
        return result

    def diff_task_configs(self, new: TaskNode, old: TaskNode) -> list[str]:
        # We'll do a diff of the config strings (in config-override-file form),
        # but excise all of the config.connections lines that we know will have
        # differences, as well as all of the comments and blank lines.
        ignore_prefixes = ["connections."]
        ignore_prefixes.extend(self.config_ignores.get(new.label, []))
        messages: list[str] = []

        def output(msg: str) -> None:
            if not any(msg.startswith(prefix) for prefix in ignore_prefixes):
                messages.append(msg)

        compareConfigs(new.label, new.config, old.config, output=output)
        return messages

    def write_task_csv(self, filename: str, new: PipelineGraph, old: PipelineGraph) -> None:
        """Write the mapping between tasks to a CSV file.

        Parameters
        ----------
        filename : `str`
            Name of the file.
        new : `lsst.pipe.base.PipelineGraph`
            New pipeline graph.
        old : `lsst.pipe.base.PipelineGraph`
            Old pipeline graph.
        """
        with open(filename, "w") as stream:
            writer = csv.writer(stream, delimiter=";")
            n = 0
            for new_label, new_task_node in new.tasks.items():
                step = new.get_task_step(new_label)
                old_label = self.tasks_new_to_old.get(new_label, "")
                writer.writerow(
                    [
                        n,
                        step,
                        new_label,
                        old_label,
                        new_task_node.task_class_name,
                        ", ".join(new_task_node.dimensions.required),
                    ]
                )
                n += 1
            for old_label, old_task_node in old.tasks.items():
                if old_label in self.unmappable_old_tasks:
                    writer.writerow(
                        [
                            n,
                            "",
                            "",
                            old_label,
                            old_task_node.task_class_name,
                            ", ".join(old_task_node.dimensions.required),
                        ]
                    )
                    n += 1

    def write_dataset_type_csv(self, filename: str, new: PipelineGraph, old: PipelineGraph) -> None:
        """Write the mapping between dataset types to a CSV file.

        Parameters
        ----------
        filename : `str`
            Name of the file.
        new : `lsst.pipe.base.PipelineGraph`
            New pipeline graph.
        old : `lsst.pipe.base.PipelineGraph`
            Old pipeline graph.
        """
        with open(filename, "w") as stream:
            writer = csv.writer(stream, delimiter=";")
            n = 0
            for new_name in without_automatic_connections(new.dataset_types):
                new_dataset_type_node = new.dataset_types[new_name]
                old_name = self.dataset_types_new_to_old.get(new_name, "")
                writer.writerow(
                    [
                        n,
                        new_name,
                        old_name,
                        new_dataset_type_node.storage_class_name,
                        ", ".join(new_dataset_type_node.dimensions.required),
                    ]
                )
                n += 1
            for old_name in without_automatic_connections(old.dataset_types):
                if old_name in self.unmappable_old_dataset_types:
                    old_dataset_type_node = old.dataset_types[old_name]
                    writer.writerow(
                        [
                            n,
                            "",
                            old_name,
                            old_dataset_type_node.storage_class_name,
                            ", ".join(old_dataset_type_node.dimensions.required),
                        ]
                    )
                    n += 1


@dataclasses.dataclass
class _CorrespondenceFinderSide:
    """An alternate data structure for pipeline-pipeline mapping, used in
    `Correspondence.find_matches`.

    One instance of this class is expected to be paired with another
    representing the reverse mapping.
    """

    pipeline_graph: PipelineGraph
    """Pipeline graph this side maps from."""

    map_tasks: dict[str, str] = dataclasses.field(default_factory=dict)
    """Mapping of tasks, from this side to the other."""

    map_dataset_types: dict[str, str] = dataclasses.field(default_factory=dict)
    """Mapping of dataset types, from this side to the other."""

    unmappable_tasks: set[str] = dataclasses.field(default_factory=set)
    """Tasks on this side that cannot be mapped."""

    unmappable_dataset_types: set[str] = dataclasses.field(default_factory=set)
    """Dataset types on this side that cannot be mapped."""

    @property
    def unmatched_tasks(self) -> set[str]:
        """Tasks on this side that could be mapped but have not yet been."""
        result = set(self.pipeline_graph.tasks.keys())
        result.difference_update(self.map_tasks.keys())
        result.difference_update(self.unmappable_tasks)
        return result

    @property
    def unmatched_dataset_types(self) -> set[str]:
        """Dataset types on this side that could be mapped but have not yet
        been.
        """
        result = set(without_automatic_connections(self.pipeline_graph.dataset_types.keys()))
        result.difference_update(self.map_dataset_types.keys())
        result.difference_update(self.unmappable_dataset_types)
        return result

    def relate_tasks(self, label: str, other_label: str, other: _CorrespondenceFinderSide) -> None:
        """Add a mapping between the given task labels."""
        self.map_tasks[label] = other_label
        other.map_tasks[other_label] = label

    def relate_dataset_types(self, name: str, other_name: str, other: _CorrespondenceFinderSide) -> None:
        """Add a mapping between the given dataset type names."""
        self.map_dataset_types[name] = other_name
        other.map_dataset_types[other_name] = name

    def task_nodes_match(self, label: str, other_label: str, other: _CorrespondenceFinderSide) -> bool:
        """Test whether two tasks can be matched.

        This checks whether the tasks are still available to be matched and
        whether they have the same task class and dimensions.
        """
        if label in self.map_tasks:
            return False
        if label in self.unmappable_tasks:
            return False
        if other_label in other.map_tasks:
            return False
        if other_label in other.unmappable_tasks:
            return False
        new_node = self.pipeline_graph.tasks[label]
        old_node = other.pipeline_graph.tasks[other_label]
        return (
            new_node.dimensions == old_node.dimensions
            and new_node.task_class_name == old_node.task_class_name
        )

    def dataset_type_nodes_match(self, name: str, other_name: str, other: _CorrespondenceFinderSide) -> bool:
        """Test whether two dataset types can be matched.

        This checks whether the dataset types are still available to be matched
        and whether they have the same storage class and dimensions.
        """
        if name in self.map_dataset_types:
            return False
        if name in self.unmappable_dataset_types:
            return False
        if other_name in other.map_dataset_types:
            return False
        if other_name in other.unmappable_dataset_types:
            return False
        new_node = self.pipeline_graph.dataset_types[name]
        old_node = other.pipeline_graph.dataset_types[other_name]
        return (
            new_node.dimensions == old_node.dimensions
            and new_node.storage_class_name == old_node.storage_class_name
        )

    def match_task_via_output_producers(
        self, label: str, other: _CorrespondenceFinderSide, direction: str
    ) -> bool:
        """Look for a match for the given task by inspecting the mappings of
        its outputs' producers.
        """
        my_outputs = self.pipeline_graph.outputs_of(label).keys() - self.unmappable_tasks
        other_outputs = {
            other_output
            for my_output in my_outputs
            if (other_output := self.map_dataset_types.get(my_output)) is not None
        }
        other_output_producers = {
            other_producer_node.label
            for other_output in other_outputs
            if (other_producer_node := other.pipeline_graph.producer_of(other_output)) is not None
            and self.task_nodes_match(label, other_producer_node.label, other)
        }
        other_output_producers -= other.unmappable_tasks
        if len(other_output_producers) == 1:
            other_label = other_output_producers.pop()
            _LOG.debug(f"Successful output producer match {label} {direction} {other_label}.")
            self.relate_tasks(label, other_label, other)
            return True
        else:
            _LOG.info(f"No unique output producer match for {label} {direction}: {other_output_producers}.")
        return False

    def match_task_via_input_consumers(
        self, label: str, other: _CorrespondenceFinderSide, direction: str
    ) -> bool:
        """Look for a match for the given task by inspecting the mappings of
        its inputs' consumers.
        """
        my_inputs = self.pipeline_graph.inputs_of(label).keys() - self.unmappable_dataset_types
        other_inputs = {
            other_input
            for my_input in my_inputs
            if (other_input := self.map_dataset_types.get(my_input)) is not None
        }
        other_input_consumers = {
            other_input_consumer_node.label
            for other_input in other_inputs
            for other_input_consumer_node in other.pipeline_graph.consumers_of(other_input)
            if self.task_nodes_match(label, other_input_consumer_node.label, other)
        }
        other_input_consumers -= other.unmappable_tasks
        if len(other_input_consumers) == 1:
            other_label = other_input_consumers.pop()
            _LOG.debug(f"Successful input consumer match {label} {direction} {other_label}.")
            self.relate_tasks(label, other_label, other)
            return True
        else:
            _LOG.info(f"No unique input consumer match for {label} {direction}: {other_input_consumers}.")
        return False

    def match_dataset_type_via_producer_outputs(
        self,
        name: str,
        other: _CorrespondenceFinderSide,
        direction: str,
    ) -> bool:
        """Look for a match for the given dataset type by inspecting the
        mappings of its producer's outputs.
        """
        if (my_producer_node := self.pipeline_graph.producer_of(name)) is None:
            _LOG.info(f"No producer output match for {name} {direction}; it is an overall input.")
            return False
        if my_producer_node.label in self.unmappable_tasks:
            _LOG.debug(f"No producer output match for {name} {direction}; its producer is unmappable.")
            self.unmappable_dataset_types.add(name)
            return True
        if (other_producer := self.map_tasks.get(my_producer_node.label)) is None:
            _LOG.info(f"No producer output match for {name} {direction}; its producer is not mapped yet.")
            return False
        other_producer_outputs = {
            other_producer_output
            for other_producer_output in other.pipeline_graph.outputs_of(
                other_producer,
                init=(my_producer_node.key.node_type is NodeType.TASK_INIT),
            )
            if self.dataset_type_nodes_match(name, other_producer_output, other)
        }
        other_producer_outputs -= other.unmappable_dataset_types
        if len(other_producer_outputs) == 1:
            other_name = other_producer_outputs.pop()
            _LOG.debug(f"Unique producer output match {name} {direction} {other_name}.")
            self.relate_dataset_types(name, other_name, other)
            return True
        elif len(other_producer_outputs) > 1:
            common_suffix_scores = [
                (self.compute_common_suffix_length(name, other_name), other_name)
                for other_name in other_producer_outputs
            ]
            common_suffix_scores.sort(reverse=True)
            best_score, other_name = common_suffix_scores[0]
            next_best_score, _ = common_suffix_scores[1]
            if best_score > next_best_score:  # no tie for first place
                _LOG.debug(f"Scored producer output match {name} {direction} {other_name}.")
                self.relate_dataset_types(name, other_name, other)
                return True
            _LOG.info(f"No unique producer output match for {name} {direction}: {common_suffix_scores}.")
        else:
            _LOG.info(f"No producer output matches for {name} {direction}.")
        return False

    def match_dataset_type_via_consumer_inputs(
        self,
        name: str,
        other: _CorrespondenceFinderSide,
        direction: str,
    ) -> bool:
        """Look for a match for the given dataset type by inspecting the
        mappings of its consumers' inputs.
        """
        my_consumers = {my_consumer_node.label for my_consumer_node in self.pipeline_graph.consumers_of(name)}
        my_consumers -= self.unmappable_tasks
        other_consumers = {
            other_consumer
            for my_consumer in my_consumers
            if (other_consumer := self.map_tasks.get(my_consumer)) is not None
        }
        other_consumer_inputs = {
            other_consumer_input
            for other_consumer in other_consumers
            for other_consumer_input in other.pipeline_graph.inputs_of(other_consumer)
            if self.dataset_type_nodes_match(name, other_consumer_input, other)
        }
        other_consumer_inputs -= other.unmappable_dataset_types
        if len(other_consumer_inputs) == 1:
            other_name = other_consumer_inputs.pop()
            _LOG.info(f"Successful consumer input match {name} {direction} {other_name}.")
            self.relate_dataset_types(name, other_name, other)
            return True
        else:
            _LOG.info(f"No unique consumer input match for {name} {direction}: {other_consumer_inputs}.")
        return False

    @staticmethod
    def compute_common_suffix_length(name1: str, name2: str) -> int:
        """Count the number of consecutive characters the two strings have in
        common, starting from their ends.
        """
        rev1 = name1[::-1]
        rev2 = name2[::-1]
        return len(os.path.commonprefix([rev1, rev2]))


def _main():
    import argparse
    from lsst.pipe.base import Pipeline

    parser = argparse.ArgumentParser("Create CSV files from a pipeline correspondence.")
    parser.add_argument("new", help="New pipeline YAML filename.")
    parser.add_argument("old", help="Old pipeline YAML filename.")
    parser.add_argument("correspondence", help="Correspondence JSON file.")
    parser.add_argument("--tasks", default="tasks.csv", help="Filename for task CSV.")
    parser.add_argument("--dataset-types", default="dataset-types.csv", help="Filename for dataset type CSV.")
    args = parser.parse_args()
    new = Pipeline.from_uri(args.new).to_graph(visualization_only=True)
    old = Pipeline.from_uri(args.old).to_graph(visualization_only=True)
    correspondence = Correspondence.read(args.correspondence)
    if args.tasks:
        correspondence.write_task_csv(args.tasks, new, old)
    if args.dataset_types:
        correspondence.write_dataset_type_csv(args.dataset_types, new, old)


if __name__ == "__main__":
    _main()
