__author__ = 'adean'

import re
from utils import utils


class DetectorRuleSet:
    def __init__(self, detector_rules_string):
        self.detector_rule_groups = []
        self.set_rule_groups(detector_rules_string)

    def set_rule_groups(self, detector_rules_string):
        results = re.findall('\{.*?\}', detector_rules_string)
        for result in results:
            self.detector_rule_groups.append(DetectorRuleGroup(result))

    @staticmethod
    def get_status_from_detector_group(self, detectors, config, logger):
        detector_result = False
        for detector in detectors:
            klass = utils.Utils.reflect_class_from_classname('detectors', detector)
            if klass.detect_presence(logger, config):
                return True
        return False

    def get_status_for_detector_rule_set(self, config, logger):
        is_system_active = False
        for detector_groups in self.detector_rule_groups:
            is_system_active = is_system_active or DetectorRuleSet.get_status_from_detector_group(self,
                                                                                                  detector_groups.detectors,
                                                                                                  config, logger)
        return is_system_active


class DetectorRuleGroup:
    def __init__(self, detectors):
        detectors = detectors.strip("{").strip("}").split(",")
        self.detectors = detectors
