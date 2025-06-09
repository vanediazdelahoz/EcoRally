# EcoRally

**EcoRally** is a local 2D video game, board-style, with a **pixel art** aesthetic that promotes environmental awareness in a playful and educational way.  
Players move around a board collecting **recyclable waste**, which they must deposit at **recycling points** to earn **badges**.  
At the end of the game, the player with the most badges wins. In case of a tie, the total amount of collected waste is used as a tiebreaker.

## Game Modes

- **Human vs Human**: Two players compete against each other.  
- **Human vs Bot**: A player competes against an **AI-controlled agent**, trained using **Reinforcement Learning** with the **Dyna-Q** algorithm.  
  This agent makes strategic decisions whenever it reaches a **board fork**, evaluating which of the two available paths is more beneficial based on the current game state.  
  It considers factors such as the **amount of collected waste**, the **remaining steps**, and the **proximity to active recycling points**.

## Tile Types on the Board

- 🟩 **Green tiles**: Increase the amount of collected waste.  
- 🟥 **Red tiles**: Decrease the amount of collected waste.  
- 🟦 **Blue tiles**: Have no effect.  
- 🟪 **Purple tiles**: The player rolls a die; the result is **doubled** and added to their waste total.

## Minigames

After each round, a **random minigame** is triggered, available in both **Human vs Human** and **Human vs Bot** modes.  
In the bot mode, its performance in minigames is handled through **randomized logic**, **not** through AI models.

Available minigames:

- 🎯 **Sky in Crisis**: Catch as much falling trash as possible using a trash bin.  
- 🗑️ **To the Bin**: Sort waste correctly into green, white, and black bins.  
- 🎣 **Responsible Fishing**: Fish out as much trash as possible.

## Agent Training and Evaluation

To train or evaluate the agent, run the file `agent/train_agent.py`.  
This will launch an **interactive console menu** that allows you to:

- Train the model with a **fixed or custom number of episodes**.  
- Evaluate the agent’s performance.  
- Check the **win rate**.  
- View the **parameters used** during training.

---

**EcoRally** combines **strategy**, **local competition**, and **environmental education** into a fun, didactic, and visually charming experience.