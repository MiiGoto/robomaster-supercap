"""Generate the existing project's Rev A electrical sheets (never project/PCB).

Own package-box symbols and label-connected wires. Deterministic UUIDs preserve
reviewable diffs. Global labels connect sheets; no No-ERC objects are generated.
Datasheet facts and candidate land names are in rev_a_parts.py. This is a
schematic draft with explicit external fault-containment boundaries, not a PCB.
"""
from pathlib import Path
from collections import defaultdict
import uuid, json, re
from rev_a_parts import P, part, RFP, CFP, mcu
from rev_a_passives import mpn
ROOT=Path(__file__).resolve().parents[1]
K=ROOT/'hardware/kicad'
NAME='robomaster_supercap'
NS=uuid.UUID('b2b13ce0-d767-49a4-82e9-164ea247930b')
def uid(key): return str(uuid.uuid5(NS,key))
def q(s): return json.dumps(str(s),ensure_ascii=False)
def effects(size=1): return f'(effects (font (size {size} {size})))'
pages=defaultdict(list); notes=defaultdict(list); seq=defaultdict(int)
def add(sheet,typ,nets,value=None,fp=None,ref=None,dni=False):
    prefix=('R' if typ in ('R','WSK25123L000FEA') else 'C' if typ=='C' else 'L' if typ=='L' else 'Q' if typ.startswith('Q_') or typ=='CSD18540Q5B' else 'D' if typ in ('D','LED') else 'J' if typ.startswith('J') else 'F' if typ=='FUSE' else 'K' if typ=='CONTACT' else '#FLG' if typ=='PWR_FLAG' else 'U')
    if ref is None: seq[prefix]+=1; ref=prefix+str(seq[prefix])
    spec=P[typ]
    nets={str(k):v for k,v in nets.items()} if isinstance(nets,dict) else dict(zip(spec.pins,nets))
    assert set(nets)==set(spec.pins),(ref,typ,set(spec.pins)-set(nets))
    chosen_fp=spec.footprint if fp is None else fp
    pages[sheet].append(dict(ref=ref,typ=typ,nets=nets,value=value or typ,fp=chosen_fp,dni=dni,mpn=mpn(typ,value or typ,chosen_fp)))
    return ref
def r(s,a,b,v,fp=None,dni=False):return add(s,'R',[a,b],v,fp,dni=dni)
def c(s,a,b,v,fp=None,dni=False):return add(s,'C',[a,b],v,fp,dni=dni)
def dec(s,rail='V3V3'):c(s,rail,'GND','100nF / 16V X7R')
def pull(s,net,rail='GND',v='10k'):r(s,net,rail,v)
def gate(s,a,b,out,a2,b2,out2):
    add(s,'SN74LVC2G08DCUR',{1:a,2:b,3:out2,4:'GND',5:a2,6:b2,7:out,8:'V3V3'});dec(s)
def npn(s,cmd,collector):
    base=collector+'_BASE';r(s,cmd,base,'4.7k');pull(s,base,v='100k');add(s,'Q_NPN',[base,'GND',collector],'BC847B')
def relay(s,a,b,cmd,tag):
    if tag.startswith('PRE_'):
        # External AC/DC PhotoMOS, manufacturer physical pins. No body-diode
        # shortcut around the resistor when input LED is off.
        led=tag+'_LED_P';sink=tag+'_LED_M';base=tag+'_SSR_BASE'
        add(s,'AQZ202G',{1:sink,2:led,3:a,4:b},'AQZ202G / external precharge SSR',fp='')
        r(s,'V3V3',led,'150R');r(s,cmd,base,'1.5k');pull(s,base)
        add(s,'Q_NPN',[base,'GND',sink],'BC847B')
        pull(s,tag+'_FB')
        notes[s].append(tag+' SSR has no auxiliary contact: infer conduction using raw/link ADC; FB pin reserved LOW, not confirmation.')
        return
    # Contacts and coil represent an EXTERNAL DC-rated assembly, not an onboard
    # low-current signal relay. Candidate/polarity/coil budget in review document.
    coil=tag+'_COIL_M';add(s,'CONTACT',[a,b,'ACTUATOR_12V',coil],tag+' external NO contact / AEV14012 bench selection',fp='')
    # Separate external actuator supply (bus-derived), not a 1A gate-bias rail.
    g=tag+'_COIL_GATE';pn=tag+'_PNP_B';nc=tag+'_NPN_C'
    add(s,'CSD18540Q5B',{1:'GND',2:g,3:coil});pull(s,g,v='10k')
    add(s,'Q_PNP',[pn,'ACTUATOR_12V',tag+'_PNP_C'],'BC857B');pull(s,pn,'ACTUATOR_12V');r(s,pn,nc,'10k')
    npn(s,cmd,nc);r(s,tag+'_PNP_C',g,'47R')
    add(s,'D',['ACTUATOR_12V',coil],'SMBJ18CA bidirectional coil suppression / release MUST VERIFY',fp='Diode_SMD:D_SMB')
    add(s,'J4',['ACTUATOR_12V',coil,tag+'_FB','GND'],tag+' actuator+reserved diagnostic / no intrinsic auxiliary contact',fp='')
    pull(s,tag+'_FB')

# INPUT and inrush boundaries. External contacts are not claimed as coordinated
# fault interrupt devices. No hot-plug/energizing allowed before assembly review.
s='POWER_INPUT'
add(s,'J2',['BUS_ROBOT_INPUT','GND'],'ROBOT BUS / external covered bolted power terminals',fp='')
add(s,'DISCONNECT',['BUS_ROBOT_INPUT','BUS_RAW'],'Blue Sea6006 / external manual source disconnect;not a fault breaker',fp='')
add(s,'FUSE',['BUS_RAW','BUS_FUSED'],'0997010.WXN / MINI997 58V10A / external 0FHM0002ZXJM holder')
add(s,'D',['BUS_FUSED','GND'],'SMBJ28A / no surge-energy guarantee',fp='Diode_SMD:D_SMB')
relay(s,'BUS_FUSED','BUS_ISOLATED','BUS_ISO_DRIVE','BUS_ISO')
add(s,'J3',['BUS_RAW','GND','REFEREE_PERMIT'],'referee permit interface / no bypass',fp='')
pull(s,'REFEREE_PERMIT')
add(s,'FUSE',['BUS_RAW','ACTUATOR_INPUT'],'0997005.WXN / MINI997 58V5A / external 0FHM0002ZXJM holder')
add(s,'DDR60L12',{1:'GND',2:'GND',3:'ACTUATOR_12V',4:'ACTUATOR_12V',5:'ACTUATOR_INPUT',6:'GND'},'DDR-60L-12 / external bench actuator supply',fp='')
add(s,'PWR_FLAG',['ACTUATOR_12V'],'external reviewed actuator supply required')
notes[s]+=['Aux input is BUS_FUSED upstream of NO isolate. No bank-fed control rail.',
           'Four AEV14012 main/bypass contacts, 12V coils; external DDR-60L-12. Bench only: total contact mass about1.6kg.',
           'Fuse+TVS values provisional. TVS cathode positive; reverse insertion is not authorized.']
