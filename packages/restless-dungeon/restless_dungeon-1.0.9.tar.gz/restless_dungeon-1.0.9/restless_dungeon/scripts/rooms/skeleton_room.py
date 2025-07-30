from time import sleep

from rich import print


def skeleton_room(player):
    print("[orange]You enter a room and hear the sound of bones rattling.[/orange]")
    sleep(1)
    print("[red]An army of skeletons armed with bats and clubs turn to you and charge.[/red]")
    sleep(1)
    print("Do you fight them or try to run?")
    choice = input(">> ").lower()
    if choice == "fight":
        print("It was a gruelling fight against the army, yet you came out victorious.")
        player.take_damage(int(player.health * 0.7))  # damage the player by 60% of their current health
    elif choice == "run":
        print("You sprinted through the army to the end of the room. You were hit a few times as you ran.")
        player.take_damage(int(player.health * 0.3))
        player.consume_energy(int(player.energy * 0.6))  # consume 60% of player's current energy
    else:
        print("I don't understand.")
        skeleton_room(player)
