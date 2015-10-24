__author__ = 'adean'

import re


class DetectorRuleSet:
    def __init__(self, detector_rules_string):
        self.detector_rules = []
        self.set_rule_groups(detector_rules_string)

    def set_rule_groups(self, detector_rules_string):
        results = re.findall('\{.*?\}', detector_rules_string)
        for result in results:
            self.detector_rules.append(DetectorRuleGroup(result))


class DetectorRuleGroup:
    def __init__(self, detectors):
        detectors = detectors.strip("{").strip("}").split(",")
        self.detectors = detectors