s='PRECHARGE'
relay(s,'BUS_ISOLATED','BUS_PRE_R_IN','PRE_BUS_DRIVE','PRE_BUS')
r(s,'BUS_PRE_R_IN','BUS_LINK_IN','100R / HS25 100R F / external chassis mount',fp='')
relay(s,'BUS_ISOLATED','BUS_LINK_IN','BYP_BUS_DRIVE','BYP_BUS')
relay(s,'CAP_ISOLATED','CAP_PRE_R_IN','PRE_CAP_DRIVE','PRE_CAP')
r(s,'CAP_PRE_R_IN','CAP_LINK_IN','100R / HS25 100R F / external chassis mount',fp='')
relay(s,'CAP_ISOLATED','CAP_LINK_IN','BYP_CAP_DRIVE','BYP_CAP')
notes[s]+=['Separate NO isolate plus NO resistor-path and NO bypass contacts; no permanent path around isolation.',
           'Six470uF per link; 26V/100R t95 nominal0.845s, worst target<1.1s. Timeout3s and delta-V<1V.',
           'SSR path acceptance uses link voltage progression and open-path diagnosis; no resistor-only bank charge.']
s='POWER_STAGE'
for name,a,b in [('BUS','BUS_LINK_IN','BUS_LINK'),('CAP','CAP_LINK_IN','CAP_LINK'),('IL','SW_NODE_A','IL_TO_L')]:
    add(s,'WSK25123L000FEA',{1:a,2:name+'_KELVIN_P',3:name+'_KELVIN_M',4:b},'WSK25123L000FEA / 3mR 1% 1W')
for rail in ['BUS_LINK','CAP_LINK']:
    for _ in range(6):c(s,rail,'GND','470uF /63V EEUFR1J471 / ripple1.995Arms at100kHz',fp='Capacitor_THT:CP_Radial_D12.5mm_P5.00mm')
    for _ in range(2):c(s,rail,'GND','2.2uF / 100V X7R / effective C MUST VERIFY',fp='Capacitor_SMD:C_1210_3225Metric')
for n,drain,source in [('AH','BUS_LINK','SW_NODE_A'),('AL','SW_NODE_A','GND'),('BH','CAP_LINK','SW_NODE_B'),('BL','SW_NODE_B','GND')]:
    add(s,'CSD18540Q5B',{1:source,2:'GATE_'+n,3:drain})
    r(s,'GATE_'+n,source,'10k GS mandatory')
    # Two-terminal gate clamp functional K/A; positive VGS clamp, reverse diode.
    add(s,'D',['GATE_'+n,source],'BZT52H-C15 / gate clamp candidate',fp='Diode_SMD:D_SOD-123F')
add(s,'L',['IL_TO_L','SW_NODE_B'],'XAL1510-223MED / 22uH +/-20%',fp='Inductor_SMD:L_Coilcraft_XAL1510-223')
for sw in ['SW_NODE_A','SW_NODE_B']:
    r(s,sw,sw+'_SNUB','10R DNI tunable',dni=True)
    c(s,sw+'_SNUB','GND','1nF /100V DNI tunable',dni=True)
notes[s]+=['Body diode S -> D: healthy all-OFF positive rails block static DC; inductor decay or a short high-side FET can feed the other rail.',
           'Shunts: power pads1/4, Kelvin pads2/3. WSK3mR terminal T=2.21mm (not the>=5mR T1.19 land).',
           'Primary fs=200kHz; initial average current cap9.5A maximum,8A normal;12A remains later design goal.']
s='GATE_DRIVER'
for leg in ['A','B']:
    sw='SW_NODE_'+leg;hb='HB_'+leg
    add(s,'UCC27282DRCR',{1:'V12_DRIVER',2:None,3:hb,4:'HO_'+leg,5:sw,6:'GATE_PERMIT',7:'PWM_'+leg+'H_SAFE',8:'PWM_'+leg+'L_SAFE',9:'GND',10:'LO_'+leg,11:'GND'})
    c(s,hb,sw,'470nF /50V X7R bootstrap / effectiveC>=200nF target')
    c(s,'V12_DRIVER','GND','1uF /25V X7R');dec(s,'V12_DRIVER')
    for level,out in [('H','HO_'+leg),('L','LO_'+leg)]:
        dest='GATE_'+leg+level;r(s,out,dest,'4.7R gate / tunable',fp='Resistor_SMD:R_0603_1608Metric')
        r(s,out,out+'_FAST','2.2R DNI turnoff option',dni=True)
        add(s,'D',[out+'_FAST',dest],'1N4148W DNI turnoff bypass',dni=True)
    pull(s,'PWM_'+leg+'H_SAFE');pull(s,'PWM_'+leg+'L_SAFE')
pull(s,'GATE_PERMIT');c(s,'GATE_PERMIT','GND','1nF EN filter')
gate(s,'PWM_AH','GATE_PERMIT','PWM_AH_SAFE','PWM_AL','GATE_PERMIT','PWM_AL_SAFE')
gate(s,'PWM_BH','GATE_PERMIT','PWM_BH_SAFE','PWM_BL','GATE_PERMIT','PWM_BL_SAFE')
notes[s]+=['DRC package only: EN pin6, exposed pad11 to VSS. Internal bootstrap diode used.',
           '470nF is provisional: Qg53nC / Ceff200nF=0.265V plus bias/leak loss; both legs refresh each cycle.',
           'No 100% high-side duty. Minimum off/refresh time and deadtime require gate-waveform validation.',
           'Independent AND inhibit stops HI/LI; EN secondary (typ1.5us is not a maximum guarantee).']

