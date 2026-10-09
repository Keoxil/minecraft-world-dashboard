# /function pvp_duelos:prueba  -> vista previa del título del duelo con tu propia cabeza
tag @s add pvp_n1
tag @s add pvp_n2
tag @s add pvp_titulo
data modify storage pvp_duelos:tmp u1 set from entity @s UUID
data modify storage pvp_duelos:tmp u2 set from entity @s UUID
title @s times 10 70 25
title @s subtitle {"text":"Así se verá el título del duelo","color":"gray"}
function pvp_duelos:titulo with storage pvp_duelos:tmp
tag @s remove pvp_n1
tag @s remove pvp_n2
tag @s remove pvp_titulo
