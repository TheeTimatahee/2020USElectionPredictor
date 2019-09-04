CIS 400, Spring 2019 Term Project
Timothy Kilmer, Aiden Herlan, Sergio Santos, Alan Zumou, Jay Hoffacker
Repo link: gitlab.com/ssants/CIS400-Final

To install: Copy all files except the .pptx file to a folder of your choice
- Make sure all files included go in the same folder when run
	- Same goes for any data you mine yourself
	
To mine data for analysis,
- Run miner.py and follow the prompts to find for a candidate
- This process will write data to a .txt file with each tweet mined separated by line returns

To run analysis:
- Make sure you have data to analyze
- Run Sentiment_Analysis.py, and it will analyze all the data for each the candidates,
  and put the resulting data into a folder named "<candidate'snamehere>sent.txt"
- NOTE: This takes quite a long time

To display data:
- Run displayer.py
- You will be prompted whether or not you have done analysis yet. Respond "y" if you have,
  and it will retrieved the analyzed data
	- Otherwise, it will perform analysis 

Dependencies:
matplotlib (pip install matplotlib)
numpy 	   (pip install numpy)
tweepy     (pip install tweepy)
nltk       (pip install nltk)
textblob   (pip install textblob)
functools