"""
Update Sredictio.py

Created on 2019-12-21
Updated on 2019-12-22

Copyright Ryan Kan 2019

Description: A program which obtains the latest RELEASE and updates Sredictio.
"""

# IMPORTS
import os
import base64
import re
import zipfile
from shutil import copy, copytree, rmtree


# FUNCTIONS
def hd82bch8(u9183dco, k83tcg72):
    ac82nc7g = bytes(u9183dco, "UTF-8")

    for p927cp2e in range(k83tcg72)[::-1]:
        ac82nc7g = base64.b64decode(ac82nc7g) if p927cp2e % 2 == 1 else base64.b85decode(ac82nc7g)

    return str(ac82nc7g, "UTF-8")


# CODE
# Get web page contents
request = None
downloadRequest = None
latestVersionInfo = None

access = """QEW|YSTb5pV{3RYVMakXQ)yW@R5EB%N^LPzSy)<aWNd42QbtBMRzylqWo%?pT4`%FVliiNQZP<WR76TgO=?<eO*2YQP*+MaSy)0
^Rxog7STH$GV{TSVPE~j_PgY7aQ&&ncP;PK(WmIfyVlqj3N<>y#RC#kZS$cS3N=I2}QdUB3VQE@2QZQ(
5Nmw;fQBzh?Vryq`WH44%Q%6QsRBlRHQ%7rTPcceZOIBofRC#o8Q8HFkWK&KuP*+A+S5#UtO)*wSVQE%rW^PJNP;6vJReDM=QEEyyRc$d=RaJ0GN
=0aCQ$;a(Q!`3SOKEIUT1QrBW<_X3QCLEGQEo+TVlreyWL7yxQASxfVns?%RYzJ&NiZ>5OKe7NN<~(
2WNLU+RBdZGP%=4JSZy&YWmZ9SRaAFqS8YvdOjt2aWJXypO;=K8STRL<SyNU}Pe*i8OKveoS~6BpPHtH%Su<>FN>*A(Q8PkAT2*vfT30l8RYy{
BWNc1WWinYfT1QSfVO3FjR7Oo~T2@wCT2*XDQ87VpOIB7#Qb<8EP*-ScV^%_SV{Bw~Wmr-(S5$ayR#bRWOL=o~O+`{
qW<_XWQ&&<!RY-7QT0~hiPB3dVT6u6*RYh85N?1lxN^3AUN=HdBSZ!!`SyN7HS!`@oPF6HCQ!zzqO)zYDR%|qRVQz3zQEqTiWNUahPBUalQ$sL!Pe?{
lQ$<BLVrw-_NmE%kQZQ^XVli52NmorYWo<=oQfpOfRYNgUP<lpaS8O;iV@6tKR#j(
fQ*Kc?Ojt@;QZh~}VMa-6Pg71SRWoZbWol$pWK&IQOjk~3S!qT~QbllgVKQt~PDfHzQ7}$YW@%_gQ8O?rVMaz#OE6A0Sw&=QRWmg+RaH
@HWqNp1Ni$MROjUF+RBJIoS7~Q&W@>azRWVLZW=275O)_UPT1G}PPF6-rSyy9vOE6M*V?{
!BR8=`tRxnahS4KHaN^C)KS}=4`Q&&-NRaZ)3N>xfiVlh@xWk_r?RYO&JNij86V=!7~PDfIDQB*-_Q&&z}Ni#-GV{UA5OKe4LT2*UmSus*?OL}-$Vl!(
vPewv%VMa-9R#!P_SZXm+VMT0tPe(>!SZOh9R7EvXS6DSvSyO0ORWLP7PenOQReEGAQ!z?uPFGTCO>1yfSTII4T17caW@=7ER!C%KV^%_IOEPFPT3A9
@WNvg?Q$#sLRWNTgQ$uiZS64}BT4``mOG9iyVK8JzQdMs?RzyiKQAJ8rR#r4@Wov9&W@=J4RYOs5Vn|L{R77lcQZRToR7h(
tS4VGfRBJIyW=2L@T2@ADT17#3R8}=eWNB<nRz-7qQ$=TOQ%71&Sy*E^W=2v`N@+1}Q!#9AO+;06Q)x~xV^eTdO;l%WO-DvyS5!tdRYNgUVn#JYRa7}EP
-|l~Wm864RWVUHRY)~hV^mU5WiduYRakIoQ*LW{N@;LfVN_0UPE|@VSb20qQ$%c2OGRu_Qb%txWNdG2N>x#DRBLZ-V=`7rOKNCvPcU;aWK(
EqRaa<AWJhFBPkCB+R#ruFS8GalR8~rHV@Fa%O)^SERWU_sQdL1~QZi$DQZq3~S~6BnN>@r%VpvUdT0~A-WK&X9O)*(
FWkqi>Rxw&dS5$OpR#j3?W<y#yP*zq|V{LdgRYOv5VpC{gS$R!2O-4>RVQp|!Re42dP**iVWoc-1NmfQ{T2^Z{
RBALZWidinR7GfcV@7K@R5DpBRBACoQ$|)&Nme;CWou4SWH4GrR8%=;Q&o6MRx?g|WifCzT39hjRccm7Nij-CPcdjWS5-=8N^N9MS7~QCS$alEOL
=U0Rct|PT5B~^R7i9&P%%nUOKehhP*r$mRYyiLRcd5*Sy)z5N^Mq0OjR{
=OEYkKR7O%qQb<ZmS4BotRWN63Sw%ueRaZrNVR=SZRBJeTRxwd`Vn;$nSyxI(
S6DSlPBKnmVMazaQ)*~cRYPz_S4cuuSwuo+Vnt_gWJhRBQde|&PB3gyT5EK9T2@hcR&G*uRBAXmT2oF@QdDzlSyxGTSw>QMRYO&JT1Z+~SZX<SSw
=-`VKHPyT2*v8PE<xiWivufT1G-_Vs30tS4C)3RBlp5Vnb3vPey2UVKP}cQ$$&8W<)VkNqSO8QZZIjQfxU-Qdcx|VMbC-O?pZ*WiewfWHCuJRaZ((
Qde4NNiZ=^PF841S8h&gS!!r;W=2Y3Q88<5O))`mQ!{6GQbsjwWm8gEOEE%4Wim!=RYPlRR%&=?Rctv@PHb#WPHjarRYgT>QZQCXV{
TGYWmI@oWK~KwV^lC|RYPZQQfgL5OjtE_W>#-+N^MaqQCMefPgY84WNLIqVQfigP-#UoRcTE$RYy5&VR>vxS5;DVR#!<eR4{
CESut!<NicYFPgZbiS4LVlRzy-}OKMU}WHCi-Rz_q@W@%b=RYOu`O+-0JQd4wBR4{l>R!CY}RYzlTP)IdYPBKnJRcuCUT1ZM!RWocxS5|09QF>NQR%}{
KVMA7WQ7}0$V{AfHPDoZcR%}{!WmiRVRC+KlQZZ6%O-OTcR7GQNNi%OWRYgv3STSg8RaRtBW>!{
DWLQdURc%doOEXegP)IRsQdUN2PDW^PR#;6lO)_|CNqS^PQ!z$IP-{YRS5;(DOH@`;PBKw4S5`u8W>{x>R#sM7Qbc4(S!q^gP-`(
%R4__cRYz=bOKEUdSZq~lQ!!RCNiuXRRxvqiPB2DHR(eKiVr)rjQ*2T<R984JWNc(
nQfzE;VQfZ2WkxkvQEqrlV@POHPHtpbO-D*KPHbdwRWnj-O-MpoQ$t#2S}|5mRBd=cRaR_5T3BpsRC;7sVpUdgN@;U<Q&d`aQ!{
i;Ra9tjN>)WOQAb)<Su-_iP*qxCN<(OHVO4ZmQEqrEQ))snW>->EN?0*BV=-%ROGQa)Q*A{
!WHWG4T3BOxRYhktQ*J^vRc>%lPe)EnW@}?IQ8GnpT18S&QZi0LO>KBWN=RfkW^6`9VQNxERcdH+WK%IuSbA(
LW@}?NW>ZdhReDu3WK~vDSygy8R!2@UO=&T4R8~$!P%&szT2^F5VlqW<PeW`+Raa6oQC3P+PFP8JRBJVJQ$#gGT2@9$PFHAXS64<WPHasuS$RfiRYPn
!OjK-4WJg+5WHCxLOjBq?RxopUS}{sePHu2bWmRKwT5dsTRBlCUWmPd!S~4*?WJOA5WH3r?RcUB+V{TSNRcb{
vOKfCLQAjaVR%&=@R#rkpSTbZbRYpcyQCDbmQ*LW`WO{T&QAas!W=29nRYh5AS66c}O)_{
=T1QfNSTIgEVN^LsRx)feQbajnQb$#7OGaaKO)zsWRcTsbO>1~*WkfM;RaIncP*zfQR8&GpPBUavPe^2FOKd_(VKFpnReDx>RYq)SWNvhHRaRs{
QF>WwRx)&VVKGioOG9WfW^8b3V|h(5Q&mPoOGS81R#Rw7R#k90R8)9qRaZttOEOkkQdU-PQf);vSZhIOSut5`R(VcJPE%PhVQfZeRaj(
7RcdH4WkqmSR8=*4WmQsnV{B}4Q$%b`QdK!rPE=?!S}|*IW^GDCR#-|)R5Ex@W>iW;VK7-aO=?vyRa0;{
Rcl&IO>RzjOGZLPQbsjbS8GW%Q$#UqR#bOuS}{gwQF(82S#E4_R%<avVQWrlRBT#hT2(
b#R%>);N=QmlNik?fS8I5BPDfHkRaH_-R75dWRWeRlN>@^OQdny@RaR_5T3B#MQd359Vnt|SPDo@(
Rc>c`QB_7sOEEP~Wo$`pS88Z=QZQChWHU8OWK}tEWJY9mVQy$;QfhQbR&HofT5MKCP;6vOT0>e;SyWO&NmWv5S64W3WL0NuW^OTQRYy{
BNibGZSyn|kO)zY1Q*AkKQblWYP*yckSyOONQEWvrS4KitS5;a=R9Hq~QEqr?NmWW(PgYfQQ&enPRx)r?N^5I*QEW{
yWok4rQ$t!eP)AlsT18SdW>r#VP;OFiRYPcXS~EsjOjklrS}=2YO;$NDRYyukVMkI=VOLIRR7OE?O-MCZRWoaPRe4%iRBB0hP(@^FS8jMnSu#O2T18S(
QfxVRP(@BtRzzeoS5sLzOGPniW@=GuT2^Z}VQOqpRaa6nOjJT)N@`j-Pccq5VKa1fSu<5PPkB;dQbSfoQbtNPRC;J_S5t6FVrx!RR&7x;R4`I@Q
&%xkQZi^%Vpcg(QfxUeN>wpWVn<e3Qbaj3PenpfQdU`OWkqLgSx8oHReDZHNmOK5Q!!33Pe(
>WQA161S$a}>S5#z9R5C_PW^6@oPI*>XRBd;3PccebPcw6IW>-xxW<^d@Qh8Q4T1HM%Wo%JzN^Me7VlZrLQ!`FdT5DEXQ&@9qVpeELVQx}oRZ~t
*PggZWWiv`ES}{U#QfqT^R#kX%V`_LsRck>qRxw6zO+`jBQ!!C(PeW2kS#EH4Q$;j%Q&cfhRBJU-PHZ(
&NitSAO)z*;Vl#I+SyfFrVN+~EWk)bKVlZblQ!rLnRa9qkVK7!{S4C(}VQg!0RWW2nR%>r-S4A~cN=8aKVpc{(
T3A_eQbjm1Q%7u8W>sr5SZz*PO;=V)Q$%QXRC-!cOL{
^`SusXxQA2MuQbs~6S!r-#S};~?T5C0PQ$|TRRccm6N^U|#Wim=?VpeQ#Qf)zORYhboReDlGRajD5Q$|WQRBdoWRxosGV?$b0S#5JOWJOX@N
>)ZrQ$uuRP(xBuT1QfLR!3G)QZZ6XR4{BzO;kBhVN+`{Vrxw>PDD{ORa9D8RYgi^R(
g19STROgVn=jsRa9D7QEEb3Q$;i~QbtK?QB_trRaHuPWJpF-WkhIKV=!klVpwE)RxoTiWms@hNibGtPcV3TQdM+#Q)*IEQCL!HO>RnWS8Qi5RaRO
<ReDu5P%=tVQENGQV{15YPHSU0Ra0;?O;}PxV=zKYRBT3UN=0loS5;PQSygOKQAAEqN^E3KWHU4|Q&d%JWinDzPE<~2RWNHbV{
T|uQ!`FUVN^;=Q8Q;VP;6{TRBL!fRYNgUVQWTEPcc?XN>*e+S!yvvR7fx~V`@@RQ&ekhRz^)TW>Zd3R#-`FSyWbRRYgiSV^>aQW^P$=Q)*6ERYz=6S5
<IWRaHtdWHU}~R#;YgV{0)<T52#WWkyYCS8GaFRYNgyNitGcR77lWS}|-xWmIfxT30njQf^vHRWnvYSusX#W=Kv?RYzKLQ)+ZfS65PXVKPotV^>NmR97
)mP%$}CVOMlCP*qA*STSdDQ&wbYV@GIMVQWP=Q!r;VRx?d9RYOv2S8i-pWiez$PBKn;V=ziuRxo5ySu!<6WJgXkSZql#O))uXRC;r4Vr^DaQF%sGOGR
%oT2yFDQfV<&Su$2qS~GZhPclk1VOCmCRa0wmR!DS0Nik?aVpeQ#QfX{7RaR_EReCi{
W^QbFPBCa}STROnQbjauS5$aMPcS%bQEWnKV^?%SQEoJCV?=aWOjki|VQX10QEoJAR7W*AR#j+GOGh<vSw&-UQ8GDKQ&w+xQhH=;VrzGJP;6RFPE
<m7RYNgCRckp;V@OUxOGa9FNia%6Su<#FVnb3%PBU;gWky19VQph@Sus{dN<~s>Ni%RUT2)qdVr^(
`R&GjnN<?T<OKvetP*+B1R%%*iQ!_PDV|g)8Q$tlZWiWJlRaaIyRYO`gR76H<R!B;6WJPpRVpdXZQblk<T3C2#Nmx;LPBB4nQ!!F&S#E54R#Y`fQbbx%R
!2rNW>{k|S7~oCS4d=1Qb%lQWNR@`T1Hk!R4`~pRBUWfVMkI$WNcA+Rx?I%RaR(aPDENvR!B{
9WH3@WQZjdHQBy@YSx8D~PH9?BPHaVTS8GZ~S!`r<V^&&CSw&<`WifC?T3A_XR7f#)W@|B0WoklLS4T=UQZO(#T1Z(pR8(|mNitP3V{
2?$W@<`pRYz5DOjtrtQ$;a%Q*BOAWoklaRclQ$Q&?n8V^?@|Vr)$`V@6dgSyX6kO+{o>S4Ub_Ojk-+VKHxOR%&>3Pep7}S!;AiNij)kQ&ePYQ*A~#WO{
g5VMRG^RBU8)VOCOiRakIKWHU-wVnbFpS}|vEO+-aCQEXK(S}{
URRBUT8T2@A3OE54rR%<miPgqK5S!#1KP%v~<STRX>R8>MwWLHK~PHZ`DS65CeO?oj&RY!DdPF8GDVMk6hVrz7IRcl3YRcUB-OH@i}PFOK=S
~5y7QfYKISu<p5S~6@&PBU;?VKGKoSZY}}Q&w*`Q)@9+Rc=O1NitF~OGjvDQ886&T0>4!OEGY5RYf&(OL}xSS5;YfRBLcgVr)(
^WH4-5Q$}!4RYguvP*pirWinc4PB3&UWo}wQRYzlVP(?XVQ$<-ZT1G-?Vrg$NRWocyT6uI&Vn;<XQbkgES8GyhQ87wXQdewKPE<}>T1IScSuk)kR#Z7gV
@7CDOjS;DQdd!WS7|YBRYO)&Sx8D)Q!-I>OI0;aWLQ!$RBJSHP%uJGVtI6HRYpcdNmfE-Q)*UEVMaz_S!`NUQ)^OBN>)KQS8i}^S5{
V3PBS%fW@|JnS4Bd4RxoTzWo=eVPF7?#VK8HCW<_W-RYy&DS8I4uN@-e4T1Q1}Wk*^oQ*3Z_WimNKW>#oHO))}kRcbVFQ+i5hT30n|W^6_|WotNZW
>srwQh9SXS!;MwOEEbySw(PIV@PmKS!zmaN^VX?Rc>T*S!+&HQ&wYgRaZ(%NqR9(
SZZf&VK7cXRBS;xQ+ifuS6DGxQZZ~xSusXgQAIUWReDx<RB16tOIAWOS5<UpQENCeRYzn;SyWn7PE>4AW>#x)Pe@I1R#r-QR5CG9QdoFuV?}3dQ7}m}Rc
>%lQdc=vRcmNrS#3#ZWJ6hPSyxU_Qd3%LWJE<ZQ&vrSQd3TPRzylyVtP_jPeo2uO;t5VOjAZ^T0}~0QbTZ3Wok}tSygy?Qbbl%Q$t2HPgYV*V
>4QGVlqZTVOCl+RakF&T1R9}V=#0@V?|?fW<^?bRc>f=SwuoiW><7MO>9PMWHVVSQ87htWqE8#T5eiQVOLgqR%=2rSyO0HPDpf7S$axPSTa&lN
^VhbR7Of{QEW9@Su$u)RBT#IPH9?0Ra0;|Q&w6_WmH0WS4DI;VOM83Q$}z>Q&mz&OKwUsV@5@4Qdf9uS4C)1O+|D}O-N2fR7Ef=S$aY+QF>BHQEW
<5S4K5>OI1cSS4VR>T0}{0OIK)EQ!+F(S4T;BSw>@MReESgR5M0RO+-#IWmP$FRxwg#S$alPQ$tQ_S4d+sV{
Af1RY+rMQ87g;Pcu?ZWJgwJSuiwoSx8BAQh9SYRc?4vT1Z)PWNT<dQ%EpzR#h=rN^DM0VOKOOVlX*LT6#EfRYyv7N^C}2S~5;oP%=(
ZSyVzvReD-QP<b&(OL}-yQdU81O-M;-Q&ea+W>#=mOEGL}STHqmQCCW4R4{mYR5C_VQB*=TVK8(
uR5EBnR7OfORaIzfRaG=?N^4|nRcuZ~RZ~qcW^O`QVn|hLP)1HQQAkc~QEq2+Vro`OPghz|WNbliVpw=bS!z{
!Wo=SKR75pZQ!q_;Rz+iRT1ZAvQEpCCPE<~2WH59qPenOLS#E1+VR>*?R!4M2Vr*7VP;PfORYz=bOEOAKW^O`vW<_^+V>2;QQ)*UkRcdHaT5L^dSw=={
T1Z82Q*LZAS!zO7QA1X7Pe(;GOI2txS41>9P*!MCQb%-gSyo1BV`@@EQ!#8-S3_t>Q$=KYPHRRsWHU`QRYPn`T5UB%WqD09RBLcEWiUBsQ87
|=Pg8JBRBUWdVlhQ>O+{o`QZi&jR8%o&PHRmoWNcPeWo|-dRYg^5SZ#DsQ8I96WHM5DW@}P&T1G;7QCB%=NmFkzO;vbJV?%6bRYO&GV`?#3VOUB;O
)yGSO>0?fQEXOCRcd%lV{3SGVOB+IQdm}ZS!`o$S$b$qV|i#yS!_aWP)9j4Qh8N3Rc%^PN@+1{
O;<%UWk_goRc%IkQZQ&}S88N7V=#AkRcuLlRZ~t`Qddq?R(VcNQZRUSVOB;$Q&&c8R(
fnqPFOK@Wo%6}OEEQ0RYzknSy)O_PHl8yT1QcLWJGLOR&6y)WO_<dNmyi5R4`U_QF(
M&R%>@JOEP3lSZz5`SuizFQdC)aRYNgCRx>qOVOUOBWL8!<O)*w*Q*2f<O;>10OKn*<WNb}(
QfV<&SyM)3QdKoXSZYRcWH4xMOjlVqRYhcLO;>PINqSC7V^&IGN@`MBQ*JR(T1ZN2V^&gfVQXtLV^}b7Ra0;{
Rc&NfSZz*9Nmo*IW^77NT17E$N=Hs%QEEkOQdUAqVKYu?R5ELDQfh2cQfo?jWHE0wQ&d(
}R97`+R5LMBPBKk$QdM+SP**W9Q$}!hRc&xfSyX3jT5V2vR&GfvRYOs5Vn;PpRx)gFV?{
MhPFGQRR%$U}RWUhQVO36POEE=iO?o+3S4C)3RBU8SSx0zhWH4(
nNi%CVS41=`Qf_EcS!-`OVrz6OVOVr%S5;1PVpdK?W=BeHWHDN0N>w>@RYPlcR#R|VQdU-4QB`AWT0}y5R7XO1V@PO8QhHKqSyn-BP
%>I8S8GaBRabOaQZi_ERcmN(RBU5<Rx)&NR#iq)PgO#BS}<00R8(
wuQ)*;kQ!++MS6DG>WiUBPSus&}RaR>?V?|n7VQN}PSw?6`WK=XOS7};rWo}MZRBkYARz^l_N=0}uSyX6kVQNZCPg7DbN=0Z|NicX%RWnj6R7f#XNmou
`SyxUnVrp49Qbjp;Vn=jQQZiaKVK7>5WqL_$RYy^DWO`CoRaQ-LSw>_>S!^{!RzyK;O>AscPB2<>Syn}DT1Zw_SyM%FS!{
4kO;b`#R8~$lWK~W>QZPnWQ&wnFWoklFQZZUjWmiQxR9ARGO;uV`QE6I1WHCZXRaHh*ReET7Swn13VpLLDVpd9MVQfxUR%>`}O+__MR540MQ!znwVKPN
@ReDx&Qf@IzRc>T=VMQ@GRB3Q+R8?~?VnuLLNia@CVO2GBVlr!QQfYH=W^QOxN?1)VWL8=@Q$#goRaH`PWo%AQP;6Q&V^wD~OIA`aS#C99VpwcVRa9s
+Ojbr~T1P@fR5EaKQAk#6V{1}HSut5TS5#<lS66UJSynkxS5<E~WmPdxOGRgKRcu;FWJEb^O-40WO)z9iOGi#HRYyv9V^eTUO>IVYT17c@Pg8JrT2(
Z7R5ENuV@5f3S4K)UR4`U*Q8RQ?T19kIT0=%iN>^5MReDKlQCL<*N<=YHOjb@xQf*3DN^4|sRYyf?OIT7vWiv%JT5D`YRe5YgRaZ(
<WHL%ePcm#yWim->STbx{RBJGLS!_l~OKmwdSw==-OjS;1Q!`pnS}`?NR7Y<$QbjZ`W^8OmR8=u<WNbB2OI37KN^3E9VOUx#QF>BOOGPzHPgr*|P)2ZQV
`)xxRaaJVQ8QXjR53|#V?{V|VpK{vS$bAwS4A~MRe5Z1VOB+QRYi0+ReDx&QZZITRWM3RR4_0&WmYsfR#rxHRc$#^S7}XXOI1cSR5Ma(
Sus*)T2^FGVryC}R%=#qQEfDEReDk~RaG%XRBAC{QddQ6Wk^~!RYY?ySTjyxQF>W)QbtB$NmEWnRWWE;Sy)n0OGjCEPB3&*P;G2eQ7}S9Q!-9bOjmGIVr
)@)QAl(!RYg`*Swm=3PgFueO;u<|RaQz(Ra10XP((sPWmIQzRxofiSus^=T1HN0S7}C2VQNZGQfx(PT2?hTR#!qfVpC2_W>z$9PF6-kVlz%qQ886GQ&((
LPE~kOVQXY=Q7}?@R5DgdWJN-1WLIc3PHS^9Vn=gwRYNgxV^w%WRcdEAQ!-L`OEY*gT2*v8Sw>E3S4d+sW>!LJV^~2eQ8RQ(
O>S&aVQe)uS!`NQOE7mdR&GggPI)m?NmMmqPDM3zPDe&gRYy`%R7G@7Q*CfgV=+Q(
T3Aj)RaH)GWNtM`QdVqLQ7}q3QA1}rRYzJ%P;F#bR9HeYOKd`HVlqZWRC;t%RC-QDR7Px8V^>9NQdD#@R8@E|WJO9;O*2YMQCC)WP)KYyR7hHDO
*3p$Ni$MbRx(a{R4`I_Raa7LVnj|)Q!`CBRWVv+QEoJ9R8=u%S4TBfPE=8OO>9XqR(e4-RaHtgRaQz%O>Ap<Q)@L$PeX8bQdewcOEWQ2S5<I1PHa{
;PFQzpSui;@P)K-bS5s_CS}|5nP;N0(RYOuiQbaXsWNJ=qWiUoHNmpxZT1HM#OKogeVMk<nP;5qNQ*2UjRcdH*WimNzVnb3lPghb_NikV(
Q87YyRz+4)Pg86;VpVf_S!q%<Q7}1kR%%vkRYXd3S5-<iP&0T|RaS3wQf)?8RBmi&T2^dHP%v6@R%}8zRWn9tPI*#EV@5@4S4Bp7R#<d)QAA2qRx
?R2VliiOT1IF@S5;(DOG9u{S!_vqSukX7QEf3qSu;{OV^lR*Q$<d5S}|}!QEE6aRYyvAV@PakV=`|qRWVj8Vl#JgS!{
1NV^nBGV=-rNWNb!7VK8`CR%<y#Wk@wtS8HT#SZi5vW<+RhQCM&_WJqvQQB`zCPDO7qV?|ClRcux{
R#Y`kO+`65V^uLyQEGU0RaH@FRzyxvQ&mPuQ889QW>-0FR9ARxSuku@V|iM4W^6`6RcTI6S65?qQfyjMPHZ(
rVntF>T30kPQ!`C7N^C+=OGh+uV=`8DNisD<S66F#T10qkR8%=QS8Fk5Qbl-GReDi5Ra0nGPHIweR#j4ZVlpu|Q87U`Su<=yRajD5Vn$6cWO
`#YRWoaPVOUN}Rx@WWPDXHSP%<$yR&Gi(OjbftQ8HFFP-{+7WNBJKQ+iT$N@`A6Q&d56SZr2KR5MOcRYPn{
RYOK<Rzq}DOGRUHW<@zgQEqQ&VMkI|WiWVgVKGKRQ*AjxRa06{QB^r;N>o)fP*+JYN>yYyR8~bfRYy5eQb%wzR%>{
AQdL%TQ86@lV^e5TQEgIfVQXY>S8X{&RYhoWPFQSeW@=G*QfqKHV>2~#SusXwO=~q;N<>0<NmfN_PDe&GT2(nlVQy$tWO-UkRYqh%O>As(
Q&ebjOKogZPDpcVS#3sPQAlSmT1PP}SyxI{VtO%fVrwufN=Rf@RYNgxV^wfdNibwVRxor_Wk^OhS8G;EW@%PLW<zUiOGZI#O=)yTQZQC`Q&llVSw
=>3RYyu%R7XKFRe45ePBL^+OI2$tVlqWEV`@=(RWWd9QCKljQF>J}Rxwd}ReC~ARakF&QbbZ{Nij}AP)1ELRakg5QbsjyW>{
oUPccqyOEF1nVr_RdQdcoTVQN}JWmjxcOjc}3R8>xPQEX0VOjJ2iQb%x9QfyjxSu<>SQ%6>AS4CE8R#sM5SZzu$PBKP0Rc>!FRzopRQ$uu4O)zUTNi$
<?RCzFOVpm32W<_UhWJXCbR6}%GR#;9?P%$}9O-4pmOKWgiQfX3FRx)dBVn{
+#T32vHV@F9bQCKl`Q%6=%QF=LAQC4tjSye@AVn%RwReET5SywS^VtFxXRWL>}Q&mN6S7}ypQ+Y8?Vr@cdSyn=AQ!+SsR5ENcNqRX`N^ERrW<_f?S65
>+T0~A$V{BScQ8H{RVpd5tPgZAaR9I4NQfp{
MP*iI%S}<!hS66FoRYh87O-E8wNij}qPe)OAQ))_OSy*U!O?pm4Sb1nsQAS2ZNmfyJRaa4YVQNxTWNTVRQC4JhVN`TNSypgmQ)+lrO)xo0Nmoi(
N=Hs%Q)*{$Q*JR-S8Z!-VQWe@V^lFvRa0{~O;l_{W^GPpVMc61Rcl5^Rc%ITO+|EAVtP$5O;$y6S8Ga0R5EOLRaQb)V^vabT5B<SP(
?~GQ$%b_Qd4YEOjb^DNilG1R5E91T3A9gVpTOzR7ZGKVr)$@Pgi6(RaZ(
%WNl7RPccqXV=+cySx7=yT2?`NWK%IqW=CvGO>9PNVQW%NT1a$NQ$;yiVQXwmSw(nNVtFudQ+iHXS4B!xPBSriSw~JXQE662Q!{
u*PDFHJQdMY0Q*1_WV=z)URakF&S!+^GRBl>mQbjRLR%u2?RYh!2W^8a+VN+;JS}{dxT0>HFS4V4VRz^l@WNR^RVQg?=Q+ZJ^R%>%{N@_|{
QbST`Q&mz=V{K$=QEpi;P;D_&S$cPBW<@kBQdKofRYgvCSy)<3W^7|GPccz>T5C;gQ$<cmWL0ogPE<KbVMa!8O+-?3S8YytSZz{
LN<&g`QZO+=N@_JRR984JQ!qJFWo%J$RaI<gR(g1JS$bMBSw~J!PcS)XOjJ%yWqN09Q&d$sPDnLST5VZ$QEWvuP&0IMR4{O1VK7QjOH_DpW^G9^QEN(
6R8~rQR#r|?P)1H>RckSIRB3E#RWWc;Pe^cBP)B2WT2*XXWNv72R8=)JPBUyzQ%6O4S4C_@R7f>2S$bA)W><7-Rz+lQWmRZlWmr~sS$a`7OEW@QVOMZ)P
*zG<T4`1*R5EXQVn<R=RYz!1T2*XeNqRXsRB144N>oZsW@<1nS}|mHN=0xsSu-^>T1G-iN>^2MO-D*mPe?&CRx&hiQF>BXQ$#gYVr*JxWO*@gSye`8S
!zy7PE~YFWNTJOT0=%TQblVwVlr?@N^Lc3Vr*J@S~4|eS666xT2xADNibtKPgZP7S!+#tQ$s~@Q+ZNYVlh@wW<_*2VQon(
RBbVLOjcG?S8Q5tP)0#<OKo^^QZiXIR&G{QPHI|AW>-dGS};maSu<m7RB2LKVrxZhQ&wnAQEGQ`S7~Q2Q))^|PE%HGQC4VfRYXpAR&6m>S87^nR#Z|{
R90woWI;VW""".replace("\n", "")

