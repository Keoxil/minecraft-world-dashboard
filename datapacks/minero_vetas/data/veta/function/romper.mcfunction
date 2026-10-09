# Macro ($(x) = experiencia): suelta el botín con TU pico (respeta Fortuna y Toque de seda), quita la mena y sigue
execute if score #cuenta veta_cfg matches ..0 run return 0
loot spawn ~ ~ ~ mine ~ ~ ~ mainhand
setblock ~ ~ ~ air
scoreboard players remove #cuenta veta_cfg 1
$execute unless score #cuenta veta_cfg matches ..-1 if data storage veta:tmp {x:$(x)} unless data storage veta:tmp {x:0} run summon minecraft:experience_orb ~ ~ ~ {Value:$(x)s}
execute if score #cuenta veta_cfg matches 1.. run function veta:paso with storage veta:tmp
