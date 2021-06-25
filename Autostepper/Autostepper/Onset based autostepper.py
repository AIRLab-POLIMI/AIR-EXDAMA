import os, sys
import random
import math
import essentia_onset #to use essentia's onset detection functions
#import librosa_onset #to use librosa's onset detection functions
import shutil#to copy files


# define some global variables used for the chart encoding
arrows = 0  # count the arrows in a line
holds = 0  # count the holds and rolls in a line

total = 0  # total number of arrows and holds at the same moment. Due to the fact that the game has to be played with two hands, this must be capped at two
out_dir = "./OUT/"  # output folder for the data. Folder and subfolder MUST EXIST. Audio preprocessing must be run beforehands
in_dir = "./CONVERTER/"  # input folder name
dance_type = "     kb7-single:\n"  # output chart format
sample_start="30"
sample_lenght="30"
selectable="YES"
out_line_size=7#Number of sensors for the output
difficulties= [0,1,2,3,4] #contain the wanted difficulties. It must be a partition of [0,1,2,3,4]
tollerance=0.1# tollerance, in seconds, for the hard difficulty filter. It is used to find equispaced notes
MAX_LEVEL=12# Highest wanted level. Max level +1 is assigned to all song that exceed the expected amount of arrows


def is_integer_num(n): #check if a number is  an integer
    if isinstance(n, int):
        return True
    if isinstance(n, float):
        return n.is_integer()
    return False


def initialize_scale(max_level):#initialize the scale variable. It contains the amount of arrows required for a song to be assigned a certain level
    x = 1 / 3.2
    beta = 0.90
    beta2=1.0
    scale=[]
    scale.append(x)
    for j in range(max_level-1):
        x = x * (beta+beta2)
        beta *= 0.767
        scale.append(x)
    return scale


def onset_to_chart(onsets, difficulty, scale):# convert an onset sequence into a song of wanted difficulty and appropriate level
    onset_tmp=[]
    flag=0
    #According to the wanted difficulty, a different filter is applied to the onset sequence. Ecpert difficulty (4) is unfiltered
    if (difficulty==3):#hard difficulty locate the costant sequences of notes and remove 1 out 2
        for x in range(len(onsets)):
            if (x==0):
                onset_tmp.append(onsets[x])
            elif(x==1):
                delta_old= onsets[x]-onsets[x-1]
            else:
                delta=onsets[x]-onsets[x-1]
                if (abs(delta-delta_old)>=tollerance or flag==1):
                    onset_tmp.append(onsets[x-1])
                    flag=0
                else:
                    flag=1
                delta_old=delta
        #onset_tmp.append(onsets[-1])
        onsets=onset_tmp
    elif (difficulty==2):#The medium difficulty filter removes 1 note out of 2
        for x in range(len(onsets)):
            if (x%2==0):
                onset_tmp.append(onsets[x])
        #onset_tmp.append(onsets[-1])
        onsets=onset_tmp
    elif (difficulty==1):#The easy difficulty filter removes 3 notes out of 4
        for x in range(len(onsets)):
            if (x%4==0):
                onset_tmp.append(onsets[x])
        onset_tmp.append(onsets[-1])
        onsets=onset_tmp
    elif (difficulty==0):#The beginner difficulty filter removes 7 notes out of 8
        for x in range(len(onsets)):
            if (x%8==0):
                onset_tmp.append(onsets[x])
        #onset_tmp.append(onsets[-1])
        onsets=onset_tmp

    step_number = len(onsets)
    song_lenght=onsets[-1]
    average_steps=step_number/song_lenght#compute the average number of steps per second
    level_flag=0
    for q in range(len(scale)):#The associated level is obtained by taking the index of the lowest value in the scale that surpasee the average notes/sec and summing 1 to it
        if average_steps<scale[q] and level_flag==0:
            level=q+1
            level_flag=1
    if level_flag==0:#if the number of steps/sec is higher than highest scale value, the given level is max_level+1
        level=len(scale)+1
    chart = [[0 for i in range(192)] for j in range(math.ceil(onsets[-1] * bpm / 240))]
    for x in range(len(onsets)):
        measure_index = math.floor(onsets[x] * bpm / 240)
        arrow_index = (onsets[x] - (measure_index * 240 / bpm)) / (240 / bpm)
        arrow_index = math.floor(arrow_index * (192))
        chart[measure_index][arrow_index] = 1
    return chart, level


file_list = []  # initialize the list that will contain the path of all files that need conversion
for root, dirs, files in os.walk(in_dir, topdown=False):  # search in the directory and every subdirectory
    for name in files:
        if (name.endswith('.ogg') or name.endswith('.mp3') or name.endswith('.wav')):  # add to the list all .sm files
            file_list.append(os.path.join(root, name))

