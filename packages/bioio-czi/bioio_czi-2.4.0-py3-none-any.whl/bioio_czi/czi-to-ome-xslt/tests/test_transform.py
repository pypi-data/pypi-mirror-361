#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path

import lxml.etree as ET
from ome_types import from_xml
import pytest

###############################################################################

TEST_DIR = Path(__file__).parent
RESOURCES_DIR = TEST_DIR / "resources"

REPO_DIR = TEST_DIR.parent


@pytest.fixture
def xslt_path():
    return str(REPO_DIR / "xslt" / "czi-to-ome.xsl")


###############################################################################


@pytest.mark.parametrize(
    "czi_xml_filename",
    [
        "s_3_t_1_c_3_z_5.czi.xml",
        "s_1_t_1_c_5_z_20.czi.xml",
        "s_3_t_1_c_3_z_5_with_subblocks.czi.xml",
        "s_1_t_1_c_5_z_20_with_subblocks.czi.xml",
        "subblocks.czi.xml",
        "RBG-8bit.czi.xml",
        "031816_Paxillin_2.czi.xml"
    ],
)
def test_transform(xslt_path: str, czi_xml_filename: str):
    # Get full path for CZI XML
    czi_xml_filepath = str(RESOURCES_DIR / czi_xml_filename)

    # Parse template and generate transform function
    template = ET.parse(xslt_path)
    transformer = ET.XSLT(template)

    # Parse CZI XML
    czixml = ET.parse(czi_xml_filepath)

    # Attempt to run transform
    try:
        omexml = transformer(czixml)

        # Uncomment this block to look at produced OME XML when manual testing
        # with open("produced.ome.xml", "w") as f:
        #     f.write(ET.tostring(omexml, pretty_print=True, encoding="unicode"))

    # Catch any exception
    except Exception as e:
        print("Error during transform")
        print("-" * 80)
        print("Full Log:")
        for entry in transformer.error_log:
            print(
                (
                    f"{entry.filename}: {entry.line}, "
                    f"{entry.column}> {entry.message}>"
                )
            )
        raise e

    # Test read from OME-Types
    from_xml(str(omexml))


@pytest.mark.parametrize(
    "czi_xml_filename, expected_lasers",
    [
        (
            "Confocal_test_4c.czi.xml",
            [
                '<ome:Laser ID="LightSource:MTBLKM980LaserLine561"/>',
                '<ome:Laser ID="LightSource:MTBLKM980LaserLine488"/>',
                '<ome:Laser ID="LightSource:MTBLKM980LaserLine405"/>',
                '<ome:Laser ID="LightSource:MTBLKM980LaserLine639"/>',
            ],
        )
    ],
)
def test_empty_wavelength_transform(xslt_path: str, czi_xml_filename: str, expected_lasers: list):
    # Arrange
    czi_xml_filepath = str(RESOURCES_DIR / czi_xml_filename)
    template = ET.parse(xslt_path)
    transformer = ET.XSLT(template)
    czixml = ET.parse(czi_xml_filepath)

    # Act
    omexml = transformer(czixml)
    omexml_str = ET.tostring(omexml, pretty_print=True, encoding="unicode")

    # Assert
    for laser in expected_lasers:
        assert laser in omexml_str, f"Expected laser {laser} not found in transformed XML"

    # Test that the resulting XML can be read by OME-Types
    from_xml(omexml_str)