s='AUXILIARY_POWER'
for tag,out,rt,ron,lv in [('DRV','V12_DRIVER','909k','100k','68uH / MSS1246T-683MLB'),('MCU','V3V3','174k','27.4k','47uH / MSS1246T-473MLB')]:
    sw='AUX_SW_'+tag;fb='AUX_FB_'+tag;en='AUX_EN_'+tag;rp='AUX_RIPPLE_'+tag;pg='PG_'+tag
    add(s,'LM5164DDAR',{1:'GND',2:'BUS_FUSED',3:en,4:'RON_'+tag,5:fb,6:pg,7:'BST_'+tag,8:sw,9:'GND'})
    add(s,'L',[sw,out],lv,fp='Inductor_SMD:L_Coilcraft_MSS1246T-XXX')
    c(s,'BST_'+tag,sw,'2.2nF /50V X7R mandatory')
    c(s,'BUS_FUSED','GND','2.2uF /100V X7R',fp='Capacitor_SMD:C_1210_3225Metric')
    c(s,out,'GND','22uF /25V X7R',fp='Capacitor_SMD:C_1210_3225Metric');c(s,out,'GND','22uF /25V X7R',fp='Capacitor_SMD:C_1210_3225Metric')
    r(s,out,fb,rt);r(s,fb,'GND','100k');r(s,'RON_'+tag,'GND',ron)
    r(s,'BUS_FUSED',en,'1M');r(s,en,'GND','82.5k')
    pull(s,pg,'V3V3')
    # Type-3 injection: RA SW->ramp, CA ramp->VOUT, CB ramp->FB.
    r(s,sw,rp,'1M' if tag=='DRV' else '475k');c(s,rp,out,'1nF C0G');c(s,rp,fb,'100pF C0G')
    add(s,'PWR_FLAG',[out],out+' regulator output')
for net in ['GND','BUS_RAW','BUS_FUSED','BANK_P_RAW','MON_REGIN','VDDA','VREF_ADC']:
    add(s,'PWR_FLAG',[net],net+' declared source (not protection)')
notes[s]+=['12V rail 1A IC capacity is not the available actuator/thermal budget. External contact coils require separate reviewed actuator supply.',
           '3.3V and driver12V independently bus-fed, no bank-fed MCU rail. UVLO approx19.68V-on/18.37V-off.',
           'COT Type3 ripple RA/CA/CB options: stability/startup/backfeed and actual auxiliary load must be verified.',
           'Feedback:1.2*(1+909k/100k)=12.108V;1.2*(1+174k/100k)=3.288V. PGOOD qualified by safety.']

# MCU net mapping by port, exact physical pins generated into docs/pinout.md.
MCU_NETS={'PG10':'NRST','PA8':'PWM_AH','PA9':'PWM_AL','PA10':'PWM_BH','PA11':'PWM_BL','PA12':'HW_FAULT_N',
 'PB8':'CAN_RX','PB9':'CAN_TX','PB13':'MON_SCLK_HOST','PB14':'MON_MISO_HOST','PB15':'MON_MOSI_HOST','PB12':'MON_CS_HOST',
 'PA13':'SWDIO','PA14':'SWCLK','PB3':'SWO','PA2':'UART_TX','PA3':'UART_RX',
 'PA0':'BUS_V_ADC','PA1':'CAP_V_ADC','PA4':'BUS_I_ADC','PA5':'CAP_I_ADC','PA6':'IL_I_ADC',
 'PC0':'TEMP_FET_ADC','PC1':'TEMP_L_ADC','PC2':'TEMP_BANK_ADC','PC3':'BUS_RAW_ADC','PC4':'CAP_RAW_ADC',
 'PB0':'ARM_PULSE','PB1':'WD_HEARTBEAT','PB2':'MCU_GATE_REQUEST','PB10':'PRE_BUS_REQUEST','PB11':'BYP_BUS_REQUEST',
 'PC6':'BUS_ISO_REQUEST','PC7':'CAP_ISO_REQUEST','PC8':'PRE_CAP_REQUEST','PC9':'BYP_CAP_REQUEST',
 'PC10':'DUMP_REQUEST','PC11':'MON_ALERT_HOST','PC12':'CAN_STANDBY','PD2':'MON_CONFIG_VALID',
 'PB4':'BUS_ISO_FB','PB5':'CAP_ISO_FB','PB6':'BYP_BUS_FB','PB7':'BYP_CAP_FB','PA15':'PRE_BUS_FB','PC13':'PRE_CAP_FB',
 'PC5':'REFEREE_PERMIT'}
s='CONTROLLER';nets={}
for i,n in mcu.items():
    nets[i]=('V3V3' if n in ['VDD','VBAT'] else 'GND' if n in ['VSS','VSSA'] else 'VDDA' if n=='VDDA' else 'VREF_ADC' if n=='VREF+' else MCU_NETS.get(n))
add(s,'STM32G474RET6',nets)
for _ in range(4):dec(s)
c(s,'V3V3','GND','4.7uF /16V X7R');r(s,'V3V3','VDDA','10R');c(s,'VDDA','GND','1uF /16V');dec(s,'VDDA')
r(s,'VDDA','VREF_ADC','0R');c(s,'VREF_ADC','GND','1uF /16V');dec(s,'VREF_ADC')
pull(s,'NRST','V3V3');c(s,'NRST','GND','100nF');pull(s,'CAN_RX','V3V3')
for n in ['PWM_AH','PWM_AL','PWM_BH','PWM_BL','ARM_PULSE','MCU_GATE_REQUEST','WD_HEARTBEAT','MON_CONFIG_VALID']:
    pull(s,n)
pull(s,'MON_CS_HOST','V3V3')
add(s,'J6',['V3V3','SWDIO','SWCLK','SWO','NRST','GND'],'SWD reference voltage ONLY / do not externally power')
add(s,'J3',['UART_TX','UART_RX','GND'],'3.3V UART / no power pin')
notes[s]+=['PG10 pin7 configured NRST; PB8 pin61 BOOT0 strap/options: boot configuration must be locked to flash before use.',
           'HSI clock for draft, no external crystal. FDCAN bit timing/HSI accuracy must be checked before robot integration.',
           'ADC HRTIM-synchronized sampling; internal comparators are secondary diagnostics, not primary OC shutdown.']

s='CURRENT_SENSING'
for tag,p,m,gain in [('BUS','BUS_LINK_IN','BUS_LINK','INA240A2D'),('CAP','CAP_LINK_IN','CAP_LINK','INA240A1D'),('IL','SW_NODE_A','IL_TO_L','INA240A1D')]:
    p,m=tag+'_KELVIN_P',tag+'_KELVIN_M'
    add(s,gain,{1:m,2:'GND',3:'GND',4:None,5:tag+'_I_RAW',6:'V3V3',7:'V3V3',8:p});dec(s)
    r(s,tag+'_I_RAW',tag+'_I_FILTER','100R');c(s,tag+'_I_FILTER','GND','1nF C0G')
    # Dedicated fast front ends differ from INA240/control ADC; both polarities.
    for pol,ip,im in [('POS',p,m),('NEG',m,p)]:
        add(s,'INA293A1DBVR',{1:tag+'_FAST_'+pol,2:'GND',3:ip,4:im,5:'V3V3'});dec(s)
