scoreboard players set @s veta 0
execute if entity @s[tag=veta_off] run tag @s add veta_a_on
execute unless entity @s[tag=veta_off] run tag @s add veta_a_off
execute if entity @s[tag=veta_a_on] run function veta:encender
execute if entity @s[tag=veta_a_off] run function veta:apagar
tag @s remove veta_a_on
tag @s remove veta_a_off
