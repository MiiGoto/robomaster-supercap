"""Original pin tables from manufacturer facts, not copied schematic assets.

Pin electrical types remain explicit for ERC. Package numbers are physical pad
numbers. Footprints are candidates; land dimensions require independent review.
"""
from dataclasses import dataclass

@dataclass
class Part:
    pins: dict
    footprint: str
    source: str = ''

P = {}
def part(name, pins, fp, source=''):
    # 'name:type'; omitted type is passive (R/C/L, contacts, semiconductor terminals).
    P[name] = Part({str(k): tuple(v.split(':')) if ':' in v else (v,'passive')
                    for k,v in pins.items()}, fp, source)

RFP='Resistor_SMD:R_0805_2012Metric'
CFP='Capacitor_SMD:C_0805_2012Metric'
SO8='Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'
VSS8='Package_SO:VSSOP-8_3x3mm_P0.65mm'
DCU8='Package_SO:VSSOP-8_2.3x2mm_P0.5mm'
part('R',{1:'A',2:'B'},RFP)
part('C',{1:'A',2:'B'},CFP)
part('L',{1:'A',2:'B'},'Inductor_SMD:L_Coilcraft_XAL1510-223')
part('D',{1:'K',2:'A'},'Diode_SMD:D_SOD-123')
part('LED',{1:'K',2:'A'},'LED_SMD:LED_0805_2012Metric')
part('Q_NPN',{1:'B',2:'E',3:'C'},'Package_TO_SOT_SMD:SOT-23','https://www.nexperia.com/product/BC847B')
part('Q_PNP',{1:'B',2:'E',3:'C'},'Package_TO_SOT_SMD:SOT-23','https://www.nexperia.com/product/BC857B')
part('FUSE',{1:'A',2:'B'},'','https://www.littelfuse.com/products/fuses-overcurrent-protection/fuses/automotive-passenger-car/blade-fuses/atof.aspx')
# KiCad functional aliases: 1=S physical1/2/3, 2=G physical4,
# 3=D physical5/6/7/8 and drain metal. See pinout review before layout.
part('CSD18540Q5B',{1:'S_DS1_2_3',2:'G_DS4',3:'D_DS5_6_7_8'},
     'Package_SON:VSONP-8-1EP_5x6_P1.27mm','https://www.ti.com/lit/ds/symlink/csd18540q5b.pdf')
part('UCC27282DRCR',{1:'VDD:power_in',2:'NC:no_connect',3:'HB:passive',4:'HO:output',5:'HS:passive',6:'EN:input',7:'HI:input',8:'LI:input',9:'VSS:power_in',10:'LO:output',11:'EP:power_in'},
     'Package_SON:VSON-10-1EP_3x3mm_P0.5mm_EP1.65x2.4mm','https://www.ti.com/lit/ds/symlink/ucc27282.pdf')
for n in ('INA240A1D','INA240A2D'):
    part(n,{1:'INM:input',2:'GND:power_in',3:'REF2:input',4:'NC:no_connect',5:'OUT:output',6:'VS:power_in',7:'REF1:input',8:'INP:input'},SO8,'https://www.ti.com/lit/ds/symlink/ina240.pdf')
part('WSK25123L000FEA',{1:'I_P',2:'K_P',3:'K_M',4:'I_M'},
     'Resistor_SMD:R_Shunt_Vishay_WSK2512_6332Metric_T1.19mm','https://www.vishay.com/docs/30108/wsk2512.pdf')
part('INA293A1DBVR',{1:'OUT:output',2:'GND:power_in',3:'INP:input',4:'INM:input',5:'VS:power_in'},'Package_TO_SOT_SMD:SOT-23-5','https://www.ti.com/lit/ds/symlink/ina293.pdf')
part('INA301A1DGKR',{1:'VS:power_in',2:'OUT:output',3:'LIMIT:input',4:'GND:power_in',5:'RESET:input',6:'ALERT_N:open_collector',7:'INM:input',8:'INP:input'},VSS8,'https://www.ti.com/lit/ds/symlink/ina301.pdf')
part('TLV3202DGKR',{1:'OUT1:output',2:'INM1:input',3:'INP1:input',4:'GND:power_in',5:'INP2:input',6:'INM2:input',7:'OUT2:output',8:'VCC:power_in'},VSS8,'https://www.ti.com/lit/ds/symlink/tlv3202.pdf')
part('SN74LVC1G74DCUR',{1:'CLK:input',2:'D:input',3:'QN:output',4:'GND:power_in',5:'Q:output',6:'CLR_N:input',7:'PRE_N:input',8:'VCC:power_in'},DCU8,'https://www.ti.com/lit/ds/symlink/sn74lvc1g74.pdf')
part('SN74LVC2G08DCUR',{1:'A1:input',2:'B1:input',3:'Y2:output',4:'GND:power_in',5:'A2:input',6:'B2:input',7:'Y1:output',8:'VCC:power_in'},DCU8,'https://www.ti.com/lit/ds/symlink/sn74lvc2g08.pdf')
part('TPS3431SDRBR',{1:'VDD:power_in',2:'CWD:passive',3:'EN:input',4:'GND:power_in',5:'SET1:input',6:'WDI:input',7:'WDO_N:open_collector',8:'ENOUT:open_collector',9:'EP:power_in'},
     'Package_SON:VSON-8-1EP_3x3mm_P0.65mm_EP1.65x2.4mm','https://www.ti.com/lit/ds/symlink/tps3431.pdf')
