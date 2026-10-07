/* Local deterministic grid path search; native KiCad DRC remains authoritative. */
import java.io.*;
import java.util.*;
public class RevAGridSearch {
  static final int NX=Integer.getInteger("grid.nx",3201),NY=Integer.getInteger("grid.ny",2401),N=NX*NY;
  static byte[][] raw={new byte[N*2],new byte[N*2],new byte[N*2],new byte[N*2],new byte[N*2],new byte[N*2]};
  static float[] cost=new float[N*3];
  static int[] seen=new int[N*3],prev=new int[N*3];
  static int generation=0,net;
  static boolean free(int layer,int x,int y) {
    if(x<0||x>=NX||y<0||y>=NY)return false;
    int i=(y*NX+x)*2;int v=(raw[layer][i]&255)|((raw[layer][i+1]&255)<<8);
    return v==0||v==net;
  }
  static float h(int x,int y,int ex,int ey) {
    int dx=Math.abs(x-ex),dy=Math.abs(y-ey);
    return (float)(Math.max(dx,dy)+0.41421356237*Math.min(dx,dy));
  }
  static class Node implements Comparable<Node> {
    int i;float g,f;Node(int i,float g,float f){this.i=i;this.g=g;this.f=f;}
    public int compareTo(Node q){return Float.compare(f,q.f);}
  }
  public static void main(String[] args)throws Exception {
    DataInputStream in=new DataInputStream(new BufferedInputStream(System.in));
    DataOutputStream out=new DataOutputStream(new BufferedOutputStream(System.out));
    while(true){
      try{net=in.readInt();}catch(EOFException e){return;}
      int sx=in.readInt(),sy=in.readInt(),ex=in.readInt(),ey=in.readInt(),limit=in.readInt();
      int startMask=in.readInt(),endMask=in.readInt();
      for(byte[] image:raw)in.readFully(image);generation++;
      int end=ey*NX+ex,start=sy*NX+sx,visited=0;boolean found=false;
      PriorityQueue<Node> queue=new PriorityQueue<>();
      for(int layer=0;layer<3;layer++)if((startMask&(1<<layer))!=0&&free(layer,sx,sy)&& (((endMask&1)!=0&&free(0,ex,ey))||((endMask&2)!=0&&free(1,ex,ey))||((endMask&4)!=0&&free(2,ex,ey)))){int i=start+layer*N;queue.add(new Node(i,0,2.5f*h(sx,sy,ex,ey)));seen[i]=generation;cost[i]=0;prev[i]=-1;}
      while(!queue.isEmpty()){
        Node q=queue.poll();if(q.g>cost[q.i]+.0001)continue;
        if(q.i%N==end&&(endMask&(1<<(q.i/N)))!=0){end=q.i;found=true;break;}
        if(++visited>limit)break;
        int layer=q.i/N,pos=q.i%N,x=pos%NX,y=pos/NX;
        if(free(3,x,y))for(int other=0;other<3;other++)if(other!=layer&&free(other,x,y)){
          int i=pos+other*N;float g=q.g+20;
          if(seen[i]!=generation||g<cost[i]-.0001){seen[i]=generation;cost[i]=g;prev[i]=q.i;queue.add(new Node(i,g,g+2.5f*h(x,y,ex,ey)));}
        }
        for(int dx=-1;dx<=1;dx++)for(int dy=-1;dy<=1;dy++){
          if(dx==0&&dy==0)continue;int xx=x+dx,yy=y+dy;
          if(!free(layer,xx,yy)||(dx!=0&&dy!=0&&(!free(layer,xx,y)||!free(layer,x,yy))))continue;
          int i=yy*NX+xx+layer*N;float g=q.g+(dx!=0&&dy!=0?1.41421356237f:1f);
          if(layer<2){int at=(yy*NX+xx)*2,v=(raw[4+layer][at]&255)|((raw[4+layer][at+1]&255)<<8);if(v!=0&&v!=net)g+=20;}
          if(seen[i]==generation&&g>=cost[i]-.0001)continue;
          seen[i]=generation;cost[i]=g;prev[i]=q.i;queue.add(new Node(i,g,g+2.5f*h(xx,yy,ex,ey)));
        }
      }
      if(!found){out.writeInt(0);System.err.println("Grid search blocked net="+net+" nodes="+visited+" from="+sx+","+sy+" to="+ex+","+ey);}
      else{
        ArrayList<Integer> path=new ArrayList<>();int i=end;
        while(i!=-1){path.add(i);i=prev[i];}
        out.writeInt(path.size());for(int k=path.size()-1;k>=0;k--)out.writeInt(path.get(k));
      }
      out.flush();
    }
  }
}
