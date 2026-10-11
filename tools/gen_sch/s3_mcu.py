"""Sheet 3: aux 3.3 V supply, STM32G431 MCU, clock, SWD, CAN, referee UART, LEDs."""
import sys
from kisch2 import Sheet2
from parts import *

s = Sheet2("Rev B control board - 3/4 MCU and aux power", paper="A3", path=sys.argv[2], ref_base=200, global_nets=GLOBALS)
r, c, gnd, v33 = mk(s)

s.text(15, 15, "3/4  Aux 3.3 V supply, MCU (STM32G431CBT6), CAN, referee UART", 2.5, bold=True)
s.text(15, 20.5, "3V3 is fed from PM input OR the bank (NODE), so the MCU stays alive while the robot is unpowered "
                 "(bank drain ~0.15 W).  MCU runs only the slow outer loop.", 1.27)

# ================= aux power
s.frame(15, 30, 160, 45, "Aux 3.3 V  (AP63203, 3.8-32 V in)")
Y = 45.72
Da = s.add(DS, 35.56, Y, "SS34", {"1": "AUX_OR", "2": "VIN_F"}, rot=180, text="above", props={"Footprint": "Diode_SMD:D_SMA"})
Db = s.add(DS, 35.56, Y + 10.16, "SS34", {"1": "AUX_OR", "2": "NODE"}, rot=180, text="above", props={"Footprint": "Diode_SMD:D_SMA"})
s.wire(Da[2], (Da[2][0] - 5.08, Y))
s.label("VIN_F", (Da[2][0] - 5.08, Y), "L")
s.wire(Db[2], (Db[2][0] - 5.08, Y + 10.16))
s.label("NODE", (Db[2][0] - 5.08, Y + 10.16), "L")
xo = 45.72
s.wire(Da[1], (xo, Y))
s.wire(Db[1], (xo, Y + 10.16), (xo, Y))
Ra = s.add(R, 53.34, Y, "10R", {"1": "AUX_OR", "2": "AUX_IN"}, rot=90, text="above", props={"Footprint": R06})
s.wire((xo, Y), Ra[1])
U = s.add(AP, 109.22, Y + 2.54, "AP63203WU", {"1": "3V3", "2": "AUX_IN", "3": "AUX_IN", "4": "GND", "5": "AUX_SW",
                                              "6": "AUX_BST"}, text="box",
          props={"Footprint": "Package_TO_SOT_SMD:TSOT-23-6", "Note": "EN tied to IN (EN abs max = VIN): confirm"})
s.wire(Ra[2], U["3"])
Dt = s.add(DZ, 66.04, Y + 7.62, "SMAJ28A", {"1": "AUX_IN", "2": "GND"}, rot=270, props={"Footprint": "Diode_SMD:D_SMA"})
s.wire((66.04, Y), Dt[1])
gnd(Dt[2])
for i, x in enumerate((76.2, 86.36)):
    k = c(x, Y + 7.62, "10u 50V", "AUX_IN", "GND", fp=C12)
    s.wire((x, Y), k[1])
    gnd(k[2])
xe = U["2"][0] - 2.54
s.wire(U["2"], (xe, U["2"][1]), (xe, Y))
gnd(U["4"])
s.wire((66.04, Y), (66.04, Y - 5.08))
s.power(FLAG, (66.04, Y - 5.08))
# switch node, bootstrap, inductor, output
xsw = U["5"][0]
Lx = s.add(L, 137.16, U["5"][1], "6.8uH", {"1": "AUX_SW", "2": "3V3"}, rot=90, text="above",
           props={"Footprint": "Inductor_SMD:L_Wuerth_MAPI-4030", "LCSC": "C167876", "Note": "FNR4030S6R8MT 4x4: verify land"})