add(s,'J5',['BUS_FAST_POS','BUS_FAST_NEG','CAP_FAST_POS','CAP_FAST_NEG','GND'],'OC diagnostic outputs / do not load')
notes[s]+=['WSK Kelvin pads2/3 route separately to amplifiers; no power current in sense tracks.',
           'INA240 refs REF1=VS, REF2=GND -> midscale1.65V. +-8A bus and +-20A cap/IL nominal ADC windows.',
           'All fast front ends INA293 CM -4..110V; INA301 rejected because40V absmax is below SMBJ28A45.4V rated clamp.',
           'IL dedicated INA293 opposite polarities, CM -4..110V; PWM edge recovery and latency must be measured.']

s='VOLTAGE_SENSING'
for tag,src,bot in [('BUS','BUS_LINK','5.1k'),('CAP','CAP_LINK','6.8k'),('BUS_RAW','BUS_FUSED','5.1k'),('CAP_RAW','BANK_P_RAW','6.8k')]:
    r(s,src,tag+'_DIV_TOP','33k /1%');r(s,tag+'_DIV_TOP',tag+'_V_FILTER','33k /1%')
    r(s,tag+'_V_FILTER','GND',bot+' /1%');c(s,tag+'_V_FILTER','GND','4.7nF C0G')
    add(s,'D',['ADC_CLAMP_2V7',tag+'_V_FILTER'],'BAT54H signal clamp',fp='Diode_SMD:D_SOD-123F')
    add(s,'D',[tag+'_V_FILTER','GND'],'BAT54H negative clamp',fp='Diode_SMD:D_SOD-123F')
# Independent bank/bus powered clamp sink; not a connection to MCU VDD.
for src in ['BUS_FUSED','BANK_P_RAW']:
    add(s,'D',['CLAMP_OR',src],'1N4148W /100V',fp='Diode_SMD:D_SOD-123')
r(s,'CLAMP_OR','ADC_CLAMP_2V7','3.3k /1W',fp='Resistor_SMD:R_2512_6332Metric')
add(s,'TLV431AIDBZR',{1:'CLAMP_REF',2:'ADC_CLAMP_2V7',3:'GND'})
r(s,'ADC_CLAMP_2V7','CLAMP_REF','11.8k /1%');r(s,'CLAMP_REF','GND','10k /1%')
add(s,'PWR_FLAG',['ADC_CLAMP_2V7'],'independent shunt clamp rail')
signals=[('BUS_V_FILTER','BUS_V_ADC'),('CAP_V_FILTER','CAP_V_ADC'),('BUS_RAW_V_FILTER','BUS_RAW_ADC'),('CAP_RAW_V_FILTER','CAP_RAW_ADC'),('BUS_I_FILTER','BUS_I_ADC'),('CAP_I_FILTER','CAP_I_ADC'),('IL_I_FILTER','IL_I_ADC'),('TEMP_FET_FILTER','TEMP_FET_ADC'),('TEMP_L_FILTER','TEMP_L_ADC'),('TEMP_BANK_FILTER','TEMP_BANK_ADC')]
for index in range(0,len(signals),4):
    ns={1:'RAIL_OK',4:'RAIL_OK',7:'GND',10:'RAIL_OK',13:'RAIL_OK',14:'V3V3'}
    for k,(sp,dp) in enumerate([(2,3),(5,6),(9,8),(12,11)]):
        src,dst=signals[index+k] if index+k<len(signals) else ('GND',None)
        ns[sp]=src;ns[dp]=dst
    add(s,'TMUX1511PWR',ns);dec(s)
for src,dst in signals:
    r(s,dst,'GND','100k off leakage drain')
notes[s]+=['TMUX1511 powered-off isolation <=3.6V; independent 2.7V clamp proposal avoids dumping into dead MCU rail.',
           'Divider bus36V ->2.582V; cap24.3V ->2.270V nominal. Clamp forward-V and all partial-power cases MUST VERIFY.',
           '100k ADC-side drain:2uA max powered-off leakage gives0.2V estimate. Include loaded divider/NTC calibration.',
           'Current/NTC outputs are bus-fed; partial-power/backfeed and probe effects remain test gates.']
s='TEMPERATURE_SENSING'
for tag in ['FET','L','BANK']:
    r(s,'V3V3','TEMP_'+tag+'_FILTER','10k /1%');r(s,'TEMP_'+tag+'_FILTER','GND','NTCLE100E3103JB0 /10k NTC B3977',fp='Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical')
    c(s,'TEMP_'+tag+'_FILTER','GND','10nF');add(s,'J2',['TEMP_'+tag+'_FILTER','GND'],tag+' NTC probe option',fp='Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical',dni=True)
notes[s]+=['3 representative hotspots; optional connector replaces fitted NTC, not parallel second thermistor.',
           'Open NTC reads high, short reads zero. Firmware faults both extremes; hardware thermal window also in SAFETY.',
           'Trip reference options: bank ~55C, FET/L ~70C investigation only; hotspot-to-junction lag unresolved.']

s='SUPERCAP_BANK'
add(s,'J2',['BANK_P_RAW','GND'],'9S bank power -> official module external boundary',fp='')
add(s,'DISCONNECT',['BANK_P_RAW','BANK_MANUAL_OUT'],'Blue Sea6006 / external manual bank disconnect;not a fault breaker',fp='')
add(s,'FUSE',['BANK_MANUAL_OUT','BANK_FUSED'],'0997015.WXN / MINI997 58V15A / external 0FHM0002ZXJM holder')
relay(s,'BANK_FUSED','CAP_ISOLATED','CAP_ISO_DRIVE','CAP_ISO')
raw=['GND']+['CELL'+str(i)+'_RAW' for i in range(1,9)]+['BANK_P_RAW']
for i in range(1,10):c(s,raw[i],raw[i-1],'50F /2.7V SCCV40B506SRB / external cell',fp='')
protected=['TAP'+str(i)+'_SOURCE_PROTECTED' for i in range(10)]
for i,net in enumerate(raw):r(s,net,protected[i],'1k /1W EXTERNAL cell-terminal tap resistor',fp='')
add(s,'J10',protected,'Protected 9S taps / source resistors at electrodes,never at cable end',fp='')
for i,net in enumerate(protected):
    r(s,net,'CELL'+str(i)+'_FILTER','1k /1W tap protection / no bypass',fp='Resistor_SMD:R_2512_6332Metric')
