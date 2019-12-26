"""
Update Sredictio.py

Created on 2019-12-21
Updated on 2019-12-26

Copyright Ryan Kan 2019

Description: A program which obtains the latest RELEASE and updates Sredictio.
"""

# IMPORTS
import base64
import os
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

access = "BQrK+Nlj%-HAq2rG(&APaZ+_zcWF3QctdM7YHw?9PeWQaQg&}aWO!9}Fl;qBRBumgH$!$#Z$UG8GH`ZtSVK2(G&VywbU0{XPDOH8P<26eT6tA8H92odV`NHKIWcm2b7g5Xb3;@)F*a{%SZPo+I8Qfo3L{5aWJYFjVo-NAOH4vmOIUU@H*82wPFhf7XHso2LTNR4RY7Y=W_fxucy&2hZ)8hVXhv#5XhU~vYB^$3PjymwM{`12XH7(6Rc}IhI8RPBW-@GRN>NH;GdE~(V>UTsVrNlUH&r!eLrp<LR#`Gka&a<9ObT^$H!@;FYGFMhQ#3JNO;1HOL2ph#Ei_G1S7k#rR&F~aC{r~gPcl+tB~>|3OICVpQz2h1J5pguG-6U?RAhBfWj{%7QAJKhdQe4tML<?^W@|rFbvt`~R$gv+a#S@kK4DfreR6wGJ9KhjQ!_w$N>@EXWPDI-LUle+L{@n!QD{edLQy7dZhBE9d`opxR8oF?S3V<eQB!?9K1fqIIBX<WX>MXYR&ZrwRZ=v2ZA4NxXe~@rG%+S)PenyhQ&2=iSR+w4ekNE>X?0mhQbKGpcTpsDXkJ!wcr7SUWq5sYQ(9?bQc^fQDSl9AM^+|QQEon2QDjY7GEQxIBqmQODr-|#JuP%9QCezALQpCpL1R=iLQ-;3W?48^R&ppnKvQ{dVS7<RU}8;BDspamQYC#kS5RdtR$oy?S8i8QBXe0$R5L+2c2an6NO)IXNM|chDtTI8Q&duWQ&(*{X+Tj!PBti0RAM!EP)IpqPf=P=D0Eg|FeyAzdU<SdS3NR0C{lPSRANynKv_#sMQ|`$QbIvtDN;Bnd{R?1L^ozqH&AO|Q#M90G*Ux5bS778D?4*gL}oKGR%~fnPEco9KvGgUNi;D~C_jE=R&G2*P*7)RT2WU%Au35yS5{R=P%14yOjI#9Q8rd`DsE>`J5V@lQ#4dPa#ucDMP65NPGfFRWp61aQdxO2BU5=;Hg!;Ccvo>zVm>oHP-jqUW>YmJPefBSJT_`kWJEu2PHk^UNl->NY*tP_Z+lTvdU`lbR(n)ac}{Ibb#YK7c5P@=HG4cWQaC^}R!(VjG)q%?cqS-UJ|itVP(^)Zd{HDNP+(FhRy}1?I7ewHP$*t<I97aVBu7&;L^dl=MK(V@QhF<ROjC7fdN@}~Mto*dGeCAGP)1QlL{T_7GdNdoCPy?>GI?+@Qa5KMB~y8CVlh)Ud{t*qB|T_FR54LgZ&NfxM_N-<NhWktRAD|zP$hRlXiqylR5?;NMRsvgH#dD@PCqePKv5xaUocZRM=32+BQtYQQ6X?(MNv36XeCcAL@IVqOK)>pQA0yYU{FL(R4Z0<F=!}IDsfF?S8pa$LQ*AtIZja}He+Z{MMXVlPiku_GE!M+eP&ZNBu`9JG)z2RR#9dxVoyFnb4yWXUovG<LTi3<Q+aS_a#J)idq`7MQdl%jURFU$Q#e{eF;X`-EiqFeU_e?|N@rMTP)JHXVo_#RJXBF6dnS2ML^V4xPHkpyVNfa|O<7ZQJw-KEPgP-7QAI_5D^DpZK|@wcT0B5gHa1CaS4cxzX;4KyKu%F)RatXTDM~XkQ#e{eC{SllT3Aw7WKd*MS59_WQdw~_IZ|O^G*3|`JwSC=N=G(gPeo5nVpnT<VLVebLn&uYK0s7@Pik~tHBv%VW-U%>VqiB?H&0YwQdxO*Zd5T*dT38-VrG0%D`7-WQe#tIbW}AnDo9X8d~!ffYEw94QejeGYf?CVQz}<JS|c@6G&6c%S4vnkHdA*dH8fH+MOaZ+NL4sgQ6V8JZB|WEM`KoAC{80%B|S2IR&qZrJWoeBKQvH6OLsg`CO&9+Qz0R5MNuX{dP`3`Bq32&Y+7z?PCZ9FcTzV`Mle$~J5PL8Kt)PHPf0RzRaQ?kEqzfTdumNlWJ76GQa5QqNKQRCVRBJgX<tWDS64+LR!w4IU{-u_WkyeGRB=8}JAP$sQD$gSdQoCLT0l@nNH!){Ybr@{Q+ZB&bW%AuS#DQMIagRvLPKIOS3YxfYFA!HEpJj|B_TXgCN_B{PCi~oeNsY9GI&=?a4=X>cyDiJQ6W2UNls~MHBeSSMnhLlJSH<JQ6_CsMo?ubGImllV19R3UN~WLPe?#^HB%vRRCrM(He+g5QCD(kP-js$V@`2WSaVW%ZCEH)O;JE3Q#M6OeOGN#X);eees48XG(=TAR&Z80R#GNNI6_e&b7NjmLPAq|Q#LhUZcjx<M^#c+O>j?FNKG^$R&riYWl}<9ct%n*Utd*GB}QO(P)KTRa#3VtazRr#M>|DNOLufRQz3CaYfe6QK4MZOB`P;lI5<~7R&y~mQddk-Z+ugAX)0h*K}%43QbI~fMN~9kGGk9kL2^-1LSANkQ6wa4G*dJ~C1X}@BT92oBs_0eP-ARXaZyEYK}%A2DR5C%U_f$0QD$&MZ&Wo+Jy}+6Bx+z%C46vMQ#4gzHcn|_W=&RmN_A>eeJx%)QCd+?X;N8cCS_AvQ9VmkF;Pb=S8ZBMRZ>DsV{TS(L|1E3CTuNmR53SWJy9VoYI9K}byjOuZemACPdz?;Mo}hgEoV?;Q*}X7CPyktPCP#*GEhZ6VtG<RRX8S7G-GvIQ+ZfPQc@*8DLqh0D|J9oK~!l}P$)oQGE;eGH&Rw~NGLZ_Au&F8Q+GZ>Gf_iJY*<n#WO86qVNqgoPfKM-T2@U{JX%p&S#)|+BSczPQ+a1FL04&Hbx2M=cOzF(Vr+P6QbQ|Rcv3Y*cwSOCemrbXMK?2MQ#3O@S5tL7AzoHLdpvbiHgY>rQ#Ct3Zc$`3Sxr)SZD&4GV{J}qQD#{<K~h&$e0Ek#QC2%sHFI7jP&+m%WKv;BR&7r$L@G>INHaifQe`w$c~gBYd}&j4Ycn!XNNOV`R5fL3R8b}-Y(h~fDRU@KD<m>DQ9)EoR!~G%NitM1NKGVDT4^|EPfJ!!QCCPaZ%0x%c6VM<cqVpUR(nBaV^1wKa3fPTHA8VyCO1!FR5B`9BvV>gd3;etHhD%-MNK?YS8slBWl}d!Kv_>mM<`WLMSg2_R!cZjYfvpbb1hPMc3~=0c~3A-RzOE4a8`RUHCk6pFhzD#c~@R0PHkstGE-VDbv9Fdd?{;AX=*KQQ#CtZHCA$YL?KdoUrtO<J~=}uP(ngCa#AHEWl&IKZZafMLqcYLP-SjIP*7__UNurVI9EqeMOaTxQbJ=)RaQ|>Y*AAoU_pITH-2(`Q+Gc%Qcga3G%ZmfAuB>wPgW&pQAJojJyKU~Rx?p%DL+Y8PfS%eRy}%kOHz7yPDM~_Of76uI6YuxS8I7gbx%xvPD4|9Wnef?X(dK{PHkpmDNtuoN@G?}R#Zz;B|LXkQe!?;WKt+*D^X8NS2jgbV<jVMQD#;=R9A6LIc`!yY%P0NOgU*LR5E#Oa#DD0Dmzz7Mp8RZJ0w0cQ&dW9bXIbAEpbsLH&%03Z)8j@P-A2>NmMc_Np4U^NM}7#S8roLQD!MacvB=}LugSrM?5`HWmhR*Qe{MSG)_Kwcr;dCZg@pjJt1OiS4>DMMp86;PH0wMC1fK|DqvVBQ+GZ=SWsnnJ4;e{Z*WyqFnu^sPF_Szd{Z@hXfjq$Gk#T4CN^y*Q7d6(b5t=mV^UIMbwgEGPHRO|QdwvrPf<Z*L|#*Mb1FwtIWS*rQCeDlB~o~8O=D4LIX5X(HB4t>S8I7{Yfw8zBVtoDL{@TAV{1}(R53S2Vp3OCd~{PZLLq!pG*(i2Q6^SsLsoopQejp-Utl3uJYGLdQ+0G>BTp-PJ~K~AR5eLfdqR9{PHlL2Wl|<dMKVxGNN9XlZzO$sS59O!HcnnwK5kMtKr?ewHbhftP-A3vRZv7uc}!7ec{xH-cqVjcR5m0xc~@y=S2RycRzxvSWmi!uQ+X;<X;*7_Yj#l~aeOpZY*~IeQ#eOLdr>BBYh+eWOnzBUOLk>*P()ZUbyIykG;>iVZDU4PK6^b?PeoaGG*3rTRA^ImYH(~)LQElMPHAC4Q&V{=MP5)XdoyTIC|+hwQe!1^N>D;oJU388O(tGeaAPP;P%S%UVpAb;b5vGSFf&F_Whqf_P-SjIOi@KnbW>7ec1UDbJwtnAQ7TL=WKd&lC_qqWaX3O!G<$4vQ#dvxNKYwVQz1`kV^C;UJwquxQz0QGc~T}vdr?<wXf{GuPGW3nS8Y*pd{ISMUQAC&KudB{Hb!AfP(njbaaU<>DM?c_F+Mz2Zah+ZP()TXcUMSEKu}L=bwq4YCMG<7Pd-5=W=?5zWhPfWGHQNQG+!Y*Q6_C-XH+#+K1fn{KzTz}O<`;?R!=izXj372SYlHld3Ik@eLG=JP(m?yX-_+2OG;9BCRtKfZCZIaR$go-Y*#%pbXih(KzJcjGeCJ`QX@PwNKqw5b1+kVe0?ZUW+`G%Q+0E8NmMg2Gc8hhKw2$MX=-0zQbQqiaZ@8iKx9xxMnEA^LMnY>PChAhSW-7eJ26paDM2$)WJFU+QDjwXEl?_YML1AGRCH5MDS9evQ7STXNmhJtd@WK!RaaS4I5v7mQ#XA=bWuS{I6PBzJR?O@I8j=5QDkH!EmAlpL{w2hOEF$kBw=YGPF_t!OHv^;RX<W;FgH(DZha$6P%3&;c~WC*WGYT+a(#AELP0?^P-9elXHqw4H9}K;dsRzLK4&dqQ*}Hza#u)1Kr~W9LTz|aVst`UQYJWHWm9=(HfdK%PD*D`Dl0fRP&+k0RZ%!nGIdjVW;T3KMLbJtR!>4ZY)>gFSz%EtYC$VfB|a%`R#8t=WlukFX+2jxGHPH}ZgVjsQYd6+PE&bKRen}ZUTr*6b#quGP)S~POj0;MVI)#QV=7fpEqiuuPHAE&OixQgJycRRW;=RUN;flFQh0YZJ6CT#Fkn`0Jxp0rV?Jg=P-jp?Bv(v1X-igedP+=JZD??0Q+aqaQdUhtHa$@!d}=~hX>Bb`Qa3h9F;OODC_PSXa3NPvWoAfOS8H%6SWshBNk391NPSXMI7TWdPF^!(GEXaeJtbChd31MCCU<T%R&H!$VNqIPLUvGRT2M1lWJ_;aQ6xMqXHZ0DEq+f+O*Vd4X=OD-PfJ8YKvFqKByCVAc~nDCC3bo<Q6)BSR8UB2Wi?V)Z&7$wJt{j=R!u=keo#U~YFbc6Mnxo3b#rEZR&y~aRaQVXKV(osOIUtTNNIR9Qg}Z$RZu7?J48@tNHJPgUMNmaS58z`SW!hqes)koLMS0oMm=>VQ9(*|c~U4>D0xw2Of*$cB_=R#R&aMhb5dDxL~2wqIZZiJc}`V5Q6_C6Mo&9_R%cRKaYQ>;NLET=QYC#$c}{J5N@`9%cs@i^cRp@zS6)XsUr}apX=YYEEiouob1`TrP%0}+OHOTOJv>t(U_C%qQC1--S3WB{eo|Lfc5hZaUsOd?A$oZ@Pf0N$B~M98LSauSd1X;hC_g(bQ6zO#P*-VpR&-HhWK(obX=^-EQ#LhWJ5pguHegq2R6A@=K6x}PQ6V8KLRL>!awt=IPDe^tPheqrR&pwLNKZ>{K}%LqO({Q8C4E>$S4vQDL{ULXOCeWlad~c6KqG!hQdxOmCRa{kAzDyEL2e;YK~qjlQ8#>dBT_X(Mk!G$F<((vZzM{2QYC#jK36?5Om<T>J5W(paBVVvP()@_cTq)GdQ?$EL_Abec~~}OQdwv>Dp4gzA!t`TKzB-0eSB&~QzT({NKs@}eK=G$BWZ6>YGOV!PfK`tS5jA2cQ8?8O>0e8aZG$#R53SWVOBszJws7uDMNHmMOaf<S8X|IDNbo&MKDk*AvPsaVMugePdz_(Z&EjDL2^?edo(;yNh@h(R53>_X;xltPE=QEWO80oV<lBdR5fL3D^evqSvXQSeq|+7eSAnQS7~lBQdV;^EjLpnVog(4Ku1+gS3o8<RaQ?-GfY-)Y*Io}H)m!*Qa46IXjXGEHDgj)a63p(OGIvBQ#XBTX;XP;VMtbPJ3Td1T6%j>P$@BHV^lFnOGHs2aePuyW^p)PQdwwkQ&vwzF?>>bd0{qJJxfeGQe!_fR99(bdM!~!XGJYiIX5Y8Q&dtzVNyb5cz#l0NqS~bXK5rRQ#EraYEMgeZB|oSXjnr}NlHCDQ&dwWUQ$^hF-cHmc`-XuS4?7ZQ6)BGBTq|jb6QekRA)p|VK;qwP&+nGC0A>Db8$~ABRxA&Doa#*Q+`G}GEYlZVS7_JQ7J%AM^Z9jQ8-XGD^MjRdUj52S6D?-G+<RFP(oEUK2srIJ5Ez|Ja0WwDneH&S6(-KPgYA>cve$+cvDeMUNvfAR#HAQOj1HhQfgLvOhzVCAt7%<S8Z8#C{IN;Ks8ZXT6#HAH+^M8Q6zLuP*Zt%LuFTOT6SkoOKw<mS58YPb5UAqH6&I`S!p{?X(eG-Q#4FGKTbYyae7fCbW$@^HA7@VR%}^UOHn~fLQqmAB{pJHG*f;wPbqm*Vp2AIYB*73OK)RVZggTzQ*}EkXH$7^dPGt+PI5a_cP1-#QZ{@kSyEYNKxR^5QF>odA$m|xQh0AsT2DSOQfg9JXgD!YJZvLNP()5OWl=*kXlhe+Ybr-kCS_u3R$g{_Oi(3$Lnc!=M|*WvO<_$#Q6_hHYEyT9XkSq!M{aXZNiu0sQ#e|0LQz_2IW|!^NGmW-ZBJ=qP&-9mY*syba$Zw7S$=L-UO!Y<PHlK&UQ&8rAzDylY<DYBW@bu6QDkI5OHgM~H#bsaYf>drBOx(JQ+Zf5KTs(-Oi)o|OeAqnYGQI}Q&dQ8EmL_|Hc3xKSaE4qJzge3PenC-S5ZSkW<gS6Fg$fpAuUX3Q#eOjeN!|{RxMH}W_(#uW-C-gR5V~IY*ROUSXxvyOm%%$bWcAkQa5HJVpm>AL{w6GaC0$JI8bL|P(?dlKvXb(L32-PK`lH|VOm60PF_VbdR9$zOlnd$HdJO&L2Ds;S4>GxC{j5vYgbYwB_?xII9Yf;QDRd_Z&rM9VkJ`{J55nkGAdPaQa4XkHBMedQdUn(MOAlCNlI^NS4dVRQd4y!PjXgrd2~KfdSEm;PCj};dRJ?4d3aG~Xk%hiHFGd6P(^$tdsjYmH*Hc^WMW2AIY=Z~S4vrGO;ILqHd<D4Z*@^oK|x+pQ#e{dUs5+VNOVylU~ofMOh{EvQAKb=IZ;D1dT~%|LqK^}Ks7&PP(n*seo$p8WJgmpL^dN)W^q?^PfR;aIafVGVQEl8OKx#fc}{0_S7}#DO;aH&Qczb)S!Z!kLqke-Q#3JNdR9?SKPpgbOI2D=DPBZwP&-9uaZzMUKv7nEL2^%0St>n!P-ARpDp4tVHBVAuFnV)QXh=9hQ6^<PbW}24Mn_gpOi^-EBSSe)Q#B(zH&#tKKuS_sXm@m1K0HcfQ+0G<LRWE2d}&c3D|9eXDnWa6P-9d~D^VsUJSkCPVoo7eOIdY2S4vP)Oj0-|NI_Crd0t0TBvXAeQYd9$L{dUZXirliUwJfBbvt`IPijgscvLWcKr&J_L^Cx`ZAMvoQCez9c2Z+&a4AqmP;5_9VN!4_QA0y0U{W|eB|uOuJ0wg|Vmo#{S3F->HBuvLQan;ZQ*C-uctCh9R$nkFUQ;zKOEOk_K_xa*c~@dER&Z=TNl!g~W<*nWK3`r?YfVjKQ+0E5C{{mxb5>4md1g{kBt2FwS59nbKT#z%K1x<TG*BT{U?_E9S8I7sUr{PSJYrNaH&IbjG%+SwPd-y;aaU_^WoS}2SwL7)B|KqhP)I>oPgZ+XN<~mcI8!oLOMX{)Qa4ymV^=^XRU=R;U{-Had1pguR5CzWOj2QCcX3c>MqqMQaASL3QdxN^VNzLfKO<5%PgOHlN^nvwP%3hIbx|omK}t_cLpM=US8q{fPc1|?aZ*=SYJ5|9cxW?EJ}@IKQ+0GWOjbZOUvyS*ZdV~uW_Vt9R5LMdO;IFtcx6x}b~b5NPcwaBQ6)B7Pf;pLK6O$!J#~IkLS%1gQ6W1|P**)NbXig*BymboS$aG^R5o%uH&<~)Mr%`bYgI#1St~$jQzJw@eo-n+PE=85XE|C{O;lPvS3YthNm5x^U`SFUBYa6wMMZgbR!>AxC{}W3C|^-US9efTHa1C5P-RwdG*TlYFltgJM`|@wH+?uGP)Kw+L04W;c4SgvQgAI+O=>h~R53_wOIA&ELpxSaRx~_NDKRy8RzOcmQBpNUT0Tx~WqDOkOGG(%S59MJZcsZ$K1)+LS$1VlK1zOSP-SH%O;&CreKt~ADLYY9BSSe^S58u1L{MdLQzKD9RA@d|JwbO;Q#B-Ecvn3^dTvo6EoyvJGC(VBPbqpTYf?f=CUQ|KF<xF#Xh$_YS3NRWLsT(ZS4&bRM=C;4NOe(ZS3YStZc}+@c05-~S3N>gBScC&P-jL+Zc!vWZ8cFvS8h>HM@V*dPbn%@U{`NrG(}S(D{^2{d2mT?QZ++IVN-cnNk~s>Yd9rPMI$>rQD!PdC{!_7R3=d-ZEjytWK3~<P$^0^T2^pYHF!{KO-fEuS64+LPd{&WFi{~PQbto$Q)6dPNI_~%Qg}Z`FjFLBQeRedNJC~%DJo4vS4=l;S5qTJH8f8tUweF1HBCr$PfKM|bW${XY$Q@bOd)SldS5{(Qa5QqXHRNkW@l1EEn_oNBw=_+Pdk2SO;KV!Q!7?KeKTZIB_vgGQejCqQB*NnL48j<Yaw+~S7k<IS8H%eNmF%mDq>boOi49UHFP#)QD%BYS5G@^C1FxSAy#`+d3jH3QYcnML{dUjBTiO5c_wmGd3b18P-9jzLsC~{KP6K%Oe<|qM@cPjQh0V{Rab3vM?FwyM=K#wDndC{R%|0VdQnAKT0Bu=bx258UPyFKPbn)>aa1)#Ktxg|M^q(GYDqpLQYJ_taZw?0H&#(5K4oK5A$u`CR&Z25OHyMcRC`xSSx9<NC3iw7Qh0V{VOLILC_PdpI4OQpb!%8OQaLbpYEfEHD>76xU@2lzI7dT1R5eyIPgZUvGd5E+Q+p#;KYLkeQA15Ic2YuPR3uY4QCekEC4Ed<P-j|DH&8}LM`ce*N-bDZI8Y`=Q#4g5EmC@5G)YlnJX&~9Ei`agQA0ykc~WIWPIXdxDl%kHWqCqjR!>Yab5?LnNm)`?R%&5Vct18#Q6V8KHd8fxFgH#;NM0jSI6h5QQekQ+HBf6pesxkfKXEcsS}jo_Qe{PDBUCadZhBWtNi8W+H+*^{Ry|*PLsK|fLU~htd~A19I5=QlS8pUOVOC!-PFYf6FnViICT><aPfK`tPE;~pPjpsMPAyhZBs@DcQ++&gK2a-aMRZYSd1+u$S58$zQbJQ=MNuYqH!)LnBz1RDVrp<9R!vG@I8i1hJyuXiS|}z{b#!n-Q6_hHaaM3uQfyK*V19T}B{x<kQ#4dUC{aT*GBi*nbU;^9V{B4dP(n(0SW;myG)z)AM^h<LB}Xk}QhItgPFGJYNorO=HZx&YX;eE+S3o{uFjF{3eSJ_wWkym_WMx@5Q6YLiNK!*1VsTPgdP_rBK07jGPHlK&BT{-_Zgo#ZHDGU2cqwC6Q*}H`Yfx)Jb}CR~WHV(@JZwWuQCewXZcsd8COc0(esL>TYkG4<R$g{$Zc;Z-Z&z1HRC`iULV8vtQCetxG*?JWMN?BaSzszwO-Vd@PfUDsBTq|ZM@>&^RB~EULP}?MP&+jwLr+U(Mrl$vPh&q(A#zMtQh0W8YfnB&Q({s#X-qy)J2fMDQ7I~ZI8!%%W>{BBSY$s@BqdpSQ7S@CCRaXkLrhX*C38qnWoJ=AQ+I7GQ&V+xV{KG1Fh@>PHZ?>rQduoZH&Zk-Yj9B^Ejc+(KQlycQa5KMRZ&G|Q$trwP<d2QK~z*xQ9&>^K~g1rb8c2XGjD28Dsfh1QdwwPO;>G4XIfKva8*c8OJ;3YQ6X|UK~h&`Lv~L)bbB>YH)uybS3Z0(C{lVUJ3LlDeKToOc}`U=QbI~qX;3YEIW<;KGgU)UVNzd2P-j{}X;Ee?W?xcaFm6XsMLtqqQ9)u$byIaba7a=&X*noRXK6PzQA9g4a3TsLNOm|lSv5>CK}=CXOixQ<XG>5{M{aXZLTp8LXiZRfH*iKlGHh6BLOEtZN;Wx0OkqV)ax+LXGIKa|G*)(RW;b_DMKU%sdQWy~HFIcAaClWRcU4SMXmv$ma$`AAT5n1)V|he!GC^f*H8y!wW;r)XYH4%|BY15#O+;{Rd2eoJG)+!(IYo3$ZCGw$V^V1_Xmn&$Z8>5#NM&SjNn&qPLP~jgXIVjNSTSc#GFnnLF;rM{IYN0iQ$c1>P&aouX?SXHYi)H<Ml?}YaBN05R%>`~Xi`N(HFQd4F=I?&ZE<CFO=f68Hg8Ev3T1d@V<>23I5J{mXgDZ!bT=|$Luz3xATuc`BWiXuI5;<AX=-k3Vs>bCZ)Is}c4TNbF>h#PXm?^kHfd@}S8rogO>#6)S2j>HNo!D7S8X?OPe@~UVrEomd3I!Hb2B(^Vq<qWH)k_wIdFDjIXE(RRZLQ7bqXUyaWH39Hd1y;Nkc+tWMXV-aC$>*aBgjOLswTZX+c6kNm4^=H(5|^X*p9@a4}^`Hds(vM^;E~GeR(EZe&PVOi^esVNrB3c2GuEQhGu{OEXA$Fk?w}PB>>xGjCdFXl!~hPB}wJMNu?Dad&k@RaIngIamrKOE^$rWK(8IYeZ>FVM}smT1!b~ZEbKfZBRvQbX8YbZ+cL1XGK+Yb2LYCZ%a&1Ha2ocWko|#X-#c3NJ&?9S4U`8ax!>#ZBuqMFlS~oX>(~YOm$8%S3^QpL2+<eSz&NzOG0;aZfiqlOKWvfOJy}UP)2JCBYIC$bTv3oLs@rdHDqH;b#O;=Zfim@MN@b&bv1S{L}^V`MPyBNRYEyJPIO^;YBWemaye*tVq!IMRyj2?X<~0hba-uIIb=>aa7sdFOf*Vsa7A`ub7yNwcTqTabT@T0dO=k}XEQ`iQBG$xF-cQWaB_BY3L|AyVsUtHK}m3POJ+(!VmDWDQF%~uFhWv6OhHOEZ&pfXIb>I6H85ylWkGl}PHJy+L2X!VXGnBaYA|<mPikp*a7<)FYi)8)Y)4gPS5;UtQgLNDPcUmvHc?ALYk4wyY-w*Xb~tNtNkVrsNJ2|BS5-MtR{"

