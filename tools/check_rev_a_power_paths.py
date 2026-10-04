"""Native connectivity checks for every converter power trunk (not its branches)."""
import argparse,json
import pcbnew as p
from build_rev_a_pcb import ROOT
CHECKS={
 'BUS_LINK_IN':[('J24','1'),('R33','1')],
 'CAP_LINK_IN':[('J33','1'),('R34','1')],
 'BUS_LINK':[('R33','4'),('Q12','3')]+[(f'C{i}','1') for i in range(1,9)],
 'CAP_LINK':[('R34','4'),('Q14','3')]+[(f'C{i}','1') for i in range(9,17)],
 'SW_NODE_A':[('Q12','1'),('Q13','3'),('R35','1')],
 'SW_NODE_B':[('Q14','1'),('Q15','3'),('L1','2')],
 'IL_TO_L':[('R35','4'),('L1','1')],
}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('board');ap.add_argument('--result');a=ap.parse_args()
 b=p.LoadBoard(str(ROOT/a.board));b.BuildConnectivity();c=b.GetConnectivity()
 pads={(f.GetReference(),x.GetNumber()):x for f in b.GetFootprints() for x in f.Pads()}
 result=[]
 for net,required in CHECKS.items():
  anchor=pads[required[0]];assert anchor.GetNetname()==net
  linked={x.m_Uuid.AsString() for x in c.GetConnectedItems(anchor)}|{anchor.m_Uuid.AsString()}
  targets=[x for f in b.GetFootprints() for x in f.Pads() if (f.GetReference(),x.GetNumber()) in required]
  missing=[(x.GetParentFootprint().GetReference(),x.GetNumber()) for x in targets if x.m_Uuid.AsString() not in linked]
  assert not missing,(net,missing)
  result.append({'net':net,'required_pads':len(targets),'passed':True})
 if a.result:(ROOT/a.result).write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
 print('PASS:',len(result),'physical power-trunk connectivity groups; signal branches require full-board DRC')
if __name__=='__main__':main()