for i in range(1,10):c(s,'CELL'+str(i)+'_FILTER','CELL'+str(i-1)+'_FILTER','100nF /50V X7R')
bqns={i:None for i in P['BQ7694204PFBR'].pins}
bqns.update({'2':'CELL8_FILTER','4':'CELL8_FILTER','6':'CELL7_FILTER','8':'CELL6_FILTER','10':'CELL5_FILTER','12':'CELL4_FILTER','13':'CELL3_FILTER','14':'CELL2_FILTER','15':'CELL1_FILTER','16':'CELL0_FILTER','17':'GND','18':'GND','20':'GND','21':'MON_TS1','22':'MON_TS2','23':'MON_TS3','24':'MON_REG18','25':'MON_ALERT','26':'MON_SCLK','27':'MON_MISO','28':'MON_MOSI','29':'MON_CS','30':'GND','31':'MON_DCHG','32':'MON_DDSG','33':'GND','35':'MON_REG1','36':'MON_REGIN','37':'MON_BREG','41':'MON_LD','42':'MON_PACK','46':'MON_CP','47':'MON_BAT','48':'CELL9_FILTER'})
add(s,'BQ7694204PFBR',bqns)
add(s,'SN74LV1T34DBVR',{1:None,2:'MON_MISO',3:'GND',4:'MON_MISO_SHIFTED',5:'MON_REG1'});dec(s,'MON_REG1');pull(s,'MON_MISO')
add(s,'TPS3839K33DBZR',{1:'GND',2:'MON_POWER_OK',3:'MON_REG1'});dec(s,'MON_REG1')
gate(s,'RAIL_OK','MON_POWER_OK','MON_COMM_PERMIT','GND','GND',None)
for index,group in enumerate([[('MON_SCLK_HOST','MON_SCLK'),('MON_MOSI_HOST','MON_MOSI'),('MON_CS_HOST','MON_CS'),('MON_MISO_SHIFTED','MON_MISO_HOST')],[('MON_ALERT','MON_ALERT_HOST'),('GND',None),('GND',None),('GND',None)]]):
    ns={1:'MON_COMM_PERMIT',4:'MON_COMM_PERMIT',7:'GND',10:'MON_COMM_PERMIT',13:'MON_COMM_PERMIT',14:'V3V3'}
    for (sp,dp),(src,dst) in zip([(2,3),(5,6),(9,8),(12,11)],group):ns[sp]=src;ns[dp]=dst
    add(s,'TMUX1511PWR',ns);dec(s)
pull(s,'MON_ALERT','MON_REG1')
pull(s,'MON_CS','MON_REG1');pull(s,'MON_SCLK');pull(s,'MON_MOSI')
r(s,'BANK_P_RAW','MON_BAT','100R');c(s,'MON_BAT','GND','1uF /50V X7R');r(s,'MON_CP','MON_BAT','0R')
r(s,'BANK_P_RAW','MON_PACK','10k');r(s,'BANK_P_RAW','MON_LD','10k')
# BREG external emitter follower: B=pin1 E=pin2 C=pin3; base controlled by IC.
add(s,'Q_NPN',['MON_BREG','MON_REGIN','MON_BAT'],'BC847B preregulator / voltage thermal MUST VERIFY')
c(s,'MON_REGIN','GND','1uF /16V');c(s,'MON_REG1','GND','1uF /16V');c(s,'MON_REG18','GND','1uF /16V')
for ts in ['MON_TS1','MON_TS2','MON_TS3']:r(s,ts,'GND','10k TS commissioning option')
for net in ['MON_DCHG','MON_DDSG']:pull(s,net)
add(s,'PWR_FLAG',['MON_BAT'],'bank-fed monitor input')
notes[s]+=['BQ7694204 SPI/CRC +3.3V REG1 variant. 9S mask: cells1..8 +cell10, VC9 tied to VC8, unused cell9 disabled.',
           'RAM profile firmware/config/bq76942_rev_a.json: COV2.530V, CUV1.2144V, delay~10ms; readback mandatory.',
           'DCHG/DDSG active-LOW fault / healthy-HIGH REG1 permission,0xA6,pull-down. Never use Li-ion defaults.',
           'Host-only balance,2k total input resistance/tap including external1k; slow trim,not full-current balancing.',
           'Open-wire current/settling plus input R must be validated; harness source protection before connector is mandatory.',
           'TMUX SPI/ALERT disconnect if either MCU or REG1 power missing; LV1T34 handles initial1.8V MISO level.',
           'BQ battery-ground SPI is not galvanically isolated; partial-power/backfeed review still mandatory.']

s='SAFE_DISCHARGE'
r(s,'BANK_P_RAW','GND','10k /1W permanent bleed',fp='Resistor_SMD:R_2512_6332Metric')
r(s,'BANK_P_RAW','DUMP_DRAIN','100R /HS25 100R F / external chassis mount',fp='')
add(s,'CSD18540Q5B',{1:'GND',2:'DUMP_GATE',3:'DUMP_DRAIN'})
pull(s,'DUMP_GATE',v='10k');r(s,'DUMP_PNP_C','DUMP_GATE','47R')
add(s,'Q_PNP',['DUMP_PNP_B','V12_DRIVER','DUMP_PNP_C'],'BC857B');pull(s,'DUMP_PNP_B','V12_DRIVER')
r(s,'DUMP_PNP_B','DUMP_NPN_C','10k');npn(s,'DUMP_DRIVE','DUMP_NPN_C')
add(s,'D',['DUMP_GATE','GND'],'BZT52H-C15',fp='Diode_SMD:D_SOD-123F')
r(s,'BANK_P_RAW','RESIDUAL_LED_A','22k /0.25W');add(s,'LED',['GND','RESIDUAL_LED_A'],'red residual-energy indicator / bank-powered')
add(s,'J2',['BANK_P_RAW','GND'],'KEYED service meter / rated discharge tool connection',fp='')
add(s,'DISCONNECT',['BANK_P_RAW','SERVICE_R_IN'],'Blue Sea6006 / external independent service tool;guarded manual operation',fp='')
r(s,'SERVICE_R_IN','GND','100R / HS25 100R F / external service tool',fp='')
notes[s]+=['OFF is not safe. LED dark is not safe. Independent meter + all cells + local links + rebound required.',
           'Switched100R initial4.862W, energy up to1752J(+30%); 10k bleed alone ~62h to1V. No guaranteed service time.',
           'Dump unavailable after bus aux loss: permanent bleed + independent service tool remain; do not add unauthorized bank-to-bus supply.',
           'DUMP_DRIVE requires temperature permission; MOSFET-short leaves100R permanently on, resistor thermal review mandatory.']

