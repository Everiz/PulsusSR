map_file = input("map? ")
with open(f"examples/{map_file}.txt", "r") as f:
    notes = f.read()
notes = notes.split("\n")
notes = [x for x in notes if x != ""] # remove trailing newline
rate = float(input("rate? "))
rate = min(max(rate, 0.5), 2)
for i in range(len(notes)): # get note data - position, time, hold, hold time (if a hold)
    temp = notes[i][1:-1].split(",")
    notes[i] = [int(temp[0]),int(float(temp[1])*(1000/rate)),(temp[2] == "1"),int(float(temp[3])*(1000/rate))]


first_hand = (notes[0][0] != 0)
hand = bool(first_hand)
hands = []
streak = 0
streaks = []
streak_total = [0]

for note in notes: # handing pass
    if (note[0]%3 == 0 and hand) or (note[0]%3 == 2 and not hand):
        hand = not hand
        streak_total += [streak+streak_total[-1]]
        streaks.append(streak)
        streak = 0
    hands.append(hand)
    streak += 1
if streak >= 1:
    hand = not hand
    streak_total += [streak+streak_total[-1]]
    streaks.append(streak)

for i in range(len(streaks)):
    if streaks[i] > 3: # convert to full alt
        for j in range(streak_total[i]+1,streak_total[i]+streaks[i],2):
            hands[j] = not hands[j]

streak = 0
streaks = []
streak_total = [0]

for i in range(len(hands)): # get the new streaks
    if (hands[i] != hands[i-1]) and i > 0:
        streak_total += [streak+streak_total[-1]]
        streaks.append(streak)
        streak = 0
    streak += 1
if streak >= 1:
    streak_total += [streak+streak_total[-1]]
    streaks.append(streak)


for i in range(1,5):
    print(i*len([x for x in streaks if x == i]))
streak_multipliers = [0,1,0.77,1.2,1]
note_multipliers = []
hand = bool(first_hand)
meta_streaks = [[0 for i in range(5)],[0 for i in range(5)]]
hands = []

for streak in streaks: # pattern multipliers 
    multiplier = 0
    current_streak = 0
    for i in range(5):
        if streak == i + 1:
            current_streak = meta_streaks[hand][i] 
            meta_streaks[hand][i] += 1
        else:
            meta_streaks[hand][i] = max(0,meta_streaks[hand][i]-(2+(meta_streaks[hand][i]//3)))
    hands += [hand] * streak
    hand = not hand
    multiplier = (((0.85**(current_streak))+5)/6)**1.5 # crank the exponent up for lulz
    note_multipliers += [multiplier*streak_multipliers[streak]]*streak


print(sum(note_multipliers)/len(note_multipliers))
hold_stack = [[],[]]
strain_exp = [1,1]
current_strain = [0,0]
last_notes = [0,0]
note_strain = 0
section_start = notes[0][1]
section_strains = []
graph_starts = []
section = []

for i in range(len(notes)): # strain pass
    note = notes[i]
    hand = hands[i]
    
    # check and remove holds that have been released
    hold_stack[hand] = [x for x in hold_stack[hand] if x > note[1]]
    
    if note[1] >= section_start + (400/rate):
        section_strains.append(max(section))
        graph_starts.append(section_start)
        section = []
        section_start += (400/rate)
    
    if i != 0:
        note_strain = current_strain[hand]
        dt = (note[1] - notes[i-1][1]) / 1000
        strain_exp[hand] = (note[1] - notes[last_notes[hand]][1]) / 1000
        vert_diff = abs((note[0]//3)-(notes[last_notes[hand]][0]//3))
        vert_mul = 1+(vert_diff/((6+ (strain_exp[hand]) /20)))
        if notes[i-1][1] + 10 > note[1]: # chord detection, with a small chording window
            current_strain[hand] += note_multipliers[i] * vert_mul * ((1 + (len(hold_stack[hand])*2)) / (12 + (3*current_strain[hand])))
        else: # do strain right
            current_strain[hand] += note_multipliers[i] * vert_mul * (3 + (len(hold_stack[hand])**0.4 * 3) + note[2]) \
                                    / (15 + (3*current_strain[hand]))
        current_strain[0] *= (0.63 ** dt)
        current_strain[1] *= (0.63 ** dt)
        last_notes[hand] = i
    else:
        note_strain = current_strain[hand] 
 
    if note[2] == True: # hold
        hold_stack[hand].append(note[1] + note[3])

    section.append((current_strain[hand]**1.2)+(current_strain[not hand]) ** (1/1.2))

section_strains.append(max(section))
graph_starts.append(section_start)

graph_starts = [x/1000 for x in graph_starts]
graph_strains = [x for x in section_strains]
roll_amt = 2  # num of sections to avg across (in each direction)
graph_strains_roll = [sum(section_strains[min(max(y, 0), len(section_strains)-1)] for y in range(x-roll_amt, x + roll_amt + 1))/(roll_amt*2+1) for x in range(len(section_strains))]  # this sucks - snekk

# print((section_strains.index(max(section_strains))*(400/rate))+notes[0][1])
section_strains.sort(reverse=True)
section_strains = [x for x in section_strains if x > 0]

for i in range(len(section_strains)):
    section_strains[i] /= (1.5+i)


#print(sum(section_strains))
#"""
star_rating = ((sum(section_strains)+0.2)**0.83)/2.2
diff_pulse = (star_rating**2.2)*5/2
acc_pulse = (star_rating**2.7)*8/5
max_pulse = (( (diff_pulse**(1/1.1)) + (acc_pulse**(1/1.1)) ) ** 1.1)
print(star_rating)
print(max_pulse)
#"""
input()
