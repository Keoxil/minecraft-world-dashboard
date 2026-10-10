# El hacha se ha gastado del todo con este árbol
item replace entity @s weapon.mainhand with minecraft:air
playsound minecraft:entity.item.break player @a ~ ~ ~ 1 1
title @s actionbar [{"text":"¡Tu hacha se ha roto talando! Sin durabilidad el árbol puede quedar a medias.","color":"red"}]
