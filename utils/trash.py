# # ####################
# # keys / metres / type
# # ####################
# fig, axs = plt.subplots(2, 2, figsize=(15, 12))
#
# key_dict = {}
# metre_dict = {}
# type_dict = {}
# mode_dict = {}
# for progression in prog_list:
#     if progression.meta['tonic'] not in key_dict:
#         key_dict[progression.meta['tonic']] = 1
#     else:
#         key_dict[progression.meta['tonic']] += 1
#     if progression.meta['metre'] not in metre_dict:
#         metre_dict[progression.meta['metre']] = 1
#     else:
#         metre_dict[progression.meta['metre']] += 1
#     if progression.meta['type'] not in type_dict:
#         type_dict[progression.meta['type']] = 1
#     else:
#         type_dict[progression.meta['type']] += 1
#     if progression.meta['mode'] not in mode_dict:
#         mode_dict[progression.meta['mode']] = 1
#     else:
#         mode_dict[progression.meta['mode']] += 1
# print(key_dict)
# print(metre_dict)
# print(type_dict)
# print(mode_dict)
# axs[0, 0].bar(key_dict.keys(), key_dict.values())
# axs[0, 0].set_title("Key Statistics")
# axs[0, 0].set(xlabel="Tonic", ylabel="Appeared Times")
# axs[0, 1].bar(metre_dict.keys(), metre_dict.values())
# axs[0, 1].set_title("Metre Statistics")
# axs[0, 1].set(xlabel="Metre", ylabel="Appeared Times")
# axs[1, 0].bar(mode_dict.keys(), mode_dict.values())
# axs[1, 0].set_title("Mode Statistics")
# axs[1, 0].set(xlabel="Mode", ylabel="Appeared Times")
# axs[1, 1].bar(type_dict.keys(), type_dict.values())
# axs[1, 1].set_title("Type Statistics")
# axs[1, 1].set(xlabel="Type", ylabel="Appeared Times")
#
# plt.xticks([i for i in range(len(type_dict))], type_dict.keys(), rotation=90)
# plt.show()


# # ###
# weird
# # ###
# plt.figure(figsize=(15, 12))
# count_weird = 0
# for progression in prog_list:
#     for i in progression:
#         if type(i) is not int:
#             count_weird += 1
#             break
# print(count_weird)
# plt.pie([count_weird, len(prog_list) - count_weird], explode=[0.05, 0], labels=["Weird", "Normal"])
# plt.show()


# # ######################
# # patterns types 3d plot
# # ######################
# progression_logic = {}
# for progression in prog_list:
#     if progression.meta["metre"] == "4/4":
#         logic = list()
#         memo = -1
#         for i in progression:
#             if i != memo:
#                 memo = i
#                 logic.append(i)
#                 if len(logic) == 4:
#                     pattern = ""
#                     for j in logic:
#                         pattern += str(j)
#                     logic = (pattern, progression.meta["type"])
#                     if logic not in progression_logic.keys():
#                         progression_logic[logic] = 1
#                     else:
#                         progression_logic[logic] += 1
#                     logic = list()
# new_prog_logic = {}
# for item in progression_logic.items():
#     for i in item[0][0]:
#         if type(i) is float:
#             break
#     else:
#         new_prog_logic[item[0]] = item[1]
# progression_logic = {k: v for k, v in sorted(new_prog_logic.items(), key=lambda item: item[1], reverse=True)}
# print(progression_logic)
#
# new_prog_logic = {}
# number = 40
# for item in progression_logic.items():
#     new_prog_logic[item[0]] = item[1]
#     number -= 1
#     if number == 0:
#         break
# progression_logic = new_prog_logic
#
# number_pattern_map = {}
# number_type_map = {}
# count_pattern = 0
# count_type = 0
# for item in progression_logic.items():
#     pattern = item[0][0]
#     type = item[0][1]
#     times = item[1]
#     if pattern not in number_pattern_map.values():
#         number_pattern_map[count_pattern] = pattern
#         count_pattern += 1
#     if type not in number_type_map.values():
#         number_type_map[count_type] = type
#         count_type += 1
#
# type_number_map = {type: number for number, type in number_type_map.items()}
# pattern_number_map = {pattern: number for number, pattern in number_pattern_map.items()}
# new_prog_logic = {}
# for item in progression_logic.items():
#     mapped_type = type_number_map[item[0][1]]
#     mapped_pattern = pattern_number_map[item[0][0]]
#     new_prog_logic[(mapped_pattern, mapped_type)] = item[1]
# print(new_prog_logic)
#
# x = [x[0] for x in new_prog_logic.keys()]
# y = [y[1] for y in new_prog_logic.keys()]
# z = [z for z in new_prog_logic.values()]
#
# cmap = plt.get_cmap('RdYlBu', len(z))
# colors = cmap(range(cmap.N))
#
# indexx = [i for i in range(len(set(x)))]
# indexy = [i+0.5 for i in range(len(set(y)))]
# zeros = np.zeros_like(x)
# fig = plt.figure(figsize=(30, 24))
# ax = plt.axes(projection='3d')
# ax.bar3d(x, y, zeros, 1, 1, z,color=colors)
# plt.xticks(indexx, [number_pattern_map[i] for i in indexx])
# plt.yticks(indexy, [number_type_map[i-0.5] for i in indexy])
# plt.show()