exec(hd82bch8(access, len(open("Main.py", "r").read()) % 7))

# Load web page as a dictionary
latestVersion = latestVersionInfo["tag_name"]

# Get current version
with open("VERSION", "r") as f:
    currentVersion = f.read().strip()
    f.close()

# Check if current version is not the latest version
if currentVersion < latestVersion:
    print(f"A new version, {latestVersion}, is available. (Current Version: {currentVersion})")
    while True:
        print()
        print("Do you want to update the software?")
        response = input("[Y]es or [N]o? ")

        if response.upper() not in ["Y", "N"]:
            print(f'"{response}" is not a valid option. Please enter Y for Yes or N for No.')
            continue

        response = response.upper()
        break

    if response == "N":
        print("Quiting updater...")
        exit()
else:
    print("Latest version is installed. Quiting...")
    exit()

# If Yes, download latest version
print("Downloading latest version...")

open(f"Sredictio-{latestVersion}.zip", "wb").write(downloadRequest.content)
print("Done!")

# Extract contents of update package
print("Installing latest version...")

with zipfile.ZipFile(f"Sredictio-{latestVersion}.zip", "r") as zr:
    zr.extractall(".")
    zr.close()

# Check if Update Package was downloaded and extracted correctly
originalFiles = os.listdir(".")
updatePackage = None

for originalFile in originalFiles:
    if re.search(r"(Ryan-Kan-Sredictio)-.+", originalFile):
        updatePackage = originalFile
        break

if updatePackage is None:
    raise FileNotFoundError("Cannot find update package. Abort.")

# Replace current contents with update package's contents
updateFiles = os.listdir("./" + updatePackage)

for updateFile in updateFiles:
    fullFilePath = os.path.join("./" + updatePackage, updateFile)

    if os.path.isfile(fullFilePath):  # That means that the current package is a file
        print("Updated the file", "./" + updateFile)
        copy(fullFilePath, ".")

    elif os.path.isdir(fullFilePath):  # Is a folder
        print("Updated the directory", "./" + updateFile)
        try:
            rmtree("./" + updateFile)

        except FileNotFoundError:
            pass

        copytree(fullFilePath, "./" + updateFile)

# Remove update packages
os.remove(f"./Sredictio-{latestVersion}.zip")
rmtree("./" + updatePackage)
print("Done!")

# Update version number
open("VERSION", "w").write(latestVersion)
