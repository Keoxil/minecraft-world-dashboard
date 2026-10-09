# segundos que quedan (redondeando hacia arriba)
scoreboard players operation #seg pvp_cfg = @s pvp_timer
scoreboard players add #seg pvp_cfg 19
scoreboard players operation #seg pvp_cfg /= #20 pvp_cfg
title @s actionbar [{"text":""},{"text":"⚔ Modo PvP ","color":"red","bold":true},{"score":{"name":"#seg","objective":"pvp_cfg"},"color":"white","bold":false},{"text":" s","color":"gray","bold":false}]
