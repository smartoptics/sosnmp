# Roadmap

## Background

Ilya started this project and worked on the 1.0-4.0 releases.

> Ilya left his ideas on the future of the project in the `TODO.txt` file.

LeXtudio Inc. took over the ecosystem during the 5.0 release cycle after
[its initial announcement](https://github.com/etingof/pysnmp/issues/429).

Now the Python landscape has changed a lot due to frequent Python releases
and breaking changes in each of them. The PySNMP project needs to adapt to
the new reality and provide a better user experience. So after a few
successful releases such as 6.x and 7.0, we decided to plan the future of
the project as below.

## 7.1 Releases

The goals are

- Adapt to async DNS queries.
- Rework on GET NEXT and GET BULK related API surface.
- Fix more known issues reported in the past few years.

Planned tasks are

- [x] Introduced async DNS queries.
- [x] Identified how the new GET NEXT and GET BULK related API should be
  designed.
- [x] Adapt to Python 3.8 end of life.
- [x] PEP 8 cleanup on method names.
- [ ] TODOs

Breaking changes are

- Transport type construction API is completely changed to support
  async DNS queries.

  For example, calls to ``UdpTransportTarget()`` need to move to
  ``await UdpTransportTarget.create()``.
- ``next_cmd`` and ``bulk_cmd`` parameters and return types are revised.
- ``walk_cmd`` and ``bulk_walk_cmd`` are updated accordingly.

## 8.0 Releases

The goals are

- Remove legacy bits related to Python 3.8.
- TODOs

Planned tasks are

- [ ] TODOs

Breaking changes are

- TODOs
