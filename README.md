# hypixel-online

A discord bot for hypixel / bedwars.

Right now it only does bedwars.

## Invite bot
Invite the bot using this [link.](https://discord.com/api/oauth2/authorize?client_id=694645515983519794&permissions=523328&scope=bot)
If it doesn't work, copy and paste this url into your browser:
https://discord.com/api/oauth2/authorize?client_id=694645515983519794&permissions=523328&scope=bot


## Setting up

1. Install docker
2. Set up a firebase database and put the private key in ho/firebase-key.json
3. Add collections `linked`, and `guild` to the firebase database
4. Add a file ho/sudoers.txt and add any ID's you want into it, separated by carraige returns.
5. Put your discord bot token as HYPIXELONLINETOKEN in ho/.env
6. Put your hypixel api key as HYPIXELAPITOKEN in ho/.env
7. If using the deploy script, do `chmod +x deploy` and then `./deploy <docker image name>` to run in a detached docker container
8. If not using the deploy script, just do `docker build .` to get the docker image.
