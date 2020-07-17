"""
July 12, 2020
"""

"""
This python script generates a synthetic TIS dataset for training a prediction model.
It makes use of consensus sequence, upstream start codon, downstream stop codon, splice site, and nucleotide frequency to generate the dataset.
It takes a file containing the position weight matrix (pwm).
It creates two files as outputs, each containing the positive and negative samples.

It is a more simplified, randomized version of GenerateTIS.py
"""


'''
This function turns a file with consensus into a dictionary.
It reads a file containing pwm and length of consensus sequence 'l' (default: 10).
The pwm must have the nucleotides in the first column and following columns have the weights. Each column is separated by an empty space.
It outputs a dictionary containing the weights with positions as key and a list of weights as value.
'''
def readConsensus(file,l):

    #Get a list of the positions of consensus sequence
    #   Exclude the TIS site
    #   To be used to insert the consensus into the right position
    position = [j for j in range(-l, l + 3) if j not in [0, 1, 2]]

    #Make an empty list cons that will have each sequence into a list
    cons = []
    count = 0       #will check that the file has 4 rows
    for row in open(file, 'r').readlines():
        cons += [row.split(' ')]
        count += 1
    assert count == 4, 'There should be 4 rows, one for each nucleotide'

    #This section sees how the pwm is ordered.
    #   It will give a number for each nucleotide so that the values from the pwm match the correct nucleotide
    #Each nucleotide is ordered as seen (from 0-3)
    A,C,G,T = 0,1,2,3
    order = []
    #In the list 'order' numbers 0-3, which indicate for a nucleotide each, will be inserted according to the order of pwm
    for nuc in range(0,4):
        if cons[nuc][0] == 'A':
            order.append(A)
        elif cons[nuc][0] == 'C':
            order.append(C)
        elif cons[nuc][0] == 'G':
            order.append(G)
        elif cons[nuc][0] == 'T':
            order.append(T)
    #Ordered consensus sequence with rows A,C,G,T
    cons = [cons[i] for i in order]

    #Dictionary for the consensus sequence
    consensus = dict()
    #A loop along the weights from each row on the same column
    for k in range(1, l*2+1):
        nucleotide = []         #list as value of dictionary consensus
        for seq in cons:
            nucleotide.append(float(seq[k]))
        #Add the weights
        consensus[position[k-1]] = nucleotide

    return consensus


'''
This function forms the basic structure of the synthetic sequence.
It takes in the start codon and a certain length where len(seq) = length*2+3.
'''
def BasicStructure(start, length):

    seq = []
    seq += 'u' * length     #upstream sequence
    seq += start            #start codon
    seq += 'd' * length     #downstream sequence

    #print("".join(i for i in seq))
    return seq


'''
This function takes in either four numbers (probabilities) or a list of the four numbers
and gives a certain nucleotide that could be selected based on the probability.
'''
def PWMtoBase(A,C=None,G=None,T=None):
    import random

    #If only a list is given, then separate it into the corresponding nucleotide.
    if C == None and type(A) is list:
        C,G,T = A[1],A[2],A[3]
        A = A[0]

    total = A+C+G+T
    prob = random.uniform(1,total)
    if prob <= A:
        return 'A'
    elif prob > A and prob <= A+C:
        return 'C'
    elif prob > A+C and prob <= A+C+G:
        return 'G'
    else:
        return 'T'


'''
This function adds the consensus sequence around the start codon for the positive sample.
It takes a certain length (len(seq) = length*2+3), a sequence, a file with consensus, and l which is the length of consensus.
'''
def ConsensusSequence(length, seq, conFile, l):
    consensus = readConsensus(conFile, l)       #consensus sequence into a dictionary

    #keys span from negative to positive number, with ATG being 0,1,2
    for i in consensus.keys():
        seq[length+i] = PWMtoBase(consensus[i][0],consensus[i][1],consensus[i][2],consensus[i][3])

    #print("".join(i for i in seq)+"hey?")
    return seq


'''
This function adds the upstream start codon to the positive samples.
It takes in the start codon, length, sequence, and the length of consensus sequence.
'''
def UpstreamStart(start, length, seq, l):
    import random

    #there can be up to two upstream start codons
    n = random.randint(0,2)

    #set in_len so that consensus sequence and any codon overlaping it will be disregarded for insert site.
    in_len = int((length-(l+5))/3)      #divide by 3 to select each codon not nucleotide

    #select random codon position to insert start codon
    if n == 1:
        pos1 = random.randint(0, in_len)        #0-45 -> 0-135
        seq[pos1*3:pos1*3+3] = start
    elif n == 2:
        pos1 = random.randint(0, in_len-1)
        pos2 = random.randint(pos1+1, in_len)
        seq[pos1*3:pos1*3+3] = start
        seq[pos2*3:pos2*3+3] = start

    #print("".join(i for i in seq))
    return seq


