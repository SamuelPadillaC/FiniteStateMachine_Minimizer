########################################
# Created by Samuelito Perro #
########################################
# This is a Finite State Mahcine Minimizer
# Takes 3 files, the first is an FSA description, the second one is the name of the minimized FSA file, and the last one is a modifications record
# Check specifications document to understand the format of these documents

# IMPORTS #
import time, sys
import queue
from collections import deque
start = time.time()
##########################


def main ():
    # Checking for the amount of parameters #
    if len(sys.argv) != 4:
        print("\nUSAGE: Please enter 3 parameters in the following order:")
        print("1. An FSA descrption file\n2. The name of the FSA Output File \n3. The name of a modification record file")
        exit()

    # Defining paths #
    FSA_Output = sys.argv[2]
    Modification_Record = sys.argv[3]

    # Read File and Assign Values #
    vector_lines, Alphabet, States, Accepting_States = ReadFSA(sys.argv[1])

    # Create Transition Function Table #
    Transition_Function = Create_Table(vector_lines, Alphabet, States, Accepting_States)
    
    # Informing User of Succesful read of FSA #
    print("\nSUCCESFUL READ OF FSA DEFINITION FILE\n\nThe Alphabet is: ")
    print(Alphabet, "\n\nThe initial number of States is: ")
    print(States, "\n\nThe initial Acepting States are: ")
    print(Accepting_States, "\n\nThe initial Transition Function table is: ")
    print(Transition_Function)
    print("\n\n\n###############################################\n###############################################")


    ##############
    # Minimizing #
    ##############

    # Opening Record File #
    Record = open(Modification_Record, 'w+') #Opening record file

    # Getting Rid of Unreachable States and Defining New Transition_Funtion, New States, and Accepting_States #
    print ("\n\nEliminating Unreachable States...")
    Transition_Function, States, Accepting_States = Delete_Unreachable (Transition_Function, States, Accepting_States, Record)

    # Defining Initial Impossible and Possible States #
    print ("\n\nDefining Initial Possible and Impossibe pairs...")
    Possible, Impossible = Define_Impossible(States, Accepting_States)

    # Finding Redundant States #
    print ("\n\nFinding Redundant States...")
    Redundant = Find_Redundant (Possible, Impossible, Transition_Function, States, Alphabet)
    
    # Combining Redundant States #
    if len(Redundant) >= 2: #Only execute if two or more redundant states exist
        print ("\n\nEliminating Redundant States...")
        Transition_Function, States, Accepting_States = Delete_Redundant (Redundant, Transition_Function, States, Accepting_States, Record)
    else:
        print("There were no Redundant States")

    ############
    ############


    # Writing out to FSA Output File #
    Output = open(FSA_Output, 'w+')
    Output.write("%s\n" % Alphabet)
    Output.write("%s\n" % States)
    for i in Accepting_States:
        Output.write("%s " % i)
    Output.write("\n")
    for Line in Transition_Function:
        for State in Line:
            Output.write("%s " % State)
        Output.write("\n")
    #################################

    # Final Message #
    print("\n\nSuccesful run.\nCheck created FSA file and created action report file.")
    print("\n\n\n###############################################")
    print ("Execution time was: ", time.time() - start)



#########################################################
#               FUNCTION DEFINITIONS                    #
#########################################################

def ReadFSA (FSA_Description):
    # Opening the file #
    file_object = open(FSA_Description, 'r')

    vector_lines = (file_object.readlines()) # Reads all the lines into the vector vector_lines

    file_object.close()
    #Define variables
    Alphabet = ''
    for i in vector_lines[0]: #This for loop is to get rid of the extra \n at the end of the alphabet line
        if i is not '\n':
            Alphabet += i       
    States = int(vector_lines[1])
    Accepting_States = vector_lines[2].split() #Split the string by ' '

    # Check if the amount of lines in the file matches the amount of states #
    if States + 3 != len(vector_lines):
        print("\nThe FSA description file does not have the correct amount of lines.")
        print("The file should have ", States + 3, "lines and it has ", len(vector_lines), "lines.")
        exit()

    # Transforming items in Accepting_States to ints and checking if they are in the proper range 0 - (States - 1) #
    for i in range(0, len(Accepting_States)):
        if not Accepting_States[i].isdigit(): #If it is not a number
            print("\n The line 3 - Accepting States - contains invlid characters")
            exit()
        else: #Else transform into a number
            Accepting_States[i] = int(Accepting_States[i]) #Transform to int
        if Accepting_States[i] < 0 or Accepting_States[i] >= States: #If out of range
            print("\nAt least one of the Accepted states is off range")
            exit()
    
    return vector_lines, Alphabet, States, Accepting_States


#################################################
#################################################


