#!/usr/bin/env python3

from foca.foca import foca

PETS = {}


def listPets():
    return {"pets": [pet for pet in PETS.values()]}


def createPets(pet):
    PETS[pet] = 1
    return {"pets": [pet for pet in PETS.values()]}


def showPetById(id):
    if id in PETS:
        return PETS[id]
    else:
        return {"No pets found"}


if __name__ == '__main__':
    app = foca("config.yaml")
    app.run(port=8080)