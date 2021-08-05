# Troubleshooting

## Introduction
This guide aims to provide you with some assistance when emulated PIO programs
don't work the way you expect them to.

## Instructions consume more clock-cycles than expected
One cause of this issue is when a PIO program uses the side-set feature.
The bits that are encoded into an opcode share the same 5-bit field used to
specify the delay cycles. If the state machine, either real or virtual, is not
made aware of how many bits are being used for the side-set then they will be
misinterpreted as delay cycles instead. You can specify the number of bits to
use for the side-set when you initialise the emulator as shown below.

```python
generator = emulate(opcodes, stop_when=stop_condition, side_set_base=0, side_set_count=2)
```
