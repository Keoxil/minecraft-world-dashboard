# Lo ejecuta, como la víctima, la advancement golpe.json: otro jugador acaba de herirla
advancement revoke @s only pvp_duelos:golpe
# marca que ESTE daño viene de un jugador (así no se confunde con lava, caídas, mobs...)
scoreboard players set @s pvp_origen 1
tag @s add pvp_n1
execute on attacker if entity @s[type=minecraft:player,tag=!pvp_n1] run tag @s add pvp_n2
function pvp_duelos:armar
tag @a remove pvp_n1
tag @a remove pvp_n2