s='CAN'
add(s,'SN65HVD230DR',{1:'CAN_TX',2:'GND',3:'V3V3',4:'CAN_RX',5:None,6:'CAN_L',7:'CAN_H',8:'CAN_STANDBY'});dec(s)
pull(s,'CAN_TX','V3V3');pull(s,'CAN_STANDBY','V3V3')
add(s,'J3',['CAN_H','CAN_L','GND'],'robot telemetry CAN / official module CAN separate',fp='')
r(s,'CAN_H','CAN_TERM','120R /1%');add(s,'J2',['CAN_TERM','CAN_L'],'selectable termination shunt, fit only at bus end')
notes[s]+=['Classic CAN initial protocol, bitrate/ID/timeouts TBD. CAN comm must not bypass official cutoff.',
           'CAN powered-off impedance/common-mode protection and external power through UART/SWD/taps require validation.']
s='SAFETY'
for tag,top in [('BUS','58.7k'),('CAP','35.7k')]:
    lim=tag+'_LIMIT';r(s,'V3V3',lim,top+' /1%');r(s,lim,'GND','10k /PROVISIONAL')
    add(s,'TLV3202DGKR',{1:tag+'_POS_OK',2:tag+'_FAST_POS',3:lim,4:'GND',5:lim,6:tag+'_FAST_NEG',7:tag+'_NEG_OK',8:'V3V3'});dec(s)
gate(s,'BUS_POS_OK','BUS_NEG_OK','BUS_OC_OK','CAP_POS_OK','CAP_NEG_OK','CAP_OC_OK')
gate(s,'BUS_OC_OK','CAP_OC_OK','PORT_OC_N','GND','GND',None)
# Comparator outputs high only when below trip: low asynchronously clears permit.
add(s,'TLV3202DGKR',{1:'IL_POS_OK',2:'IL_FAST_POS',3:'IL_LIMIT',4:'GND',5:'IL_LIMIT',6:'IL_FAST_NEG',7:'IL_NEG_OK',8:'V3V3'});dec(s)
r(s,'V3V3','IL_LIMIT','35.7k');r(s,'IL_LIMIT','GND','10k / IL12.035A PROVISIONAL')
gate(s,'IL_POS_OK','IL_NEG_OK','IL_OK','PG_DRV','PG_MCU','AUX_OK')
gate(s,'IL_OK','PORT_OC_N','OC_OK','AUX_OK','RAIL_OK','POWER_OK')
add(s,'TPS3839K33DBZR',{1:'GND',2:'RAIL_OK',3:'V3V3'});dec(s)
add(s,'TPS3431SDRBR',{1:'V3V3',2:'WD_CWD',3:'V3V3',4:'GND',5:'V3V3',6:'WD_HEARTBEAT',7:'WATCHDOG_OK',8:None,9:'GND'});dec(s)
pull(s,'WATCHDOG_OK','V3V3');r(s,'WD_CWD','V3V3','10k / preset timeout; verify SET1 table')
# Bank permits are combined with host commissioning permit; no MCU-only cell OV.
gate(s,'MON_DCHG','MON_DDSG','CELLS_HW_OK','OC_OK','POWER_OK','FAST_OK')
gate(s,'CELLS_HW_OK','MON_CONFIG_VALID','CELLS_OK','FAST_OK','WATCHDOG_OK','BASE_OK')
gate(s,'BASE_OK','CELLS_OK','PROTECT_OK','PROTECT_OK','REFEREE_PERMIT','FAULT_CLEAR_N')
gate(s,'FAULT_CLEAR_N','NRST','LATCH_CLEAR_N','MCU_GATE_REQUEST','FAULT_LATCH_Q','REQUEST_PERMIT')
# Async clear dominant: Q false at reset/fault. CLK arm request accepted only
# after all permits valid; fault release alone does not rearm.
add(s,'SN74LVC1G74DCUR',{1:'ARM_PULSE',2:'V3V3',3:'FAULT_LATCH_QN',4:'GND',5:'FAULT_LATCH_Q',6:'LATCH_CLEAR_N',7:'V3V3',8:'V3V3'});dec(s)
add(s,'J2',['FAULT_LATCH_QN','GND'],'latched fault diagnostic output')
gate(s,'REQUEST_PERMIT','FAULT_CLEAR_N','GATE_PERMIT','FAULT_CLEAR_N','V3V3','HW_FAULT_N')
gate(s,'FAULT_LATCH_Q','FAULT_CLEAR_N','CONTACT_PERMIT','GND','GND',None)
pull(s,'FAULT_LATCH_Q');pull(s,'GATE_PERMIT')
for request,drive in [('BUS_ISO_REQUEST','BUS_ISO_DRIVE'),('CAP_ISO_REQUEST','CAP_ISO_DRIVE'),('PRE_BUS_REQUEST','PRE_BUS_DRIVE'),('BYP_BUS_REQUEST','BYP_BUS_DRIVE'),('PRE_CAP_REQUEST','PRE_CAP_DRIVE'),('BYP_CAP_REQUEST','BYP_CAP_DRIVE')]:
    # Precharge must be allowed before gate permit. Protection valid is still
    # required; main bypass validity/feedback additionally supervised by MCU.
    other=request+'__UNUSED_Y';gate(s,request,'PROTECT_OK',drive,'GND','GND',other);pull(s,request)
# Separate dump thermal signal: external TEMP-window comparator added below.
for tag,threshold in [('FET','1.74k'),('L','1.74k'),('BANK','3.01k')]:
    lim='TEMP_'+tag+'_LIMIT';r(s,'V3V3',lim,'10k');r(s,lim,'GND',threshold+' /PROVISIONAL')
    # Two channels form hot/short lower and open upper limit window.
    add(s,'TLV3202DGKR',{1:tag+'_TEMP_LO_OK',2:lim,3:'TEMP_'+tag+'_FILTER',4:'GND',5:'TEMP_OPEN_LIMIT',6:'TEMP_'+tag+'_FILTER',7:tag+'_TEMP_HI_OK',8:'V3V3'});dec(s)
    gate(s,tag+'_TEMP_LO_OK',tag+'_TEMP_HI_OK',tag+'_THERM_OK','GND','GND',tag+'_THERM_UNUSED')
