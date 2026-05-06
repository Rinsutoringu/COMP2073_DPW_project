How clean.py works?

**for Step1.** 

检查是否存在未正确包裹的逗号，未正确包裹的逗号会导致数据解析器出问题。我们可以认为引号外的逗号数量就是真实的列数

逐行扫描，给没有双引号的数据块加双引号，并尝试修复异常列。



**for Step2.**

观察列名，classfication拼错了，我们对它进行替换

可能有重复行、可能存在一些首尾空格。检查并剔除。



**for Step3.**

每个实体的一些特定属性必须有值填充，而另一些特定属性并不必须被填充。

这些属性必须有值："name", "pokedex_number", "type1", "hp", "attack", "defense", "sp_attack", "sp_defense", "speed", "generation"

这些属性的值可有可无："type2", "percentage_male", "height_m", "weight_kg"



**for Step4.**

列 abilities 存储的是字符串格式的伪列表，为了分析，我们需要将其进行转换，存入 abilities_parsed 列

转换完毕后，我们需要统计技能数量是否超出正常范围 我们统计技能数量，然后记录到 ability_count 列中。

如果一个宝可梦的技能大于4，那说明可能进化形态和常规形态被合并了。



**for Step5.**

需要把进化形态的宝可梦拆出去。使用 form_index 来标记这是个进化形态。

``````
Rattata, 6 abilities, type1=normal, type2=dark   // 原有格式
Rattata, 3 abilities, form_index=0               // 常规形态
Rattata, 3 abilities, form_index=1               // 进化形态
``````



**for Step6.**

优化数据类型

pandas会把数据读成object，类型不安全

- hp/attack/... → Int64	
- height_m/weight_kg → float64
- is_legendary → bool
- type1/type2/generation → category



**for Step7.**

根据既有宝可梦规则检查异常值