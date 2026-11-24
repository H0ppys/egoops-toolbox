import json

d = json.load(open(r"C:\Users\Administrator\Documents\deepseek-harness\default-workspace\egoops_agg.json", encoding="utf-8"))
agg = d["agg"]
tot = sum(a["dur"] for a in agg.values())
pas = sum(a["pass"] for a in agg.values())
rej = sum(a["rej"] for a in agg.values())
print(f"状态法: 总 {tot/3600:.1f}h 通过 {pas/3600:.1f}h 拒绝 {rej/3600:.1f}h")
print("页面显示: 总 684.5h 通过 615.2h 拒绝 47.8h 待质检 0s 失败 0s 通过率 90%")
print(f"差额: 总-通过-拒绝 = {(tot-pas-rej)/3600:.1f}h")