r(s,'V3V3','TEMP_OPEN_LIMIT','1k');r(s,'TEMP_OPEN_LIMIT','GND','10k')
gate(s,'FET_THERM_OK','L_THERM_OK','POWER_THERM_OK','POWER_THERM_OK','BANK_THERM_OK','THERM_OK')
# Thermal trip also asynchronously vetoes all fault permissions via pull-down
# transistor on a separate series AND; avoid tying push-pull outputs together.
gate(s,'PROTECT_OK','THERM_OK','THERM_PROTECT_OK','DUMP_REQUEST','THERM_OK','DUMP_DRIVE')
# Independent rail voltage window from separate dividers and 1.24V reference.
r(s,'V3V3','HW_REF_1V24','2.2k');add(s,'TLV431AIDBZR',{1:'HW_REF_1V24',2:'HW_REF_1V24',3:'GND'})
for tag,src,top in [('BUS_OV','BUS_FUSED','221k'),('BUS_UV','BUS_FUSED','154k'),('BANK_OV','BANK_P_RAW','172k')]:
    r(s,src,tag+'_DIV',top+' /1%');r(s,tag+'_DIV','GND','10k /1%');c(s,tag+'_DIV','GND','1nF /50V')
add(s,'TLV3202DGKR',{1:'BUS_OV_OK',2:'BUS_OV_DIV',3:'HW_REF_1V24',4:'GND',5:'BUS_UV_DIV',6:'HW_REF_1V24',7:'BUS_UV_OK',8:'V3V3'});dec(s)
add(s,'TLV3202DGKR',{1:'BANK_OV_OK',2:'BANK_OV_DIV',3:'HW_REF_1V24',4:'GND',5:'GND',6:'V3V3',7:None,8:'V3V3'});dec(s)
gate(s,'BUS_OV_OK','BUS_UV_OK','BUS_WINDOW_OK','BUS_WINDOW_OK','BANK_OV_OK','RAILS_WINDOW_OK')
gate(s,'THERM_PROTECT_OK','RAILS_WINDOW_OK','ALL_PROTECT_OK','GND','GND',None)
# Gate bias rail window, independent of PGOOD (which is mainly UV monitoring).
r(s,'V12_DRIVER','DRIVER_UV_DIV','80.6k');r(s,'DRIVER_UV_DIV','GND','10k')
r(s,'V12_DRIVER','DRIVER_OV_DIV','100k');r(s,'DRIVER_OV_DIV','GND','10k')
add(s,'TLV3202DGKR',{1:'DRIVER_UV_OK',2:'HW_REF_1V24',3:'DRIVER_UV_DIV',4:'GND',5:'HW_REF_1V24',6:'DRIVER_OV_DIV',7:'DRIVER_OV_OK',8:'V3V3'});dec(s)
gate(s,'DRIVER_UV_OK','DRIVER_OV_OK','DRIVER_WINDOW_OK','ALL_PROTECT_OK','DRIVER_WINDOW_OK','DRIVER_PROTECT_OK')
for tag,top in [('ACTUATOR_UV','78.7k'),('ACTUATOR_OV','100k')]:
    r(s,'ACTUATOR_12V',tag+'_DIV',top);r(s,tag+'_DIV','GND','10k')
add(s,'TLV3202DGKR',{1:'ACTUATOR_UV_OK',2:'HW_REF_1V24',3:'ACTUATOR_UV_DIV',4:'GND',5:'HW_REF_1V24',6:'ACTUATOR_OV_DIV',7:'ACTUATOR_OV_OK',8:'V3V3'});dec(s)
gate(s,'ACTUATOR_UV_OK','ACTUATOR_OV_OK','ACTUATOR_WINDOW_OK','DRIVER_PROTECT_OK','ACTUATOR_WINDOW_OK','ASSEMBLY_PROTECT_OK')
notes[s]+=['Independent IL INA293 + comparator -> async latch clear -> PWM AND + EN LOW, plus HRTIM FLT1.',
           'Port INA293 pairs + TLV3202 windows + AND. No ADC polling in OC path; maximum delay unverified.',
           'Hardware cell permission requires BQ provisioning; missing/invalid commissioning inhibits startup.',
           'Thermal comparator hot/short/open window; source supply/shared sensor/common shunt failures remain in FMEA.',
           'External contacts release slower than gate kill; coil current/release/fuse coordination require separate review.']
# Route every source/precharge/PWM permit through thermal qualification.
for page,items in pages.items():
    for item in items:
        if item['typ']=='SN74LVC2G08DCUR':
            if item['nets'].get('3')=='FAULT_CLEAR_N':item['nets']['5']='ASSEMBLY_PROTECT_OK'
            if item['nets'].get('7') in ['BUS_ISO_DRIVE','CAP_ISO_DRIVE','PRE_BUS_DRIVE','BYP_BUS_DRIVE','PRE_CAP_DRIVE','BYP_CAP_DRIVE']:item['nets']['2']='CONTACT_PERMIT'
            if (item['nets'].get('3') or '').endswith(('_UNUSED_Y','_THERM_UNUSED')):item['nets']['3']=None

pages['SENSING'];notes['SENSING']=['Electrical sensing now on CURRENT_SENSING, VOLTAGE_SENSING and TEMPERATURE_SENSING.',
 'Global labels connect actual package pins and wires across hierarchy. No firmware or PCB placement.',
 'Review all external assemblies, source-side tap protection and provisional ratings before energizing.']

# Explicit board/harness boundary. External contacts, cells, source resistors
# and service parts remain outside the PCB rather than silently acquiring pads.
board_nets={n for items in pages.values() for x in items if x['fp'] for n in x['nets'].values() if n}
external_nets={n for items in pages.values() for x in items if not x['fp'] and not x['ref'].startswith('#') for n in x['nets'].values() if n}
power_boundary={'BUS_FUSED','BUS_LINK_IN','CAP_LINK_IN','CAP_BANK_RAW','CAP_FUSED','BUS_RAW','GND','DISCHARGE_DRAIN'}
for net in sorted(board_nets & external_nets):
    fp=('Connector_Wire:SolderWire-2sqmm_1x01_D2mm_OD3.9mm' if net in power_boundary else
        'Connector_Wire:SolderWire-0.5sqmm_1x01_D0.9mm_OD2.1mm')
    add('PCB_INTERFACE','J1_PAD',[net],net+' / soldered harness with fixture strain relief',fp=fp)
notes['PCB_INTERFACE']=['Bench prototype only: wire lands are NOT plug connectors. Harness continuity/polarity inspection mandatory.',
 'External isolation/fuses/precharge/cells remain separate. Each named terminal is a distinct net; do not bridge protection.',
 '2026-10-04 user authorized PCB work without preceding hardware measurement. No fabrication or energizing release.']

