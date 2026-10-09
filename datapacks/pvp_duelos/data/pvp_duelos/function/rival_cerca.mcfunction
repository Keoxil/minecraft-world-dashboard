# Deja #cerca = 1 si otro jugador del MISMO duelo está a 32 bloques o menos de @s
scoreboard players set #cerca pvp_cfg 0
scoreboard players operation #id pvp_cfg = @s pvp_par
tag @s add pvp_yo
execute at @s as @a[distance=..32,tag=pvp_combate,tag=!pvp_yo] if score @s pvp_par = #id pvp_cfg run scoreboard players set #cerca pvp_cfg 1
tag @s remove pvp_yo
