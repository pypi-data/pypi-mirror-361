How to use logging in this package
==================================

All loggers in this package report to one central logger, which has the name 'smiet'.
This logger is equipped with a ``StreamHandler`` that outputs log messages to the console, using
a somewhat soothing color scheme. The setup is such that all submodule loggers follow the logging
level of this top-level logger. If you want to see debug output, you can simply retrieve the
top-level logger and set the level accordingly:

.. code-block:: python

    import logging

    # Retrieve the top-level logger
    logger = logging.getLogger('smiet')

    # Set the top-level logger to DEBUG
    logger.setLevel(logging.DEBUG)
