# Changelog

## Unreleased

### Added
- Additional documentation - a Tour of pioemu.

### Changed
- Update dependencies used by the Jupyter Notebook example. Thanks Renovate Bot.

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
