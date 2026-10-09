# M1-A2.2 measured codec freeze

11 October 2026. This record documents the production port of the accepted S11 movement
and durable shapes. It is not new transport or presentation evidence.

## Frozen layout and island range

The production codec retains S11's measured sizes: a 12-byte movement header, 16-byte
complete movement rows, no more than 74 rows and 1,196 bytes per full chunk, plus the
exact 16-byte durable lifecycle record. At 148 rows the codec still produces two
1,196-byte chunks, preserving the cardinality and bandwidth basis measured by S11.
No Variant dictionary, health, equipment, seat or historical effect data was added to
the movement row.

The final-district range review found that S11's original signed centimetre X/Z fields
covered only -327.68 through 327.67 m, while saved Brackett node origins span about
X -555.16..554.13 and Z -291.14..690.0 m. Owner decision 51 keeps the row size and changes
planar position quantization to two-centimetre units around the fixed island-centred
origin `(-0.51565, 199.42865)`. This covers approximately ±655 m around that origin and
leaves more than the required 50 m margin around the current saved node origins.

A GUT regression instantiates the saved Brackett city and checks every `Node3D` global
origin against that safe range. Runtime values beyond the numeric domain saturate and
increment `position_clamp_count`; they never wrap. Host state stays full precision and
wire error is at most 1 cm. The row has no Y field. It therefore makes no claim about
footbridge, road-bridge or falling height and does not silently repurpose another field;
a vertical wire field needs a separately measured codec revision.

The port was written against the production owner contract after inspecting S11; production
code does not load or copy the archived fixture.
