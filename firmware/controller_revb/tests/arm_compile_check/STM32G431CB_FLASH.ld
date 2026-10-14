/* Compile-check only (project-authored): STM32G431CB 128 KiB flash, 32 KiB SRAM (SRAM1+SRAM2 contiguous).
 * STM32CubeIDE generates its own STM32G431CBTX_FLASH.ld. */
ENTRY(Reset_Handler)
MEMORY { FLASH (rx) : ORIGIN = 0x08000000, LENGTH = 128K
         RAM (rwx) : ORIGIN = 0x20000000, LENGTH = 32K }
_estack = ORIGIN(RAM) + LENGTH(RAM);
SECTIONS {
 .isr_vector : { KEEP(*(.isr_vector)) } > FLASH
 .text : { *(.text*) *(.rodata*) KEEP(*(.init)) KEEP(*(.fini)) . = ALIGN(4); _etext = .; } > FLASH
 .ARM.extab : { *(.ARM.extab*) } > FLASH
 .ARM.exidx : { __exidx_start = .; *(.ARM.exidx*) __exidx_end = .; } > FLASH
 .preinit_array : { PROVIDE_HIDDEN(__preinit_array_start = .); KEEP(*(.preinit_array*)) PROVIDE_HIDDEN(__preinit_array_end = .); } > FLASH
 .init_array : { PROVIDE_HIDDEN(__init_array_start = .); KEEP(*(SORT(.init_array.*))) KEEP(*(.init_array*)) PROVIDE_HIDDEN(__init_array_end = .); } > FLASH
 .fini_array : { PROVIDE_HIDDEN(__fini_array_start = .); KEEP(*(SORT(.fini_array.*))) KEEP(*(.fini_array*)) PROVIDE_HIDDEN(__fini_array_end = .); } > FLASH
 _sidata = LOADADDR(.data);
 .data : { . = ALIGN(4); _sdata = .; *(.data*) . = ALIGN(4); _edata = .; } > RAM AT> FLASH
 .bss (NOLOAD) : { . = ALIGN(8); _sbss = .; __bss_start__ = _sbss; *(.bss*) *(COMMON) . = ALIGN(8); _ebss = .; __bss_end__ = _ebss; } > RAM
 . = ALIGN(8);
 PROVIDE(end = .);
 ASSERT(_ebss + 0x400 + 0x200 <= _estack, "SRAM overflow (stack 1 KiB + heap 0.5 KiB as in the .ioc)")
}
