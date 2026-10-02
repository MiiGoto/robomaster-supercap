# Project instructions

## Before editing

1. Read PROJECT_CONTEXT.md.
2. Read requirements.md.
3. Read docs/safety.md.
4. Read docs/fmea.md.
5. Check git status.
6. Never discard user changes or delete existing user files.

## Hardware

1. Use manufacturer datasheets; record source and revision.
2. Verify voltage/current ratings including transients and derating.
3. Verify pin numbers and package mapping.
4. Verify thermal margins.
5. Run ERC after schematic changes; document skeleton limitations.
6. Run DRC after PCB changes; no routed board exists in Task 1.

## High-power safety

1. Never infer voltage/current rating without a source.
2. Do not bypass protection to silence ERC.
3. Do not remove fail-safe circuits without explicit justification.
4. Record unresolved risks and classify evidence as Confirmed / Assumption / TBD.
5. Enable must default OFF during float, reset, crash and missing auxiliary power.
6. PWM OFF is not electrical isolation; examine body-diode and short-failure paths.
7. Preserve the human review gate in PROJECT_CONTEXT.md. No detailed power stage in Task 1.

## Git / publication

- Make small meaningful commits; inspect status, diff and staged diff before each commit.
- No force push, reset --hard, clean -fd, history rewrite or discarded changes.
- Check secrets, private information and third-party licensing before commit and push.
- Record references with URL, author, license, accessed date, use and differences.
- Do not copy external schematics, PCB, PDFs or images without verified rights.
- Public availability does not imply an open license. Project license remains TBD by owner.