s.wire(U["5"], Lx[1])
Cb = c(124.46, U["6"][1] + 3.81, "100n", "AUX_BST", "AUX_SW")
s.wire(U["6"], Cb[1])
s.wire(Cb[2], (128.27, Cb[2][1]), (128.27, U["5"][1]))
yfb = Cb[2][1] + 5.08
s.wire(U["1"], (120.65, U["1"][1]), (120.65, yfb), (143.51, yfb), (143.51, U["5"][1]))
xr = 167.64
s.wire(Lx[2], (xr, U["5"][1]))
for x in (148.59, 158.75):
    k = c(x, U["5"][1] + 7.62, "22u 25V", "3V3", "GND", fp=C08)
    s.wire((x, U["5"][1]), k[1])
    gnd(k[2])
v33((xr, U["5"][1]))
s.wire((xr, U["5"][1]), (xr, U["5"][1] + 5.08))
s.power(FLAG, (xr, U["5"][1] + 5.08))
s.text(18, Y + 22, "D: SS34 (40V 3A).  R 10R limits SMAJ28A current so AUX_IN stays below the AP63203 35 V abs max.", 1.27)

# ================= MCU
MX, MY = 236.22, 160.02
mcu_named = {
    "PA0": "VNODE_S", "PA1": "VINC_S", "PA2": "TEMP_S", "PA3": "IIN_S", "PA4": "ILIM_DAC", "PA6": "ICAP_S",
    "PB0": "EN_CHG", "PB1": "EN_PMOS", "PB2": "PGOOD", "PB12": "NODE_OK", "PB13": "PMOS_EN",
    "PA11": "CAN_RX", "PA12": "CAN_TX", "PB10": "UART_TX", "PB11": "UART_RX",
    "PB5": "LED1", "PB6": "LED2", "PA13": "SWDIO", "PA14": "SWCLK", "PG10": "NRST",
    "PF0": "OSC_IN", "PF1": "OSC_OUT", "PB8": "BOOT0",
    "VDD": "3V3", "VDDA": "3V3", "VREF+": "3V3", "VBAT": "3V3", "VSS": "GND", "VSSA": "GND",
}
M = s.add(MCU, MX, MY, "STM32G431CBT6", {}, named=mcu_named, props={"LCSC": "C529355",
          "Footprint": "Package_QFP:LQFP-48_7x7mm_P0.5mm"}, tpos=((MX + 6, MY - 47), (MX + 6, MY + 46)))
s.frame(160, 92, 120, 125, "MCU")
yb = MY - 40.64 - 5.08
for nm in ("VBAT", "VDD", "VDDA"):
    for num, n2 in MCU.names.items():
        if n2 == nm:
            s.wire(M[num], (M[num][0], yb))
xs = [M[n][0] for n, n2 in MCU.names.items() if n2 in ("VBAT", "VDD", "VDDA")]
s.wire((min(xs), yb), (max(xs), yb))
vref = [n for n, n2 in MCU.names.items() if n2 == "VREF+"][0]
s.wire(M[vref], (M[vref][0] - 5.08, M[vref][1]), (M[vref][0] - 5.08, yb), (min(xs), yb))
s.wire((min(xs), yb), (min(xs), yb - 2.54))
v33((min(xs), yb - 2.54))
vss = [n for n, n2 in MCU.names.items() if n2 in ("VSS", "VSSA")]
yv = MY + 40.64 + 3.81
for n in vss:
    s.wire(M[n], (M[n][0], yv))
xv = sorted({M[n][0] for n in vss})
s.wire((xv[0], yv), (xv[-1], yv))
gnd((xv[0], yv))
skip = set()
for num, n2 in MCU.names.items():
    if n2 in ("VDD", "VDDA", "VREF+", "VBAT", "VSS", "VSSA"):
        continue
    if num in M.nets:
        s.stub_label(M, num, M.nets[num], length=5.08)
s.nc_unused(M)
s.text(163, 210, "PA4 = DAC1_OUT1 (ILIM_DAC), PA6 = ADC2_IN3, PA11/12 = FDCAN1, PB10/11 = USART3.", 1.27)

