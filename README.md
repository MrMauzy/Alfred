# Alfred
A personal assistant of sorts who play games, rolls dice and most importantly entertains you with music. 

Commands Currently:

  .roll
    - Used to initiate a dice roll. You can use it as '.roll' to roll a d20 or use '.roll x' with any number you want for the dice sides.
  .play
    - Use this to search youtube to play a song link. You can enter the full url to search words to search youtube. 
    - Currently this will download the song and use file functions to find and play the song. 
  .que
    - I store the already downloaded songs in the 'Music' folder to randomly play songs.
    - One the program runs it grabs all those fong filenames and stores them into a json file for later use.
    - Then I use random shuffle on the json file after turning it into a list to feed the que function. 
  .music
    - Just a simple function to play one song that is in your main directory. 
  .quote
    - Will give a Stoic quote with the author in the chat window. 
