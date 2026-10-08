# Prototype Rev A の使い方

現在はfirmwareコードとCADの段階です。実機commissioningは未実施です。通常buildはSAFE_MONITOR_ONLYで、PWM・ARM・接触器・dumpを動かせません。以下は将来の操作手順であり、現時点の通電許可ではありません。

## 装置の役割

robot busから9Sスーパーキャパシタへ充電し、必要時に蓄積energyをbusへ返します。bus/bank電圧、双方向電流、温度、個別cellと保護状態を監視します。40 W充電、80 W assist、120 W peakは設計要求であり実測保証ではありません。低電圧・高温・電流限界では要求より小さい出力になります。

## 接続と起動前確認

実PCBのconnector識別は`docs/interfaces.md`、`docs/pinout.md`とschematicを確認してください。robot bus、9S bankとcell taps、CAN、SWD、UART、外部接触器/補助電源/保護アセンブリ、service放電経路は別系統です。記憶した別基板のpin番号で配線しないでください。CAN終端とGND接続をbus構成に合わせます。外部保護アセンブリなしで安全性を仮定しないでください。

起動前にpolarity、bank/全cell電圧、tap順、fuse、接触器/抵抗配線、締結、残留energy、firmware modeとcommit/hashを確認します。PWM OFFでもbody diodeから電流が流れ得ます。接触器feedbackはreserved diagnosticであり、LOW/HIGHだけで開閉済みと判定しません。

## 初回commissioning

auxiliary only → MCU → BQ → sensors → CAN/UART → 無energyでhardware fault → low-energy precharge → low-energy converterの順です。詳細のPhase0–11を`firmware_commissioning.md`でPASSしてから進みます。最初から22 V、fullbank、120 Wを使いません。今回これらの実機操作は行っていません。

## 通常起動・充電・assist

将来のレビュー済み運用ではPOWER ON → BOOT_SAFE → MONITOR_INIT → SELF_TEST → DISARMEDです。robotから有効なARMを送ると両側PRECHARGE、ΔV確認、bypass/抵抗切替、READYとなります。SELF_TEST PASSだけでは自動ARMしません。

CHARGEはREADY/STANDBYから0..40 Wの入力power要求を送ります。cell2.45 V normal ceilingへ近づくと充電を絞ります。ASSISTはREADY/STANDBYから0..120 Wを要求し、80 W nominalとpeak予算・9.5 A software cap limit等に従います。方向を変える時はSTANDBYを経由します。120 Wは1 s/30 sの仮定予算で、実機検証前に使用できる保証値ではありません。

robotは新しいsequenceのSTATUS/keepaliveを100 ms以内の間隔で送り続けます。250 ms失効でgate OFFとfault latchになります。CAN commandの形式・ID・単位は`can_protocol.md`を実装の正とします。SAFE buildではARM要求は拒否されます。

## shutdownとfault

SHUTDOWN/DISARMはgateを止め、電流減衰を確認して接触器要求を落とします。OFFはbankを放電したことを意味しません。通信断、BQ loss、温度/NTC異常、hardware faultはFAULT_LATCHEDとなります。原因を調べ、除去し、冷却後にexplicit REARM → SELF_TEST → DISARMED → 新しいARMです。通信や電源が戻っただけでは復帰しません。BQ_FAILEDは自動再設定せず、修理/確認後の安全なresetが必要です。

UART2は115200/8N1で `status`, `sensors`, `cells`, `temps`, `faults`, `bq status`, `can status`, `version` を表示します。`gate on`等の生出力commandはありません。LED消灯は放電証拠ではありません。telemetryのstate/fault、ADC/BQ/calibration validityを確認し、未校正値を実測精度の値と解釈しません。SOEは電圧二乗に基づくenergy割合でbattery SOCではありません。

## serviceと残留energy

permanent bleed、switched dump、独立電圧表示を使える構成ですが、dumpはdefault未許可で、SERVICEと別のreviewed permissionが必要です。hardware/BQ UV等の保護で途中停止し得るため、dumpだけで完全放電を保証しません。必要時はレビュー済み外部service dischargeを使います。

独立meterで **bankと両local link <1 V、各cell電圧の絶対値 <0.5 V、残留energy <4 J** を確認し、**2分間reboundを観察**します。cell逆転も確認します。nominal容量ではなく最大容量/不均衡も考慮してください。OFF、LED消灯、MCU停止だけでは安全な放電済みと判断できません。放電時間と抵抗温度は未実測です。

firmware更新は`firmware_flash_setup.md`に従い、電源・bank・接触器を隔離したうえで人間レビューを経て行います。option-byteを自動変更するコードはありません。初回flashと初回通電は別々の承認事項です。