# decoupling row
dx0, dy0 = 290, 105
s.frame(285, 92, 115, 30, "MCU decoupling (one 100n per VDD pin, 1u at VDDA)")
s.wire((dx0, dy0), (dx0 + 7.62 + 5 * 12.7, dy0))
v33((dx0, dy0))
for i, val in enumerate(("100n", "100n", "100n", "1u", "100n", "4.7u 25V")):
    x = dx0 + 7.62 + i * 12.7
    k = c(x, dy0 + 6.35, val, "3V3", "GND", fp=C06 if val != "4.7u 25V" else C08)
    s.wire((x, dy0), k[1])
    gnd(k[2])

# clock
cx0, cy0 = 290, 140
s.frame(285, 127, 55, 45, "8 MHz crystal (FDCAN clock)")
Y1 = s.add(XTAL, cx0 + 22.86, cy0, "8MHz", {"1": "OSC_IN", "2": "OSC_OUT"}, rot=0, text="above",
           props={"Footprint": "Crystal:Crystal_SMD_5032-2Pin_5.0x3.2mm", "LCSC": "C115962", "Note": "X50328MSB2GI CL 20pF"})
s.wire(Y1[1], (cx0 + 7.62, cy0))
s.label("OSC_IN", (cx0 + 7.62, cy0), "L")
s.wire(Y1[2], (cx0 + 38.1, cy0))
s.label("OSC_OUT", (cx0 + 38.1, cy0), "R")
for x in (Y1[1][0] - 2.54, Y1[2][0] + 2.54):
    k = c(x, cy0 + 7.62, "33p", "OSC_IN" if x < Y1[1][0] else "OSC_OUT", "GND")
    s.wire((x, cy0), k[1])
    gnd(k[2])

# reset / boot
bx0, by0 = 350, 140
s.frame(345, 127, 55, 45, "Reset / BOOT0")
Cn = c(bx0 + 5.08, by0 + 6.35, "100n", "NRST", "GND")
s.wire((bx0 + 5.08, by0), Cn[1])
s.wire((bx0 + 5.08, by0), (bx0 - 0.0, by0))
s.label("NRST", (bx0, by0), "L")
gnd(Cn[2])
Rb = r(bx0 + 30.48, by0 + 6.35, "10k", "BOOT0", "GND")
s.wire((bx0 + 30.48, by0), Rb[1])
s.wire((bx0 + 30.48, by0), (bx0 + 22.86, by0))
s.label("BOOT0", (bx0 + 22.86, by0), "L")
gnd(Rb[2])

# SWD
sx0, sy0 = 350, 190
s.frame(345, 177, 55, 40, "SWD")
J = s.add(CON5, sx0 + 30.48, sy0, "SWD 1.27mm (DNP)", {"1": "3V3", "2": "SWDIO", "3": "SWCLK", "4": "NRST", "5": "GND"},
          text="right", props={"Footprint": "Connector_PinHeader_1.27mm:PinHeader_1x05_P1.27mm_Vertical", "DNP": True})
s.wire(J["1"], (J["1"][0] - 5.08, J["1"][1]), (J["1"][0] - 5.08, J["1"][1] - 2.54))
v33((J["1"][0] - 5.08, J["1"][1] - 2.54))
for p in ("2", "3", "4"):
    s.stub_label(J, p, length=7.62)
s.wire(J["5"], (J["5"][0] - 5.08, J["5"][1]), (J["5"][0] - 5.08, J["5"][1] + 2.54))
gnd((J["5"][0] - 5.08, J["5"][1] + 2.54))

# ================= CAN
kx, ky = 60, 125
s.frame(15, 92, 140, 55, "Robot CAN  (SN65HVD230, 1 Mbps)")
UC = s.add(CAN, kx + 30.48, ky, "SN65HVD230", {"1": "CAN_TX", "2": "GND", "3": "3V3", "4": "CAN_RX", "6": "CANL",
                                               "7": "CANH", "8": "GND"}, text="box",
           props={"Footprint": "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"})
for p in ("1", "4"):
    s.stub_label(UC, p, length=7.62)