'''
This function adds a downstream stop codon for negative samples.
It takes a list of stop codons, length, sequence, and length of consensus.
'''
def DownstreamStop(stop_list, length, seq, l):
    import random

    stop = random.choice(stop_list)     #select a random stop codon

    #select a random codon position
    in_len = int(length/3)
    stop_site = random.randint(in_len+int((l+5)/3), in_len*2)     #54-100
    seq[stop_site*3:stop_site*3+3] = stop

    #print(seq)
    #print("".join(i for i in seq))
    return seq

"""
'''
This function adds splice site consensus sequence to upstream for negative and downstream for positive sample.
It takes in length, sequence, length of consensus, and either pos or neg to indicate the sample.
'''
def SpliceSite(length, seq, l, train):
    import random

    #splice site consensus sequence (exons only)
    splice = [[352,361,154,132], [621,131,87,159], [85,45,777,91],
              [242,87,549,120],[251,156,163,428]]

    #add splice site downstream for positive and upstream for negative sample
    if train == 'pos':
        n = random.randint(length+l+3, length*2-3)
    else:
        n = random.randint(0, length-16)

    for i,s in enumerate(splice):
        seq[n+i] = PWMtoBase(s)

    return seq
"""

'''
This function is used to fill all the bases in the sequence other than those already filled.
It takes in length, sequence, and either pos or neg to indicate the sample.
'''
def Fill(length, seq, train):

    #negative training set
    if train == 'neg':
        for i in range(0,len(seq)):
            if seq[i] not in ['u','d']:     #do not add bases in positions already filled
                continue
            #fill with probability for both upstream and downstream of start codon
            if i in range(0, length):
                seq[i] = PWMtoBase(31.4,18.4,18.5,31.7)
            elif i in range(length+3, len(seq)):
                seq[i] = PWMtoBase(31.3,18.1,18.5,31.4)
        #print("".join(i for i in seq))
        return seq

    #for positive training set
    for j in range(0, len(seq)):
        if seq[j] not in ['u','d']:     #do not add bases in positions already filled
            continue
        # fill with probability for both upstream and downstream of start codon
        if j in range(0, length):
            seq[j] = PWMtoBase(31.1,19.6,15.5,33.8)
        elif j in range(length + 3, len(seq)):
            seq[j] = PWMtoBase(26.1,23.0,20.4,29.7)
    #print("".join(i for i in seq))
    return seq


'''
This function generates TIS sequence by combining the above functions.
It takes in either 'pos' or 'neg, length, file containing consensus, and length of consensus sequence.
'''
def Generate(train, length, conFile, l):

    start = ['A','T','G']
    stop_list = [['T', 'A', 'A'], ['T', 'A', 'G'], ['T', 'G', 'A']]

    #generate the sequence
    seq = BasicStructure(start, length)
    #Positive set has consensus and upstream start codon
    if train == 'pos':
        seq = ConsensusSequence(length, seq, conFile, l)
        seq = UpstreamStart(start, length, seq, l)
    #Negative set has downstream stop codon
    if train == 'neg':
        seq = DownstreamStop(stop_list, length, seq, l)
    """seq = SpliceSite(length, seq, l, train)"""
    seq = Fill(length, seq, train)

    return seq


'''
This function writes the generated TIS dataset into a file.
It takes in the number of sequences, a file containing consensus, output files for positive and negative set, length and length of consensus.
It outputs the two file containing synthetic datasets.
'''
def WriteTIS(rows, conFile, posFile, negFile, length=150, l=10):

    #length must be kept at multiples of 3 (codon)
    assert length%3==0, 'length must be a multiplier of 3'

    tis_pos = open(posFile, "w+")
    tis_neg = open(negFile, "w+")

    stop_list = ['TAA', 'TAG', 'TGA']

    #Generate TIS dataset
    for i in range(0, rows):
        positive = "".join(i for i in Generate('pos',length,conFile,l))
        negative = "".join(j for j in Generate('neg',length,conFile,l))

        for p in range(0, len(positive), 3):
            if p >= length+3 and positive[p:p + 3] in stop_list:
                positive = positive[:p] + PWMtoBase(26.1, 23.0, 20.4, 29.7) \
                           + PWMtoBase(26.1, 23.0, 20.4, 29.7) \
                           + PWMtoBase(26.1, 23.0, 20.4, 29.7) + positive[p + 3:]

        tis_pos.write(positive+'\n')
        tis_neg.write(negative+'\n')
    tis_pos.close()
    tis_neg.close()


#Generate('pos')
#Generate('neg')
WriteTIS(27000,'consensus.txt','arab_TISrand.pos','arab_TISrand.neg',150,10)
#check()