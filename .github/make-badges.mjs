// Copyright 2021 Nathan Young
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//    https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
import { readFileSync, writeFileSync } from "fs"
import { makeBadge } from "badge-maker"

function determineBadgeColour(percentage) {
  let colour;

  if (percentage >= 75) {
    colour = "success"
  } else if (percentage >= 50) {
    colour = "important"
  } else {
    colour = "critical"
  }

  return colour;
}

function writeCoverageBadge(filename, percentageCovered) {
  writeFileSync(filename, makeBadge({
    label: "coverage",
    message: `${percentageCovered.toFixed(0)}%`,
    color: determineBadgeColour(percentageCovered),
    style: "flat",
  }))
}

// Make coverage badge
const coverageReport = JSON.parse(readFileSync("coverage.json"))
writeCoverageBadge("docs/images/coverage-badge.svg", coverageReport.totals.percent_covered)
