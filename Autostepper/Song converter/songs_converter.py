import os, sys
import random

#define some global variables used for the chart encoding
arrows=0 #count the arrows in a line
holds=0#count the holds and rolls in a line

total=0#total number of arrows and holds at the same moment. Due to the fact that the game has to be played with two hands, this must be capped at two
out_dir="./OUT/"#output folder for the data. Folder and subfolder MUST EXIST. Audio preprocessing must be run beforehands
in_dir="./CONVERTER/"#input folder name
out_step_size=7#number of sensors for the ouput format
in_step_size=4#number of sensors for the input format
hold_status=[0]*in_step_size#keep track of the holds in the input chart
memo=[[-1,-1],[-1,-1]]#keep track of the relation between input hold and output hold. It has two slots that keep track of respectively the input and the output index of the hold
dance_type="     kb7-single:\n"#output format

def tot():#This is a macro that computes the number of commands in a chart's line (arrows+holds)
	global total
	total=arrows+holds

def encode_line(line):#encode a line in the desired output format. Everything aside holds, rolls=holds and arrows is discarded and they are capped to 2 per line
	global arrows #obtain acces to global variables
	global holds
	global total
	global encode
	global in_step_size
	global out_step_size
	global memo
	arrows=0 #initialize variables
	holds=0
	corrector=0#keep track of the holds that end whhile parsing a line
	if (len(line)!=in_step_size+1):
		sys.exit("non standard chart beat line detected. Input line= " + line) # terminate the the program if an unexpected chart format is found (not n_in character long ("\n" taken into account), with non-numerical or non mines commands and not terminating with a new line
	for x in range(in_step_size):#count how many holds, rolls and arrows are present in a line. Rolls are considered as holds for this
		if( line[x]=='1'):
			arrows+=1
		elif (line[x]=='2'):
			if (sum(hold_status)+corrector<2):#holds/rolls are capped to 2 already to avoid some errors (they would have been capped eitherway since 2 commands max at a time is a game prerequisite)
				holds+=1
				hold_status[x]=1
		elif (line[x]=='4'):
			if (sum(hold_status)+corrector<=2):
				holds+=1
				hold_status[x]=1
		elif (line[x]=='3'):
			if (hold_status[x]!=0):
				hold_status[x]=0
				corrector+=1
	tot() #compute the total number of commands in a line
	if (total>2):# if i have more than 2 commands, some information is omitted till i have no more than 2, in order of removal:
		if (holds>2): #holds are capped to 2
			holds=2
		tot()
		if (total>2):
			if (arrows>2): #arrows are capped to 2
				arrows=2
		tot()
		if (total>2):
			if (arrows>1): #arrows are capped to 1
				arrows=1
		tot()
		if (total>2):
			if (arrows>0): #arrows are capped to 0
				arrows=0
		tot()
		if (total>2): #if i get here an unforseen scenario has happened and the code returns an error
			sys.exit("critical error,step encoding not possible, line has value: " +line)
	encode=[0]*out_step_size#initialize the variable holding the encoded line

	if (memo[0][0]>=0):#if an hold is progress (first memo slot)
		holds-=1
		if (line[memo[0][0]]=="3"):#if it's ending the memo is restored to default (and the appropriate terminal character is encoded)
			encode[memo[0][1]]=3
			memo[0][0]=-1
			memo[0][1]=-1
	if (memo[1][0]>=0):#repeat the same of the first memo slot
		holds-=1
		if (line[memo[1][0]]=="3"):
			encode[memo[1][1]]=3
			memo[1][0]=-1
			memo[1][1]=-1

	x2=0
	for x in range(holds):#the eventually remaining holds are all starts and are added
		while(True):
			if (line[x2]=="2" or line[x2]=="4"):#to simplify things (especially since no real way to determine the best one exist) in case of "hands" commands, first come fist served from left to right between different holds and rolls
				i=random.randint(0, out_step_size-1)#Find an availbale index (must not superimpose on precedent commands)
				while (encode[i]!=0 or memo[0][1]==i or memo[1][1]==i):
					i=random.randint(0, out_step_size-1)
				encode[i]=line[x2]
				if(memo[0][0]==-1):#update the memo
					memo[0][0]=x2
					memo[0][1]=i
				elif(memo[1][0]==-1):
					memo[1][0]=x2
					memo[1][1]=i
				else:
					print("holds, memo1")
					print(holds)
					print(memo)
					sys.exit("abnormal amount of holds detected: "+line)#if both the memo slot are used something unexpected happened
				x2+=1
				break
			x2+=1
			if (x2>=in_step_size):#if it can't find any hold head in the given line an error has occurred
				print("holds, memo1")
				print(holds)
				print(memo)
				sys.exit("Abnormality in holds encoding happened: "+line)
	for x in range (arrows):#add the remaining arrows in the remaninig free slots
		i=random.randint(0,out_step_size-1)
		while (encode[i]!=0 or memo[0][1]==i or memo[1][1]==i):
			i=random.randint(0, out_step_size-1)
		encode[i]=1




