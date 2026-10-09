# Lo ejecuta, como el jugador, la advancement clic.json: ha hecho clic derecho en un cultivo maduro
advancement revoke @s only cosecha:clic
scoreboard players set #fin cosecha_cfg 0
scoreboard players set #pasos cosecha_cfg 70
execute anchored eyes positioned ^ ^ ^ run function cosecha:rayo
