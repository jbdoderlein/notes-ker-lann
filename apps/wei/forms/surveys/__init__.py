# Copyright (C) 2018-2021 by BDE ENS Paris-Saclay
# SPDX-License-Identifier: GPL-3.0-or-later

from .base import WEISurvey, WEISurveyInformation, WEISurveyAlgorithm
from .wei2022 import WEISurvey2022


__all__ = [
    'WEISurvey', 'WEISurveyInformation', 'WEISurveyAlgorithm', 'CurrentSurvey',
]

CurrentSurvey = WEISurvey2022
