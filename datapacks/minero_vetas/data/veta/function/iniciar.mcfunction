# Se ejecuta como el jugador, en la posición de la mena recién picada
scoreboard players set #hallado veta_cfg 1
scoreboard players operation #cuenta veta_cfg = #limite veta_cfg
function veta:paso with storage veta:tmp
