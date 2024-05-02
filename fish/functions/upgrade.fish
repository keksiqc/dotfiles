function upgrade --description 'Upgrade all the things'
    nala update
    nala upgrade -y
    bun upgrade
    pipx upgrade-all
    nvm install latest
end