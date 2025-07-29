pok plugin for `Tutor <https://docs.tutor.edly.io>`__
#####################################################

Tutor plugin to integrate POK certificates into Open edX

About POK
*********

`POK <https://pok.tech>`_ revolutionizes credential management with powerful analytics and branding capabilities.

**Smart Credentials**
  Track the real impact of your credentials with real-time metrics. See how many are viewed, shared on LinkedIn, or downloaded. Understand how they create career opportunities and improve your strategy based on concrete data.

**Brand Customization**
  Customize every aspect of your credential experience - from pages to emails - with your logo, colors, and messages. Support for AI-powered automatic translations ensures a consistent brand experience globally.

**Actionable Insights**
  Capture leads from your branded pages, access valuable insights on credential interactions, and download reports with one click. Our learning paths and analytics dashboards help improve user retention and drive growth.

Installation
************

.. code-block:: bash

    pip install git+https://github.com/aulasneo/tutor-contrib-pok

Usage
*****

.. code-block:: bash

    tutor plugins enable pok


Version Management
******************

This project uses `bump2version <https://github.com/c4urself/bump2version>`_ to manage version numbers. The version is maintained in ``tutorpok/__about__.py``.

To install bump2version:

.. code-block:: bash

    pip install bump2version

To bump the version:

- For bug fixes (0.0.x): ``bump2version patch``
- For new features (0.x.0): ``bump2version minor``
- For breaking changes (x.0.0): ``bump2version major``

Changelog
*********

See `CHANGELOG.md <CHANGELOG.md>`_ for a history of changes to this project.

License
*******

This software is licensed under the terms of the AGPLv3.
