# Copyright 2021 Nathan Young
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import anybadge
import json
from math import floor


def determine_badge_colour(percentage):
    if percentage >= 75:
        colour = "green"
    elif percentage >= 50:
        colour = "orange"
    else:
        colour = "brightred"

    return colour


def write_coverage_badge(filename, percent_covered):
    badge = anybadge.Badge(
        label="coverage",
        value=f"{percent_covered:.1f}%",
        default_color=determine_badge_colour(percent_covered),
    )

    badge.write_badge(filename, overwrite=True)


# Make coverage badge
with open("coverage.json") as file:
    coverage_report = json.load(file)
    percent_covered = coverage_report["totals"]["percent_covered"]
    write_coverage_badge("docs/coverage-badge.svg", percent_covered)
