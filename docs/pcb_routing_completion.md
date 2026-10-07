# Prototype Rev A routing closure — 2026-10-07

**Current: CAD routing complete.** Official board: `hardware/kicad/robomaster_supercap.kicad_pcb`.

| Check | Actual result |
|---|---|
| Native KiCad missing connections |0|
| Disconnected physical pad nets |0 of331 checked nets;1524 net-assigned pad records|
| Full PCB DRC (`--all-track-errors`) |0 errors /0 warnings /0 missing-connection entries|
| Schematic parity (`--schematic-parity`) |0|
| ERC |0 errors /0 warnings|
| Manifest pad/net matches |1478;481 electrical footprints plus4 mounting holes|
| Main power-path checks |7/7 pass;all pads on these nets also physically connected|
| Track segments / vias |12517 /1573|
| Native copper zones / switch-node keepouts |2 /5|
| Board SHA256 |`6d41f3989cd8532cd3654838e54a4c322754d51bcde6984e57a392c39c8e30cf`|

[Machine completion checks](../simulation/routing_completion_checks.json), [board audit](../simulation/pcb_rev_a_results.json), [power paths](../simulation/power_path_checks.json), and [remaining routes](../simulation/remaining_routes.json) describe this saved PCB. The remaining-net list is empty. Native completion guard also rejected the old incomplete board even when supplied the clean final DRC report; it does not infer connectivity from an empty report or an autorouter score.

## Final layout decisions

The610-edge checkpoint was retained in Git and ignored local candidates. Candidate work completed GND and all signal nets; no schematic components, net assignments or protections were removed. Original main power trunks and Kelvin lands were retained. A thin SW_NODE_B branch to a removed old via location was deleted only after all native connections remained complete. PWM_BH_SAFE was trimmed to the retained diagonal endpoint, preserving the hardware-gated signal.

Controller support passives were spaced locally for escape routing; MOSFET gate diode/resistor options were moved next to their respective gate paths. The MCU and all other major selected parts remain the same. V3V3/V12_DRIVER/ACTUATOR_12V routes were widened where native geometry allowed to0.30–0.70 mm;fine-pitch necks remain0.20 mm. This is geometry improvement, not an ampacity certification. Coil/common supply necks, via sharing and actual copper thickness require thermal/current review before fabrication or energizing.

### Controlled In1 reference-plane escapes

Three signal layers alone enclosed the remaining MCU ports. In1 therefore includes **48 local0.20 mm segments**, confined to x160–215 mm/y7–65 mm and only these seven nets: V3V3,CAP_I_ADC,PRE_CAP_REQUEST,TEMP_BANK_ADC,TEMP_FET_ADC,TEMP_L_ADC,WD_HEARTBEAT. All other global signals use F/In2/B. No PWM,gate,SW power or CAN route uses this exception. This replaces the earlier provisional aim of removing every In1 signal stub;it is a deliberate documented layout choice rather than a DRC exemption.

After zone filling, the In1 GND reference remains **one filled outline**;all GND pads are physically connected. The completion guard checks this polygon count,net whitelist,bounding region and trace width. Local slots can still lengthen return paths and couple switching noise;polygon continuity does not establish return impedance,ADC accuracy,EMI or transient fault behavior. These remain prototype validation items. F.Cu has local ground islands connected through the ground network;the solid In1 reference is not replaced by an assumed surface pour.

## Verification and scope

Final native CLI commands used the official project and preserved its existing check configuration:

```text
kicad-cli pcb drc --format json --all-track-errors --schematic-parity --exit-code-violations -o .local/pcb_drc_final.json hardware/kicad/robomaster_supercap.kicad_pcb
kicad-cli sch erc --format json --exit-code-violations -o .local/erc_routing_final.json hardware/kicad/robomaster_supercap.kicad_sch
```

No report cap hides remaining routes:both native ratsnest and the independent all-pad partition check are0. No additional exclusions,clearance relaxation,No ERC or unlicensed external layout assets were added. Third-party routing binaries/sources and runtime remain ignored local tooling;checked-in Java/Python routing helpers are project-authored code. Candidate output is kept separate from the live project until validation.

The unrelated KiCad project settings retain their starting SHA256 `A7E410DE47D3C18D771342145B9E7D42F80B75C98278AB78525EA8D7CDFF7031` and remain uncommitted. Main is not merged. The earlier2–3-attempt stopping policy was superseded by the user's instruction to complete routing without an iteration limit;failed candidates were retained separately and never accepted as completion.

**Unmeasured / not released:**surge and ringing,OC end-to-end latency,shoot-through behavior,fuse/contactor coordination,thermal limits,discharge time and rebound,isolation under faults,EMI,and robot mechanical/competition acceptance. This task completes CAD routing only;no physical hardware tests,firmware implementation,manufacturing order or energizing were performed.

## Historical partial-routing records (preserved)

# Rev A routing completion work

2026-10-04. **Stopped at a validated partial-routing checkpoint; routing is NOT complete.** The requested endpoint is native KiCad unconnected count0, full DRC errors0/warnings0 and schematic parity0. These CAD checks do not establish surge, fault interruption, thermal capability, fabrication approval or permission to energize.

