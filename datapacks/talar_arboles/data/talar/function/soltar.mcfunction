# Macro ($(l) = tabla de botín de las hojas): suelta lo que habrían dado las hojas talladas (palos, brotes, manzanas), una vez por hoja
execute if score #n talar_cfg matches ..0 run return 0
$loot spawn ~ ~ ~ loot $(l)
scoreboard players remove #n talar_cfg 1
function talar:soltar with storage talar:tmp
