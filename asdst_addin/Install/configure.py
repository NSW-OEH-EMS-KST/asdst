"""
report and (optionally) modify extension parameters
"""
import arcpy as ap
from asdst_addin import asdst


def main():
    """ Main entry

    Args:

    Returns:

    Raises:
      No raising or catching

    """
    asdst.config.set_user_config(ap.GetParameterAsText(0),
                                 ap.GetParameterAsText(1),
                                 ap.GetParameterAsText(2))


if __name__ == '__main__':
    main()
