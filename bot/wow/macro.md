### 魔兽世界宏入门教程


#### 条件
/cast [条件1,条件2][条件3] spell = (条件1 & 条件2) | 条件3 满足的情况下释放法术
条件列表

- target [target]
- harm [harm] 敌对
- help [help] 友方
- modifier [modifier:type]或[mod] 如果按下了功能键(ctrl,alt,shift)就返回真 [mod]则表示任意特定建


如德鲁伊有目标切目标为未死亡的友方则给目标加爪子，否则给自己加爪子
/cast [@mouseover,help,nodead][]野性印记

如果按下了功能键则法术换成荆棘术，否则同上
/cast [mod,@mouseover,help] 荆棘术;[@mouseover,help,nodead][]野性印记
