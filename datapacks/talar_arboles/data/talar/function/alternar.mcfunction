scoreboard players set @s talar 0
execute if entity @s[tag=talar_off] run tag @s add talar_a_on
execute unless entity @s[tag=talar_off] run tag @s add talar_a_off
execute if entity @s[tag=talar_a_on] run function talar:encender
execute if entity @s[tag=talar_a_off] run function talar:apagar
tag @s remove talar_a_on
tag @s remove talar_a_off
