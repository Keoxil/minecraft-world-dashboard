# Lo ejecuta, en la posición del tronco recién picado, la entidad de objeto que ha soltado
scoreboard players set #hallado talar_cfg 1
# solo se talan árboles de verdad: tiene que haber hojas naturales cerca (así no se derriba una casa de troncos)
scoreboard players set #hojas talar_cfg 0
function talar:hojas
execute unless score #hojas talar_cfg matches 1 run scoreboard players set #hallado talar_cfg 0
execute unless score #hojas talar_cfg matches 1 run return 0
scoreboard players operation #cuenta talar_cfg = #limite talar_cfg
function talar:paso with storage talar:tmp
