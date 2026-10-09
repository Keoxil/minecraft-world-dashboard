# Macro ($(s) = brote): rompe este tronco, replanta si hay tierra debajo y sigue buscando
execute if score #cuenta talar_cfg matches ..0 run return 0
setblock ~ ~ ~ air destroy
scoreboard players remove #cuenta talar_cfg 1
$execute if block ~ ~-1 ~ #minecraft:dirt run setblock ~ ~ ~ $(s)
execute if score #cuenta talar_cfg matches 1.. run function talar:paso with storage talar:tmp
