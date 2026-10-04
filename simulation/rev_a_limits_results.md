# Rev A selected protection / assembly limits

**ASSUMPTION — MUST VERIFY ON PROTOTYPE.** Calculations establish required test criteria, not shutdown, temperature or surge capability.

- Six EEUFR1J471/link: 2820.0uF nominal; 3388.8uF worst including ceramic tolerance.100R1% t95 worst=1.0254s; energy at26V=1.1454J. Startup timeout3s,delta-V<1V.
- Bulk ripple bound IL/2=6Arms at12A:6parallel and1.3sharing factor gives1.3Arms/cap vs1.995Arms rating at100kHz.20% ripple derating target; verify200kHz multiplier and actual ripple/temperature.
- OC divider35.7k/10k,3.288V,gain20,3mR: nominal 11.99125A. Provisional±7% budget; measured actual threshold must fit this interval.
- Required clearing delay<=0.5us, Vfault<=48V, measured L>=14.08uH through15A: peak bound 14.5352A. Simple dI/dt bound excludes shoot-through/local short/saturation; these need fuse/source interruption. This demanding latency is UNPROVEN; failure requires redesign or tighter current envelope.
- Initial cap average limit9.5A;12A remains eventual design goal. No operation is enabled by this offline model.

| Bus / rest cap V | Requested / delivered W | Cap A | IL peak A | Partial board loss W |
|---|---|---|---|---|
| 22/12 |120/87.980 |9.500 |10.472 |5.171 |
| 22/22.05 |120/120.000 |6.379 |6.564 |3.044 |
| 26/12 |120/87.980 |9.500 |10.604 |5.464 |
| 26/22.05 |120/120.000 |6.379 |7.107 |3.227 |

- Four AEV14012 coils: max planning current 1.5532A,12V power 18.638W. Reserve24W output including electronics; DDR-60L-12 input planning29W at83% efficiency. Referee-point total charge budget=40W+29W+2Wboard aux=71W planning ceiling,not a measured total or rule allowance.
- MINI997 typical melting I2t10A93/15A270/5A25 A2s cannot be used as guaranteed maximum clearing energy. No semiconductor protection assertion from these values.
- Dump HS25 100R F(+1%),bank+30%C: time22.05->1V=2256.400s (37.607min); bank energy removed=1752.120J. Permanent bleed ignored here conservatively.40min acceptance target includes contact/path testing; imbalance and rebound separately checked.
- Service condition: bank AND both local links<1V,every cell magnitude<0.5V,2min rebound check,total residual energy<4J,source isolated and independent meter check. This is a delegated prototype procedure target,not demonstrated safe-service capability.
- Thermal criteria: ambient<=40C/open bench;software FET/L65C and bank50C stop,hardware backup≈69.5/53.7C. Verify hotspot-to-junction/winding lag;target FET junction<100C,winding<90C,bank<55C,connectors<60C. No continuous thermal power claimed.