## Preserved baseline

Start commit113869c:935 native unconnected edges,499 CLI missing-connection entries,0 dimension/clearance errors/warnings. The unrelated expanded local `.kicad_pro` configuration remains uncommitted. The0.15mm same-package fine-pitch approval and0.20mm general clearance remain unchanged. The pre-routing PCB is retained under ignored `.local/routing_completion/before_completion.kicad_pcb`.

## Explicit power routing candidate

`route_rev_a_power.py` writes an ignored review candidate, not the live board. It replaces previous generated power routes and nine affected generated signal-net routes for later rerouting. No schematic nets or protective components change. J24/J33 move to15,52mm and117,12mm to avoid long high-current runs across auxiliary/control regions.

- Main power trunks3mm, bulk terminal branches2.4mm, ceramic branches1mm. Source fingers use three independent0.5mm local escapes and0.7mm short bottom fanout into3mm trunks.
- Both switch-node paths and inductor conduction paths use bottom copper, with nine0.6/0.3mm vias at each MOSFET drain, three source-finger fanout vias, six at each shunt power land and twelve at each inductor terminal. Link connection uses front-side drain trunks and nine-via transitions to bottom bulk spines.
- Shunt pins2/3 stay dedicated Kelvin nets; pins1/4 carry power. No copper short is added across the four-terminal resistor.
- Power trunk geometry is locked for signal autorouting. Sensor, gate and bootstrap branches sharing these net names remain signal-width connections, rather than forcing their entire nets to3mm.

The explicit power candidate passed native KiCad DRC with0 dimensional/clearance violations. Remaining signal connections are still present. Proposed widths and via sharing remain prototype engineering choices; actual laminate, plating, thermal rise and commutation-loop performance are unverified.

## Routing interchange and validation

The native ground zones remain. The local F.Cu GND polygon is omitted only from the DSN interchange, because a solid exported polygon can obstruct local non-ground connections; KiCad refills the actual zone around imported routes. The In1.Cu reference plane remains in the interchange. Fixed power wiring is exported as `type fix`.

Offline Freerouting2.4.1 uses the ignored local Java25 runtime with analytics, telemetry, API and MCP disabled. Candidate import uses `import_rev_a_completion.py`; it retains locked original power/GND copper, replaces only unlocked routes in an in-memory candidate, imports SES and saves an ignored review board. Native DRC, all-pad schematic comparison and layer inspection are required before accepting this candidate into the live PCB.

## Current results

Saved live-board result: **610 native missing edges**,239 disconnected nets,499 CLI missing-connection report entries (the CLI report is capped). DRC dimensional/clearance errors0/warnings0;schematic parity0;1478 pad/net assignments match the schematic. Seven physical power-trunk checks pass, and all pads on the seven power nets—including local driver/bootstrap returns and voltage-tap input resistors—are physically connected. Independent negative tests reject a broken inductor path and reject ignoring a disconnected ground network.

The current board contains 1304 track segments and 632 vias. All schematic protective components and original net assignments remain.107 unlocked autorouter power trace segments were removed after confirming every power pad stayed connected;the fixed explicit trunks/returns alone provide those connections. R85/R88 move to61,20mm and111,20mm so long sense runs occur after the first33k resistor. Ground fanout adds278 short0.20mm F.Cu escapes and0.6/0.3mm vias; all saved fanout passes native copper and drill-spacing DRC.

[remaining_routes.json](../simulation/remaining_routes.json) lists every disconnected net, its separate physical pad groups and pad coordinates, ranked with protection/sensing first. Its610 pad links equal the independently calculated native ratsnest count. Current GND still has11 missing links;remaining Kelvin,gate-drive,hardware-permit/latch,CAN and controller connections require completion. The saved board retains provisional In1 signal segments,so reference-plane continuity/return-path review is unresolved.

## Attempts and candidate disposition

Two initial continuations were interrupted after observing inadequate progress/exported-pour obstruction. The adjusted12-minute routing attempt endedTIMED_OUT; its partial session was imported retaining fixed trunks. Native inspection found7 dangling-item warnings across6 nets;those nets were restored from the previously DRC-clean power candidate, yielding897 edges and0/0 DRC. Ground fanout and local switch returns subsequently reduced the saved count to610.

A separate reference-plane candidate removed239 generated In1 signal segments, completed all GND/power pad groups and excluded those verified-connected classes from signal routing. The final8-minute attempt also endedTIMED_OUT: after importing its session,658 missing edges remained. This result is **not adopted into the live PCB**: it is not a completed design and still needs dangling-item/return-path repair. The last full check before that import found131 dangling-via warnings caused by deferred In1 signal routes;its final post-import DRC was not run. All experimental DSN/SES/boards/logs stay ignored under `.local/routing_completion`.

No repeated router run is scheduled. In accordance with the user's2–3-repeat limit,the task stops without claiming the requested complete routing. Next work is explicit manual routing of the ranked protection/measurement/control connections,reference-plane repair and final unconnected0/DRC0/parity0 verification. No fabrication files or energizing release are produced.
