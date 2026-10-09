# Ejecuta la víctima (tag pvp_n1); el atacante lleva pvp_n2
tag @s add pvp_titulo
tag @a[tag=pvp_n2] add pvp_titulo
data modify storage pvp_duelos:tmp u1 set from entity @s UUID
data modify storage pvp_duelos:tmp u2 set from entity @a[tag=pvp_n2,limit=1] UUID
scoreboard players operation #segtotal pvp_cfg = #duracion pvp_cfg
scoreboard players operation #segtotal pvp_cfg /= #20 pvp_cfg
title @a[tag=pvp_titulo] times 10 70 25
title @a[tag=pvp_titulo] subtitle [{"text":"Modo PvP · ","color":"gray"},{"score":{"name":"#segtotal","objective":"pvp_cfg"},"color":"white"},{"text":" s · si cae uno en el duelo, conserva su inventario","color":"gray"}]
execute store success score #ok pvp_cfg run function pvp_duelos:titulo with storage pvp_duelos:tmp
# si por lo que sea no se pudieran dibujar las cabezas, título solo con los nombres
execute unless score #ok pvp_cfg matches 1 run title @a[tag=pvp_titulo] title [{"selector":"@a[tag=pvp_n1]","color":"gold"},{"text":"  VS  ","color":"red","bold":true},{"selector":"@a[tag=pvp_n2]","color":"gold","bold":false}]
tellraw @a[tag=!pvp_titulo] [{"text":"⚔ ","color":"red"},{"selector":"@a[tag=pvp_n1]","color":"gold"},{"text":" VS ","color":"red","bold":true},{"selector":"@a[tag=pvp_n2]","color":"gold","bold":false},{"text":" ¡duelo en marcha!","color":"gray","bold":false}]
playsound minecraft:entity.wither.spawn player @a[tag=pvp_titulo] ~ ~ ~ 0.35 1.5
tag @a remove pvp_titulo
