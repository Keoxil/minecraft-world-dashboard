# Lo ejecuta, como el asesino, la advancement victoria.json: ha matado a otro jugador
advancement revoke @s only pvp_duelos:victoria
# el duelo termina en cuanto cae uno: el vencedor deja de tener la protección
scoreboard players set @s pvp_timer 0
scoreboard players set @s pvp_par 0
tag @s remove pvp_combate
title @s actionbar {"text":"⚔ Duelo terminado","color":"gold"}