part('TPS3839K33DBZR',{1:'GND:power_in',2:'RESET_N:output',3:'VDD:power_in'},'Package_TO_SOT_SMD:SOT-23','https://www.ti.com/lit/ds/symlink/tps3839.pdf')
part('LM5164DDAR',{1:'GND:power_in',2:'VIN:power_in',3:'EN:input',4:'RON:passive',5:'FB:input',6:'PGOOD:open_collector',7:'BST:passive',8:'SW:passive',9:'EP:power_in'},
     'Package_SO:TI_SO-PowerPAD-8','https://www.ti.com/lit/ds/symlink/lm5164.pdf')
part('TMUX1511PWR',{1:'SEL1:input',2:'S1:passive',3:'D1:passive',4:'SEL2:input',5:'S2:passive',6:'D2:passive',7:'GND:power_in',8:'D3:passive',9:'S3:passive',10:'SEL3:input',11:'D4:passive',12:'S4:passive',13:'SEL4:input',14:'VDD:power_in'},
     'Package_SO:TSSOP-14_4.4x5mm_P0.65mm','https://www.ti.com/lit/ds/symlink/tmux1511.pdf')
part('TLV431AIDBZR',{1:'REF:input',2:'K:passive',3:'A:passive'},'Package_TO_SOT_SMD:SOT-23','https://www.ti.com/lit/ds/symlink/tlv431.pdf')
part('SN65HVD230DR',{1:'D:input',2:'GND:power_in',3:'VCC:power_in',4:'R:output',5:'VREF:output',6:'CANL:bidirectional',7:'CANH:bidirectional',8:'RS:input'},SO8,'https://www.ti.com/lit/ds/symlink/sn65hvd230.pdf')
part('SN74LV1T34DBVR',{1:'NC:no_connect',2:'A:input',3:'GND:power_in',4:'Y:output',5:'VCC:power_in'},'Package_TO_SOT_SMD:SOT-23-5','https://www.ti.com/lit/ds/symlink/sn74lv1t34.pdf')
bq={1:'NC',2:'VC9',3:'NC',4:'VC8',5:'NC',6:'VC7',7:'NC',8:'VC6',9:'NC',10:'VC5',11:'NC',12:'VC4',13:'VC3',14:'VC2',15:'VC1',16:'VC0',17:'VSS:power_in',18:'SRP:input',19:'NC',20:'SRN:input',21:'TS1:passive',22:'TS2:passive',23:'TS3:passive',24:'REG18:power_out',25:'ALERT:open_collector',26:'SCLK:input',27:'MISO:output',28:'MOSI:input',29:'CS_N:input',30:'DFETOFF:input',31:'DCHG:output',32:'DDSG:output',33:'RST_SHUT:input',34:'REG2:power_out',35:'REG1:power_out',36:'REGIN:power_in',37:'BREG:output',38:'FUSE:passive',39:'PDSG:output',40:'PCHG:output',41:'LD:passive',42:'PACK:input',43:'DSG:output',44:'NC',45:'CHG:output',46:'CP1:passive',47:'BAT:power_in',48:'VC10:input'}
bq={i:('NC:no_connect' if s=='NC' else s+':input' if s.startswith('VC') and ':' not in s else s) for i,s in bq.items()}
part('BQ7694204PFBR',bq,'Package_QFP:TQFP-48_7x7mm_P0.5mm','https://www.ti.com/lit/ds/symlink/bq76942.pdf')
# LQFP64 physical pin map, DS12288 Rev6 Figure15 / Table12.
mcu_names='VBAT PC13 PC14 PC15 PF0 PF1 PG10 PC0 PC1 PC2 PC3 PA0 PA1 PA2 VSS VDD PA3 PA4 PA5 PA6 PA7 PC4 PC5 PB0 PB1 PB2 VSSA VREF+ VDDA PB10 VSS VDD PB11 PB12 PB13 PB14 PB15 PC6 PC7 PC8 PC9 PA8 PA9 PA10 PA11 PA12 VSS VDD PA13 PA14 PA15 PC10 PC11 PC12 PD2 PB3 PB4 PB5 PB6 PB7 PB8 PB9 VSS VDD'.split()
mcu=dict(enumerate(mcu_names,1))
part('STM32G474RET6',{i:s+(':power_in' if s in ('VBAT','VSS','VDD','VSSA','VDDA','VREF+') else ':bidirectional') for i,s in mcu.items()},
     'Package_QFP:LQFP-64_10x10mm_P0.5mm','https://www.st.com/resource/en/datasheet/stm32g474re.pdf')
for n in (2,3,4,5,6,10):
    part('J'+str(n),{i:'P'+str(i) for i in range(1,n+1)},f'Connector_PinHeader_2.54mm:PinHeader_1x{n:02}_P2.54mm_Vertical')
part('CONTACT',{1:'COM',2:'NO',3:'COIL_P',4:'COIL_M'},'','https://industry.panasonic.com/global/en/products/control/relay/vehicle/number/aev14012')
part('PWR_FLAG',{1:'SUPPLY:power_out'},'')
