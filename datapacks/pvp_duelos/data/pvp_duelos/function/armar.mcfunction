# Ejecuta la víctima (@s, tag pvp_n1); el atacante, si es otro jugador, lleva el tag pvp_n2
scoreboard players set #id pvp_cfg 0
scoreboard players set #nuevo pvp_cfg 0
# ¿ya hay un duelo en marcha de la víctima o del atacante? Se reutiliza
execute if score @s pvp_par matches 1.. run scoreboard players operation #id pvp_cfg = @s pvp_par
execute if score #id pvp_cfg matches 0 as @a[tag=pvp_n2,limit=1] if score @s pvp_par matches 1.. run scoreboard players operation #id pvp_cfg = @s pvp_par
execute if score #id pvp_cfg matches 0 run function pvp_duelos:nuevo_id
scoreboard players operation @s pvp_par = #id pvp_cfg
scoreboard players operation @s pvp_timer = #duracion pvp_cfg
scoreboard players operation @a[tag=pvp_n2] pvp_par = #id pvp_cfg
scoreboard players operation @a[tag=pvp_n2] pvp_timer = #duracion pvp_cfg
# duelo nuevo entre dos jugadores: título grande con las dos cabezas
execute if score #nuevo pvp_cfg matches 1 if entity @a[tag=pvp_n2] run function pvp_duelos:anunciar