def Create_Table (vector_lines, Alphabet, States, Accepting_States):
    
    Transition_Function = ['blank'] * States #Define transition_fucntion with fixed size equal to the number of states

    # Create Transition function table with the last n lines #
    for i in range(3, len(vector_lines)):
        Transition_Function[i-3] = vector_lines[i].split() # Separate the states by ' '
        if len(Transition_Function[i-3]) != len(Alphabet): #If the length of an item of Transition_Function does not match the size of alphabet there is something wrong.
            print("\n At least one of the last n lines doesn\'t have enough numbers")
            exit()
        # Trasform items in the nested vector of Transition_Funtion[i-3][z] into ints #
        for z in range(0, len(Transition_Function[i-3])):
            if not Transition_Function[i-3][z].isdigit(): #If it is not a number
                print("\n At least one of the last n lines contains an invalid character")
                exit()
            else: #Else transform into a number
                Transition_Function[i-3][z] = int(Transition_Function[i-3][z])

    return Transition_Function


#################################################
#################################################


def Delete_Unreachable (Transition_Function, States, Accepting_States, Record): # Breath first algorith
    # Setting things up for the algorithm #
    Q = queue.Queue(maxsize = States) # Define Queue with max size states
    Visited = [0] * States # Create Visited vercor of the size of states and mark them all as 0 (non-visited)

    # Starting by Origin, add the initial state to the queue and mark as visited #
    Q.put(0)
    Visited[0] = 1

    # While the Q has stuff in it, run breadth first algorithm
    while (not Q.empty()):
        Current_State = Q.get() # Define Current_State with the oldest element in the Q

        # Add connections of Current_Sate to the Q if they have not been visited before
        for i in Transition_Function[Current_State]:
            if Visited[i] != 1: #If this state hasn't been visited before, add to the Q and mark as visited
                Q.put(i)
                Visited[i] = 1 

    # Create New Transition Function #
    New_Transition_Function = [] #Create new table
    New_States = 0 #Create new number of States
    New_Accepting = Accepting_States #Create New_Accepting States
    Unreachable = [] #Define unreachable list
    #Create Unreachable
    for i in range(0, len(Visited)):
        if Visited[i] == 0:
            Unreachable.append(i)



    # Looping through the states in Transition_Function
    for State_index in range(0, States):
        
        #If and only if a state was marked as visited, append to the New_Transitio_Function, adjust where the state points, and add to States
        if Visited[State_index] == 1:
            
            #Readjust indexes of where the state points
            for Unreachable_Index in range(0, len(Unreachable)): #Loops through all unreachable states
                
                for letter in range(0, len(Transition_Function[State_index])): #Loops through every letter of the alphabet
                    
                    #If the State points to another state with index greater than the index of an unreachable state, readjust where it points
                    if Transition_Function[State_index][letter] > Unreachable[Unreachable_Index]:
                        Transition_Function[State_index][letter] -= 1

                # Write out that one state changed number #
                if State_index > Unreachable[Unreachable_Index]:
                    Record.write("State %s " % State_index)
                    y = State_index-1
                    Record.write("changed its number to %s \n\n" % y)

            New_Transition_Function.append(Transition_Function[State_index])
            New_States += 1

        elif Visited[State_index] == 0: #If a state was unreachable, check if there were any Accepting States above it
            Record.write("Unreachable state %s was removed\n\n" % State_index)
            for z in range(0, len(New_Accepting)):
                if New_Accepting[z] > State_index: #If there is an accepting state with index greater than an unreachable state, readjust the index by -1
                    New_Accepting[z] -= 1

    if len(Unreachable) == 0:
        Record.write("There were no Unreachable states\n\n")

    return New_Transition_Function, New_States, New_Accepting


#################################################
#################################################


def Define_Impossible (States, Accepting_States):
    # Defining Initial Variables for Algorithm
    Possible = []
    Impossible = []
    #######

    # Creating initial Possible list with all possible combinations #
    for i in range (0, States):
        combinations = [] #Initialize a buffer combinations list to store every combination as a list inside Possible[]    
        
        # Creating pairs with all states but itsef
        for z in range (i+1, States): #The +1 is avoids redundant pairs created by previous iterations of the loop.
            combinations.append([i, z])
        
        # Append only if combinations isn't empty
        if len(combinations) > 0:
            Possible.append(combinations)
    #######

    # Checking for the first group of impossible states (pairs containing an accepting state) #
    for line in Possible: #line is the first nested list of Possible
        index = 0 # Initialize a counter/index for the following while loop
        
        while 1: #Using an infinite while loop because for loops make a it harder to remove things in the list
            if index >= len(line): #Break condition for the infite loop
                break
            breaker = 0 #Bool to indicate an impossible state was found
            
            for i in Accepting_States:
                #If there is at least one accepting state in the pair, move to impossible[] and delete from line[]
                if i == line[index][0] or i == line[index][1]:
                    Impossible.append(line[index])
                    line.remove(line[index])
                    breaker = 1
                    break
            
            if breaker == 0: #If it didn't break before
                index += 1   

    return Possible, Impossible


#################################################
#################################################


