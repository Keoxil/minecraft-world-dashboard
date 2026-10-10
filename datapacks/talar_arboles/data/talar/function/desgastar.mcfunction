# Lo ejecuta el jugador tras talar: cada tronco extra gasta 1 de durabilidad del hacha (y si no aguanta, se rompe)
scoreboard players operation #nuevo talar_cfg = #dano talar_cfg
scoreboard players operation #nuevo talar_cfg += #talados talar_cfg
execute if score #talados talar_cfg matches 0 run return 0
execute if score #nuevo talar_cfg >= #max talar_cfg run function talar:romper_herramienta
execute if score #nuevo talar_cfg < #max talar_cfg store result storage talar:tmp d int 1 run scoreboard players get #nuevo talar_cfg
execute if score #nuevo talar_cfg < #max talar_cfg run function talar:poner_dano with storage talar:tmp
