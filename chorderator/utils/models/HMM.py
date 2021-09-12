import numpy as np
from copy import deepcopy

np.set_printoptions(linewidth=150)


class MyHiddenMarkovModel():

    def __init__(self, hidden_states_num, observation_num, orders=2, transform_prob=None, original_emission_prob=None):
        self.hidden_states_num = hidden_states_num
        self.orders = orders
        self.observations_num = observation_num
        self.transform_prob = np.zeros(shape=[hidden_states_num for i in range(orders + 1)])
        if transform_prob and original_emission_prob:
            self.fit(transform_prob, original_emission_prob)

    def fit(self, tranform_prob, original_emission_prob):
        if self.transform_prob.shape == tranform_prob.shape:
            self.transform_prob = tranform_prob
        else:
            raise ValueError("Shape of fitting data not matched with hidden states number or orders")
        if original_emission_prob.shape[0] == self.hidden_states_num and original_emission_prob.shape[
            1] == self.observations_num:
            self.original_emission_prob = original_emission_prob
        else:
            raise ValueError("Shape of fitting data not matched with hidden states number or observation number")

    def predict(self, x):
        # calculate the real emission probability according to the real observations from x and the original emission
        # probability
        real_emission_prob = np.zeros(shape=[self.hidden_states_num for i in range(self.orders)] + [len(x)])
        count_observations = 0
        for observation in x:
            for i in range(self.hidden_states_num):
                note_num = len(observation)
                total_prob = 0
                for note in observation:
                    total_prob += self.original_emission_prob[i, int(note) - 1]
                total_prob /= note_num
                real_emission_prob[:, i, count_observations] = total_prob
            count_observations += 1

        # Normalize
        for i in real_emission_prob:
            for j in i:
                j[:] = j[:] / sum(j)

        # convert transformation probability to foundational graph
        graph = self._trans2graph(len(x))
        # alter graph with observations
        for i in range(len(x)):
            for j in range(graph.shape[1]):
                for k in range(graph.shape[2]):
                    graph[i, j, k] = graph[i, j, k] * real_emission_prob[
                        k // self.hidden_states_num, k % self.hidden_states_num, i]
        # Absorb to T at the first state, and to D at the last state
        graph[0, :, 0:3] = 0
        graph[0, :, 4:6] = 0
        graph[0, :, 7:9] = 0
        graph[len(x) - 1, :, 0:1] = 0
        graph[len(x) - 1, :, 2:7] = 0
        graph[len(x) - 1, :, 8:9] = 0

        # solve graph using viterbi algorithm
        y = self._viterbi(graph)
        return y

    @staticmethod
    def _viterbi(graph):
        memo = {}
        for i in range(graph.shape[1]):
            memo[i] = ["", 1]
        for i in range(graph.shape[0]):
            new_memo = deepcopy(memo)
            for j in range(graph.shape[1]):
                max_prob = 0
                state_with_max_prob = 0
                for k in range(graph.shape[1]):
                    temp_prob = memo[k][1] * graph[i, k, j] * 10
                    if temp_prob > max_prob:
                        max_prob = temp_prob
                        state_with_max_prob = k
                new_memo[j] = [memo[state_with_max_prob][0] + str(j), max_prob]
            memo = deepcopy(new_memo)
        max_prob = 0
        route = ""
        for item in memo.items():
            if item[1][1] > max_prob:
                route = item[1][0]
                max_prob = item[1][1]
        return route

    def __str__(self):
        str_ = "Hidden Markov Model"
        return str(self.transform_prob)

    def _trans2graph(self, observations):
        graph = np.zeros(shape=[observations] + [self.hidden_states_num ** self.orders for i in range(2)])
        for i in range(self.hidden_states_num):
            for j in range(self.hidden_states_num):
                for k in range(self.hidden_states_num):
                    graph[:, i * self.hidden_states_num + j, j * self.hidden_states_num + k] = self.transform_prob[
                        i, j, k]
        return graph


if __name__ == '__main__':
    hmm = MyHiddenMarkovModel(3, 7)  # Hidden: T, D, S <-> Observations (not actual): 1, 2, 3, 4, 5, 6, 7
    transform_prob = np.array(
        [[[0, 0, 0],
          [0.5, 0, 0.5],
          [0.5, 0.5, 0]],
         [[0, 0.5, 0.5],
          [0, 0, 0],
          [1, 0, 0]],
         [[0, 0.5, 0.5],
          [1, 0, 0],
          [0, 0, 0]]])
    original_emission_prob = np.array(
        [[0.3, 0.05, 0.2, 0.05, 0.25, 0.05, 0.05],  # T emission to 1-7
         [0.05, 0.25, 0.05, 0.05, 0.3, 0.05, 0.2],  # D emission to 1-7
         [0.25, 0.05, 0.05, 0.3, 0.05, 0.2, 0.05]]  # S emission to 1-7
    )
    hmm.fit(tranform_prob=transform_prob, original_emission_prob=original_emission_prob)
    data = np.array(["53331","6","3331","2"])
    route = hmm.predict(data)
    for i in route:
        if i == "0" or i == "3" or i == "6":
            print("T")
        elif i == "1" or i == "4" or i == "7":
            print("D")
        else:
            print("S")
