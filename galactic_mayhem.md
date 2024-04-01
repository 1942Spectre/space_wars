**Boğaziçi University**

**Industrial Engineering Department**

**IE 201 - SPRING 202\*\***4\*\*

**Galactic** **Mayhem**

**Analysis Report**

**Group** **1**

**Ahmet Hakan Afşin  2021402303**

**Lütfi Furkan Şimşek  2020402177**

**Eren Yılmaz  2022402303**

Instructor: Ali Tamer Unal

Table of Contents

**Introduction and Description: “Galactic Mayhem”** **2**

**UML Diagram** **4**

Diagram 4

Explanation 5

**Use-Case Diagram** **7**

Diagram 7

Explanation 7

**1.** **Introduction** **and** **Description\*\***: “Galactic Mayhem”\*\*

Step into the retro world of Galactic Mayhem, a classic space-shooter game with a nostalgic twist. Inspired by the arcade era and the enduring popularity of Star Wars, this indie gem offers a blast from the past while capturing the essence of timeless gameplay. In a gaming landscape where simplicity reigns supreme, Galactic Mayhem invites players to rediscover the joy of pixelated adventures and embark on an epic journey through the stars. Get ready to pilot your ship, dodge enemy fire, and experience the thrill of old-school gaming with Galactic Mayhem.

In Galactic Mayhem, simplicity is key. We've crafted a game experience that harks back to the days of classic arcade gaming, where fun was immediate and complexity took a back seat. Our aim was to provide an accessible escape for players who crave the thrill of gaming without the burden of mastering intricate mechanics. Whether you're a busy professional looking to unwind after a long day or simply seeking a bit of nostalgic fun, Galactic Mayhem is the perfect choice. With just a double click, you're thrust into a universe where survival is the name of the game. So forget about tutorials and exhaustive learning curves – dive into Galactic Mayhem and let the retro-inspired adventure begin.

In Galactic Mayhem, we've implemented a logarithmic difficulty adjustment system to ensure that every moment is packed with adrenaline-pumping action. Unlike traditional linear difficulty curves, our system ramps up the challenge rapidly, keeping players on their toes from the very beginning. Within just three minutes, the game reaches its peak difficulty – a true test of skill where players must navigate through a torrent of enemy projectiles while engaging in intense space battles.

The old school scrolling space background is more than just a backdrop – it's a portal to a bygone era of gaming nostalgia. With its pixelated stars and retro aesthetics, it transports players back to the heyday of classic arcade games, evoking a sense of wonder and excitement reminiscent of childhood afternoons spent in dimly lit arcades. In Galactic Mayhem, this immersive backdrop isn't just window dressing – it's an integral part of the experience, enhancing the game's authenticity and charm.

The different species of enemy ships, each with their own unique behaviors and attack patterns, keep players constantly engaged and strategizing. From nimble fighters to hulking cruisers, every encounter offers a fresh challenge that demands quick reflexes and clever tactics to overcome. And with a variety of boosts scattered throughout the cosmos – from shield enhancements to firepower upgrades – players can customize their approach and turn the tide of battle in their favor. Whether you're weaving through enemy fire or unleashing a devastating barrage of lasers, Galactic Mayhem ensures that every moment is packed with adrenaline-fueled excitement.

The scoreboard feature that saves the best 10 scores will fuel players' competitive spirit as they strive to claim a spot among the galaxy's elite pilots. Whether you're aiming to beat your own personal best or gunning for the top of the leaderboard, every playthrough becomes a chance to etch your name in gaming history. With each high score saved for posterity, Galactic Mayhem transforms into a battleground where skill and determination reign supreme. So buckle up, pilot – the stars await, and the leaderboard beckons!

**UML Diagram:**

![UML Diagram](files/UML%20Diagram.png "UML Diagram")

**Explanation\*\***:\*\*

**Game:** This class handles the whole game loop, it updates all the sprites, checks collisions, adjust difficulty etc.

