# Approved fine-pitch clearance — 2026-10-04

ユーザーが同一fine-pitch部品内のパッド間0.15 mm、その他0.20 mm以上を明示承認した。39個の対象ICに同一referenceのPad/Pad例外を設定し、一般銅箔間隔0.20 mmを明示維持した。projectのhard floor0.15 mmは例外を許容するためで、一般ruleを0.15 mmへ緩めてはいない。

独立DRCテスト6件PASS：対象内0.15 mmは許容、0.14 mmは検出、非対象/別部品/pad-to-trackの0.19 mmは検出、非対象0.20 mmは許容。現行PCBの寸法・間隔DRC0 errors/0 warnings、schematic parity0。未配線はCLI報告499件／全ratsnest935本のままで、配線完成や製造承認を意味しない。

以前の自動承認拒否と218件の違反記録は以下に履歴として保持する。

## Historical records before this approval

# Prototype Rev A fabrication status

**NOT RELEASED FOR FABRICATION.** Placement/routing work was authorized2026-10-04 without earlier hardware measurements. The actual PCB and [validation](pcb_rev_a_validation.md) remain engineering drafts.

- Proposed bench outline315×235 mm,nominal1.6 mm thickness,four copper layers. Copper70 um outer/35 um inner is a budget assumption;actual substrate/prepreg/copper weights are not a purchase specification.
- Verify fine-pitch package copper spacing,mask registration and stencil/paste/EP voids with the selected fabricator. Existing hard minimum0.20 mm conflicts with some0.15 mm library pads and has not been reduced.
- Drill targets include M3 clearance3.2 mm,wire lands2.0/0.9 mm,through vias0.6/0.3 mm. THT capacitance pitch5 mm and polarity,shunt4-terminal lands,driver EP and MCU/BQ pitch must be checked on final assembly drawings.
- Mount external contactors,fuses,DDR supply,bank/source tap resistors and HS25 chassis dump resistors separately with covers and strain relief. Solder wire lands are not blind-mate connectors.
- Review all power necks/return loops/via arrays,gate return/bootstraps,Kelvin routing,ADC noise coupling,hardware-kill fanout,test access,creepage/clearance and switched-node copper areas before a manufacturing release.
- Gerber,drill,assembly order,hardware energizing and finished robot enclosure are not generated or authorized by this CAD work.