def libsymbol(typ):
    spec=P[typ];n=len(spec.pins);rows=(n+1)//2;h=max(5,(rows+1)*2.54/2)
    s=f'(symbol {q("RevA:"+typ)} (pin_names (offset 0.5)) (in_bom yes) (on_board yes)'
    for key,val in [('Reference','U'),('Value',typ),('Footprint',spec.footprint),('Datasheet',spec.source)]:
        s+=f'(property {q(key)} {q(val)} (at 0 0 0) {effects()} (hide yes))'
    s+=f'(symbol {q(typ+"_0_1")} (rectangle (start -12 {-h}) (end 12 {h}) (stroke (width 0.254) (type default)) (fill (type background))))'
    s+=f'(symbol {q(typ+"_1_1")}'
    pos={}
    for i,(number,(name,kind)) in enumerate(spec.pins.items()):
        left=i<rows;j=i if left else i-rows;y=(rows-1)*2.54/2-j*2.54;x=-15 if left else 15
        x=-15.24 if left else 15.24
        pos[number]=(x,-y,left)
        s+=f'(pin {kind} line (at {x} {y} {0 if left else 180}) (length 3.24) (name {q(name)} {effects(0.8)}) (number {q(number)} {effects(0.8)}))'
    return s+'))',pos,h

def generate():
    old=(K/(NAME+'.kicad_sch')).read_text(encoding='utf-8')
    rootid=re.search(r'\(uuid "([^"]+)"\)',old).group(1)
    sheetids=dict(re.findall(r'\(uuid "([^"]+)"\) \(property "Sheetname" "([^"]+)"',old))
    sheetids={v:k for k,v in sheetids.items()}
    root=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {q(rootid)}) (paper "A3") (lib_symbols)'
    root+=f'(text "PROTOTYPE REV A - PCB WORK AUTHORIZED; NOT RELEASED FOR ENERGIZING" (at 200 15 0) {effects(2)} (uuid {q(uid("root-title"))}))'
    registry=[]
    for index,(sheet,items) in enumerate(pages.items()):
        sid=sheetids.get(sheet,uid('sheet:'+sheet));cid=uid('page:'+sheet)
        x=20+(index%4)*95;y=40+(index//4)*58
        root+=f'(sheet (at {x} {y}) (size 82 40) (stroke (width 0.254) (type default)) (fill (color 0 0 0 0)) (uuid {q(sid)}) (property "Sheetname" {q(sheet)} (at {x} {y-1} 0) {effects()}) (property "Sheetfile" {q(sheet+".kicad_sch")} (at {x} {y+41} 0) {effects()}) (instances (project {q(NAME)} (path {q('/'+rootid)} (page {q(index+2)})))))'
        lib={typ:libsymbol(typ) for typ in sorted({item['typ'] for item in items})}
        height=max(841,230+((len(items)+6)//7)*100)
        out=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {q(cid)}) (paper "User" 1189 {height}) (title_block (title {q(sheet+" / Prototype Rev A draft")}) (rev "RevA-draft") (comment 1 "ASSUMPTION - MUST VERIFY ON PROTOTYPE; PCB engineering authorized")) (lib_symbols '+''.join(v[0] for v in lib.values())+')'
        for i,item in enumerate(items):
            # Spacious package-box electrical schematic; wires carry global nets.
            xx=88.9+(i%7)*152.4;yy=114.3+(i//7)*101.6
            typ=item['typ'];ref=item['ref'];su=uid('component:'+ref);_,pins,h=lib[typ]
            out+=f'(symbol (lib_id {q("RevA:"+typ)}) (at {xx} {yy} 0) (unit 1) (in_bom {"no" if ref.startswith("#") else "yes"}) (on_board {"yes" if item["fp"] and not ref.startswith("#") else "no"}) (dnp {"yes" if item["dni"] else "no"}) (uuid {q(su)})'
            for key,val,pos,hide in [('Reference',ref,yy-h-5,False),('Value',item['value'],yy+h+4,False),('Footprint',item['fp'],yy,True),('Datasheet',P[typ].source,yy,True),('MPN',item['mpn'],yy,True)]:
                out+=f'(property {q(key)} {q(val)} (at {xx} {pos} 0) {effects(1)}'+(' (hide yes)' if hide else '')+')'
            for number in pins:out+=f'(pin {q(number)} (uuid {q(uid(ref+":"+number))}))'
            out+=f'(instances (project {q(NAME)} (path {q("/"+rootid+"/"+sid)} (reference {q(ref)}) (unit 1)))))'
            for number,(dx,dy,left) in pins.items():
                px=round(xx+dx,6);py=round(yy+dy,6);net=item['nets'][number]
                if net is None:
                    out+=f'(no_connect (at {px} {py}) (uuid {q(uid(ref+":"+number+":nc"))}))';continue
                ex=round(px+(-5.08 if left else 5.08),6)
                out+=f'(wire (pts (xy {px} {py}) (xy {ex} {py})) (stroke (width 0) (type default)) (uuid {q(uid(ref+":"+number+":wire"))}))'
                # Global label anchor is exactly at wire endpoint; shape passive
                # bidirectional label is not a pin-type escape.
                out+=f'(global_label {q(net)} (shape bidirectional) (at {ex} {py} {0 if left else 180}) (fields_autoplaced yes) {effects(0.8)} (uuid {q(uid(ref+":"+number+":label"))}))'
            registry.append(dict(sheet=sheet,**item))
        ny=height-65
        for j,note in enumerate(notes[sheet]):
            out+=f'(text {q(note)} (at 530 {ny+j*5} 0) {effects(1.3)} (uuid {q(uid(sheet+":note:"+str(j)))}))'
        from read_kicad import parse,children
        out+=')\n'
        assert len(children(parse(out),'symbol'))==len(items),sheet
        from read_kicad import pretty
        (K/(sheet+'.kicad_sch')).write_text(pretty(parse(out))+'\n',encoding='utf-8')
    root+='(sheet_instances (path "/" (page "1"))))\n'
    (K/(NAME+'.kicad_sch')).write_text(pretty(parse(root))+'\n',encoding='utf-8')
    # Own original symbols; no external schematic/library files copied.
    (K/'rev_a.kicad_sym').write_text(pretty(parse('(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor")'+''.join(libsymbol(t)[0].replace(q('RevA:'+t),q(t),1) for t in sorted(P))+')'))+'\n',encoding='utf-8')
    (K/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "RevA")(type "KiCad")(uri "${KIPRJMOD}/rev_a.kicad_sym")(options "")(descr "Original Rev A package symbols; manufacturer pin facts")))\n',encoding='utf-8')
    (ROOT/'simulation/rev_a_connectivity.json').write_text(json.dumps(registry,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('Generated',len(pages),'electrical/overview sheets;',len(registry),'components. Project settings/PCB untouched.')
if __name__=='__main__':generate()