**Difficulty\*\***:\*\* To keep the Game class clean, this class handles the difficulty adjustments and contains the attributes and methods related with game difficulty.

**Hud:** Hud is the part of the interface that player gets info, remaining hitpoints, score, etc.

**Background:** This class handles the scrolling process of the background, we simply scroll over parts of a big image

**Object:** This class is the base class of every object that is generated inside the game, it also inherits pygame.sprite.Sprite class, so some of the methods are handled by the pygame easily, In situations that we require something more than default pygame method, we simply override the method.

**Ship\*\***:\*\* This class is a child class of object class. Both player and enemy ships inherit this class, So we don’t write the same attributes or methods over and over, simply override if needed.

**EnemyShip\*\***:\*\* This class contains the general attributes and methods shared between enemy ships, for example, we handle the update and move methods of enemy ships in that class.

**TieFighter\*\***:\*\* Default enemy class, they are small ships with a single gun and low attack rate (fire probability).

**StarDestroyer\*\***:\*\* A stronger enemy, that has a wide body (3 tiefighters), three guns, high attack rate and huge hitpoints.

**PlayerShip\*\***:\*\* This class simply represents the player’s ship. It also overrides the draw method because in a special case, when the player has an active shield, we need to call super.draw and also, draw the shield.

**Projectile\*\***:\*\* This class is another child of the Object class, Represents the projectiles in game both created by player and enemy, simply having the owner in an attribute to be able to make decisions when that info is needed.

**Boost\*\***:\*\* This is another child of the Object class, we also may inherit from the projectile itself since it acts similarly, but Projectiles don’t have image and we want to keep it that way, at least for now. When the player collides with a boost, it gets consumed and removed.

**DamageBoost\*\***:\*\* When consumed, Damage of the player increases.

**DoubleGuns\*\***:\*\* When consumed, player start firing two guns instead of one, after its first consumption, it will not be spawned again.

**Shield\*\***:\*\* When consumed, player gains a shield that will block 5 enemy projectiles

**HP_Boost\*\***:\*\* When consumed, player gains 50 hitpoints, maximum hp the player can have is 100.

**Factory\*\***:\*\* We decided to implement the Factory pattern here, this class handles the spawning process of all the objects with static methods, this way, we can handle all the spawning processes from a single place. Also, in some cases, for example while spawning enemies, we have a complicated process, we might create two different ships based on some logic, or might create multiple projectiles instead of a single one, from different parts of the ship, having this logic inside constructors would be confusing.

CPU Player **Use\*\***\-Case Diagram:\*\* ![A black and white background with white ovals
**Use-Case Diagram:**

![Use-Case Diagram](files/Use-Case%20Diagram.png "Use-Case Diagram")

**Explanation\*\***:\*\*

**CPU:**

**Update Game Objects:** Every object controlled by the cpu has an update logic, enemy ships move, fire or change direction, projectiles move up or down, boosts move down. Cpu handles them through the update functions. Also, objects collide with each other, If this collision is between a ship and a projectile that has different owners (player or CPU), ship loses some hitpoints and projectile gets removed. If this collision is between ships, ships change their directions and get teleported to the each other’s side, so they won’t keep colliding.

**Handle** **Spawns:** Based on the difficulty and some fixed rulesets, CPU spawns enemies. Those functions are handled in the Factory class.

**Update Difficulty:** Difficulty of the game increases logarithmically as the time and score increases**.**

Those processes occur independently and are automatically handled by the CPU.

**Player:**

**Start Game:** Starts a game

**Move** **Left/Move Rigth:** Player’s ship moves lef tor right in order to Dodge enemy projectiles or position itself to fire at the horizontal pozition.

**Fire:** Player’s ship creates a projectile at the top middle of its rect. This projectile will be added to the sprite groups to be updated with all the other objects.

**Exit** **Game:** Exits from the game.