file_list=[]#initialize the list that will contain the path of all files that need conversion
for root, dirs, files in os.walk(in_dir, topdown=False):#search in the directory and every subdirectory
	for name in files:
		if (name.endswith('.sm')):#add to the list all .sm files
			file_list.append(os.path.join(root, name))

print ("Files found for conversion: " + str(len(file_list)))
delay=0.009#delay (sec) for itg tuned charts
#note: POSITIVE offset mean that the chart start BEFORE the song. negative offset that the chart start after the song. The value is expressed in seconds
i=0#file counter to print a progressive value during processing
answer = input("Is the chart tuned for ITG? y/n")
for file_name in file_list:#main loop encoding all files
	f=open(file_name)
	print("\n")
	print("Encoding "+ file_name)
	i+=1
	print("File number " +str(i))
	out_data=''
	data=''
	while(data.find('NOTES')==-1):# until the notes section is reached
		data=f.readline()#read a line
#------------------------------------------------------------------------------------------------------------------------------------
		if (data.find('OFFSET')!=-1 and answer=='y'): #check for the offset value and extrapolate it. This happens only if the user request the offset correction (to use on itg tuned charts)
			while (data.find(';')==-1):
				data+=f.readline()
			offset=''
			for x in range(len(data)):
				if (data[x].isnumeric()  or data[x]=='-' or data[x]=='.'):
					offset+=data[x]
			print (data[0:-1])
			real_offset=offset.replace("-","")#remove minus sign. Necessary due to a character encoding issue that prevent conversion to float
			real_offset=float(real_offset)
			if (offset.find('-')!=-1): # if offset was negative, read the sign
				real_offset*=-1
			real_offset-=delay# real offset (songs are supposed to be tuned for ITG so a delay must be removed for SM tuning)
			print ("Real offset= "+str(real_offset))
			data="#OFFSET:"+str(real_offset)+";\n"
		out_data+=data#add line to the output
#------------------------------------------------------------------------------------------------------------------------------------------------------------
	flag2=0
	while (not flag2): #until EOF is reached keeps encoding charts, one for every iteration
		x=0
		data=f.readline()#discard the input dance type
		out_data+=dance_type#use the desired dance type
		while(x<4):#add the remining lines before the chart to the output (4 lines that end with ":")
			data=f.readline()
			if(data.find(':')!=-1):
				x+=1
			out_data+=data
		data=f.readline()
		while (len(data)!=in_step_size+1):#search for the first line of the chart (assumed as a general n_input numbers and newline). This remove eventual trailing lines
			data=f.readline()#this could give bad data since is checking only the lenght but the chances of a weird n char line that pass the encode verification is quite low not to say null
			if (data==''):# this section has as second effect the removal of charts of different types (e.g doubles) so it's necessary to check for EOF
				flag2=1
				break
		if (flag2==1):
			continue
#-----------------------------------------------------------------------------------------------------------------------------------------------------
		
		while (data.find(';')==-1): #until  the end of the chart is reached keeps encoding and writing it, one line at a time
			if (data.find("/")!=-1 or data.find(" ")!=-1):# delete stray spaces and comments
				data=data.split("/")[0]
				data=data.split(" ")[0]
				data+='\n'
			if (data.find(',')==-1):#unless an end-beat line is obtained, encode the line and write it
				encode_line(data)
				tmp_data=''
				for x in range(len(encode)):
					tmp_data+=str(encode[x])
				out_data+=tmp_data+"\n"
			else:#if an end-beat (assumed as ",\n" is found, 
				if (data!=',\n'):
					sys.exit("unexpected endbeat sintax: " + data)
				out_data+=data
			data=f.readline()#get next line
#---------------------------------------------------------------------------------------------------------	
		if (data!=';\n'):#if the  end-chart is not standard a second check for an other uncommon encoding type is done
			print("unexpected endchart sintax: " + data)
			print("Trying encoding assuming format: chart_line + \";\" + \"\\n\"")
			print("WARNING: the operation might not give an error even if the operation id succesful, manual check is suggested")#even if this encode might work, depending on the reason of the error it might cause an incorrect output
			if (len(data)==in_step_size+2):
				print("operation succesful")
				encode_line(data[0:-2]+"\n")
				for x in range(len(encode)):
					tmp_data+=str(encode[x])
				out_data+=tmp_data+"\n;\n"
			else:#if also the second encode fail an error is returned
				sys.exit("Operation failed. Unknown endchart detected")
		else:
			out_data+=data
#-----------------------------------------------------------------------------------------------------------	
		while (True):#skip lines until a new chart is found or EOF is reached
			data=f.readline()
			if (data.find('NOTES')!=-1):#if new chart is found just reapeat the loop
				out_data+=data
				break
			if(data==''):#if EOF is reached the flag to termi9nate the loop is raised
				flag2=1 #raise the EOF flag
				break
	f.close()#close the input file after reaching EOF
	f=open(file_name,"w")#overwrite the file with the new version
	f.write(out_data)
#open new file in the llist and fo at it again