s.nc(UC["5"])
s.wire(UC["8"], (UC["8"][0] - 5.08, UC["8"][1]), (UC["8"][0] - 5.08, UC["8"][1] + 5.08))
gnd((UC["8"][0] - 5.08, UC["8"][1] + 5.08))
gnd(UC["2"])
yt = UC["3"][1] - 2.54
s.wire(UC["3"], (UC["3"][0], yt))
v33((UC["3"][0], yt))
Cc = c(UC["3"][0] + 10.16, yt + 3.81, "100n", "3V3", "GND")
s.wire((UC["3"][0], yt), (Cc[1][0], yt), Cc[1])
gnd(Cc[2])
JC = s.add(CON2, kx + 76.2, UC["7"][1], "CAN (GH 1.25 2p)", {"1": "CANH", "2": "CANL"}, text="right",
           props={"Footprint": "Connector_JST:JST_GH_SM02B-GHS-TB_1x02-1MP_P1.25mm_Horizontal", "LCSC": "C225125",
                  "Note": "A1257WR-S-2P (GH compatible). 1=CANH 2=CANL"})
s.wire(UC["7"], JC["1"])
yH = UC["7"][1]
x1, xt, x2 = UC["6"][0] + 5.08, UC["6"][0] + 12.7, JC["2"][0] - 5.08
s.wire(UC["6"], (x1, UC["6"][1]), (x1, yH + 7.62), (x2, yH + 7.62), (x2, JC["2"][1]), JC["2"])
Rt = s.add(R, xt, yH + 3.81, "120R DNP", {"1": "CANH", "2": "CANL"}, props={"Footprint": R06, "DNP": True})

# ================= referee UART + LEDs
ux, uy = 30, 170
s.frame(15, 152, 140, 40, "Referee UART (3.3 V TTL)")
for i, (lab, net, pin) in enumerate((("UART_TX", "REF_TX", "1"), ("UART_RX", "REF_RX", "2"))):
    y = uy + i * 10.16
    rr = s.add(R, ux + 25.4, y, "100R", {"1": lab, "2": net}, rot=90, text="above", props={"Footprint": R06})
    s.wire(rr[1], (ux + 12.7, y))
    s.label(lab, (ux + 12.7, y), "L")
JU = s.add(CON3, ux + 55.88, uy + 2.54, "Referee (GH 1.25 3p)", {"1": "REF_TX", "2": "REF_RX", "3": "GND"}, text="right",
           props={"Footprint": "Connector_JST:JST_GH_SM03B-GHS-TB_1x03-1MP_P1.25mm_Horizontal", "LCSC": "C225126"})
r1 = s.parts[-3]
r2 = s.parts[-2]
s.wire(r1[2], (JU["1"][0] - 7.62, r1[2][1]), (JU["1"][0] - 7.62, JU["1"][1]), JU["1"])
s.wire(r2[2], (JU["2"][0] - 5.08, r2[2][1]), (JU["2"][0] - 5.08, JU["2"][1]), JU["2"])
s.wire(JU["3"], (JU["3"][0] - 2.54, JU["3"][1]), (JU["3"][0] - 2.54, JU["3"][1] + 5.08))
gnd((JU["3"][0] - 2.54, JU["3"][1] + 5.08))

s.frame(15, 197, 140, 30, "Status LEDs")
for i, (lab, val) in enumerate((("LED1", "green"), ("LED2", "red"))):
    x0 = 30 + i * 60
    rr = s.add(R, x0 + 15.24, 207.01, "1k", {"1": lab, "2": f"{lab}_A"}, rot=90, text="above", props={"Footprint": R06})
    s.wire(rr[1], (x0 + 5.08, 207.01))
    s.label(lab, (x0 + 5.08, 207.01), "L")
    dd = s.add(LED, x0 + 30.48, 207.01, val, {"1": "GND", "2": f"{lab}_A"}, rot=180, text="above",
               props={"Footprint": "LED_SMD:LED_0603_1608Metric"})
    s.wire(rr[2], dd[2])
    s.wire(dd[1], (dd[1][0] + 2.54, 207.01), (dd[1][0] + 2.54, 212.09))
    gnd((dd[1][0] + 2.54, 212.09))

s.write(sys.argv[1])
print("wrote", sys.argv[1], len(s.bom))
