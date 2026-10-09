# Ejecuta un jugador en duelo que ha recibido daño ajeno al duelo (o está en peligro): termina el modo PvP de todo su duelo
execute unless score @s pvp_par matches 1.. run return 0
scoreboard players operation #id pvp_cfg = @s pvp_par
execute as @a if score @s pvp_par = #id pvp_cfg run function pvp_duelos:terminar_cancelado
