Nacho Gouda #cook
    worker


Pierre Inkwell
# writer from west pardam
# writes artisitc and political poetry
    worker, drink lover, cat lover, artistic



Halibut Hotel
# a hotel for the middle class
# mostly empty due to low tourism
    if not player.home == self:
        "Hi there player, are you looking to stay at the Halibut tonight?"
            "Yes, as a matter of fact I do. Do you have any rooms left?"
        if missions.hotel_advertising.completed:
            "No we don't, and it's all thanks to you!"
            "Here, have this as a thank you..."
            player.inventory.append(items.fancy_watch)
        else:
            "Yes, would you like to stay here for the night?"
                "Yes, please"
                    player.gold -= 20
                "Maybe another time."
                exit()
    else:
        "I hope you didn't lose your key."
            "No, of course not. whisper: ...actually I did lose it."

    if player is Teri:
        "What do you want?"

shop
    a room for the night    # hide from the police
