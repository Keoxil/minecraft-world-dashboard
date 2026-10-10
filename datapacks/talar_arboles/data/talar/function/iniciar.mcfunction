# Lo ejecuta, en la posición del tronco recién picado, la entidad de objeto que ha soltado
scoreboard players set #hallado talar_cfg 1
# solo se talan árboles de verdad: tiene que haber hojas naturales en la copa (así no se derriba una casa de troncos)
scoreboard players set #hojas talar_cfg 0
function talar:subir with storage talar:tmp
execute unless score #hojas talar_cfg matches 1 run scoreboard players set #hallado talar_cfg 0
execute unless score #hojas talar_cfg matches 1 run return 0
scoreboard players operation #cuenta talar_cfg = #tope talar_cfg
scoreboard players set #talados talar_cfg 0
fill ~-4 ~-3 ~-4 ~4 ~4 ~4 air replace #minecraft:leaves[persistent=false]
function talar:paso with storage talar:tmp
