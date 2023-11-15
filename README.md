This is a reinforcement learning-enabled Flappy Bird model. After training for four hours, it demonstrated the ability to cover a maximum of 700 distance, where distance is calculated as GAME_SPEED / 100.

The training rewards for this model are defined as follows:

a) A negative reward of 100 is assigned if the game ends by colliding with any obstacles.
b) Another negative reward of 100 is given if the bird deviates from the center of the opening between pipes that it must navigate through.
c) Conversely, a positive reward of 30 is granted if the bird moves closer to the center of the opening between pipes.

Screen shot of the game for reference
![image](https://github.com/castlercodes/flappy-bird-rl-trained/assets/86559072/d7991f43-7dff-49e7-9e59-c8ff95f4538b)

To run the reinforcement learning agent, clone the repository to your device and type py flappy.py in the terminal. To exit training, press Ctrl+C in the terminal.
