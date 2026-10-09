# avanza por la línea de visión hasta dar con un cultivo maduro
execute if score #fin cosecha_cfg matches 1 run return 0
execute if block ~ ~ ~ minecraft:wheat[age=7] run function cosecha:trigo
execute if block ~ ~ ~ minecraft:carrots[age=7] run function cosecha:zanahoria
execute if block ~ ~ ~ minecraft:potatoes[age=7] run function cosecha:patata
execute if block ~ ~ ~ minecraft:beetroots[age=3] run function cosecha:remolacha
execute if block ~ ~ ~ minecraft:nether_wart[age=3] run function cosecha:verruga
scoreboard players remove #pasos cosecha_cfg 1
execute if score #fin cosecha_cfg matches 0 if score #pasos cosecha_cfg matches 1.. positioned ^ ^ ^0.1 run function cosecha:rayo
