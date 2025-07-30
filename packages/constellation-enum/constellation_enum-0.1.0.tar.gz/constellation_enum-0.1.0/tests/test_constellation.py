"""
Tests for constellation
"""
import unittest
from constellation import Constellation


class TestConstellation(unittest.TestCase):
    
    def test_constellation_access(self):
        """Test direct constellation access"""
        self.assertEqual(Constellation.Andromeda.name, 'Andromeda')
        self.assertEqual(Constellation.Andromeda.abbr, 'And')
    
    def test_abbreviation_access(self):
        """Test access by abbreviation"""
        self.assertEqual(Constellation['And'], Constellation.Andromeda)
        self.assertEqual(Constellation['Ori'], Constellation.Orion)
    
    def test_abbreviation_consistency(self):
        """Test that all constellations have abbreviations"""
        for constellation in Constellation:
            abbr = constellation.abbr
            self.assertIsNotNone(abbr, f"{constellation.name} should have an abbreviation")
            self.assertEqual(len(abbr), 3, f"{constellation.name} abbreviation should be 3 characters")  # type: ignore
    
    def test_unique_abbreviations(self):
        """Test that all abbreviations are unique"""
        abbreviations = [const.abbr for const in Constellation]
        self.assertEqual(len(abbreviations), len(set(abbreviations)), 
                        "All abbreviations should be unique")
    
    def test_total_constellations(self):
        """Test that we have all 88 constellations"""
        self.assertEqual(len(list(Constellation)), 88, "Should have 88 constellations")


if __name__ == '__main__':
    unittest.main()
