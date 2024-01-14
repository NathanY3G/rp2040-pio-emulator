# Changelog

## Unreleased

### Added
- Support `input_source`'s with different signatures.

### Changed
- Updated dependencies used for development.
- Updated dependencies used by examples.
- Updated dependencies used by the Jupyter Notebook example. Thanks Dependabot!

## 0.82.0 (2023-11-27)

### Added
- Options to control program wrapping. Thanks [Josverl](https://github.com/Josverl).
- Additional documentation - FAQ.
- Python 3.12 to the CI build matrix.

### Changed
- Refactored tests to be more explicit regarding program counter advance.
- Updated dependencies used for development.
- Updated dependencies used by the Jupyter Notebook example. Thanks Dependabot!

## v0.81.0 (2023-06-10)

### Added
- Additional documentation - a Tour of pioemu.

### Changed
- Fixed incorrect pin values when `input_source` was used. Thanks  [winnylourson](https://github.com/winnylourson).
- Updated dependencies used by the Jupyter Notebook example. Thanks Dependabot!

## v0.80.0 (2023-04-16)

### Added
- Support for the receive FIFO and the `PUSH` instruction. Thanks @[aaronjamt](https://github.com/aaronjamt).
- Support for the `PUSH IfFull` and `PULL IfEmpty` instruction variants.
- Additional tests.

### Changed
- Fixed reporting of FIFO contents in before state for `PUSH` and `PULL` instructions.
- Improved support for stalling the execution of instructions.
- Refactored some tests to improve consistency.
- Updates to the `README`. Thanks @[aaronjamt](https://github.com/aaronjamt).

## v0.79.0 (2023-03-31)

### Added
- Support for the `OUT PC` and `ISR` instructions. Thanks @[aaronjamt](https://github.com/aaronjamt).
- Type-hints for documentation and to improve maintainability.

## v0.78.0 (2023-03-25)

### Added
- Support for the `IN` instruction.
- Support for the `MOV PC` instruction. Thanks @[aaronjamt](https://github.com/aaronjamt).

### Changed
- Improved support for advancing the program counter.

### Removed
- Dropped support for older versions of Python (< 3.10.10)
