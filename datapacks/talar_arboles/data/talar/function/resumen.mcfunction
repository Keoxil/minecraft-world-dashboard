# Lo ejecuta, como el jugador, tras talar un árbol
scoreboard players operation #rotos talar_cfg = #limite talar_cfg
scoreboard players operation #rotos talar_cfg -= #cuenta talar_cfg
execute if score #rotos talar_cfg matches 1.. run title @s actionbar [{"text":"Árbol talado: ","color":"green"},{"score":{"name":"#rotos","objective":"talar_cfg"},"color":"white"},{"text":" troncos","color":"gray"}]
