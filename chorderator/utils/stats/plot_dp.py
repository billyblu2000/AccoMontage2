import json
import os
import pickle

from matplotlib import pyplot as plt

from settings import static_storage

if __name__ == '__main__':

    root_folder = '/Users/billyyi/PycharmProjects/Chorderator/output'
    stats = {}
    all_stats = {}
    rep = pickle.load(open(static_storage['rep'], 'rb'))
    id_label_map = {i.id:i.progression_class['new_label'] for i in rep}
    id_label_lenghth_map = {i.id: (i.progression_class['new_label'], len(i), i.meta['mode']) for i in rep}
    for j in id_label_lenghth_map.values():
        if j[0] == 'dark':
            print('dark', j[2])
        if j[0] == 'r&b':
            print('r&b', j[2])
    for file in os.listdir(root_folder):
        if file[-5:] == '.json':
            file = open(os.path.join(root_folder, file), 'r')
            data = json.load(file)
            for i in data:
                for j in i:
                    for progression_id in j['progression_ids']:
                        if progression_id not in all_stats:
                            all_stats[progression_id] = [0, 0, 0]
                            all_stats[progression_id].append(id_label_map[progression_id])
                    for progression_id in j['progression_ids']:
                        all_stats[progression_id][0] += j['micro']
                        all_stats[progression_id][2] += 1
                        if len(j['macro']) != 0:
                            all_stats[progression_id][1] += sum(j['macro']) / len(j['macro'])

    for file in os.listdir(root_folder):
        if file[-5:] == '.json':
            file = open(os.path.join(root_folder, file), 'r')
            data = json.load(file)
            path = max(data[-1], key=lambda x: x['cumulative'])['path']
            path = [data[i][path[i]] for i in range(len(path))]

            last = []
            for i in range(len(path)):

                for progression_id in path[i]['progression_ids']:
                    if progression_id not in stats:
                        stats[progression_id] = [0, 0, 0]
                        stats[progression_id].append(id_label_map[progression_id])

                if i != 0:
                    transition = path[i]['macro'][path[i]['path'][-2]]
                    if i == 1:
                        for progression_id in path[i]['progression_ids']:
                            stats[progression_id][1] += transition / 2
                        for progression_id in last:
                            stats[progression_id][1] += transition
                    elif i == len(path) - 1:
                        for progression_id in path[i]['progression_ids']:
                            stats[progression_id][1] += transition
                        for progression_id in last:
                            stats[progression_id][1] += transition / 2
                    else:
                        for progression_id in path[i]['progression_ids']:
                            stats[progression_id][1] += transition / 2
                        for progression_id in last:
                            stats[progression_id][1] += transition / 2

                for progression_id in path[i]['progression_ids']:
                    stats[progression_id][0] += path[i]['micro']
                    stats[progression_id][2] += 1

                last = path[i]['progression_ids']

    # plot 1
    stats = {k: v for k, v in sorted(stats.items(), key=lambda item: item[0], reverse=False)}
    all_stats = {k: v for k, v in sorted(all_stats.items(), key=lambda item: item[0], reverse=False)}
    all_stats_dark = {}
    all_stats_pop = {}
    all_stats_rb = {}
    for key, value in all_stats.items():
        if value[3] == 'dark':
            all_stats_dark[key] = value
        elif value[3] == 'r&b':
            all_stats_rb[key] = value
        else:
            all_stats_pop[key] = value
    print(stats)
    print(all_stats)
    # plt.bar(x=list(stats.keys()), height=[i[2] for i in stats.values()])
    # plt.show()
    # plt.bar(x=list(stats.keys()), height=[i[0] / i[2] for i in stats.values()])
    # plt.show()
    # plt.bar(x=list(stats.keys()), height=[i[1] / i[2] for i in stats.values()])
    # plt.show()
    plt.bar(x=list(all_stats.keys()), height=[i[2] for i in all_stats.values()])
    plt.title('all, count id')
    plt.show()
    plt.bar(x=list(all_stats.keys()), height=[i[0] / i[2] for i in all_stats.values()])
    plt.title('all, avg micro')
    plt.show()
    plt.bar(x=list(all_stats.keys()), height=[i[1] / i[2] for i in all_stats.values()])
    plt.title('all, avg macro')
    plt.show()

    plt.bar(x=list(all_stats_dark.keys()), height=[i[2] for i in all_stats_dark.values()])
    plt.title('dark, count id')
    plt.show()
    plt.bar(x=list(all_stats_dark.keys()), height=[i[0] / i[2] for i in all_stats_dark.values()])
    plt.title('dark, avg micro')
    plt.show()
    plt.bar(x=list(all_stats_dark.keys()), height=[i[1] / i[2] for i in all_stats_dark.values()])
    plt.title('dark, avg macro')
    plt.show()

    plt.bar(x=list(all_stats_rb.keys()), height=[i[2] for i in all_stats_rb.values()])
    plt.title('r&b, count id')
    plt.show()
    plt.bar(x=list(all_stats_rb.keys()), height=[i[0] / i[2] for i in all_stats_rb.values()])
    plt.title('r&b, avg micro')
    plt.show()
    plt.bar(x=list(all_stats_rb.keys()), height=[i[1] / i[2] for i in all_stats_rb.values()])
    plt.title('r&b, avg macro')
    plt.show()

    plt.bar(x=list(all_stats_pop.keys()), height=[i[2] for i in all_stats_pop.values()])
    plt.title('rest, count id')
    plt.show()
    plt.bar(x=list(all_stats_pop.keys()), height=[i[0] / i[2] for i in all_stats_pop.values()])
    plt.title('rest, avg micro')
    plt.show()
    plt.bar(x=list(all_stats_pop.keys()), height=[i[1] / i[2] for i in all_stats_pop.values()])
    plt.title('rest, avg macro')
    plt.show()