def Find_Redundant (Possible, Impossible, Transition_Function, States, Alphabet):
    while 1:
        
        # Define Initial Size of Possible States #
        Impossible_Size = 0
        for i in Impossible:
            Impossible_Size += 1


        for Line in Possible: #Looks at the whole Line in Possible
            index = 0 # Initialize a counter/index for the following while loop
            
            
            while 1: #Looks at each pair in Line
                if index >= len(Line): #Break condition for the infite loop
                    break
                breaker = 0 #Bool to indicate an impossible state was found

                for i in range (0, len(Alphabet)): #Counts for every letter in the alphabet and every connection in Transition_Function
                    Pair_Looks_At = [] #Initialize every time loop starts
                    
                    for State in Line[index]: #Looks at each individual State in the Pair
                        #Look in the Transition_Function and define where that Pair is pointing for every letter of the alphabet. Append to Pair_Looks_At[]
                        Pair_Looks_At.append(Transition_Function[State][i])

                    #Check if the pair is looking at an Impossible States
                    for z in Impossible:
                        if Pair_Looks_At[0] == z[0] and Pair_Looks_At[1] == z[1] or Pair_Looks_At[0] == z[1] and Pair_Looks_At[1] == z[0]:
                            Impossible.append(Line[index]) #Append State to Impossible
                            Line.remove(Line[index])
                            breaker = 1
                            break
                        
                    # Break internal loop of the alphabet (No need to check the rest of the alphabet)                    
                    if breaker == 1:
                        break

                # If it didn't find the pair pointing to an impossible state add to index
                if breaker == 0:
                    index += 1
                
        # If no more Impossible States were found Define redundant and return
        if Impossible_Size == len(Impossible):
            Redundant = []
            # Populating Redundant with Redundant States #
            for line in Possible: #looks at all the lines in Possible
                #Only execute if the line is not empty:
                if len(line) > 0:
                    for pair in line: #Looks at each pair in line
                        for state in pair: #Looks at each state in the pair
                            append = 1 
                            #Check every item of Reduntant to see if the state was previously appended
                            for i in Redundant:
                                if i == state:
                                    append = 0
                                    break
                            #If it hasn't been appended before, append.
                            if append == 1:
                                Redundant.append(state)   
            
            return Redundant


#################################################
#################################################


def Delete_Redundant (Redundant, Transition_Function, States, Accepting_States, Record):                 
    # Sort Redundant - it is important because we will be collapsing everything onto Redundant [0]
    Redundant.sort()

    # Write to modifications ro Record file
    Record.write("State(s): ")
    for i in range (1, len(Redundant)):
        Record.write("%s " % Redundant[i])
    Record.write("was(were) collapsed into state ---> %s \n\n" % Redundant[0])


    # Deleting Redundant States and creating new Transition_Function #
    New_Transition_Function = [] #Create new table
    New_States = 0 #Create new number of States
    New_Accepting = Accepting_States
    
    for State_index in range(0, States): #Loops through the states in Transition_Function
        
        # Start counting on 1, we are collapsing everything to Redundant[0]
        for Redundant_index in range (1, len(Redundant)):

            Is_Redundant = 0 #Define Bool to find redundant states
                                
            #If a state is redundant, break the loop and mark boolean
            if Redundant[Redundant_index] == State_index:
                Is_Redundant = 1
                break

            # Write out that one state changed number
            elif State_index > Redundant[Redundant_index] and i == len(Redundant)-1:
                breaker = 0

                #Check all redundant states to avoid including infor for an unreachable state
                for i in range (1, len(Redundant)):
                    if State_index == Redundant[i]:
                        breaker = 1
                        break

                if breaker == 0:        
                    Record.write("State %s " % State_index)
                    y = State_index - 1
                    Record.write("changed its number to %s \n\n" % y)


        #If and only if a state is not redundant, append to the New_Transitio_Function, and add to States
        if Is_Redundant == 0:
            New_Transition_Function.append(Transition_Function[State_index])
            New_States += 1

        else: #If a state was redundant, check if there were any Accepting States above it
                for z in range(0, len(New_Accepting)):
                    if New_Accepting[z] > State_index: #If there is an accepting state with index greater than an unreachable state, readjust the index by -1
                        New_Accepting[z] -= 1
    


    # Redirecting States that point to a Redundant State #
    for State in range(0, len(New_Transition_Function)): #Looks at every state (line) in the Transition_Function
        for Points_At in range(0, len(New_Transition_Function[State])): #Looks at where the state points to for every letter in the alphabet
            
            # Here we start counting on 1 because we are collapsing everything to Redundant[0]
            for i in range(1, len(Redundant)):
    
                # Redirecting states that point to a redundant state to Redundant[0]
                if New_Transition_Function[State][Points_At] == Redundant[i]:
                    New_Transition_Function[State][Points_At] = Redundant[0]
                    break
            
            # Readjusting states that point to a state with index greater than the index of the redundant states
            for i in range(1, len(Redundant)): #Run in different loops to avoid conflicting
                if New_Transition_Function[State][Points_At] > Redundant[i] and New_Transition_Function[State][Points_At] != Redundant[0]:
                    New_Transition_Function[State][Points_At] -= 1
    

    return New_Transition_Function, New_States, Accepting_States

#################################################
#################################################
# Calling the main function first #
if __name__ == "__main__":
    main ()
#####################