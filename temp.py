# data = pickle_read('rep')
# major = pickle_read('concat_major')
#
# count = 0
# set1 = set()
# new_major = []
# for (score, id_list) in major:
#     flag = False
#     for idx in id_list:
#         for prog in data:
#             if prog.id == idx and 'Melody' in prog.meta['source']:
#                 flag = True
#     if not flag:
#         new_major.append((score, id_list))
# print(new_major)
#
# for (score, id_list) in new_major:
#     if len(id_list) == 1:
#         set1.add(tuple(id_list))
# list1 = list(set1)
# list1 = [(1, i) for i in list1]
# print(len(list1))
# print(list1)
# file = open('chorderator/static/new_major_score(no dup, no melody, no concat).mdch', 'wb')
# pickle.dump(list1, file)