C={'1':("1 only","1 మాత్రమే"),'2':("2 only","2 మాత్రమే"),'3':("3 only","3 మాత్రమే"),'4':("4 only","4 మాత్రమే"),
'12':("1 and 2 only","1, 2 మాత్రమే"),'13':("1 and 3 only","1, 3 మాత్రమే"),'23':("2 and 3 only","2, 3 మాత్రమే"),
'14':("1 and 4 only","1, 4 మాత్రమే"),'24':("2 and 4 only","2, 4 మాత్రమే"),'34':("3 and 4 only","3, 4 మాత్రమే"),
'123':("1, 2 and 3","1, 2, 3"),'123o':("1, 2 and 3 only","1, 2, 3 మాత్రమే"),'124':("1, 2 and 4 only","1, 2, 4 మాత్రమే"),
'134':("1, 3 and 4 only","1, 3, 4 మాత్రమే"),'234':("2, 3 and 4 only","2, 3, 4 మాత్రమే"),'1234':("1, 2, 3 and 4","1, 2, 3, 4"),
'b':("Both 1 and 2","1, 2 రెండూ"),'n':("Neither 1 nor 2","1, 2 రెండూ కావు"),'none':("None of the above","పైవేవీ కావు")}
def co(*ks):return [C[k] for k in ks]
AR=[("Both A and R are true, and R is the correct explanation of A","A, R రెండూ సరైనవి; A కు R సరైన వివరణ"),
("Both A and R are true, but R is not the correct explanation of A","A, R రెండూ సరైనవి; కానీ A కు R సరైన వివరణ కాదు"),
("A is true, but R is false","A సరైనది, కానీ R తప్పు"),("A is false, but R is true","A తప్పు, కానీ R సరైనది")]
def M(*c):return [(x,x) for x in c]
def q(tp,lv,qe,qt,o,a,we,wt,st=()):
    assert len(o)==4 and 0<=a<4
    d={"tp":tp,"lv":lv,"q":{"en":qe,"te":qt},"o":[{"en":e,"te":t} for e,t in o],"a":a,"why":{"en":we,"te":wt}}
    if st:d["st"]=[{"en":e,"te":t} for e,t in st]
    return d
STM=("Consider the following statements:","కింది వాక్యాలను పరిశీలించండి:")
WC=("Which of the statements given above is/are correct?","పై వాక్యాల్లో ఏది/ఏవి సరైనవి?")
