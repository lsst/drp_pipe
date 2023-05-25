.. lsst-task-topic:: lsst.drp.pipe.forcedPhotCoadd.ForcedPhotCoaddTask

###################
ForcedPhotCoaddTask
###################

``ForcedPhotCoaddTask`` performs forced measurement on a co-added image using as a reference catalog detections which were made on coadds in other bands.

Butler datasets
===============

Input datasets
--------------

A ``Coadd_src`` variant (e.g. ``deepCoadd_src``)
   Used as the reference catalog.
   This is not loaded directly from the provided ``dataRef``; only the patch and tract are used, while the filter is set by the configuration of the references subtask.
   See ``lsst.meas.base.references.CoaddSrcReferencesTask``.

A ``Coadd_calexp`` variant (e.g. ``deepCoadd_calexp``)
   Used as the measurement image.
   Note that this means that :lsst-task:`lsst.pipe.tasks.multiBand.DetectCoaddSourcesTask` must have been run on the image previously.

Ouptut datasets
---------------

A ``Coadd_forced_src`` variant (e.g. ``deepCoadd_forced_src``)
   The resulting measurement catalog.

.. _lsst.drp.pipe.forcedPhotCoadd.ForcedPhotCoaddTask-api:

Python API summary
==================

.. lsst-task-api-summary:: lsst.meas.base.forcedPhotCoadd.ForcedPhotCoaddTask

.. _lsst.drp.pipe.forcedPhotCoadd.ForcedPhotCoaddTask-subtasks:

Retargetable subtasks
=====================

.. lsst-task-config-subtasks:: lsst.meas.base.forcedPhotCoadd.ForcedPhotCoaddTask

.. _lsst.drp.pipe.forcedPhotCoadd.ForcedPhotCoaddTask-configs:

Configuration fields
====================

.. lsst-task-config-fields:: lsst.meas.base.forcedPhotCoadd.ForcedPhotCoaddTask
