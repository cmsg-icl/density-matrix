#!/usr/bin/env python3
# -*- coding: utf-8 -*-
def cry_combine_density(density1,density2,density3,new_density='new_density.f98'):
    import sys
    import numpy as np
    
    try:
        '''file = open(density1, 'r')
        density1_data = file.readlines()
        file.close()
        file = open(density2, 'r')
        density2_data = file.readlines()
        file.close()'''
        density1_data = Density(density1).cry_read_density() #substrate
        density2_data = Density(density2).cry_read_density()
        density3_data_obj = Density(density2).cry_read_density()
        file = open(density3, 'r')
        density3_data = file.readlines()
        file.close()
    except:
        print('EXITING: a CRYSTAL .f98 file needs to be specified')
        sys.exit(1)

    #Find P_irr <-> atom correspondence
    fragment_1 = []
    fragment_2 = []

    for i,j in enumerate(density1_data.ncf):
        #density1_data.la3[j] is the shell number
        #density1_data.atom_shell[density1_data.la3[j]] is the atom position number (1-6)
        #density1_data.ghost[density1_data.atom_shell[density1_data.la3[j]]] is either 0 or atomic number depending on ghost or not
        #This tells me if the shell belongs to this fragment
        n_elements = density1_data.nstatg[i] - density1_data.nstatg[i - 1]

        #print(i, j, len(density1_data.la3), len(density1_data.la4), len(density1_data.atom_shell),
              #len(density1_data.ghost))
        '''print(i, j,
              density1_data.la3[j-1],
              density1_data.la4[j-1],
              density1_data.atom_shell[density1_data.la3[j-1]-1],
              density1_data.ghost[density1_data.atom_shell[density1_data.la3[j-1]-1]-1])'''
        if density1_data.ghost[density1_data.atom_shell[density1_data.la3[j-1]-1]-1] == 0 and \
            density1_data.ghost[density1_data.atom_shell[density1_data.la4[j-1]-1]-1] == 0:
            fragment_1.extend([True]*n_elements)
        else:
            fragment_1.extend([False]*n_elements)
        if density1_data.ghost[density1_data.atom_shell[density1_data.la3[j-1]-1]-1] != 0 and \
            density1_data.ghost[density1_data.atom_shell[density1_data.la4[j-1]-1]-1] != 0:
            fragment_2.extend([True]*n_elements)
        else:
            fragment_2.extend([False]*n_elements)
    '''for i in range(len(fragment_2)):
        if fragment_1[i] == True and fragment_2==True:
            print(fragment_1[i],fragment_2[i])'''
    beginning = density3_data.index('SPINOR\n')
    end = density3_data.index('   NCF\n')
    sum_density = np.array(density1_data.p_irr)+np.array(density2_data.p_irr)
    sum_fock = np.array(density1_data.f_irr)+np.array(density2_data.f_irr)
    sum_charges = np.array(density1_data.charges)+np.array(density2_data.charges)
    #sum_charges = [12.,12.,8.,8.,8,8.]
    spinor = ['SPINOR\n']
    charges = []
    fock = []
    density = []
    new_fock = sum_fock #TMP
    new_fock = [0] * len(density1_data.f_irr)
    new_p = []
    #print(len(density2_data.f_irr),len(fragment_1))
    for i in range(len(fragment_1)):
        if fragment_1[i] == True and fragment_2[i] == False:
            #new_fock.append(density1_data.f_irr[i])
            new_p.append(density1_data.p_irr[i])
        elif fragment_1[i] == False and fragment_2[i] == True:
            ##new_fock.append(density2_data.f_irr[i])
            new_p.append(density2_data.p_irr[i])
        elif fragment_1[i] == False and fragment_2[i] == False:
            #new_fock.append(0.)
            new_p.append(sum_density[i])
            #new_p.append(0.)
            #new_p.append(density3_data_obj.p_irr[i])

    for i in range(0,len(density1_data.spin),8):
        spinor.append(' '.join([str(x) for x in density1_data.spin[i:i+8]])+'\n')
    for i in range(0,len(sum_charges),4):
        charges.append(' '.join(["{:.13e}".format(x) for x in sum_charges[i:i+4]])+'\n')
    for i in range(0,len(new_fock),4):
        fock.append(' '.join(["{:.13e}".format(x) for x in new_fock[i:i+4]])+'\n')
    for i in range(0,len(new_p),4):
        density.append(' '.join(["{:.13e}".format(x) for x in new_p[i:i+4]])+'\n')
    
    final_fort98 = density3_data[0:beginning]+spinor+charges+fock+density+density3_data[end:] 
    with open(new_density, 'w') as file:
        for line in final_fort98:
            file.writelines(line)
