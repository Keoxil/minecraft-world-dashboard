# Macro ($(s) = brote): rompe este tronco, tala las hojas naturales de alrededor, replanta y sigue buscando
execute if score #cuenta talar_cfg matches ..0 run return 0
setblock ~ ~ ~ air destroy
scoreboard players remove #cuenta talar_cfg 1
scoreboard players add #talados talar_cfg 1
execute store result score #n talar_cfg run fill ~-4 ~-3 ~-4 ~4 ~4 ~4 air replace #minecraft:leaves[persistent=false]
function talar:soltar with storage talar:tmp
$execute if block ~ ~-1 ~ #minecraft:dirt run setblock ~ ~ ~ $(s)
execute if score #cuenta talar_cfg matches 1.. run function talar:paso with storage talar:tmp