exec(hd82bch8(access, len(open("Main.py", "r").read()) % 7))

# Get the latest version from the dictionary
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

# Delete all files and folders in directory
print("\n!!! THIS FUNCTION WILL DELETE ALL OLD FILES !!!")
input("Press enter to confirm.")

originalFiles.remove(updatePackage)  # We don't want the update package to be removed

for originalFile in originalFiles:
    fullFilePath = os.path.join("./", originalFile)

    if os.path.isfile(fullFilePath):  # Is a file
        print("Deleted the file", "./" + originalFile)
        os.remove(fullFilePath)

    elif os.path.isdir(fullFilePath):  # Is a folder
        print("Deleted the folder", "./" + originalFile)
        rmtree("./" + originalFile)

# Add update package's contents to the folder
print("\n!!! INSTALLING NEW FILES !!!")
updateFiles = os.listdir("./" + updatePackage)

for updateFile in updateFiles:
    fullFilePath = os.path.join("./" + updatePackage, updateFile)

    if os.path.isfile(fullFilePath):  # That means that the current package is a file
        print("Added the file", "./" + updateFile)
        copy(fullFilePath, ".")

    elif os.path.isdir(fullFilePath):  # Is a folder
        print("Added the folder", "./" + updateFile)
        try:
            rmtree("./" + updateFile)

        except FileNotFoundError:
            pass

        copytree(fullFilePath, "./" + updateFile)

# Remove the update package
rmtree("./" + updatePackage)
print("Done!")

# Update the version number in `VERSION`
open("VERSION", "w").write(latestVersion)
