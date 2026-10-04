import copy
import unittest

import yaml

from validate_horsemanship_tree import SKILL, validate


class HorsemanshipTreeTest(unittest.TestCase):
    def setUp(self):
        self.skill = yaml.safe_load(SKILL.read_text())

    def test_current_layout(self):
        self.assertEqual([], validate(self.skill, copy.deepcopy(self.skill)))

    def test_duplicate_visible_node(self):
        self.skill['perks']['fleetfoot']['coords'] = self.skill['perks']['long_haul']['coords']
        self.assertTrue(any('node collision' in error for error in validate(self.skill)))

    def test_connection_over_node(self):
        self.skill['perks']['rein_sense']['connection_line']['1']['position'] = '4,6'
        self.assertTrue(any('line overlaps node' in error for error in validate(self.skill)))

    def test_duplicate_line_slot(self):
        self.skill['perks']['urge']['connection_line']['1']['position'] = '1,6'
        self.assertTrue(any('line collision' in error for error in validate(self.skill)))

    def test_wrong_corner_direction(self):
        corner = self.skill['perks']['heavy_cavalry']['connection_line']['1']
        corner.update(locked='GRAY_DYE:1172716', unlockable='ORANGE_DYE:1172816', unlocked='LIME_DYE:1172916')
        self.assertTrue(any('incorrect prerequisite path' in error for error in validate(self.skill)))

    def test_gameplay_change_is_rejected(self):
        baseline = copy.deepcopy(self.skill)
        self.skill['perks']['iron_vanguard']['requireperk_all'] = ['first_impact']
        self.assertTrue(any('gameplay fields changed: iron_vanguard' in error for error in validate(self.skill, baseline)))

    def test_cost_and_experience_change_are_rejected(self):
        baseline = copy.deepcopy(self.skill)
        self.skill['perks']['urge']['cost'] = 2
        self.skill['experience']['daily_limit'] = 100
        errors = validate(self.skill, baseline)
        self.assertIn('perk gameplay fields changed: urge', errors)
        self.assertIn('skill gameplay fields / perk IDs changed', errors)

    def test_presentation_only_changes_are_allowed(self):
        baseline = copy.deepcopy(self.skill)
        self.skill['perks']['urge']['icon'] = 'SADDLE'
        self.skill['perks']['urge']['description'] = '&7Active Ability'
        self.assertEqual([], validate(self.skill, baseline))


if __name__ == '__main__':
    unittest.main()