print("Files found for conversion: " + str(len(file_list)))
# note: POSITIVE offset mean that the chart start BEFORE the song. negative offset that the chart start after the song. The value is expressed in seconds
i = 0  # file counter to print a progressive value during processing
f_to_convert=len(file_list)
for file_name in file_list:  # main loop encoding all files
    #onsets=essentia_onset.hfc_onset(file_name)
      #same as the complex one, tough a littele worse probably
    #onsets=essentia_onset.complex_onset(file_name)
      #onset complex is "correlated" to the sound, while it always predict in a balanced way, it has several
      #false positives, decent overall but not great
    #onsets=librosa_onset.standard_onset(file_name)
      #incostant, it goes from almost perfect prediction to severe underprdediction. few false positive.
      # Most efficient one overall, when it works
    #onsets=librosa_onset.superflux_onset(file_name)
      #Superflux is incostant, it might go from random prdictions, to perfect to heavily note unprediction.
      #it seems that aside from a set of sounds for which it works extremely well it's not worth
    #onsets= essentia_onset.complex_phase_onset(file_name)
      #while the positives' densitity is correlable with the music, the exact location seems random
    #onsets=essentia_onset.rms_onset(file_name)
      #Severely overpredict, it often resemble a stream
    #onsets=essentia_onset.flux_onset(file_name)
        #strong overprediction
    #onsets=essentia_onset.melflux_onset(file_name)
        #overpredicts a lot but manage to keep itself in line with the msic, possible use for high difficulties
    #onsets=essentia_onset.beat_emphasis_onset(file_name)

    #onsets=essentia_onset.infogain_onset(file_name)
    onsets=essentia_onset.mix_onset(file_name)
    print("\n")
    print("Encoding " + file_name)
    i += 1
    print("File number " + str(i))
    print("Onsets found" + str(len(onsets)))
    out_data = ''
    data = ''
    offset="0"
    bpm=150
    bpm=str(bpm)
    difficulty_scale=initialize_scale(MAX_LEVEL)
    title = file_name.split("/")[-1]
    #out_file_name=title.removesuffix(".mp3")
    #out_file_name = title.removesuffix(".ogg")
    #out_file_name = title.removesuffix(".wav")
    song_name=title[0:-4]
    #print(out_file_name)
    #print(title)

    try:
        os.mkdir(out_dir+song_name)
    except:
        pass
    out_file_name = out_dir +song_name+ "/"+ song_name+ ".sm"
    print(file_name)
    print(out_dir+title)
    shutil.copyfile(file_name, out_dir+song_name+"/"+title, follow_symlinks=True)
    #os.system("cp "+ file_name+" " + out_dir+title)
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------
    with open(out_file_name, "w") as f_out:
            title = file_name.split("/")[-1]
            print(f"Converting \"{title}\". File number {i}/{f_to_convert}")
            # title=title.replace(".dat", "")
            # f_out.write("#TITLE:" + title + ";\n")
            f_out.write("#MUSIC:" + title + ";\n")
            f_out.write("#OFFSET:" + offset + ";\n")
            f_out.write("#SAMPLESTART:" + sample_start + ";\n")
            f_out.write("#SAMPLELENGHT:" + sample_lenght + ";\n")
            f_out.write("#SELECTABLE:" + selectable + ";\n")
            f_out.write("#BPMS:0.000=" + bpm + ".000;\n")
            f_out.write("#STOPS:;\n")
            bpm=int(bpm)
            for x in range(len(difficulties)):
                f_out.write("#NOTES:\n     kb7-single:\n     :\n     ")  # write the necessary metadata for the chart (#NOTES section)
                difficulty=difficulties[x]
                chart, level=onset_to_chart(onsets, difficulty, difficulty_scale)
                if (difficulty == 0):
                    diff = "Beginner"
                    prob_diff=[0, 0.05,0.3,0.3,0.3,0.05,0]
                elif (difficulty == 1):
                    diff = "Easy"
                    prob_diff = [0.04, 0.07, 0.26, 0.26, 0.26, 0.07, 0.04]
                elif (difficulty == 2):
                    diff = "Medium"
                    prob_diff = [0.07, 0.14, 0.19, 0.20, 0.19, 0.14, 0.07]
                elif (difficulty == 3):
                    diff = "Hard"
                    prob_diff = [1/7, 1/7, 1/7, 1/7, 1/7, 1/7, 1/7]
                elif (difficulty == 4):
                    diff = "Expert"
                    prob_diff = [1/7, 1/7, 1/7, 1/7, 1/7, 1/7, 1/7]
                else:
                    sys.exit("Unrecognized difficulty code: " + str(diff))
                f_out.write(diff + ":\n     ")
                f_out.write(str(level) + ":\n     :\n")
                #f_out.write(str((difficulty * 2) + 2) + ":\n     :\n")  # since the level is arbitary for AI gener
        # -----------------------------------------------------------------------------------------------------------------------------------------------------

                for x in range(len(chart)):
                    for x2 in range(len(chart[x])):
                        if chart[x][x2] == 0:
                            f_out.write(('0' * out_line_size) + "\n")
                        elif chart[x][x2] == 1:  # in case an arrow is due, the position is randomly allocated
                            #arrow_pos = random.randint(0, out_line_size - 1)
                            arrow_pos=random.random()
                            cumulative_prob=0
                            for x3 in range(7):
                                cumulative_prob += prob_diff[x3]
                                if (cumulative_prob>arrow_pos):
                                    arrow_pos=x3+2
                            if not(is_integer_num(arrow_pos)):
                                arrow_pos=6+2
                            arrow_pos-=2
                            f_out.write('0' * arrow_pos + '1' + '0' * (out_line_size - (arrow_pos + 1)) + '\n')
                    f_out.write(",\n")
                f_out.write(";\n\n")

        # ---------------------------------------------------------------------------------------------------------


# open new file in the llist and fo at it again
