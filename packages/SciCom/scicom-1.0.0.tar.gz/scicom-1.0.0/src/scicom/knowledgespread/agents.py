
import mesa
import networkx as nx

from scicom.knowledgespread.utils import ageFunction, epistemicRange


class ScientistAgent(mesa.Agent):
    """A scientist with an idea.
    
    Each scientist has a geographic position, is related to other
    agents by a social network, and is intialized with a starttime, that
    describes the year at which the agent becomes active. 
    """

    def __init__(
        self,
        unique_id,
        model,
        pos: tuple,  # The projected position in 2D epistemic space. For actual movements and neighborhood calculations take into account z coordinate as well.
        topicledger: list,  # Representing the mental model of the agent: A list of all visited topics represented as triples [(x,y,z), (x,y,z)]
        geopos: tuple,  # Representing scientific affiliation, a tuple of latitude/longitude of current affiliation. Could also keep track of previous affiliations
        birthtime: int,  # A step number that represents the timestep at which the scientist becomes active
        productivity: tuple,  # Parameters determining the shape of the activation weight function
        opposition: bool = False,  # Whether or not an agent is always oposing new epistemic positions.
    ):
        super().__init__(unique_id, model)
        self.pos = pos
        self.a = productivity[0]
        self.b = productivity[1]
        self.c = productivity[2]
        self.topicledger = topicledger
        self.geopos = geopos
        self.birthtime = birthtime
        self.age = 0
        self.opposition = opposition

    def _currentActivationWeight(self) -> float:
        """Return an age dependent activation weight.

        A bell-shaped function with a ramp, plateuax and decend.
        Can be drawn from random distribution in model initialization.
        """
        return ageFunction(self, self.a, self.b, self.c, radius=1)

    def _changeEpistemicPosition(self, neighbors):
        """Calculate the change in epistemic space.

        From all neighbors select one random choice.
        To update the agents position, determine the heading 
        towards the selected neighbor. If the agent is an
        oposing one, inverte the direction. Then select a 
        random amount to move into the selected direction.
        The new position is noted down in the topic ledger
        an the the agent is moved.
        """
        # Select random elemt from potential neighbors
        neighborID = self.random.choice(neighbors)
        if isinstance(neighborID, (float, int)):
            neighbors = [
                x for x in self.model.schedule.agents if x.unique_id == neighborID
            ]
            if neighbors:
                neighbor = neighbors[0]
            else:
                return
        else:
            neighbor = neighborID
        # Get heading
        direction = self.model.space.get_heading(self.pos, neighbor.pos)
        # Some agents always opose the epistemic position and therefore move in the oposite direction
        if self.opposition is True:
            direction = (- direction[0], - direction[1])
        # Select new postion with random amount into direction of neighbor
        amount = self.model.random.random()
        new_pos = (self.pos[0] + amount * direction[0], self.pos[1] + amount * direction[1])
        # New mental position
        topic = (new_pos[0], new_pos[1], self.model.random.random())
        try:
            # Move agent
            self.topicledger.append(topic)
            self.model.space.move_agent(self, new_pos)
        except:
            # Out of bounds of epi space
            # TODO: What is a sensible exception of movement in this case.
            # Current solution: Append topic to ledger but do not move
            self.topicledger.append(topic)

    def updateSocialNetwork(self):
        """Create new links in agents social network."""

    def moveGeoSpace(self):
        pass

    def moveSocSpace(self, maxDist=1):
        """Change epistemic position based on social network."""
        neighbors = []
        currentTime = self.model.schedule.time
        G = self.model.socialNetwork
        H = nx.Graph(((u, v, e) for u, v, e in G.edges(data=True) if e["time"] <= currentTime))
        for dist in range(0, maxDist + 1, 1):
            neighb = nx.descendants_at_distance(
                H,
                self.unique_id,
                dist,
            )
            neighbors.extend(list(neighb))
        if neighbors:
            self._changeEpistemicPosition(neighbors)
            return True
        else:
            return False

    def moveEpiSpace(self):
        """Change epistemic position based on distance in epistemic space."""
        neighbors = self.model.space.get_neighbors(
            self.pos,
            radius=epistemicRange(
                self.model.epiRange,
                self.model.schedule.time - self.birthtime,
            ),
        )
        if neighbors:
            self._changeEpistemicPosition(neighbors)
        else:
            # Random search for new epistemic position
            direction = (self.model.random.random(), self.model.random.random())
            new_pos = self.model.random.random() * direction
            self.model.space.move_agent(self, new_pos)

    def attendConference(self):
        pass

    def step(self):
        """Agents activity starts after having reached the birthtime.
        
        After initial start, at each step the agents age is increased by one.
        Each agent has a randomly generated age-dependent activation 
        probability. Moveing happens first due to social connections. If 
        no move due to social connections was possible, a move due to 
        epistemic space search is attempted.

        Once the possible activation weight drops below a threshold, 
        the agent is removed from the schedule.
        """
        if self.model.schedule.time < self.birthtime:
            pass
        elif self._currentActivationWeight() <= 0.00001 and self.age > 1:
            self.model.schedule.remove(self)
            # self.age += 1
        else:
            self.age += 1
            currentActivation = self.model.random.choices(
                population=[0, 1],
                weights=[
                    1 - self._currentActivationWeight(), self._currentActivationWeight(),
                ],
                k=1,
            )
            if currentActivation[0] == 1:
                # TODO: Should the choice of movement be another random process?
                res = self.moveSocSpace()
                if res is False:
                    self.moveEpiSpace()
