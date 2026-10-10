# Lo ejecuta, como el jugador, tras talar un árbol
execute if score #nuevo talar_cfg >= #max talar_cfg run return 0
execute if score #cuenta talar_cfg matches ..0 if score #tope talar_cfg < #limite talar_cfg run title @s actionbar [{"text":"Tu hacha no tenía durabilidad para tanto: ha talado ","color":"gold"},{"score":{"name":"#talados","objective":"talar_cfg"},"color":"white"},{"text":" troncos y el árbol queda a medias.","color":"gold"}]
execute if score #cuenta talar_cfg matches ..0 if score #tope talar_cfg < #limite talar_cfg run return 0
execute if score #talados talar_cfg matches 1.. run title @s actionbar [{"text":"Árbol talado: ","color":"green"},{"score":{"name":"#talados","objective":"talar_cfg"},"color":"white"},{"text":" troncos más · el hacha pierde ","color":"gray"},{"score":{"name":"#talados","objective":"talar_cfg"},"color":"white"},{"text":" de durabilidad","color":"gray"}]
