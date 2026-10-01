# Ícone VitalRegistro

`icone.png` é utilizado tanto na Home quanto por `icon.filename` no Buildozer. O original era RGB, 1254 × 1254, com fundo externo preto opaco.

Na revisão pós-primeiro-build, o autor autorizou a correção determinística do canal alfa: os pixels escuros (`max(R,G,B) <= 40`) conectados às bordas externas foram tornados transparentes. Não houve redesenho; dimensões e todos os canais RGB foram preservados byte a byte. Foram removidos do alfa 242.249 pixels externos, mantendo o interior da arte opaco.

O PNG passou a RGBA. A Home foi conferida no desktop com fundo claro. O launcher usa o mesmo arquivo, mas sua aparência após reconstruir/reinstalar o APK ainda requer teste no aparelho. Não há ícone adaptativo separado nesta versão.
